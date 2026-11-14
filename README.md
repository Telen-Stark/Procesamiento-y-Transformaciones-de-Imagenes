# Procesamiento Paralelo de Imágenes BMP con C y OpenMP
Este repositorio contiene la implementación de una aplicación en **C** desarrollada para la transformación y manipulación de imágenes de gran formato (más de 2000 píxeles de ancho y alto) utilizando **programación paralela con OpenMP**.

El proyecto procesa un lote de **10 imágenes BMP** aplicando múltiples transformaciones multihilo para evaluar el rendimiento computacional.

## Prerrequisitos
* Compilador **GCC** con soporte para OpenMP (`-fopenmp`).
* Entorno de ejecución Linux (o WSL / MinGW en Windows).
* Estructura de carpetas local con el directorio `./img/` creado.

## Compilación y Ejecución
1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/Telen-Stark/Procesamiento-y-Transformaciones-de-Imagenes.git](https://github.com/Telen-Stark/Procesamiento-y-Transformaciones-de-Imagenes.git)
   cd Procesamiento-y-Transformaciones-de-Imagenes
    ```
2. **Crear la carpeta de imágenes e incluir las 10 imágenes de prueba:**
```bash
mkdir -p img
# Asegúrate de nombrar tus imágenes como img1.bmp, img2.bmp, ..., img10.bmp dentro de ./img/
```
3. **Compilar el proyecto:**
```bash
gcc -fopenmp demo_lib_v2.c -o procesador_imagenes
```
4. **Ejecutar la aplicación:**
```bash
./procesador_imagenes
```

## Estructura del Repositorio
| Archivo / Carpeta | Descripción |
| --- | --- |
| `demo_lib_v2.c` | Punto de entrada principal (`main`). Controla el bucle de procesamiento de 10 imágenes y ejecuta secciones paralelas mediante `#pragma omp sections`.
| `img_trans_v2.h` | Librería nativa con las funciones de procesamiento BMP (`img2gray`, `invHorizontal`, `invVertical`, `desenfoque`, `gray2color`).
| `img/` | Carpeta de trabajo donde deben depositarse las imágenes de entrada y donde se generan las imágenes procesadas de salida. |
| `README.md` | Guía de compilación, ejecución y resumen general del proyecto. |

## Funcionalidades Implementadas (Avance 1)
En el primer avance se implementó el procesamiento paralelo de **4 transformaciones concurrentes por imagen**:
* **img2gray**: Conversión a escala de grises y exportación de frecuencias para histogramas.
* **invHorizontal**: Transformación horizontal sobre imagen a color y sobre versión a escala de grises.
* **invVertical**: Transformación vertical sobre imagen a color y sobre versión a escala de grises.

## Funcionalidades Implementadas (Avance 2)
En el segundo avance se implementó el procesamiento paralelo de **8 transformaciones concurrentes por imagen**:
* Las tres transformaciones que ya se tenían del avance 1: **img2gray**, **invHorizontal** e **invVertical**}
* **blur**: Efecto de desenfoque sobre imagen a color y sobre versión a escala de grises mediante kernel.
* **bordesX**: Detección de bordes verticales mediante derivada parcial en X (Sobel).
* **bordesY**: Detección de bordes horizontales mediante derivada parcial en Y (Sobel).

## Documentación (Wiki)
Para ver el análisis explicativo línea por línea de las funciones más importantes, el detalle de las directivas OpenMP empleadas y las **tablas y métricas comparativas de rendimiento entre los 3 equipos de prueba**, consulta nuestra [https://github.com/Telen-Stark/Procesamiento-y-Transformaciones-de-Imagenes/wiki].
