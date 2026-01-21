#animacion.py
import os
import sys
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
from PIL import Image
from primes import generate_primes, factorize_number
import pygame.mixer

def resource_path(relative_path):
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class Sphere:
    def __init__(self, num, radius, position, velocity, is_prime=False):
        self.num = num
        self.radius = radius
        self.position = np.array(position)
        self.velocity = np.array(velocity)
        self.color_t = 0.0
        self.alive = True
        self.is_prime = is_prime
        self.flash_state = False
        self.rotation_angle = 0.0
        self.rotation_speed = np.random.uniform(0.5, 2.0)

        if self.is_prime:
            self.color_start = (0.0, 1.0, 0.0)  # Verde
            self.color_end = (1.0, 1.0, 0.0)  # Amarillo

        else:
            self.color_start = (1.0, 0.0, 0.0)  # Rojo
            self.color_end = (0.0, 0.0, 1.0)  # Azu

    def update_position(self, bounds):
        self.position += self.velocity

        # Actualizar rotación
        self.rotation_angle += self.rotation_speed
        if self.rotation_angle >= 360:
            self.rotation_angle -= 360

        # Interpolación de colores
        self.color_t += 0.01
        if self.color_t > 1.0:
            self.color_t = 0.0

        # Interpolación de color según si es primo o no
        if self.is_prime:
            if self.color_t < 0.5:
                # Primera mitad del ciclo: de verde a naranja
                self.color = self.interpolate_color(self.color_start, (1.0, 0.5, 0.0), self.color_t * 2)
            else:
                # Segunda mitad del ciclo: de naranja a amarillo
                self.color = self.interpolate_color((1.0, 0.5, 0.0), self.color_end, (self.color_t - 0.5) * 2)
        else:
            # Esferas no primas
            self.color = self.interpolate_color(self.color_start, self.color_end, self.color_t)

        # Verificar colisiones con los límites del espacio
        for i in range(3):
            if self.position[i] - self.radius < -bounds[i]:
                self.position[i] = -bounds[i] + self.radius
                self.velocity[i] *= -1  # Invertir dirección
            elif self.position[i] + self.radius > bounds[i]:
                self.position[i] = bounds[i] - self.radius
                self.velocity[i] *= -1

    def interpolate_color(self, color_start, color_end, t):
        """Realiza la interpolación lineal entre dos colores."""
        return tuple(color_start[i] + (color_end[i] - color_start[i]) * t for i in range(3))

    def draw_face(self):
        """Dibuja una carita feliz en la esfera."""
        glPushMatrix()
        glTranslatef(0.0, 0.0, self.radius + 0.01)

        # Dibujar ojos
        glColor3f(0.0, 0.0, 0.0)  # Negro para los ojos
        glPointSize(4)  # Tamaño de los puntos (ojos)
        glBegin(GL_POINTS)
        glVertex2f(-0.09, 0.09)  # Ojo izquierdo
        glVertex2f(0.09, 0.09)  # Ojo derecho
        glEnd()

        # Dibujar boca (invertida)
        glBegin(GL_LINE_STRIP)
        for angle in np.linspace(0, np.pi, 100):  # Rango de 0 a π para invertir el arco
            x = 0.30 * np.cos(angle)  # Radio de la boca
            y = -0.30 * np.sin(angle)  # Y negativo para invertir
            glVertex2f(x, y)
        glEnd()

        glPopMatrix()

    def draw(self):
        if not self.alive:
            return

        glPushMatrix()
        glTranslatef(*self.position)  # Mueve la esfera a su posición actual

        # Aplica rotación
        glRotatef(self.rotation_angle, 1.0, 1.0, 0.0)  # Rotación uniforme en todos los ejes

        if self.is_prime:
            # Dibujar contorno brillante para las esferas primas
            glColor3f(1.0, 1.0, 1.0)  # Contorno blanco
            quad = gluNewQuadric()
            gluSphere(quad, self.radius + 0.05, 50, 50)

        # Dibujar la esfera con iluminación
        glColor3f(*self.color)  # Color de la esfera
        quad = gluNewQuadric()
        gluSphere(quad, self.radius, 50, 50)

        # Dibujar la carita feliz
        self.draw_face()
        glPopMatrix()

    def set_color(self):
        """Asigna un color basado en si la esfera es primo o no."""
        if self.is_prime:
            self.color = (0.0, 1.0, 0.0)  # Verde para primos
        else:
            self.color = (1.0, 0.0, 0.0)  # Rojo para no primos


    def check_collision(self, x, y, display_width, display_height):
        """Verifica si el clic del ratón colisiona con la esfera (vista en 2D)."""
        if not self.alive:
            return False

        # Convertir la posición 3D de la esfera a coordenadas 2D en la pantalla
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)
        win_x, win_y, win_z = gluProject(self.position[0], self.position[1], self.position[2], modelview, projection, viewport)
        mouse_y = display_height - y
        dist = np.sqrt((win_x - x) ** 2 + (win_y - mouse_y) ** 2)
        scale_factor = 40
        scaled_radius = self.radius * viewport[3] / display_height * scale_factor
        return dist <= scaled_radius

class Animation:
    def __init__(self, width, height, num_spheres):
        #Inicialización de propiedades principales:
        self.width = width
        self.height = height
        self.num_spheres = num_spheres
        #Configuración inicial del estado del juego:
        self.level = 1
        self.prime_ratio = 0.5
        self.current_spheres = 40
        #Listas y colecciones:
        self.spheres = []
        self.particles = []
        #Manejo de los límites y propiedades del juego:
        self.bounds = [9, 6, 6] #cubo delimitador
        self.primes = generate_primes(100)
        #Variables relacionadas con la puntuación y estado del juego:
        self.score = 0
        self.hit_primes = []
        self.eliminated_spheres = 0
        #eventos
        self.paused = False
        self.defeat_displayed = False
        self.lost = False
        self.defeat = False
        #Tiempo y niveles:
        self.remaining_time = 90
        self.last_time_update = pygame.time.get_ticks()
        self.time_decrement_per_level = 15
        self.sad_faces = []
        self.victory_gif_frames = []
        self.victory_gif_index = 0
        self.victory_gif_timer = 0
        self.victory_gif_delay = 100
        self.non_prime_destroyed = 0
        self.max_non_prime_destroyed = 5
        self.lose_score = -50
        self.primes_destroyed = 0
        self.total_spheres_destroyed = 0

        #Inicialización de botones y efectos visuales:
        self.buttons = []
        self.init_lighting()
        self.load_textures()
        self.victory_displayed = False
        self.victory = False

        #Configuración de audio:
        pygame.mixer.init()
        self.sound_prime = pygame.mixer.Sound(resource_path("Resource/esfera-prima.mp3"))
        self.sound_non_prime = pygame.mixer.Sound(resource_path("Resource/esfera-no-prima.mp3"))
        self.victory_music = resource_path("Resource/ganar.mp3")  # Ruta al archivo de música de victoria
        self.game_music = resource_path("Resource/Soundtrack.mp3")

        pygame.mixer.music.load(self.game_music)
        pygame.mixer.music.set_volume(0.5)  # Ajustar volumen
        pygame.mixer.music.play(-1)  # Reproducir en bucle

        self.defeat_texture_id = self.load_defeat_image(resource_path("Resource/MEMES/A-dar-lastima-a-otro-lado.jpg"))
        self.load_victory_gif(resource_path("Resource/MEMES/gmod-skeleton.gif"))
        self.current_victory_frame = 0

        # Inicializar caritas tristes
        self.spawn_sad_faces()

        self.reset_game()

    def reset_game(self):

        self.score = 0
        self.hit_primes = []
        self.eliminated_spheres = 0
        self.spheres = []
        self.remaining_time = max(90 - (self.level - 1) * 15, 15)  # Reinicia el tiempo según el nivel
        self.last_time_update = pygame.time.get_ticks()
        self.create_spheres(self.num_spheres)  # Usa el número actual de esferas
        self.victory = False
        self.victory_displayed = False
        self.defeat_displayed = False
        self.lost = False
        self.defeat = False
        self.paused = False

        # Reproducir la música del juego
        pygame.mixer.music.stop()
        pygame.mixer.music.load(self.game_music)
        pygame.mixer.music.play(-1)  # Reproducir en bucle

    def update_timer(self):
        """Actualiza el temporizador, """
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - self.last_time_update) / 1000  # Convertir a segundos

        if elapsed_time >= 1:
            self.remaining_time -= 1
            self.last_time_update = current_time

        if self.remaining_time <= 0:
            self.remaining_time = 0
            self.lost = True

    def draw_timer(self):
        """Dibuja el temporizador en la parte superior del cubo."""
        if self.victory or self.lost:  # No mostrar el temporizador en estas pantallas
            return

        glColor3f(1.0, 1.0, 1.0)  # Color blanco para el texto
        viewport = glGetIntegerv(GL_VIEWPORT)
        text_position = (viewport[2] // 2 - 100, viewport[3] - 50)  # Centrar el texto en la parte superior

        # Formatear el tiempo restante como MM:SS
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        timer_text = f"Tiempo restante: {minutes:02}:{seconds:02}"

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, viewport[2], 0, viewport[3])
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # Renderizar el texto
        self.render_text(timer_text, text_position)

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def create_spheres(self, total_spheres=None):
        """Crea las esferas según el nivel actual."""
        if total_spheres is None:
            total_spheres = self.num_spheres  # Valor predeterminado

        prime_count = int(20 * (0.95 ** (self.level - 1)))  # Primas disminuyen un 5% por nivel
        non_prime_count = total_spheres - prime_count  # El resto son no primas

        self.spheres = []

        # Multiplicador de velocidad ajustado
        speed_multiplier = 0.5 * (1.30 ** min(self.level - 1, 15))

        initial_prime_radius = 0.70

        for i in range(prime_count):
            position = [
                np.random.uniform(-self.bounds[0], self.bounds[0]),
                np.random.uniform(-self.bounds[1], self.bounds[1]),
                np.random.uniform(-self.bounds[2], self.bounds[2])
            ]
            velocity = [
                np.random.uniform(-0.05 * speed_multiplier, 0.05 * speed_multiplier),
                np.random.uniform(-0.05 * speed_multiplier, 0.05 * speed_multiplier),
                np.random.uniform(-0.05 * speed_multiplier, 0.05 * speed_multiplier)
            ]
            radius = initial_prime_radius * (0.95 ** (self.level - 1))
            sphere = Sphere(i + 1, radius, position, velocity, is_prime=True)
            sphere.set_color()
            self.spheres.append(sphere)

        # Crear esferas no primas
        for i in range(non_prime_count):
            position = [
                np.random.uniform(-self.bounds[0], self.bounds[0]),
                np.random.uniform(-self.bounds[1], self.bounds[1]),
                np.random.uniform(-self.bounds[2], self.bounds[2])
            ]
            velocity = [
                np.random.uniform(-0.05 * speed_multiplier, 0.05 * speed_multiplier),
                np.random.uniform(-0.05 * speed_multiplier, 0.05 * speed_multiplier),
                np.random.uniform(-0.05 * speed_multiplier, 0.05 * speed_multiplier)
            ]
            radius = 0.90  # Mantener el tamaño de las esferas no primas constante
            sphere = Sphere(prime_count + i + 1, radius, position, velocity, is_prime=False)
            sphere.set_color()
            self.spheres.append(sphere)

    def update_scene(self):
        """Actualiza la escena."""
        if self.victory or self.lost or self.paused:  # Detener actualizaciones si hay victoria, derrota o pausa
            return

        self.update_timer()
        for sphere in self.spheres:
            sphere.update_position(self.bounds)
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update()

        # Verificar si se pierde el juego
        if self.score <= -40:
            self.lost = True
            pygame.mixer.music.stop()  # Detener música del juego
            self.play_defeat_music()

        self.check_victory()

    def render_scene(self):
        """Renderiza la escena."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Limpia la pantalla en cada renderizado

        # Si hay victoria, mostrar pantalla de victoria con el GIF animado
        if self.victory:

            self.draw_victory_gif()  # Renderiza el GIF animado
            self.draw_win_screen()
            self.handle_victory_events()

            return

        # Si hay derrota, mostrar pantalla de derrota
        if self.lost:
            if not hasattr(self, 'sad_faces') or not self.sad_faces:
                self.spawn_sad_faces()  # Generar caritas si aún no existen
            self.draw_defeat_screen()
            self.handle_loss_events()

            return

        # Renderizar el juego normal
        self.draw_wireframe_cube()
        for sphere in self.spheres:
            sphere.draw()
        for particle in self.particles:
            particle.draw()

        # Dibujar HUD y temporizador
        self.draw_hud()
        self.draw_timer()

        # Si el juego está pausado
        if self.paused and not self.victory and not self.lost:
            self.draw_pause_message()


    def next_level(self):
        self.paused = True
        self.victory = False
        self.victory_displayed = False
        self.victory_gif_index = 0
        self.victory_gif_timer = pygame.time.get_ticks()
        self.level += 1
        for sphere in self.spheres:
            if self.level <= 15:
                if sphere.is_prime:
                    sphere.radius *= 1.1
                sphere.velocity *= 1.1
            else:

                sphere.velocity = sphere.velocity
                if sphere.is_prime:
                    sphere.radius = sphere.radius

        prime_count = int(20 * (0.95 ** (self.level - 1)))
        non_prime_count = self.num_spheres - prime_count
        self.create_spheres(prime_count + non_prime_count)
        self.reset_game()
        self.remaining_time = max(15, 90 - (self.level - 1) * 15)
        self.last_time_update = pygame.time.get_ticks()


        print(
            f"Nivel {self.level} iniciado: {prime_count} esferas primas, {non_prime_count} no primas. Tiempo restante: {self.remaining_time} segundos.")


        self.paused = False

    def load_textures(self):

        image_files = [
            resource_path("Resource/Backgrounds/frente_2.jpg"),
            resource_path("Resource/Backgrounds/izquierda_2.jpg"),
            resource_path("Resource/Backgrounds/derecha_2.jpg"),
            resource_path("Resource/Backgrounds/arriba_2.jpg"),
            resource_path("Resource/Backgrounds/abajo_2.jpg"),
        ]

        self.texture_ids = glGenTextures(len(image_files))

        for i, image_file in enumerate(image_files):
            texture_image = pygame.image.load(image_file)
            texture_data = pygame.image.tostring(texture_image, "RGB", True)
            width, height = texture_image.get_size()

            glBindTexture(GL_TEXTURE_2D, self.texture_ids[i])
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)


            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    def draw_wireframe_cube(self):
        glEnable(GL_TEXTURE_2D)


        glBindTexture(GL_TEXTURE_2D, self.texture_ids[0])
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-self.bounds[0], -self.bounds[1], -self.bounds[2])
        glTexCoord2f(1.0, 0.0)
        glVertex3f(self.bounds[0], -self.bounds[1], -self.bounds[2])
        glTexCoord2f(1.0, 1.0)
        glVertex3f(self.bounds[0], self.bounds[1], -self.bounds[2])
        glTexCoord2f(0.0, 1.0)
        glVertex3f(-self.bounds[0], self.bounds[1], -self.bounds[2])
        glEnd()


        glBindTexture(GL_TEXTURE_2D, self.texture_ids[1])
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-self.bounds[0], -self.bounds[1], self.bounds[2])
        glTexCoord2f(1.0, 0.0)
        glVertex3f(-self.bounds[0], -self.bounds[1], -self.bounds[2])
        glTexCoord2f(1.0, 1.0)
        glVertex3f(-self.bounds[0], self.bounds[1], -self.bounds[2])
        glTexCoord2f(0.0, 1.0)
        glVertex3f(-self.bounds[0], self.bounds[1], self.bounds[2])
        glEnd()


        glBindTexture(GL_TEXTURE_2D, self.texture_ids[2])
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(self.bounds[0], -self.bounds[1], -self.bounds[2])
        glTexCoord2f(1.0, 0.0)
        glVertex3f(self.bounds[0], -self.bounds[1], self.bounds[2])
        glTexCoord2f(1.0, 1.0)
        glVertex3f(self.bounds[0], self.bounds[1], self.bounds[2])
        glTexCoord2f(0.0, 1.0)
        glVertex3f(self.bounds[0], self.bounds[1], -self.bounds[2])
        glEnd()

        glBindTexture(GL_TEXTURE_2D, self.texture_ids[3])
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-self.bounds[0], self.bounds[1], -self.bounds[2])
        glTexCoord2f(1.0, 0.0)
        glVertex3f(self.bounds[0], self.bounds[1], -self.bounds[2])
        glTexCoord2f(1.0, 1.0)
        glVertex3f(self.bounds[0], self.bounds[1], self.bounds[2])
        glTexCoord2f(0.0, 1.0)
        glVertex3f(-self.bounds[0], self.bounds[1], self.bounds[2])
        glEnd()

        # Cara inferior
        glBindTexture(GL_TEXTURE_2D, self.texture_ids[4])
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-self.bounds[0], -self.bounds[1], self.bounds[2])
        glTexCoord2f(1.0, 0.0)
        glVertex3f(self.bounds[0], -self.bounds[1], self.bounds[2])
        glTexCoord2f(1.0, 1.0)
        glVertex3f(self.bounds[0], -self.bounds[1], -self.bounds[2])
        glTexCoord2f(0.0, 1.0)
        glVertex3f(-self.bounds[0], -self.bounds[1], -self.bounds[2])
        glEnd()

        glDisable(GL_TEXTURE_2D)

        # Dibujar contorno del cubo
        self.draw_cube_wireframe()

    def draw_cube_wireframe(self):
        """Dibuja los contornos del cubo usando OpenGL puro en lugar de glutWireCube."""
        glColor3f(1.0, 1.0, 1.0)  # Contornos blancos
        glPushMatrix()

        # Escalar según los bounds del cubo
        glScalef(self.bounds[0], self.bounds[1], self.bounds[2])

        # Definir los vértices del cubo unitario
        vertices = [
            # Cara frontal
            [-1, -1, 1],  # 0
            [1, -1, 1],  # 1
            [1, 1, 1],  # 2
            [-1, 1, 1],  # 3
            # Cara trasera
            [-1, -1, -1],  # 4
            [1, -1, -1],  # 5
            [1, 1, -1],  # 6
            [-1, 1, -1],  # 7
        ]

        # Definir las aristas del cubo (pares de índices de vértices)
        edges = [
            # Aristas de la cara frontal
            (0, 1), (1, 2), (2, 3), (3, 0),
            # Aristas de la cara trasera
            (4, 5), (5, 6), (6, 7), (7, 4),
            # Aristas que conectan frente con atrás
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]

        # Dibujar las aristas usando líneas
        glBegin(GL_LINES)
        for edge in edges:
            for vertex_index in edge:
                glVertex3fv(vertices[vertex_index])
        glEnd()

        glPopMatrix()

    def draw_hud(self):
        """Dibuja el HUD """
        # Establecer color blanco para el texto
        glColor3f(1.0, 1.0, 1.0)
        viewport = glGetIntegerv(GL_VIEWPORT)
        y_offset = 20
        line_height = 20  # Altura de línea para el texto del HUD

        # Usar proyección ortográfica para texto HUD
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, viewport[2], 0, viewport[3])
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # Renderizar el texto con las posiciones correctas
        self.render_text(f"Nivel: {self.level}", (10, viewport[3] - y_offset))
        self.render_text(f"Puntuacion: {self.score}", (10, viewport[3] - (y_offset + 1 * line_height)))
        self.render_text(f"Esferas restantes: {len(self.spheres)}",
                         (10, viewport[3] - (y_offset + 2 * line_height)))

        self.render_text(f"Primes golpeados: {len(self.hit_primes)}",
                         (10, viewport[3] - (y_offset + 3 * line_height)))
        self.render_text(f"Eliminados: {self.eliminated_spheres}",
                         (10, viewport[3] - (y_offset + 4 * line_height)))

        # Instrucciones en la parte izquierda
        self.render_text("'P' para pausar", (10, viewport[3] - (y_offset + 6 * line_height)))
        self.render_text("'R' para reiniciar", (10, viewport[3] - (y_offset + 7 * line_height)))

        # Instrucciones en la esquina superior derecha
        esc_text = "'ESC' para salir"
        esc_text_width = len(esc_text) * 8  # Aproximadamente 8 píxeles por carácter
        self.render_text(esc_text, (viewport[2] - esc_text_width - 10, viewport[3] - y_offset))

        # Restaurar matrices
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def draw_win_screen(self):
        """Dibuja la pantalla de victoria con partículas de confeti y el GIF animado."""
        self.draw_color_changing_background()  # Fondo dinámico

        viewport = glGetIntegerv(GL_VIEWPORT)
        center_x, center_y = viewport[2] // 2, viewport[3] // 2

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, viewport[2], 0, viewport[3])
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # Dibujar texto de victoria
        glDisable(GL_LIGHTING)
        glColor3f(1.0, 1.0, 1.0)  # Blanco
        glRasterPos2f(center_x - 60, center_y + 40)  # Posición para "¡GANASTE!"
        for char in "¡GANASTE!":
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
        glRasterPos2f(center_x - 100, center_y)  # Posición para "Presiona 'X' para continuar"
        for char in "Presiona 'X' para continuar":
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
        glRasterPos2f(center_x - 100, center_y - 40)  # Posición para "Presiona 'ESC' para salir"
        for char in "Presiona 'ESC' para salir":
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
        glEnable(GL_LIGHTING)

        # Dibujar partículas de confeti
        for particle in self.particles:
            particle.draw()

        # Dibujar el GIF animado
        self.draw_victory_gif()

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def draw_color_changing_background(self):
        """Dibuja un fondo con colores cambiantes dinámicos."""
        time_elapsed = pygame.time.get_ticks() / 1000  # Tiempo en segundos
        r = (np.sin(time_elapsed) + 1) / 2  # Oscilación de 0 a 1
        g = (np.sin(time_elapsed + 2) + 1) / 2
        b = (np.sin(time_elapsed + 4) + 1) / 2

        glClearColor(r, g, b, 1.0)  # Establece el color de fondo
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        def spawn_confetti(self):
            """Genera partículas de confeti en la pantalla de victoria."""
            for _ in range(50):  # Número de partículas
                position = [
                    np.random.uniform(-self.bounds[0], self.bounds[0]),
                    np.random.uniform(-self.bounds[1], self.bounds[1]),
                    np.random.uniform(-self.bounds[2], self.bounds[2])
                ]
                velocity = [
                    np.random.uniform(-0.05, 0.05),
                    np.random.uniform(-0.05, 0.05),
                    np.random.uniform(-0.05, 0.05)
                ]
                color = (np.random.uniform(0.0, 1.0),  # Rojo aleatorio
                         np.random.uniform(0.0, 1.0),  # Verde aleatorio
                         np.random.uniform(0.0, 1.0))  # Azul aleatorio
                lifespan = 60  # Duración de las partículas
                self.particles.append(Particle(position, velocity, color, lifespan))

    def check_victory(self):
        """Verifica si todas las esferas primas fueron eliminadas."""
        if all(not s.is_prime for s in self.spheres):  # Verifica si no hay más esferas primas
            self.victory = True
            self.paused = True
            self.victory_displayed = True

            # Detener la música del juego y reproducir la música de victoria
            pygame.mixer.music.stop()
            pygame.mixer.music.load(self.victory_music)
            pygame.mixer.music.play(-1)



            print("¡GANASTE! Esperando entrada para continuar al siguiente nivel.")

    def load_victory_gif(self, gif_path):
        """Carga un GIF animado y lo divide en fotogramas."""
        try:
            gif = Image.open(gif_path)  # Abre el GIF con Pillow
            gif_frames = []

            for frame in range(gif.n_frames):  # Iterar sobre todos los fotogramas
                gif.seek(frame)  # Moverse al siguiente fotograma
                frame_surface = pygame.image.fromstring(
                    gif.tobytes(), gif.size, gif.mode
                )
                gif_frames.append(frame_surface)

            self.victory_gif_frames = gif_frames
        except Exception as e:
            print(f"Error al cargar el GIF: {e}")
            self.victory_gif_frames = []



    def draw_victory_gif(self):
        """Dibuja el GIF animado en el centro de la pantalla con colores originales."""
        if not self.victory_gif_frames:  # Verificar si los fotogramas del GIF están cargados
            print("No se cargaron los fotogramas del GIF.")
            return

        # Calcular el tiempo transcurrido para determinar el fotograma actual
        current_time = pygame.time.get_ticks()
        if current_time - self.victory_gif_timer >= self.victory_gif_delay:
            self.victory_gif_index = (self.victory_gif_index + 1) % len(self.victory_gif_frames)
            self.victory_gif_timer = current_time

        # Obtener el fotograma actual
        current_frame = self.victory_gif_frames[self.victory_gif_index]

        # Asegurarse de que el formato sea RGB
        frame_surface = pygame.transform.flip(current_frame, False, True)  # Voltear verticalmente para OpenGL
        frame_surface = frame_surface.convert(24)  # Convertir explícitamente a RGB sin alfa
        texture_data = pygame.image.tostring(frame_surface, "RGB", True)

        # Configurar la textura del fotograma actual
        width, height = frame_surface.get_size()
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)

        # Configurar parámetros de la textura
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # Dibujar el fotograma como un cuadrado en el centro de la pantalla
        viewport = glGetIntegerv(GL_VIEWPORT)
        center_x = viewport[2] // 2
        center_y = viewport[3] // 4
        size = min(viewport[2], viewport[3]) // 6

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)

        glColor3f(1.0, 1.0, 1.0)  # Asegurarnos de que el color sea blanco para no alterar la textura
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 1.0)
        glVertex2f(center_x - size, center_y - size)  # Esquina inferior izquierda
        glTexCoord2f(1.0, 1.0)
        glVertex2f(center_x + size, center_y - size)  # Esquina inferior derecha
        glTexCoord2f(1.0, 0.0)
        glVertex2f(center_x + size, center_y + size)  # Esquina superior derecha
        glTexCoord2f(0.0, 0.0)
        glVertex2f(center_x - size, center_y + size)  # Esquina superior izquierda
        glEnd()

        glDisable(GL_TEXTURE_2D)

        # Eliminar la textura después de usarla
        glDeleteTextures([texture_id])

    def draw_defeat_screen(self):
        """Dibuja la pantalla de derrota con una imagen de fondo correctamente proporcionada y caritas tristes."""
        if hasattr(self, 'defeat_texture_id') and self.defeat_texture_id:
            # Calcular las proporciones de la imagen
            texture_width = self.defeat_image.get_width()
            texture_height = self.defeat_image.get_height()
            aspect_ratio = texture_width / texture_height

            # Establecer las dimensiones para mantener proporción
            display_width = 6.0  # Ajusta este valor para hacerla más grande
            display_height = display_width / aspect_ratio  # Calcular altura en base al ancho y proporción

            # Ajustar la posición vertical para colocar más abajo del texto
            y_offset = -1.0  # Más abajo en la pantalla

            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.defeat_texture_id)

            # Dibujar la imagen con la proporción adecuada
            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 1.0)  # Coordenadas de textura (invertidas para corregir orientación)
            glVertex2f(-display_width / 2, y_offset - display_height)  # Esquina inferior izquierda
            glTexCoord2f(1.0, 1.0)
            glVertex2f(display_width / 2, y_offset - display_height)  # Esquina inferior derecha
            glTexCoord2f(1.0, 0.0)
            glVertex2f(display_width / 2, y_offset)  # Esquina superior derecha
            glTexCoord2f(0.0, 0.0)
            glVertex2f(-display_width / 2, y_offset)  # Esquina superior izquierda
            glEnd()

            glDisable(GL_TEXTURE_2D)

        # Usar proyección ortográfica para texto y HUD
        viewport = glGetIntegerv(GL_VIEWPORT)
        center_x = viewport[2] // 2
        center_y = viewport[3] // 2

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, viewport[2], 0, viewport[3])
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # Texto de derrota
        glDisable(GL_BLEND)
        self.render_text("¡PERDISTE!", (center_x - 60, center_y + 80))
        self.render_text("Presiona 'R' para reiniciar", (center_x - 100, center_y + 40))
        self.render_text("Presiona 'ESC' para salir", (center_x - 100, center_y))
        glEnable(GL_BLEND)

        # Dibujar caritas tristes
        self.draw_sad_faces()

        # Restaurar matrices
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def load_defeat_image(self, image_path):
        """Carga la imagen de derrota, quita el ruido visual y la guarda para el HUD."""
        try:
            # 1. Cargar y guardar en el atributo de la clase para evitar el AttributeError
            self.defeat_image = pygame.image.load(image_path)

            # 2. Preparar la imagen para OpenGL (voltear y convertir a string)
            flipped_image = pygame.transform.flip(self.defeat_image, False, True)
            image_data = pygame.image.tostring(flipped_image, "RGB", True)
            width, height = flipped_image.get_size()

            # 3. Generar y configurar la textura
            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)

            # --- LÍNEA CLAVE PARA QUITAR LAS RAYAS DE COLORES ---
            # Fuerza a OpenGL a leer los bytes uno por uno, sin importar el ancho de la imagen.
            glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
            # ---------------------------------------------------

            # 4. Configurar filtros para que la imagen no se vea borrosa
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

            # 5. Cargar los datos en la tarjeta de video
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, image_data)

            return texture_id

        except pygame.error as e:
            print(f"Error al cargar la textura de derrota: {e}")
            self.defeat_image = None
            return None

    def check_loss(self):
        """Verifica si se ha perdido la partida."""
        if self.non_prime_destroyed >= 4:  # Solo la condición de destruir 4 esferas no primas
            if not self.lost:  # Solo activar la pérdida si no está ya activada
                self.lost = True
                self.paused = True  # Pausar el juego al perder
                pygame.mixer.music.stop()  # Detener música
                self.play_defeat_music()
                self.spawn_sad_faces()  # Generar caritas tristes
                print("¡Has perdido! Se destruyeron 4 esferas no primas.")  # Depuración

    def play_defeat_music(self):
        """Reproduce música de derrota."""
        pygame.mixer.music.load(resource_path("Resource/Lose.mp3")) # Ruta de tu archivo de música de derrota
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(1)  # Reproducir una sola vez

    def spawn_sad_faces(self):
        """Genera una mayor cantidad de caritas tristes en posiciones aleatorias."""
        self.sad_faces = []
        viewport = glGetIntegerv(GL_VIEWPORT)
        width, height = viewport[2], viewport[3]

        for _ in range(30):  # Generar más caritas (ajustar el número si se necesita más)
            position = (
                np.random.uniform(0, width),  # Posición X dentro del viewport
                np.random.uniform(0, height)  # Posición Y dentro del viewport
            )
            size = np.random.uniform(10, 20)  # Tamaño aleatorio (en píxeles)
            self.sad_faces.append({'position': position, 'size': size})

    def draw_sad_faces(self):
        glColor3f(1.0, 1.0, 1.0)  # Color blanco para las caritas

        for face in self.sad_faces:
            x, y = face['position']
            size = face['size'] * 1.5  # Aumentar el tamaño de las caritas multiplicando por un factor

            glPushMatrix()
            glTranslatef(x, y, 0)

            # Dibujar ojos (más arriba)
            glPointSize(size * 0.25)  # Aumentar el tamaño de los puntos para los ojos
            glBegin(GL_POINTS)
            glVertex2f(-0.3 * size, 0.5 * size)  # Ojo izquierdo más grande y más arriba
            glVertex2f(0.3 * size, 0.5 * size)  # Ojo derecho más grande y más arriba
            glEnd()

            # Dibujar boca invertida (curva hacia abajo, más grande)
            glBegin(GL_LINE_STRIP)
            for angle in np.linspace(0, np.pi, 100):
                glVertex2f(0.5 * size * np.cos(angle), 0.3 * size * np.sin(angle))  # Boca más grande
            glEnd()

            glPopMatrix()

    def render_text(self, text, position):
        glDisable(GL_LIGHTING)
        glColor3f(1.0, 1.0, 1.0)  # Color blanco brillante
        glRasterPos2f(*position)  # Establecer posición
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
        glEnable(GL_LIGHTING)
        # Usa una fuente más nítida

    def check_mouse_collision(self, x, y, display_width, display_height):
        """Verifica colisiones con el clic del ratón, priorizando las esferas no primas si están más cerca."""
        if not self.spheres:
            return

        # Convertir la posición 3D de cada esfera a coordenadas 2D en la pantalla
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)

        # Crear lista con las distancias de las esferas al clic
        spheres_distances = []
        for sphere in self.spheres:
            if sphere.alive:
                win_x, win_y, _ = gluProject(sphere.position[0], sphere.position[1], sphere.position[2], modelview,
                                             projection, viewport)
                mouse_y = display_height - y  # Corregir la coordenada Y
                dist = np.sqrt((win_x - x) ** 2 + (win_y - mouse_y) ** 2)
                spheres_distances.append((sphere, dist))  # Almacena la esfera junto con su distancia

        # Ordenar las esferas por distancia (de más cercana a más lejana)
        spheres_distances.sort(key=lambda x: x[1])

        # Procesar colisiones, priorizando las esferas no primas si están más cerca
        for sphere, _ in spheres_distances:
            if sphere.is_prime:
                # Si es prima y la distancia es suficientemente pequeña, hacer algo (ejemplo, explotar, etc.)
                if sphere.check_collision(x, y, display_width, display_height):
                    self.handle_prime_collision(sphere)
                    return  # Salir tras procesar una esfera
            else:
                # Si no es prima y la distancia es suficientemente pequeña, hacer algo (ejemplo, explotar, etc.)
                if sphere.check_collision(x, y, display_width, display_height):
                    self.handle_non_prime_collision(sphere)
                    return  # Salir tras procesar una esfera

        # Si no colisionó con ninguna, no hacer nada.

    def handle_prime_collision(self, sphere):
        self.score += 10
        self.hit_primes.append(sphere)
        self.eliminated_spheres += 1
        self.spheres.remove(sphere)
        self.spawn_explosion(sphere.position, True)
        self.sound_prime.play()

    def handle_non_prime_collision(self, sphere):
        self.score -= 15
        self.eliminated_spheres += 1
        self.spheres.remove(sphere)
        self.spawn_explosion(sphere.position, False)
        self.sound_non_prime.play()

    def spawn_explosion(self, position, is_prime):
        """Crea partículas para la explosión, con colores específicos según el tipo."""
        color = (0.0, 1.0, 0.0) if is_prime else (1.0, 0.0, 0.0)  # Verde para primas, rojo para no primas
        for _ in range(15 if is_prime else 7):
            velocity = [np.random.uniform(-0.1, 0.1),
                        np.random.uniform(-0.1, 0.1),
                        np.random.uniform(-0.1, 0.1)]
            lifespan = 40 if is_prime else 20  # Más duración para primas
            self.particles.append(Particle(position, velocity, color, lifespan))

    def draw_pause_message(self):
        """Muestra un mensaje de pausa en el centro de la pantalla."""
        viewport = glGetIntegerv(GL_VIEWPORT)
        center_x = viewport[2] // 2
        center_y = viewport[3] // 2

        # Usar proyección ortográfica para texto
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, viewport[2], 0, viewport[3])
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # Mensaje de pausa
        glDisable(GL_BLEND)
        self.render_text("PAUSADO", (center_x - 40, center_y + 20))
        self.render_text("Presiona 'P' para reanudar", (center_x - 90, center_y - 20))
        glEnable(GL_BLEND)

        # Restaurar matrices
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def handle_events(self):
        """Maneja todos los eventos del juego."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Si el juego está en estado de victoria, manejamos eventos de victoria
            elif self.victory:
                print("Juego en estado de victoria.")
                self.handle_victory_events()

            # Si el juego está en estado de derrota, manejamos eventos de derrota
            elif self.lost:
                print("Juego en estado de derrota.")
                self.handle_loss_events()


            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # Pausar/reanudar
                    self.paused = not self.paused
                elif event.key == pygame.K_r:  # Reiniciar el juego
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:  # Salir
                    pygame.quit()
                    sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.check_mouse_collision(mouse_x, mouse_y, self.width, self.height)

    def handle_victory_events(self):
        """Maneja los eventos cuando se muestra el mensaje de victoria."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Salir del juego
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:  # Continuar al siguiente nivel
                    self.next_level()
                elif event.key == pygame.K_ESCAPE:  # Salir del juego
                    pygame.quit()
                    sys.exit()

    def handle_loss_events(self):
        """Maneja los eventos de la pantalla de derrota."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Salir del juego
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Reiniciar el juego
                    print("Reiniciando el juego...")
                    self.reset_game()
                    self.lost = False
                    return
                elif event.key == pygame.K_ESCAPE:  # Salir del juego
                    print("Saliendo del juego...")
                    pygame.quit()
                    sys.exit()




    def init_lighting(self):
        glEnable(GL_LIGHTING)  # Habilitar el sistema de iluminación
        glEnable(GL_LIGHT0)  # Habilitar una luz

        # Configuración de la luz
        light_position = [1.0, 1.0, 1.0, 0.0]  # Posición de la luz
        light_ambient = [0.4, 0.4, 0.4, 1.0]  # Luz ambiental más fuerte
        light_diffuse = [1.0, 1.0, 1.0, 1.0]  # Luz difusa máxima
        light_specular = [1.5, 1.5, 1.5, 1.0]  # Luz especular más brillante

        glLightfv(GL_LIGHT0, GL_POSITION, light_position)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)

        # Configuración del material para las esferas
        material_specular = [1.0, 1.0, 1.0, 1.0]  # Reflejo especular
        material_shininess = [80.0]  # Mayor brillo del material

        glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular)
        glMaterialfv(GL_FRONT, GL_SHININESS, material_shininess)

        # Habilitar el suavizado de colores
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)

class Particle:
    def __init__(self, position, velocity, color, lifespan):
        self.position = np.array(position)
        self.velocity = np.array(velocity)
        self.color = color
        self.lifespan = lifespan
        self.age = 0

    def update(self):
        """Actualiza la posición y reduce la opacidad con el tiempo."""
        self.position += self.velocity
        self.age += 1

    def is_alive(self):
        """Devuelve True si la partícula aún está viva."""
        return self.age < self.lifespan

    def draw(self):
        alpha = max(0, 1 - self.age / self.lifespan)  # Opacidad decreciente
        glColor3f(self.color[0], self.color[1], self.color[2])
        glPointSize(6)  # Aumenta el tamaño de la partícula para que sea más visible
        glBegin(GL_POINTS)
        glVertex3f(*self.position)
        glEnd()