#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <omp.h>

#include "img_trans_v2.h"

static long num_pasos=1.5E9;
#define NUM_THREADS 1500
#define NUM_IMAGES 10

int main() {
    double t1, t2, tiempo;

    const char *imagenes[NUM_IMAGES] = {
        "img1.bmp", "img2.bmp", "img3.bmp", "img4.bmp", "img5.bmp",
        "img6.bmp", "img7.bmp", "img8.bmp", "img9.bmp", "img10.bmp"
    };

    t1 = omp_get_wtime();

    for (int i = 0; i < NUM_IMAGES; i++) {
        img2gray(imagenes[i]);

        char out_h_bn[50], out_v_bn[50], out_h_color[50], out_v_color[50];
        sprintf(out_h_bn, "grises_h_%d.bmp", i);
        sprintf(out_v_bn, "grises_v_%d.bmp", i);
        sprintf(out_h_color, "orig_h_%d.bmp", i);
        sprintf(out_v_color, "orig_v_%d.bmp", i); 
     
        #pragma omp parallel
        {
            #pragma omp sections
            {
                #pragma omp section
                {
                    invHorizontal("img_grises.bmp", out_h_bn);
                }
                #pragma omp section
                {
                    invVertical("img_grises.bmp", out_v_bn);
                }
                #pragma omp section
                {
                    invHorizontal(imagenes[i], out_h_color);
                }
                #pragma omp section
                {
                    invVertical(imagenes[i], out_v_color);
                }
            }
        }

        //desenfoque("img_grises.bmp", 15);
    }

    t2 = omp_get_wtime();
    tiempo = t2 - t1;

    printf("\nProcesamiento terminado\n");
    printf("Cant de threads: %d\n", NUM_THREADS);
    printf("Tiempo de procesamiento: %lf segundos\n", tiempo);
    return 0;
}