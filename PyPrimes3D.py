import os
import sys
import pygame
from pygame.locals import *
import sys
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from AimLabs.Menu import Menu, InstructionsScreen
from animacion import Animation


def resource_path(relative_path):
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def show_intro(screen, display):
    # Cargar música de introducción
    pygame.mixer.init()
    pygame.mixer.music.load(resource_path("Resource/intro.mp3"))
    pygame.mixer.music.set_volume(0.2)  # Ajusta el volumen (0.0 a 1.0)
    pygame.mixer.music.play(-1)  # Reproducir en bucle

    intro_start_time = pygame.time.get_ticks()
    font = pygame.font.Font(None, 80)  # Fuente para el texto

    while True:
        elapsed_time = pygame.time.get_ticks() - intro_start_time
        # Salir de la introducción después de 3 segundos
        if elapsed_time > 3000:
            break

        # Dibujar fondo negro
        screen.fill((0, 0, 0))

        # Dibujar texto
        text_surface = font.render("Desarrollado en Flacow.py", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(display[0] // 2, display[1] // 2))
        screen.blit(text_surface, text_rect)

        pygame.display.flip()  # Actualizar pantalla

        # Manejar eventos para permitir cierre
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    # Detener la música al finalizar la introducción
    pygame.mixer.music.stop()


def main():
    # PASO 1: Inicializar pygame primero
    pygame.init()

    # PASO 2: Inicializar GLUT de forma segura
    try:
        glutInit(sys.argv)
        print("GLUT inicializado correctamente")
    except Exception as e:
        print(f"Advertencia: Error al inicializar GLUT: {e}")
        print("Continuando sin GLUT - usando implementación alternativa")

    # PASO 3: Configurar el display
    info = pygame.display.Info()
    display = (info.current_w, info.current_h)
    screen = pygame.display.set_mode(display, pygame.FULLSCREEN)
    pygame.display.set_caption("PyPrimes 3D")

    # Mostrar pantalla de introducción
    show_intro(screen, display)

    # Configurar las instrucciones (mantener el código original)
    instructions = [
        {
            "image": pygame.image.load(resource_path("Resource/Instructions/instruccion 1.PNG")),
            "text": "Usa el mouse para hacer clic en las esferas primas.",
        },
        {
            "image": pygame.image.load(resource_path("Resource/Instructions/instruccion 2.PNG")),
            "text": "Evita hacer clic en las esferas no primas.",
        },
        {
            "image": pygame.image.load(resource_path("Resource/Instructions/instruccion 3.PNG")),
            "text": "No dejes que se te acabe el tiempo, ¡CUIDADO! En cada nivel las esferas son más pequeñas y veloces.",
        },
        {
            "image": pygame.image.load(resource_path("Resource/Instructions/instruccion 4.PNG")),
            "text": "Revienta todas las esferas primas para ganar.",
        },
        {
            "image": None,
            "text": "¡Suerte, flacow!",
        },
    ]

    instructions_screen = InstructionsScreen(screen, instructions)
    gif_frames = instructions_screen.load_gif(resource_path("Resource/Instructions/esqueleto.gif"))
    instructions[4]["image"] = gif_frames  # Reemplazar el GIF cargado
    in_help = False

    # Inicializar el menú
    menu = Menu(display[0], display[1])

    # Ciclo principal del menú
    while menu.running:
        if not in_help:
            action = menu.handle_events()
            if action == "START":
                menu.stop_music()  # Detener la música del menú
                break  # Salir del menú y empezar el juego
            elif action == "HELP":
                in_help = True  # Activar pantalla de ayuda
            elif action == "QUIT":
                menu.stop_music()  # Detener la música al salir
                pygame.quit()
                return

            menu.update()  # Actualizar animaciones del menú
            menu.render(screen)
            pygame.display.flip()

        else:  # Si estamos en la pantalla de ayuda
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                result = instructions_screen.handle_event(event)
                if result == "MENU":  # Regresar al menú
                    in_help = False

            instructions_screen.draw()
            pygame.display.flip()

    # PASO 4: Cambiar a modo OpenGL DESPUÉS de GLUT
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL | FULLSCREEN)

    # PASO 5: Configurar OpenGL
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, 21, 0, 0, 0, 0, 1, 0)

    # PASO 6: Inicializar la animación
    animation = Animation(display[0], display[1], 40)  # Inicializa con 40 esferas
    animation.create_spheres(40)  # Genera las 40 esferas iniciales

    # PASO 7: Loop principal del juego
    clock = pygame.time.Clock()
    while True:
        animation.handle_events()  # Maneja eventos
        animation.update_scene()  # Actualiza la lógica del juego
        animation.render_scene()  # Renderiza la escena actual
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()