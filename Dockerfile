# Usar Python 3.11 como base (coincidiendo con tu sistema)
FROM python:3.11-slim

# Instalar dependencias de Linux para gráficos, GLUT y servidor web VNC 
RUN apt-get update && apt-get install -y \
    xvfb \
    x11vnc \
    novnc \
    websockify \
    libgl1-mesa-dri \
    libgl1-mesa-glx \
    libglu1-mesa \
    freeglut3 \
    && rm -rf /var/lib/apt/lists/*

# Definir el directorio de trabajo
WORKDIR /app

# Copiar el archivo de requerimientos e instalar paquetes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código y recursos (Carpeta AimLabs y Resource)
COPY . .

# Exponer el puerto 8080 para acceder desde el navegador
EXPOSE 8080

# Configurar el entorno para la pantalla virtual
ENV DISPLAY=:99
ENV PYTHONPATH=/app

# Comando de inicio:
# 1. Crea la pantalla virtual (Xvfb)
# 2. Inicia el servidor VNC para capturar los gráficos
# 3. Inicia noVNC para convertir el flujo a una web
# 4. Ejecuta tu juego principal
CMD Xvfb :99 -screen 0 1250x650x24 & \
    sleep 2 && \
    x11vnc -display :99 -nopw -forever & \
    /usr/share/novnc/utils/launch.sh --vnc localhost:5900 --listen 8080 & \
    python AimLabs/PyPrimes3D.py