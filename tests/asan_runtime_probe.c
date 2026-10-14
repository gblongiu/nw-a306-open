/* SPDX-License-Identifier: GPL-2.0-or-later */
/* Intentional negative cases to verify instrumentation, unrelated to Rockbox. */
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv)
{
    puts("probe entered main");
    fflush(stdout);
    if (argc > 1 && !strcmp(argv[1], "overflow")) {
        volatile int value = INT_MAX;
        volatile int result = value + 1;
        return result == 0;
    }
    int *values = calloc(16, sizeof(*values));
    if (!values)
        return 2;
    volatile int index = argc > 1 ? 16 : 0;
    values[index] = 7;
    printf("value=%d\n", values[0]);
    free(values);
    return 0;
}
