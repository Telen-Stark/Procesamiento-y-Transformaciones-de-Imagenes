/* POOKIES: bridge between PySide6 and the original C/OpenMP functions.
   Compile from the same folder as img_trans_v2.h. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <omp.h>
#include "img_trans_v2.h"

static int exists_nonempty(const char *name) {
    char path[140];
    snprintf(path, sizeof(path), "img/%s", name);
    FILE *f = fopen(path,"rb");
    if (!f) return 0;
    if (fseek(f, 0, SEEK_END) != 0) {fclose(f);return 0;}
    long sz = ftell(f); fclose(f);
    return sz > 54;
}

int main(int argc, char **argv) {
    if (argc != 4 && argc != 5) {
        fprintf(stderr, "Uso: ./pookies_engine [all|gray|hcolor|hgray|vcolor|vgray|bcolor|bgray|edge_x|edge_y] [threads] [archivo.bmp]\n");
        return 2;
    }
    const char *op = argv[1];
    int threads = atoi(argv[2]);
    const char *source = argv[3];
    int kernel = argc == 5 ? atoi(argv[4]) : 15;
    if (kernel < 1 || kernel > 99) { fprintf(stderr,"Kernel invalido (1-99)\n"); return 2; }
    if (threads < 1 || threads > 256 || strlen(source)>60 || strstr(source,"/") || strstr(source,"\\") || !strstr(source,".bmp")) {
        fprintf(stderr,"Argumentos invalidos\n"); return 2;
    }
    if (!exists_nonempty(source)) {fprintf(stderr,"No se encuentra img/%s\n", source);return 3;}
    const char *valid[] = {"all","gray","hcolor","hgray","vcolor","vgray","bcolor","bgray","edge_x","edge_y"};
    int ok=0;for(int i=0;i<10;i++) if(strcmp(op,valid[i])==0)ok=1;
    if(!ok){fprintf(stderr,"Operacion desconocida: %s\n",op); return 2;}
    omp_set_dynamic(0);
    omp_set_num_threads(threads);
    double start = omp_get_wtime();
    img2gray(source);
    if (!exists_nonempty("img_grises.bmp")) {fprintf(stderr,"Fallo la conversion a grises\n");return 4;}
    if(strcmp(op,"all")==0) {
        #pragma omp parallel sections
        {
            #pragma omp section
            invHorizontal(source,"pookies_h_color.bmp");
            #pragma omp section
            invHorizontal("img_grises.bmp","pookies_h_gray.bmp");
            #pragma omp section
            invVertical(source,"pookies_v_color.bmp");
            #pragma omp section
            invVertical("img_grises.bmp","pookies_v_gray.bmp");
            #pragma omp section
            blur(source,"pookies_b_color.bmp",kernel);
            #pragma omp section
            blur("img_grises.bmp","pookies_b_gray.bmp",kernel);
            #pragma omp section
            bordesX("img_grises.bmp","pookies_edge_x.bmp");
            #pragma omp section
            bordesY("img_grises.bmp","pookies_edge_y.bmp");
        }
    } else if(strcmp(op,"hcolor")==0) invHorizontal(source,"pookies_h_color.bmp");
    else if(strcmp(op,"hgray")==0) invHorizontal("img_grises.bmp","pookies_h_gray.bmp");
    else if(strcmp(op,"vcolor")==0) invVertical(source,"pookies_v_color.bmp");
    else if(strcmp(op,"vgray")==0) invVertical("img_grises.bmp","pookies_v_gray.bmp");
    else if(strcmp(op,"bcolor")==0) blur(source,"pookies_b_color.bmp",kernel);
    else if(strcmp(op,"bgray")==0) blur("img_grises.bmp","pookies_b_gray.bmp",kernel);
    else if(strcmp(op,"edge_x")==0) bordesX("img_grises.bmp","pookies_edge_x.bmp");
    else if(strcmp(op,"edge_y")==0) bordesY("img_grises.bmp","pookies_edge_y.bmp");
    double seconds = omp_get_wtime() - start;
    if(strcmp(op,"all")==0) {
       const char *outputs[]={"pookies_h_color.bmp","pookies_h_gray.bmp","pookies_v_color.bmp","pookies_v_gray.bmp","pookies_b_color.bmp","pookies_b_gray.bmp","pookies_edge_x.bmp","pookies_edge_y.bmp"};
       for(int i=0;i<8;i++)if(!exists_nonempty(outputs[i])) {fprintf(stderr,"No se genero %s\n",outputs[i]);return 5;}
    } else if(strcmp(op,"gray")!=0) {
       const char *outputs[]={"hcolor","hgray","vcolor","vgray","bcolor","bgray","edge_x","edge_y"};
       const char *files[]={"pookies_h_color.bmp","pookies_h_gray.bmp","pookies_v_color.bmp","pookies_v_gray.bmp","pookies_b_color.bmp","pookies_b_gray.bmp","pookies_edge_x.bmp","pookies_edge_y.bmp"};
       for(int i=0;i<8;i++)if(strcmp(op,outputs[i])==0 && !exists_nonempty(files[i])){fprintf(stderr,"No se genero %s\n",files[i]);return 5;}
    }
    printf("OK|%s|%d|%.6f\n",op,threads,seconds);
    return 0;
}
