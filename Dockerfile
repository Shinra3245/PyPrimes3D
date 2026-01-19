FROM python:3.11-slim

# 1. Instalar dependencias de sistema, PulseAudio para el motor de sonido y procps
RUN apt-get update && apt-get install -y \
    xvfb x11vnc novnc websockify \
    libgl1-mesa-dri libgl1 libglu1-mesa libglut3.12 \
    libglib2.0-0 libsm6 libxext6 libxrender1 procps \
    pulseaudio alsa-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Configurar variables de entorno para gráficos y audio
ENV DISPLAY=:99
ENV PYTHONPATH=/app
ENV SDL_AUDIODRIVER=pulseaudio

# 3. Instalar librerías de Python según tus versiones verificadas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar todo el proyecto respetando tu estructura de carpetas
COPY . .

EXPOSE 8080

# 5. Comando de inicio corregido para encontrar la carpeta 'Resource/'
CMD pulseaudio --start --exit-idle-time=-1 && \
    Xvfb :99 -screen 0 1250x650x24 & \
    sleep 3 && \
    x11vnc -display :99 -nopw -forever -shared -rfbport 5900 & \
    # Usamos websockify directamente para mayor control sobre el puerto de Render
    websockify --web /usr/share/novnc ${PORT:-8080} localhost:5900 & \
    cd AimLabs && python PyPrimes3D.py