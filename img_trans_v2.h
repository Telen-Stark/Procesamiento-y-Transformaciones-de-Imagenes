/*
FUNCION: img2gray
Convertir a escala de grises y genera histogramas en txt
*/
extern void img2gray(const char *input_name) {
    FILE *image, *outputImage, *lecturas;
    char input_path[100] = "./img/";
    char output_path[100] = "./img/";
    strcat(input_path, input_name);
    strcat(output_path, "img_grises.bmp");

    image = fopen(input_path, "rb");
    outputImage = fopen(output_path, "wb");
    lecturas = fopen("histogramas.txt", "w");

    if (!image || !outputImage || !lecturas) {
        printf("Error abriendo archivos en img2gray\n");
        if (image) fclose(image);
        if (outputImage) fclose(outputImage);
        if (lecturas) fclose(lecturas);
        return;
    }

    //copiar la cabecera de 54 bytes
    unsigned char header[54];
    fread(header, sizeof(unsigned char), 54, image);
    unsigned int pixel_offset = *(unsigned int*)&header[10];

    // Volver al inicio y copiar la cabecera COMPLETA
    fseek(image, 0, SEEK_SET);
    unsigned char *full_header = (unsigned char *)malloc(pixel_offset);
    fread(full_header, 1, pixel_offset, image);
    fwrite(full_header, 1, pixel_offset, outputImage);
    free(full_header);

    int width = *(int*)&header[18];
    int height = abs(*(int*)&header[22]);
    int row_padded = (width * 3 + 3) & (~3);
    int ar[256] = {0}, ag[256] = {0}, ab[256] = {0};

    unsigned char *row = (unsigned char *)malloc(row_padded);

    for (int y = 0; y < height; y++) {
        fread(row, sizeof(unsigned char), row_padded, image);
        for (int x = 0; x < width; x++) {
            int idx = x * 3;
            unsigned char b = row[idx + 0];
            unsigned char g = row[idx + 1];
            unsigned char r = row[idx + 2];

            ab[b]++;
            ag[g]++;
            ar[r]++;

            unsigned char pixel = (unsigned char)(0.21 * r + 0.72 * g + 0.07 * b);
            row[idx] = pixel;
            row[idx + 1] = pixel;
            row[idx + 2] = pixel;
        }
        fwrite(row, sizeof(unsigned char), row_padded, outputImage);
    }
    //escribir histogramas
    fprintf(lecturas, "Histograma -b - g - r\n");
    for(int i = 0; i < 256; i++) {
        fprintf(lecturas, "%d\t %d\t %d\t %d\n", i, ab[i], ag[i], ar[i]);
    }

    free(row);
    fclose(lecturas);
    fclose(image);
    fclose(outputImage);
}

/*
FUNCION: invHorizontal
Invertir una imagen horizontalmente
*/
extern void invHorizontal(const char *input_name, const char *output_name) {
    FILE *image, *outputImage;
    char input_path[100] = "./img/";
    char output_path[100] = "./img/";
    strcat(input_path, input_name);
    strcat(output_path, output_name);

    image = fopen(input_path, "rb");
    outputImage = fopen(output_path, "wb");

    if (!image || !outputImage) {
        printf("Error abriendo archivos en invHorizontal\n");
        if (image) fclose(image);
        if (outputImage) fclose(outputImage);
        return;
    }

    //copiar la cabecera de 54 bytes
    unsigned char header[54];
    fread(header, sizeof(unsigned char), 54, image);
    unsigned int pixel_offset = *(unsigned int*)&header[10];

    fseek(image, 0, SEEK_SET);
    unsigned char *full_header = (unsigned char *)malloc(pixel_offset);
    fread(full_header, 1, pixel_offset, image);
    fwrite(full_header, 1, pixel_offset, outputImage);
    free(full_header);

    int width = *(int*)&header[18];
    int height = abs(*(int*)&header[22]);
    int row_padded = (width * 3 + 3) & (~3);

    unsigned char *in_row = (unsigned char *)malloc(row_padded);
    unsigned char *out_row = (unsigned char *)malloc(row_padded);

    for (int y = 0; y < height; y++) {
        fread(in_row, sizeof(unsigned char), row_padded, image);
        // Inversión horizontal pixel a pixel (BGR)
        for (int x = 0; x < width; x++) {
            int src_idx = x * 3;
            int dst_idx = (width - 1 - x) * 3;

            out_row[dst_idx + 0] = in_row[src_idx + 0]; // B
            out_row[dst_idx + 1] = in_row[src_idx + 1]; // G
            out_row[dst_idx + 2] = in_row[src_idx + 2]; // R
        }

        // Mantener el padding
        for (int p = width * 3; p < row_padded; p++) {
            out_row[p] = in_row[p];
        }

        fwrite(out_row, sizeof(unsigned char), row_padded, outputImage);
    }

    free(in_row);
    free(out_row);
    fclose(image);
    fclose(outputImage);
}

/*
FUNCION: invVertical
Invertir verticalmente una imagen
*/
extern void invVertical(const char *input_name, const char *output_name) {
    FILE *image, *outputImage;
    char input_path[100] = "./img/";
    char output_path[100] = "./img/";
    strcat(input_path, input_name);
    strcat(output_path, output_name);

    image = fopen(input_path, "rb");
    outputImage = fopen(output_path, "wb");

    if (!image || !outputImage) {
        printf("Error abriendo archivos en invVertical\n");
        if (image) fclose(image);
        if (outputImage) fclose(outputImage);
        return;
    }

    unsigned char header[54];
    fread(header, sizeof(unsigned char), 54, image);
    unsigned int pixel_offset = *(unsigned int*)&header[10];

    fseek(image, 0, SEEK_SET);
    unsigned char *full_header = (unsigned char *)malloc(pixel_offset);
    fread(full_header, 1, pixel_offset, image);
    fwrite(full_header, 1, pixel_offset, outputImage);
    free(full_header);
    
    int width = *(int*)&header[18];
    int height = abs(*(int*)&header[22]);
    int row_padded = (width * 3 + 3) & (~3);

    unsigned char *row = (unsigned char *)malloc(row_padded);

    for (int i = height - 1; i >= 0; i--) {
        fseek(image, pixel_offset + (long)i * row_padded, SEEK_SET);
        fread(row, sizeof(unsigned char), row_padded, image);
        fwrite(row, sizeof(unsigned char), row_padded, outputImage);
    }
    
    free(row);
    fclose(image);
    fclose(outputImage);
}

/*
FUNCION: blur
Blur de imagen con un kernel
*/
extern void blur(const char* input_name, int kernel_size) {
    FILE *image, *outputImage;
    char input_path[100] = "./img/";
    char output_path[100] = "./img/";
    strcat(input_path, input_name);
    strcat(output_path, "img_blur.bmp");

    image = fopen(input_path, "rb");
    outputImage = fopen(output_path, "wb");

    if (!image || !outputImage) {
        printf("Error abriendo archivos en funcion blur\n");
        if (image) fclose(image);
        if (outputImage) fclose(outputImage);
        return;
    }

    unsigned char header[54];
    fread(header, sizeof(unsigned char), 54, image);
    unsigned int pixel_offset = *(unsigned int*)&header[10];

    fseek(image, 0, SEEK_SET);
    unsigned char *full_header = (unsigned char *)malloc(pixel_offset);
    fread(full_header, 1, pixel_offset, image);
    fwrite(full_header, 1, pixel_offset, outputImage);
    free(full_header);

    int width = *(int*)&header[18];
    int height = abs(*(int*)&header[22]);
    int row_padded = (width * 3 + 3) & (~3);

    unsigned char** input_rows = (unsigned char**)malloc(height * sizeof(unsigned char*));
    unsigned char** output_rows = (unsigned char**)malloc(height * sizeof(unsigned char*));
    unsigned char** temp_rows = (unsigned char**)malloc(height * sizeof(unsigned char*));

    for (int i = 0; i < height; i++) {
        input_rows[i] = (unsigned char*)malloc(row_padded);
        output_rows[i] = (unsigned char*)malloc(row_padded);
        temp_rows[i] = (unsigned char*)malloc(row_padded);
        fread(input_rows[i], sizeof(unsigned char), row_padded, image);
    }
    int k = kernel_size / 2;
    // Paso intermedio: desenfoque horizontal
    for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
            int sumB = 0, sumG = 0, sumR = 0, count = 0;
            for (int dx = -k; dx <= k; dx++) {
                int nx = x + dx;
                if (nx >= 0 && nx < width) {
                    int idx = nx * 3;
                    sumB += input_rows[y][idx + 0];
                    sumG += input_rows[y][idx + 1];
                    sumR += input_rows[y][idx + 2];
                    count++;
                }
            }
            int index = x * 3;
            temp_rows[y][index + 0] = sumB / count;
            temp_rows[y][index + 1] = sumG / count;
            temp_rows[y][index + 2] = sumR / count;
        }
        // Copiar padding sin modificar
        for (int p = width * 3; p < row_padded; p++) {
            temp_rows[y][p] = input_rows[y][p];
        }
    }
    // Paso final: desenfoque vertical
    for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
            int sumB = 0, sumG = 0, sumR = 0, count = 0;
            for (int dy = -k; dy <= k; dy++) {
                int ny = y + dy;
                if (ny >= 0 && ny < height) {
                    int idx = x * 3;
                    sumB += temp_rows[ny][idx + 0];
                    sumG += temp_rows[ny][idx + 1];
                    sumR += temp_rows[ny][idx + 2];
                    count++;
                    }
                }
            int index = x * 3;
            output_rows[y][index + 0] = sumB / count;
            output_rows[y][index + 1] = sumG / count;
            output_rows[y][index + 2] = sumR / count;
        }
        // Copiar padding sin modificar
        for (int p = width * 3; p < row_padded; p++) {
            output_rows[y][p] = temp_rows[y][p];
        }
    }
    // Escritura final
    for (int i = 0; i < height; i++) {
        fwrite(output_rows[i], sizeof(unsigned char), row_padded, outputImage);
        free(input_rows[i]);
        free(temp_rows[i]);
        free(output_rows[i]);
    }

    free(input_rows);
    free(temp_rows);
    free(output_rows);
    fclose(image);
    fclose(outputImage);
}

/*
FUNCION: bordesX
Detección de bordes verticales mediante derivada parcial en X
*/
extern void bordesX(const char *input_name, const char *output_name) {
    FILE *image, *outputImage;
    char input_path[100] = "./img/";
    char output_path[100] = "./img/";
    strcat(input_path, input_name);
    strcat(output_path, output_name);

    image = fopen(input_path, "rb");
    outputImage = fopen(output_path, "wb");

    if (!image || !outputImage) {
        printf("Error abriendo archivos en bordesX\n");
        if (image) fclose(image);
        if (outputImage) fclose(outputImage);
        return;
    }

    unsigned char header[54];
    fread(header, sizeof(unsigned char), 54, image);
    unsigned int pixel_offset = *(unsigned int*)&header[10];

    fseek(image, 0, SEEK_SET);
    unsigned char *full_header = (unsigned char *)malloc(pixel_offset);
    fread(full_header, 1, pixel_offset, image);
    fwrite(full_header, 1, pixel_offset, outputImage);
    free(full_header);

    int width = *(int*)&header[18];
    int height = abs(*(int*)&header[22]);
    int row_padded = (width * 3 + 3) & (~3);

    unsigned char **in_rows = (unsigned char **)malloc(height * sizeof(unsigned char *));
    unsigned char **out_rows = (unsigned char **)malloc(height * sizeof(unsigned char *));

    for (int y = 0; y < height; y++) {
        in_rows[y] = (unsigned char *)malloc(row_padded);
        out_rows[y] = (unsigned char *)calloc(row_padded, sizeof(unsigned char));
        fread(in_rows[y], sizeof(unsigned char), row_padded, image);
    }

    // Kernel Sobel para derivada parcial respecto a x (d/dx)
    int Gx[3][3] = {
        {-1, 0, 1},
        {-2, 0, 2},
        {-1, 0, 1}
    };

    for (int y = 1; y < height - 1; y++) {
        for (int x = 1; x < width - 1; x++) {
            int sumB = 0, sumG = 0, sumR = 0;

            for (int ky = -1; ky <= 1; ky++) {
                for (int kx = -1; kx <= 1; kx++) {
                    int idx = (x + kx) * 3;
                    int weight = Gx[ky + 1][kx + 1];
                    sumB += in_rows[y + ky][idx + 0] * weight;
                    sumG += in_rows[y + ky][idx + 1] * weight;
                    sumR += in_rows[y + ky][idx + 2] * weight;
                }
            }

            // Magnitud absoluta y saturación (0 - 255)
            sumB = abs(sumB); if (sumB > 255) sumB = 255;
            sumG = abs(sumG); if (sumG > 255) sumG = 255;
            sumR = abs(sumR); if (sumR > 255) sumR = 255;

            int out_idx = x * 3;
            out_rows[y][out_idx + 0] = (unsigned char)sumB;
            out_rows[y][out_idx + 1] = (unsigned char)sumG;
            out_rows[y][out_idx + 2] = (unsigned char)sumR;
        }
        // Mantener padding original
        for (int p = width * 3; p < row_padded; p++) {
            out_rows[y][p] = in_rows[y][p];
        }
    }

    for (int y = 0; y < height; y++) {
        fwrite(out_rows[y], sizeof(unsigned char), row_padded, outputImage);
        free(in_rows[y]);
        free(out_rows[y]);
    }

    free(in_rows);
    free(out_rows);
    fclose(image);
    fclose(outputImage);
}

/*
FUNCION: bordesY
Detección de bordes horizontales mediante derivada parcial en Y
*/
extern void bordesY(const char *input_name, const char *output_name) {
    FILE *image, *outputImage;
    char input_path[100] = "./img/";
    char output_path[100] = "./img/";
    strcat(input_path, input_name);
    strcat(output_path, output_name);

    image = fopen(input_path, "rb");
    outputImage = fopen(output_path, "wb");

    if (!image || !outputImage) {
        printf("Error abriendo archivos en bordesY\n");
        if (image) fclose(image);
        if (outputImage) fclose(outputImage);
        return;
    }

    unsigned char header[54];
    fread(header, sizeof(unsigned char), 54, image);
    unsigned int pixel_offset = *(unsigned int*)&header[10];

    fseek(image, 0, SEEK_SET);
    unsigned char *full_header = (unsigned char *)malloc(pixel_offset);
    fread(full_header, 1, pixel_offset, image);
    fwrite(full_header, 1, pixel_offset, outputImage);
    free(full_header);

    int width = *(int*)&header[18];
    int height = abs(*(int*)&header[22]);
    int row_padded = (width * 3 + 3) & (~3);

    unsigned char **in_rows = (unsigned char **)malloc(height * sizeof(unsigned char *));
    unsigned char **out_rows = (unsigned char **)malloc(height * sizeof(unsigned char *));

    for (int y = 0; y < height; y++) {
        in_rows[y] = (unsigned char *)malloc(row_padded);
        out_rows[y] = (unsigned char *)calloc(row_padded, sizeof(unsigned char));
        fread(in_rows[y], sizeof(unsigned char), row_padded, image);
    }

    // Kernel Sobel para derivada parcial respecto a y (d/dy)
    int Gy[3][3] = {
        {-1, -2, -1},
        { 0,  0,  0},
        { 1,  2,  1}
    };

    for (int y = 1; y < height - 1; y++) {
        for (int x = 1; x < width - 1; x++) {
            int sumB = 0, sumG = 0, sumR = 0;

            for (int ky = -1; ky <= 1; ky++) {
                for (int kx = -1; kx <= 1; kx++) {
                    int idx = (x + kx) * 3;
                    int weight = Gy[ky + 1][kx + 1];
                    sumB += in_rows[y + ky][idx + 0] * weight;
                    sumG += in_rows[y + ky][idx + 1] * weight;
                    sumR += in_rows[y + ky][idx + 2] * weight;
                }
            }

            // Magnitud absoluta y saturación (0 - 255)
            sumB = abs(sumB); if (sumB > 255) sumB = 255;
            sumG = abs(sumG); if (sumG > 255) sumG = 255;
            sumR = abs(sumR); if (sumR > 255) sumR = 255;

            int out_idx = x * 3;
            out_rows[y][out_idx + 0] = (unsigned char)sumB;
            out_rows[y][out_idx + 1] = (unsigned char)sumG;
            out_rows[y][out_idx + 2] = (unsigned char)sumR;
        }
        // Mantener padding original
        for (int p = width * 3; p < row_padded; p++) {
            out_rows[y][p] = in_rows[y][p];
        }
    }

    for (int y = 0; y < height; y++) {
        fwrite(out_rows[y], sizeof(unsigned char), row_padded, outputImage);
        free(in_rows[y]);
        free(out_rows[y]);
    }

    free(in_rows);
    free(out_rows);
    fclose(image);
    fclose(outputImage);
}