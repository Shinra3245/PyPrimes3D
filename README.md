
# PyPrimes 3D: Aim Trainer & Mathematical Challenge

PyPrimes 3D es un videojuego de entrenamiento de puntería (estilo AimLabs) desarrollado en Python utilizando OpenGL para el renderizado de gráficos en tiempo real. El juego combina mecánicas de reflejos con desafíos matemáticos, donde el jugador debe identificar y destruir esferas que contienen números primos mientras evita las no primas.

## Caracteristicas Técnicas

 - Motor Gráfico: Implementación de iluminación `(GL_LIGHTING)`, texturizado de cubos y renderizado de esferas dinámicas mediante `gluSphere`.
 - Dificultad Adaptativa: El radio de las esferas disminuye y su velocidad de traslación y rotación aumenta conforme el jugador sube de nivel.
 - Optimización de Texturas: Uso de `GL_UNPACK_ALIGNMENT` para garantizar que las imágenes de los menús y HUD se carguen sin distorsión visual.
 - Lógica Matemática: Sistema de generación de números y factorización en tiempo real para determinar el estado de cada esfera.

## Stack Tecnologico

| Componente           | Versión / Tecnología                                                        |
| ----------------- | ------------------------------------------------------------------ |
| Lenguaje | Python 3.11.9 |
| Graficos 3D | PyOpenGL 3.1.7|
| Interfaz y Audio | Pygame 2.6.1|
| Cálculo Numérico | NumPy 1.26.4 |
| Procesamiento de Imágenes | Pillow 12.1.0 |
| Matemáticas Simbólicas | SymPy 1.14.0 y Mpmath 1.3.0 |
| Contenedor | Docker (Linux Debian-slim) |


## Estructura del proyecto

La organización del código sigue una jerarquía modular para facilitar el despliegue y mantenimiento:

```Arbol
PyPrimes3D/
├── AimLabs/                # Paquete principal del videojuego
│   ├── Resource/           # Assets (Audios, Fondos, Texturas y Memes)
│   ├── animacion.py        # Motor de renderizado y física de esferas
│   ├── Menu.py             # Lógica de menús e instrucciones
│   ├── primes.py           # Algoritmos de números primos
│   └── PyPrimes3D.py       # Punto de entrada (Main)
├── .gitignore              # Archivos excluidos de Git
├── Dockerfile              # Configuración de imagen Docker (Xvfb + noVNC)
├── docker-compose.yml      # Orquestación de servicios y puertos
├── README.md               # Documentación del proyecto
└── requirements.txt        # Dependencias del intérprete
```

## Despliegue con Docker (noVNC)

Para integrar este juego en un portafolio web de forma desacoplada, se utiliza una arquitectura de pantalla virtual:




**Xvfb:** Simula un monitor físico en la memoria del servidor Linux.

**noVNC:** Permite que los gráficos generados por OpenGL sean transmitidos a través de un navegador web mediante WebSockets.


## Instrucciones de uso con docker

1. Construir la imagen:

```bash
  docker-compose build
```

2. Iniciar el contenedor:

```bash
  docker-compose up
```

3. Acceder desde el navegador:

`http://localhost:8080/vnc.html?autoconnect=true`



### Instalación Local

Si deseas ejecutar el proyecto directamente en Windows, asegúrate de tener instalado Python 3.11.9 y los binarios de freeglut correspondientes a tu arquitectura.

1. Instalar dependencias:

```bash
  pip install -r requirements.txt
```


1. Ejecutar el juego:

```bash
  python AimLabs/PyPrimes3D.py
```



## Imagenes del juego

![Menu](https://via.placeholder.com/468x300?text=App+Screenshot+Here)


## Autor

- [@Shinra3245](https://github.com/Shinra3245)