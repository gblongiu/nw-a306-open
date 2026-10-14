/* SPDX-License-Identifier: GPL-2.0-or-later
 * Test-only software-rendered Rockbox -> Linux KMS dumb-buffer scanout.
 * Restricted to the generic QEMU guest and virtio_gpu; no Sony settings.
 */
#include <SDL.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <poll.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
/* Raw pinned UAPI headers carry sparse annotations removed by headers_install. */
#ifndef __user
#define __user
#endif
#include "drm.h"
#include "drm_mode.h"
#include "drm_fourcc.h"

struct buffer { uint32_t handle, fb, pitch; uint64_t size; void *map; };
static struct buffer buffers[2];
static int fd=-1, current;
static uint32_t connector;
static struct drm_mode_crtc saved;
static FILE *logfile;
static unsigned frames;
static int width, height;

static void fail(const char *why)
{
    fprintf(stderr,"M6_KMS_ERROR %s: %s\n",why,strerror(errno));
    exit(102);
}
static void control(unsigned long request, void *arg, const char *why)
{
    int rc; do { rc=ioctl(fd,request,arg); } while(rc<0 && errno==EINTR);
    if(rc<0) fail(why);
}
static void cleanup(void)
{
    if(fd<0) return;
    /* This guest started with one virtual connector. Restore its original CRTC,
     * including the disabled state. Never reuse this assumption on a real board. */
    saved.set_connectors_ptr=(uintptr_t)&connector;
    saved.count_connectors=saved.mode_valid?1:0;
    int restored=ioctl(fd,DRM_IOCTL_MODE_SETCRTC,&saved);
    for(int i=0;i<2;i++) {
        if(buffers[i].map && buffers[i].map!=MAP_FAILED)
            munmap(buffers[i].map,buffers[i].size);
        if(buffers[i].fb) ioctl(fd,DRM_IOCTL_MODE_RMFB,&buffers[i].fb);
        if(buffers[i].handle) {
            struct drm_mode_destroy_dumb d={.handle=buffers[i].handle};
            ioctl(fd,DRM_IOCTL_MODE_DESTROY_DUMB,&d);
        }
    }
    int dropped=ioctl(fd,DRM_IOCTL_DROP_MASTER,0);
    close(fd); fd=-1;
    if(logfile) {
        fprintf(logfile,"CLEANUP frames=%u restore=%d drop_master=%d\n",frames,restored,dropped);
        fclose(logfile); logfile=NULL;
    }
}
static void initialize(void)
{
    char model[64]={0}; FILE *f=fopen("/proc/device-tree/model","rb");
    if(!f || !fread(model,1,sizeof(model)-1,f)) fail("guest model");
    fclose(f);
    if(strcmp(model,"linux,dummy-virt")) fail("not the generic QEMU machine");
    fd=open("/dev/dri/card0",O_RDWR|O_CLOEXEC);
    if(fd<0) fail("open virtual DRM card");
    char name[64]={0};struct drm_version v={.name_len=sizeof(name)-1,.name=name};
    control(DRM_IOCTL_VERSION,&v,"driver identity");
    if(strcmp(name,"virtio_gpu")) fail("not virtio_gpu");
    logfile=fopen("/run/kms.log","wx"); if(!logfile) fail("log");
    struct drm_get_cap cap={.capability=DRM_CAP_DUMB_BUFFER};
    control(DRM_IOCTL_GET_CAP,&cap,"dumb capability");
    if(!cap.value) fail("no dumb buffers");
    control(DRM_IOCTL_SET_MASTER,NULL,"DRM master");
    struct drm_mode_card_res r={0};control(DRM_IOCTL_MODE_GETRESOURCES,&r,"resources count");
    if(r.count_connectors!=1 || !r.count_crtcs || r.count_crtcs>16) fail("unsupported resource topology");
    uint32_t cs[16],es[16],con[1],fbs[64];
    if(r.count_encoders>16 || r.count_fbs>64) fail("resource bounds");
    r.crtc_id_ptr=(uintptr_t)cs;r.encoder_id_ptr=(uintptr_t)es;
    r.connector_id_ptr=(uintptr_t)con;r.fb_id_ptr=(uintptr_t)fbs;
    control(DRM_IOCTL_MODE_GETRESOURCES,&r,"resources");
    if(r.count_connectors!=1 || !r.count_crtcs || r.count_crtcs>16 ||
       r.count_encoders>16 || r.count_fbs>64) fail("changed resource counts");
    connector=con[0];
    struct drm_mode_get_connector c={.connector_id=connector};
    control(DRM_IOCTL_MODE_GETCONNECTOR,&c,"connector count");
    if(c.connection!=1 || !c.count_modes || c.count_modes>64 ||
       c.count_props>128 || c.count_encoders>16) fail("connector bounds");
    struct drm_mode_modeinfo modes[64];uint32_t props[128],encoders[16];uint64_t values[128];
    c.modes_ptr=(uintptr_t)modes;c.props_ptr=(uintptr_t)props;
    c.prop_values_ptr=(uintptr_t)values;c.encoders_ptr=(uintptr_t)encoders;
    control(DRM_IOCTL_MODE_GETCONNECTOR,&c,"connector modes");
    if(!c.count_modes || c.count_modes>64 || c.count_props>128 ||
       !c.count_encoders || c.count_encoders>16) fail("changed connector counts");
    int selected=-1;
    for(unsigned i=0;i<c.count_modes;i++) {
        fprintf(logfile,"MODE %ux%u clock=%u flags=%u\n",modes[i].hdisplay,modes[i].vdisplay,modes[i].clock,modes[i].flags);
        if(modes[i].hdisplay==320 && modes[i].vdisplay==480) selected=i;
    }
    if(selected<0) fail("no advertised 320x480 mode");
    struct drm_mode_get_encoder encoder={.encoder_id=c.encoder_id?c.encoder_id:encoders[0]};
    control(DRM_IOCTL_MODE_GETENCODER,&encoder,"encoder");
    int crtc=-1;
    for(unsigned i=0;i<r.count_crtcs;i++)if(encoder.possible_crtcs&(1U<<i)){crtc=i;break;}
    if(crtc<0) fail("no compatible CRTC");
    saved.crtc_id=cs[crtc];control(DRM_IOCTL_MODE_GETCRTC,&saved,"save CRTC");
    width=modes[selected].hdisplay;height=modes[selected].vdisplay;
    atexit(cleanup);
    for(int i=0;i<2;i++) {
        struct drm_mode_create_dumb d={.width=width,.height=height,.bpp=32};
        control(DRM_IOCTL_MODE_CREATE_DUMB,&d,"create dumb");
        buffers[i].handle=d.handle;buffers[i].pitch=d.pitch;buffers[i].size=d.size;
        if(d.pitch<(unsigned)width*4 || d.size<(uint64_t)d.pitch*height || d.size>64*1024*1024)
            fail("invalid dumb layout");
        struct drm_mode_map_dumb map={.handle=d.handle};
        control(DRM_IOCTL_MODE_MAP_DUMB,&map,"map offset");
        buffers[i].map=mmap(NULL,d.size,PROT_READ|PROT_WRITE,MAP_SHARED,fd,map.offset);
        if(buffers[i].map==MAP_FAILED) fail("mmap dumb");
        memset(buffers[i].map,0,d.size);
        struct drm_mode_fb_cmd2 fb={.width=width,.height=height,.pixel_format=DRM_FORMAT_XRGB8888};
        fb.handles[0]=d.handle;fb.pitches[0]=d.pitch;
        control(DRM_IOCTL_MODE_ADDFB2,&fb,"XRGB8888 framebuffer acceptance");buffers[i].fb=fb.fb_id;
    }
    struct drm_mode_crtc first={.crtc_id=saved.crtc_id,.fb_id=buffers[0].fb,
        .set_connectors_ptr=(uintptr_t)&connector,.count_connectors=1,.mode_valid=1,.mode=modes[selected]};
    control(DRM_IOCTL_MODE_SETCRTC,&first,"set advertised mode");
    fprintf(logfile,"READY driver=%s mode=%dx%d format=XRGB8888 pitch=%u crtc=%u connector=%u\n",
            name,width,height,buffers[0].pitch,saved.crtc_id,connector);fflush(logfile);
    f=fopen("/dev/ttyAMA0","w");if(f){fputs("M6_KMS_READY\n",f);fclose(f);}
}

void m4_present(SDL_Renderer *renderer);
void __wrap_SDL_RenderPresent(SDL_Renderer *renderer)
{
    if(getenv("M6_DRM_GUEST")) {
        if(strcmp(getenv("M6_DRM_GUEST"),"generic-arm64-vm")) fail("invalid test guard");
        if(fd<0)initialize();
        int w,h;
        if(SDL_GetRendererOutputSize(renderer,&w,&h) || w!=width || h!=height) fail("renderer/mode alignment");
        int next=current^1;struct buffer *b=&buffers[next];
        if(SDL_RenderReadPixels(renderer,NULL,SDL_PIXELFORMAT_ARGB8888,b->map,b->pitch)) fail("read application pixels");
        uint32_t hash=2166136261U;
        for(int y=0;y<height;y++)for(int x=0;x<width;x++) {
            uint32_t pixel=((uint32_t*)((char*)b->map+y*b->pitch))[x];
            for(int shift=16;shift>=0;shift-=8){hash^=(pixel>>shift)&255;hash*=16777619U;}
        }
        struct drm_mode_fb_dirty_cmd dirty={.fb_id=b->fb};
        control(DRM_IOCTL_MODE_DIRTYFB,&dirty,"notify damage");
        struct drm_mode_crtc_page_flip flip={.crtc_id=saved.crtc_id,.fb_id=b->fb,.flags=DRM_MODE_PAGE_FLIP_EVENT};
        control(DRM_IOCTL_MODE_PAGE_FLIP,&flip,"page flip");
        struct pollfd p={.fd=fd,.events=POLLIN};int ready;
        do{ready=poll(&p,1,2000);}while(ready<0 && errno==EINTR);
        if(ready!=1)fail("page flip deadline");
        unsigned char event[4096];ssize_t n=read(fd,event,sizeof(event));
        if(n<(ssize_t)sizeof(struct drm_event))fail("short DRM event");
        struct drm_event *e=(void*)event;
        if(e->type!=DRM_EVENT_FLIP_COMPLETE || e->length<sizeof(*e) ||
           e->length>(unsigned)n)fail("unexpected DRM event");
        current=next;fprintf(logfile,"PRESENT frame=%u rgb_fnv1a32=%08x fb=%u\n",++frames,hash,b->fb);fflush(logfile);
    }
    m4_present(renderer);
}
