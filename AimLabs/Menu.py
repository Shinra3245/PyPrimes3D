# Menu.py
import os
import sys
import pygame
import math
from PIL import Image

def resource_path(relative_path):
    """ Obtiene la ruta absoluta de los recursos, compatible con PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Menu:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.running = True
        self.title_font = pygame.font.Font(None, 100)  # Fuente para el título
        self.button_font = pygame.font.Font(None, 50)  # Fuente para los botones
        self.buttons = {
            "INICIAR": pygame.Rect(self.width // 2 - 100, self.height // 2 - 50, 200, 50),
            "SALIR": pygame.Rect(self.width // 2 - 100, self.height // 2 + 20, 200, 50),
        }
        # Botón de ayuda circular
        self.help_button_center = (70, self.height - 70)
        self.help_button_radius = 50
        # Cargar música de fondo
        pygame.mixer.init()
        self.menu_music = resource_path("Resource/MenuMusic.mp3")
        pygame.mixer.music.load(self.menu_music)
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(-1)
        # Cargar la imagen de fondo
        self.background_image = pygame.image.load(resource_path("Resource/Backgrounds/Background image.jpg")).convert()
        self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))
        self.background_alpha = 255
        self.start_sound = pygame.mixer.Sound(resource_path("Resource/boton-Iniciar.mp3"))
        self.frame_count = 0

    def stop_music(self):
        pygame.mixer.music.stop()

    def render(self, screen):
        """Dibuja el menú en la pantalla."""
        self.background_image.set_alpha(self.background_alpha)
        screen.blit(self.background_image, (0, 0))
        # Efecto de "baile" en el título con fondo detrás de las letras
        title_surface = self.create_dancing_text("PyPrimes 3D", (255, 255, 255), background_color=(0, 0, 0), padding=10)
        title_rect = title_surface.get_rect(center=(self.width // 2, self.height // 4))
        screen.blit(title_surface, title_rect)
        # Dibujar los botones con tambaleo
        self.render_buttons(screen)
        blink_interval = 30
        color_index = (self.frame_count // blink_interval) % 2
        colors = [(200, 0, 0), (0, 200, 0)]  # Blanco y amarillo
        current_color = colors[color_index]

        # Dibujar botón de ayuda circular
        pygame.draw.circle(screen, current_color, self.help_button_center, self.help_button_radius)
        # Renderizar el signo de interrogación siempre visible
        question_mark = self.button_font.render("?", True, (0, 0, 0))
        question_rect = question_mark.get_rect(center=self.help_button_center)
        screen.blit(question_mark, question_rect)
        # Texto "¿Cómo jugar?" con fondo detrás
        help_text_font = pygame.font.Font(None, 20)  # Fuente más pequeña
        help_text = help_text_font.render("¿Cómo jugar?", True, (255, 255, 255))
        help_text_rect = help_text.get_rect(midleft=(self.help_button_center[0] + self.help_button_radius + 20,
                                                     self.help_button_center[1]))
        padding = 10  # Espacio adicional alrededor del texto
        arrow_width = 20  # Anchura de la flecha
        background_width = help_text_rect.width + 2 * padding + arrow_width
        background_height = help_text_rect.height + 2 * padding
        background_x = help_text_rect.left - padding - arrow_width
        background_y = help_text_rect.top - padding
        # Dibujar flecha
        arrow_points = [
            (background_x, background_y + background_height // 2),
            (background_x + arrow_width, background_y + background_height // 2 - arrow_width // 2),
            (background_x + arrow_width, background_y + background_height // 2 + arrow_width // 2),
        ]
        pygame.draw.polygon(screen, (0, 0, 0), arrow_points)

        pygame.draw.rect(screen, (0, 0, 0),
                         (background_x + arrow_width, background_y, background_width - arrow_width, background_height))

        # Dibujar bordes blancos
        pygame.draw.polygon(screen, (255, 255, 255), arrow_points, 2)
        pygame.draw.rect(screen, (255, 255, 255),
                         (background_x + arrow_width, background_y, background_width - arrow_width, background_height),
                         2)

        # Dibujar el texto encima del fondo
        screen.blit(help_text, help_text_rect)

    def create_dancing_text(self, text, color, background_color=(0, 0, 0), padding=15, letter_spacing=13):
        surfaces = []
        x_offset = 0
        amplitude = 10  # Amplitud del movimiento
        frequency = 0.09  # Frecuencia del movimiento

        # Generar superficies y calcular desplazamientos para cada letra
        for i, char in enumerate(text):
            char_surface = self.title_font.render(char, True, color)
            y_offset = amplitude * math.sin(frequency * (self.frame_count + i * 10))
            surfaces.append((char_surface, y_offset, x_offset))
            x_offset += char_surface.get_width() + letter_spacing

        # Determinar el tamaño total del título
        total_width = x_offset
        max_height = max(s.get_height() for s, _, _ in surfaces)
        buffer = int(amplitude * 2)  # Margen adicional basado en la amplitud

        # Crear superficie para todo el texto
        title_surface = pygame.Surface((total_width, max_height + buffer * 2), pygame.SRCALPHA)

        # Dibujar letras en orden inverso para apilamiento correcto
        for surface, y_offset, x in reversed(surfaces):
            char_width, char_height = surface.get_size()
            # Dibujar fondo directamente detrás de cada letra
            char_background = pygame.Rect(x - padding, buffer + y_offset - padding,
                                          char_width + padding * 2, char_height + padding * 2)
            pygame.draw.rect(title_surface, background_color, char_background)  # Fondo del texto
            pygame.draw.rect(title_surface, (255, 255, 255), char_background, 2)  # Bordes blancos

            # Dibujar letra sobre el fondo
            title_surface.blit(surface, (x, buffer + y_offset))

        return title_surface

    def render_buttons(self, screen):
        """Dibuja los botones con un efecto de tambaleo."""
        amplitude = 5  # Amplitud del tambaleo
        frequency = 0.09  # Frecuencia del tambaleo

        for i, (text, rect) in enumerate(self.buttons.items()):
            # Calcular el desplazamiento de tambaleo
            x_offset = amplitude * math.sin(frequency * (self.frame_count + i * 20))
            y_offset = amplitude * math.cos(frequency * (self.frame_count + i * 20))
            wavy_rect = rect.move(x_offset, y_offset)
            # Dibujar el botón
            pygame.draw.rect(screen, (100, 100, 255), wavy_rect)  # Botón azul
            pygame.draw.rect(screen, (255, 255, 255), wavy_rect, 2)  # Bordes blancos
            # Dibujar el texto del botón
            button_text = self.button_font.render(text, True, (255, 255, 255))
            text_rect = button_text.get_rect(center=wavy_rect.center)
            screen.blit(button_text, text_rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return "QUIT"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.buttons["INICIAR"].collidepoint(mouse_pos):
                    self.start_sound.play()
                    return "START"
                elif self.buttons["SALIR"].collidepoint(mouse_pos):
                    self.running = False
                    return "QUIT"
                elif math.sqrt((mouse_pos[0] - self.help_button_center[0]) ** 2 +
                               (mouse_pos[1] - self.help_button_center[1]) ** 2) <= self.help_button_radius:
                    return "HELP"
        return None

    def update(self):
        self.frame_count += 1

class InstructionsScreen:
    def __init__(self, screen, instructions):
        self.screen = screen
        self.instructions = instructions
        self.current_index = 0
        self.arrow_size = (50, 50)
        self.left_arrow = pygame.image.load(resource_path("Resource/Instructions/flecha-izquierda.jpg"))
        self.left_arrow = pygame.transform.scale(self.left_arrow, self.arrow_size)
        self.right_arrow = pygame.image.load(resource_path("Resource/Instructions/flecha-derecha.jpg"))
        self.right_arrow = pygame.transform.scale(self.right_arrow, self.arrow_size)
        self.font = pygame.font.Font(None, 50)
        self.gif_timer = 0
        self.gif_frame_index = 0
        self.gif_delay = 55  # Tiempo (en milisegundos) entre cada cuadro del GIF

    def load_gif(self, gif_path):
        """Carga un GIF animado """
        gif = Image.open(gif_path)
        frames = []

        try:
            while True:
                frame = gif.copy().convert("RGBA")
                frame_surface = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode)
                frames.append(frame_surface)
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass

        return frames

    def draw(self):
        self.screen.fill((0, 0, 0))
        if self.current_index < 0 or self.current_index >= len(self.instructions):
            print("Error: Índice de instrucciones fuera de rango.")
            return
        instruction = self.instructions[self.current_index]

        if isinstance(instruction["image"], list):
            current_time = pygame.time.get_ticks()
            if current_time - self.gif_timer >= self.gif_delay:
                self.gif_frame_index = (self.gif_frame_index + 1) % len(instruction["image"])
                self.gif_timer = current_time
            gif_frame = instruction["image"][self.gif_frame_index]
            image_rect = gif_frame.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 50))
            self.screen.blit(gif_frame, image_rect)
        else:
            image = pygame.transform.scale(instruction["image"], (1000, 400))
            image_rect = image.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 50))
            self.screen.blit(image, image_rect)
        # Dibuja el texto de la instrucción
        instruction_text = self.font.render(instruction["text"], True, (255, 255, 255))
        instruction_rect = instruction_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 200))
        self.screen.blit(instruction_text, instruction_rect)
        # Dibuja las flechas
        self.screen.blit(self.left_arrow, (50, self.screen.get_height() - 100))
        self.screen.blit(self.right_arrow, (self.screen.get_width() - 100, self.screen.get_height() - 100))
        # Texto para regresar al menú
        return_text = self.font.render("Presiona 'ESC' para regresar al menú", True, (255, 255, 255))
        return_rect = return_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 50))
        self.screen.blit(return_text, return_rect)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "MENU"
            elif event.key == pygame.K_RIGHT:
                self.current_index = (self.current_index + 1) % len(self.instructions)
            elif event.key == pygame.K_LEFT:
                self.current_index = (self.current_index - 1) % len(self.instructions)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if 50 <= mouse_pos[0] <= 100 and self.screen.get_height() - 100 <= mouse_pos[1] <= self.screen.get_height():
                self.current_index = (self.current_index - 1) % len(self.instructions)
            elif self.screen.get_width() - 100 <= mouse_pos[0] <= self.screen.get_width() - 50 and \
                    self.screen.get_height() - 100 <= mouse_pos[1] <= self.screen.get_height():
                self.current_index = (self.current_index + 1) % len(self.instructions)

        return None
