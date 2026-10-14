/* SPDX-License-Identifier: GPL-2.0-or-later
 * Generic VM test only: uinput -> kernel evdev -> SDL -> Rockbox buttons.
 * Refuses to run outside the explicitly named generic test guest.
 */
#include "config.h"
#include "button.h"
#include <SDL.h>
#include <linux/uinput.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <unistd.h>
#include <poll.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

static atomic_bool done, running;
static pthread_t worker;
static FILE *logfile;
static pthread_mutex_t log_lock = PTHREAD_MUTEX_INITIALIZER;
static void fail(const char *what) { perror(what); _Exit(101); }
static void emit(int fd, unsigned short type, unsigned short code, int value)
{
    struct input_event e = { .type=type, .code=code, .value=value };
    if (write(fd, &e, sizeof(e)) != sizeof(e)) fail("uinput write");
}
static void report(int fd, int x, int y, int pressed)
{
    emit(fd, EV_ABS, ABS_X, x); emit(fd, EV_ABS, ABS_Y, y);
    emit(fd, EV_KEY, BTN_TOUCH, pressed); emit(fd, EV_SYN, SYN_REPORT, 0);
}
static void *input_worker(void *unused)
{
    (void)unused;
    int ui=open("/dev/uinput", O_WRONLY|O_NONBLOCK);
    if (ui<0) fail("uinput open");
    if (ioctl(ui, UI_SET_EVBIT, EV_KEY)<0 || ioctl(ui, UI_SET_KEYBIT, BTN_TOUCH)<0 ||
        ioctl(ui, UI_SET_EVBIT, EV_ABS)<0 || ioctl(ui, UI_SET_ABSBIT, ABS_X)<0 ||
        ioctl(ui, UI_SET_ABSBIT, ABS_Y)<0) fail("uinput capabilities");
    struct uinput_user_dev dev={0};
    strcpy(dev.name,"M5 generic synthetic touch"); dev.id.bustype=BUS_VIRTUAL;
    dev.absmax[ABS_X]=319; dev.absmax[ABS_Y]=479;
    if(write(ui,&dev,sizeof(dev))!=sizeof(dev) || ioctl(ui, UI_DEV_CREATE)<0) fail("uinput create");
    int ev=-1;
    for (int retry=0; retry<40 && ev<0; retry++) {
        for (int i=0;i<16;i++) {
            char path[64],name[128]={0}; snprintf(path,sizeof(path),"/dev/input/event%d",i);
            int fd=open(path,O_RDONLY|O_NONBLOCK);
            if(fd<0) continue;
            if(ioctl(fd,EVIOCGNAME(sizeof(name)),name)>=0 && !strcmp(name,dev.name)) ev=fd;
            else close(fd);
        }
        if(ev<0) SDL_Delay(25);
    }
    if(ev<0) fail("synthetic evdev not discovered");
    struct input_absinfo ax,ay;
    if(ioctl(ev,EVIOCGABS(ABS_X),&ax)<0 || ioctl(ev,EVIOCGABS(ABS_Y),&ay)<0 ||
       ax.minimum!=0 || ax.maximum!=319 || ay.minimum!=0 || ay.maximum!=479)
        fail("unexpected synthetic dimensions");
    fprintf(logfile,"CAPS x=0..319 y=0..479 BTN_TOUCH\n"); fflush(logfile);
    Uint32 start=SDL_GetTicks(); unsigned step=0; int x=0,y=0,pressed=0,last=0;
    while(!atomic_load(&done) && SDL_GetTicks()-start<20000) {
        Uint32 age=SDL_GetTicks()-start;
        /* Two centre taps (pause/resume), followed by a drag/release.
         * Coordinates are synthetic SDL application dimensions, never Sony values. */
        static const unsigned times[]={1500,1650,2500,2650,3500,3650,3800,3950};
        static const int xs[]={160,160,160,160,80,140,220,220};
        static const int ys[]={240,240,240,240,300,300,300,300};
        static const int downs[]={1,0,1,0,1,1,1,0};
        if(step<8 && age>=times[step]) {
            report(ui,xs[step],ys[step],downs[step]); step++;
        }
        struct pollfd p={.fd=ev,.events=POLLIN};
        if(poll(&p,1,10)<0 && errno!=EINTR) fail("evdev poll");
        struct input_event e;
        ssize_t n;
        while((n=read(ev,&e,sizeof(e)))>0) {
            if(n!=sizeof(e)) fail("short input event");
            fprintf(logfile,"EV type=%u code=%u value=%d\n",e.type,e.code,e.value);
            if(e.type==EV_SYN && e.code==SYN_DROPPED) fail("lost input synchronization");
            if(e.type==EV_ABS && e.code==ABS_X) x=e.value;
            if(e.type==EV_ABS && e.code==ABS_Y) y=e.value;
            if(e.type==EV_KEY && e.code==BTN_TOUCH) pressed=e.value!=0;
            if(e.type==EV_SYN && e.code==SYN_REPORT) {
                if(x<0 || x>319 || y<0 || y>479) fail("out of range input");
                SDL_Event s; SDL_zero(s);
                if(pressed!=last) {
                    s.type=pressed?SDL_MOUSEBUTTONDOWN:SDL_MOUSEBUTTONUP;
                    s.button.button=SDL_BUTTON_LEFT; s.button.x=x; s.button.y=y;
                } else {
                    s.type=SDL_MOUSEMOTION; s.motion.x=x; s.motion.y=y;
                    s.motion.state=pressed?SDL_BUTTON_LMASK:0;
                }
                if(SDL_PushEvent(&s)!=1) fail("SDL input queue");
                fprintf(logfile,"SDL type=%u x=%d y=%d down=%d\n",s.type,x,y,pressed);
                fflush(logfile); last=pressed;
            }
        }
        if(n<0 && errno!=EAGAIN && errno!=EINTR) fail("evdev read");
    }
    close(ev); if(ioctl(ui,UI_DEV_DESTROY)<0) fail("uinput destroy"); close(ui);
    return NULL;
}

int __real_SDL_InitSubSystem(Uint32 flags);
int __wrap_SDL_InitSubSystem(Uint32 flags)
{
    int rc=__real_SDL_InitSubSystem(flags);
    if(!rc && (flags & SDL_INIT_VIDEO) && getenv("M5_TEST_GUEST") &&
       !atomic_exchange(&running,true)) {
        if(strcmp(getenv("M5_TEST_GUEST"),"generic-arm64-vm")) fail("guest guard");
        logfile=fopen("/run/evdev.log","wx");
        if(!logfile || pthread_create(&worker,NULL,input_worker,NULL)) fail("input worker");
    }
    return rc;
}
void __real_SDL_Quit(void);
void __wrap_SDL_Quit(void)
{
    if(atomic_load(&running)) {
        atomic_store(&done,true); pthread_join(worker,NULL);
        pthread_mutex_lock(&log_lock);
        atomic_store(&running,false);
        fprintf(logfile,"CLEANUP complete\n"); fclose(logfile); logfile=NULL;
        pthread_mutex_unlock(&log_lock);
    }
    __real_SDL_Quit();
}

int __real_button_read_device(int *data);
int __wrap_button_read_device(int *data)
{
    int btn=__real_button_read_device(data);
    static int last=-1,coords=-1;
    pthread_mutex_lock(&log_lock);
    if(logfile && atomic_load(&running) && (btn!=last || *data!=coords)) {
        fprintf(logfile,"ROCKBOX button=%d xy=%d,%d\n",btn,(*data>>16)&65535,*data&65535);
        fflush(logfile); last=btn; coords=*data;
    }
    pthread_mutex_unlock(&log_lock);
    return btn;
}

/* Observe consumption by the ordinary WPS UI, without replacing drawing. */
int __real_audio_take_decoder_error(void);
int __wrap_audio_take_decoder_error(void)
{
    int error=__real_audio_take_decoder_error();
    if(error<0) {
        fprintf(stderr,"M5_UI_ERROR_CONSUMED status=%d\n",error); fflush(stderr);
    }
    return error;
}
