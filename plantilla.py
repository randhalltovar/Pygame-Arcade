from pygame import *
import random
import math

init()
font.init()
mixer.init()

# CONFIGURACIÓN Y CONSTANTES
ANCHO, ALTO = 800, 600
FPS = 60
TITULO = 'Pac-Man'

# Paleta de coloresssssssssssss
COLOR_FONDO = (13, 13, 13) # Negro NEGROO
CIAN_NEON = (0, 255, 255)
BLANCO = (255, 255, 255)
AMARILLO = (255, 255, 0)
AZUL_PALIDO = (173, 216, 230)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)

# Dimensiones de la matriz del tablero
FILAS = 20
COLUMNAS = 20
TAM_CELDA = 25 # C/celda 25x25 píxeles

# Centrar tablero pa que me deje espacio para el puntaje, vidas y eso
MARGEN_X = (ANCHO - (COLUMNAS * TAM_CELDA)) // 2
MARGEN_Y = 80

# Variables globales de control
vidas = 3
sonido_activo = True
estado_juego = "MENU" # Estados posibles: "MENU", "JUEGO", "GAME_OVER"

# Temporizador para puntos especiales
modo_huida = False
tiempo_huida_restante = 0

# Matriz lógica del tablero
# 1 = Pared, 0 = Camino vacío, 2 = Punto pequeño, 3 = Punto especial, 4 = Reaparición
MATRIZ_LABERINTO = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,3,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,3,1],
    [1,2,1,1,2,1,1,1,2,1,1,2,1,1,1,2,1,1,2,1],
    [1,2,1,1,2,1,1,1,2,1,1,2,1,1,1,2,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,2,1,2,1,1,1,1,1,1,2,1,2,1,1,2,1],
    [1,2,2,2,2,1,2,2,2,1,1,2,2,2,1,2,2,2,2,1],
    [1,1,1,1,2,1,1,1,0,1,1,0,1,1,1,2,1,1,1,1],
    [0,0,0,1,2,1,0,0,0,0,0,0,0,0,1,2,1,0,0,0],
    [1,1,1,1,2,1,0,1,1,4,4,1,1,0,1,2,1,1,1,1],
    [0,0,0,0,2,0,0,1,4,4,4,4,1,0,0,2,0,0,0,0],
    [1,1,1,1,2,1,0,1,1,1,1,1,1,0,1,2,1,1,1,1],
    [0,0,0,1,2,1,0,0,0,0,0,0,0,0,1,2,1,0,0,0],
    [1,1,1,1,2,1,2,1,1,1,1,1,1,2,1,2,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,2,1,1,1,2,1,1,2,1,1,1,2,1,1,2,1],
    [1,3,2,1,2,2,2,2,2,4,4,2,2,2,2,2,1,2,3,1],
    [1,1,2,1,2,1,2,1,1,1,1,1,1,2,1,2,1,2,1,1],
    [1,2,2,2,2,1,2,2,2,1,1,2,2,2,1,2,2,2,2,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

# Fuentes (de los deseos aaaa jsjsjsjjsadjhabsj)
fuente_titulo = font.SysFont('Arial', 50, bold=True)
fuente_interfaz = font.SysFont('Arial', 25, bold=True)


def generar_mapa():
    return [fila[:] for fila in MATRIZ_LABERINTO]

mapa_actual = generar_mapa()

# Fuentes
fuente_titulo = font.SysFont('Arial', 50, bold=True)
fuente_interfaz = font.SysFont('Arial', 25, bold=True)

# Configuración del botón de sonido con bocina.png
try:
    img_bocina = transform.scale(image.load("bocina.png"), (40, 40))
except:
    img_bocina = Surface((40, 40), SRCALPHA)
    img_bocina.fill((0, 200, 0))
    draw.polygon(img_bocina, BLANCO, [(10, 15), (20, 15), (30, 5), (30, 35), (20, 25), (10, 25)])

def crear_superficie_color(color, w, h, forma="rectangulo"):
    surf = Surface((w, h), SRCALPHA)
    if forma == "circulo":
        draw.circle(surf, color, (w // 2, h // 2), w // 2)
    elif forma == "fantasma":
        draw.circle(surf, color, (w // 2, h // 3 + 2), w // 3 + 2)
        draw.rect(surf, color, (w // 6, h // 3, 2 * w // 3, h // 2))
    else:
        surf.fill(color)
    return surf

img_corazon = crear_superficie_color(ROJO, 20, 20, "circulo")
img_rojo = crear_superficie_color(ROJO, TAM_CELDA - 4, TAM_CELDA - 4, "fantasma")
img_rosa = crear_superficie_color((255, 182, 193), TAM_CELDA - 4, TAM_CELDA - 4, "fantasma")
img_cian = crear_superficie_color(CIAN_NEON, TAM_CELDA - 4, TAM_CELDA - 4, "fantasma")
img_naranja = crear_superficie_color((255, 165, 0), TAM_CELDA - 4, TAM_CELDA - 4, "fantasma")
img_huida = crear_superficie_color(AZUL_PALIDO, TAM_CELDA - 4, TAM_CELDA - 4, "fantasma")

# 3. DEFINICIÓN DE CLASES
lass GameSprite(sprite.Sprite):
    def __init__(self, superficie_img, x_matriz, y_matriz):
        super().__init__()
        self.image = superficie_img
        self.rect = self.image.get_rect() if superficie_img else Rect(0, 0, TAM_CELDA - 4, TAM_CELDA - 4)
        self.grid_x = x_matriz
        self.grid_y = y_matriz
        self.actualizar_posicion_real()

    def actualizar_posicion_real(self):
        self.rect.x = MARGEN_X + self.grid_x * TAM_CELDA + (TAM_CELDA - self.rect.width) // 2
        self.rect.y = MARGEN_Y + self.grid_y * TAM_CELDA + (TAM_CELDA - self.rect.height) // 2

    def reset(self, surface):
        if self.image:
            surface.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    """Clase Pac-Man adaptada con diseño exclusivo de carita feliz."""
    def mover(self, dx, dy):
        nueva_x = self.grid_x + dx
        nueva_y = self.grid_y + dy
        
        if 0 <= nueva_x < COLUMNAS and 0 <= nueva_y < FILAS:
            if mapa_actual[nueva_y][nueva_x] != 1:
                self.grid_x = nueva_x
                self.grid_y = nueva_y
                self.actualizar_posicion_real()

    def reset(self, surface):
        centro_x = self.rect.x + self.rect.width // 2
        centro_y = self.rect.y + self.rect.height // 2
        radio = self.rect.width // 2

        # Dibujo de círculo amarillo base
        draw.circle(surface, AMARILLO, (centro_x, centro_y), radio)
        # Ojos negros pequeños
        draw.circle(surface, (0, 0, 0), (centro_x - 4, centro_y - 3), 2)
        draw.circle(surface, (0, 0, 0), (centro_x + 4, centro_y - 3), 2)
        # Arco de sonrisa feliz
        rect_sonrisa = Rect(centro_x - 5, centro_y - 2, 10, 8)
        draw.arc(surface, (0, 0, 0), rect_sonrisa, math.pi, 2 * math.pi, 2)

class Enemy(GameSprite):
    def __init__(self, superficie_img, x_matriz, y_matriz, tipo, img_normal):
        super().__init__(superficie_img, x_matriz, y_matriz)
        self.tipo = tipo
        self.img_normal = img_normal
        self.cooldown_movimiento = 0
        # Registro de la celda previa para prohibir el retroceso inmediato
        self.last_grid_x = x_matriz
        self.last_grid_y = y_matriz
        
    def update(self, player_x, player_y):
        self.cooldown_movimiento += 1
        if self.cooldown_movimiento < 12: 
            return
        self.cooldown_movimiento = 0

        if modo_huida:
            self.image = img_huida
            self.ejecutar_movimiento_huida(player_x, player_y)
        else:
            self.image = self.img_normal
            self.ejecutar_ia_normal(player_x, player_y)

    def obtener_movimientos_validos(self):
        movimientos = []
        direcciones = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dx, dy in direcciones:
            nx = self.grid_x + dx
            ny = self.grid_y + dy
            if 0 <= nx < COLUMNAS and 0 <= ny < FILAS:
                if mapa_actual[ny][nx] != 1:
                    # Se filtra para evitar que regrese a la casilla de la que acaba de salir
                    if (nx, ny) != (self.last_grid_x, self.last_grid_y):
                        movimientos.append((nx, ny))
        
        # Si se encuentra en un callejo sin salida, se le permite regresar
        if not movimientos:
            for dx, dy in direcciones:
                nx = self.grid_x + dx
                ny = self.grid_y + dy
                if 0 <= nx < COLUMNAS and 0 <= ny < FILAS:
                    if mapa_actual[ny][nx] != 1:
                        movimientos.append((nx, ny))
        return movimientos

    def ejecutar_ia_normal(self, px, py):
        movimientos = self.obtener_movimientos_validos()
        if not movimientos:
            return
        tx, ty = px, py

        
        if self.tipo == "Perseguidor":
            tx, ty = px, py
        elif self.tipo == "Predicador":
            tx, ty = px + 2, py + 2 
        elif self.tipo == "Flanqueador":
            tx, ty = px - 3, py
        elif self.tipo == "Errático":
            dist = math.sqrt((self.grid_x - px)**2 + (self.grid_y - py)**2)
            if dist < 4:
                self.last_grid_x, self.last_grid_y = self.grid_x, self.grid_y
                self.grid_x, self.grid_y = random.choice(movimientos)
                self.actualizar_posicion_real()
                return

        mejor_movimiento = movimientos[0]
        dist_minima = float('inf')
        for nx, ny in movimientos:
            d = math.sqrt((nx - tx)**2 + (ny - ty)**2)
            if d < dist_minima:
                dist_minima = d
                mejor_movimiento = (nx, ny)

        self.last_grid_x, self.last_grid_y = self.grid_x, self.grid_y
        self.grid_x, self.grid_y = mejor_movimiento
        self.actualizar_posicion_real()

    def ejecutar_movimiento_huida(self, px, py):
        movimientos = self.obtener_movimientos_validos()
        if not movimientos:
            return

        mejor_movimiento = movimientos[0]
        dist_maxima = -1
        for nx, ny in movimientos:
            d = math.sqrt((nx - px)**2 + (ny - py)**2)
            if d > dist_maxima:
                dist_maxima = d
                mejor_movimiento = (nx, ny)

        self.last_grid_x, self.last_grid_y = self.grid_x, self.grid_y
        self.grid_x, self.grid_y = mejor_movimiento
        self.actualizar_posicion_real()

# 4. INSTANCIACIÓN DE OBJETOS
window = display.set_mode((ANCHO, ALTO))
display.set_caption(TITULO)
reloj = time.Clock()

# Buscar coordenadas iniciales de reaparición (celda tipo 4)
def obtener_posicion_reaparicion():
    for f in range(FILAS):
        for c in range(COLUMNAS):
            if MATRIZ_LABERINTO[f][c] == 4:
                return c, f
    return 1, 1

px_ini, py_ini = obtener_posicion_reaparicion()
player = Player(img_pacman, px_ini, py_ini)

# se crean los ghostys con sus personalidades 
fantasmas = [
    Enemy(img_rojo, 9, 9, "Perseguidor", img_rojo),
    Enemy(img_rosa, 10, 9, "Predicador", img_rosa),
    Enemy(img_cian, 9, 10, "Flanqueador", img_cian),
    Enemy(img_naranja, 10, 10, "Errático", img_naranja)
]

# Definición de botones de la interfaz
rect_boton_jugar = Rect(ANCHO // 2 - 100, 220, 200, 50)
rect_boton_salir = Rect(ANCHO // 2 - 100, 300, 200, 50)
rect_boton_sonido = Rect(ANCHO - 60, ALTO - 60, 40, 40)

# 5. CICLO PRINCIPAL (GAME LOOP)
run = True

while run:
    tiempo_delta = reloj.tick(FPS)
    window.fill(COLOR_FONDO)
    
    # A. Gestión de Eventos (intento 1)
    for e in event.get():
        if e.type == QUIT:
            run = False
            
        if e.type == MOUSEBUTTONDOWN:
            pos_raton = e.pos
            if estado_juego == "MENU":
                if rect_boton_jugar.collidepoint(pos_raton):
                    estado_juego = "JUEGO"
                    vidas = 3
                    modo_huida = False
                elif rect_boton_salir.collidepoint(pos_raton):
                    run = False
            
            if rect_boton_sonido.collidepoint(pos_raton):
                sonido_activo = not sonido_activo

        if e.type == KEYDOWN and estado_juego == "JUEGO":
            if e.key == K_a or e.key == K_LEFT:
                player.mover(-1, 0)
            elif e.key == K_d or e.key == K_RIGHT:
                player.mover(1, 0)
            elif e.key == K_w or e.key == K_UP:
                player.mover(0, -1)
            elif e.key == K_s or e.key == K_DOWN:
                player.mover(0, 1)

    # B. Lógica y Dibujado de Estados del Juego 
    if estado_juego == "MENU":
        # Títulocon sus colores llamativos
        texto_bienvenido = fuente_titulo.render("BIENVENIDO", True, CIAN_NEON)
        window.blit(texto_bienvenido, (ANCHO // 2 - texto_bienvenido.get_width() // 2, 100))
        
        # Botones del menú
        draw.rect(window, CIAN_NEON, rect_boton_jugar, 2)
        texto_jugar = fuente_interfaz.render("JUGAR", True, BLANCO)
        window.blit(texto_jugar, (rect_boton_jugar.x + (rect_boton_jugar.width - texto_jugar.get_width()) // 2, rect_boton_jugar.y + 10))
        
        draw.rect(window, CIAN_NEON, rect_boton_salir, 2)
        texto_salir = fuente_interfaz.render("SALIR", True, BLANCO)
        window.blit(texto_salir, (rect_boton_salir.x + (rect_boton_salir.width - texto_salir.get_width()) // 2, rect_boton_salir.y + 10))

    elif estado_juego == "JUEGO":
        # temporizador del estado de huida
        if modo_huida:
            tiempo_huida_restante -= tiempo_delta
            if tiempo_huida_restante <= 0:
                modo_huida = False

        # Dibujar la Franja Superior de Vidas e Interfaz
        texto_vidas = fuente_interfaz.render("VIDAS: ", True, BLANCO)
        window.blit(texto_vidas, (MARGEN_X, 30))
        for i in range(vidas):
            window.blit(img_corazon, (MARGEN_X + 90 + (i * 30), 35))
            
        if modo_huida:
            texto_timer = fuente_interfaz.render(f"Poder: {int(tiempo_huida_restante/1000)}s", True, AZUL_PALIDO)
            window.blit(texto_timer, (ANCHO - MARGEN_X - 150, 30))

        # Procesamiento y renderizado del Laberinto Matricial
        for f in range(FILAS):
            for c in range(COLUMNAS):
                celda = MATRIZ_LABERINTO[f][c]
                pos_celda_x = MARGEN_X + c * TAM_CELDA
                pos_celda_y = MARGEN_Y + f * TAM_CELDA
                
                if celda == 1:
                    # Líneas de cian para conformar los muros contenedores
                    draw.rect(window, CIAN_NEON, (pos_celda_x, pos_celda_y, TAM_CELDA, TAM_CELDA), 1)
                elif celda == 2:
                    # Puntos pequeños consumibles
                    draw.circle(window, AMARILLO, (pos_celda_x + TAM_CELDA // 2, pos_celda_y + TAM_CELDA // 2), 3)
                elif celda == 3:
                    # Puntos especiales grandes
                    draw.circle(window, BLANCO, (pos_celda_x + TAM_CELDA // 2, pos_celda_y + TAM_CELDA // 2), 7)

        # Interac de recolección del jugador sobre las celdas 
        celda_actual_tipo = MATRIZ_LABERINTO[player.grid_y][player.grid_x]
        if celda_actual_tipo == 2:
            MATRIZ_LABERINTO[player.grid_y][player.grid_x] = 0
        elif celda_actual_tipo == 3:
            MATRIZ_LABERINTO[player.grid_y][player.grid_x] = 0
            modo_huida = True
            tiempo_huida_restante = 30000 # de 30 segundos en milisegundos

        # Actualizar, procesar y dibujar Fantasmas
        for fantasma in fantasmas:
            fantasma.update(player.grid_x, player.grid_y)
            fantasma.reset(window)
            
            # Verificaaa colisiones en la misma celda de la matriz 
            if fantasma.grid_x == player.grid_x and fantasma.grid_y == player.grid_y:
                if modo_huida:
                    # En modo de huida el fantasma es devuelto a la zona central de reaparición
                    fantasma.grid_x, fantasma.grid_y = 9, 9
                    fantasma.actualizar_posicion_real()
                else:
                    # Decremento de la salud y recolocación del jugador
                    vidas -= 1
                    player.grid_x, player.grid_y = px_ini, py_ini
                    player.actualizar_posicion_real()
                    if vidas <= 0:
                        estado_juego = "GAME_OVER"

        # Dibujar al jugador
        player.reset(window)

    elif estado_juego == "GAME_OVER":
        # Gestión y visualización de la pantalla de derrota
        texto_derrota = fuente_titulo.render("GAME OVER", True, ROJO)
        window.blit(texto_derrota, (ANCHO // 2 - texto_derrota.get_width() // 2, ALTO // 2 - 80))
        
        texto_reintento = fuente_interfaz.render("Haz clic en cualquier parte para volver al Menú", True, BLANCO)
        window.blit(texto_reintento, (ANCHO // 2 - texto_reintento.get_width() // 2, ALTO // 2 + 20))
        
        # Captura de clic en la pantalla de derrota para regresar
        if mouse.get_pressed()[0]:
            estado_juego = "MENU"
            time.wait(200)

    # C. Componente de Audio 
    window.blit(img_altavoz, (rect_boton_sonid.x, rect_boton_sonido.y))
    if not sonido_activo:
        # Superposición visual de cancelación del canal auditivo
        draw.line(window, ROJO, (rect_boton_sonido.x, rect_boton_sonido.y), 
                  (rect_boton_sonido.x + rect_boton_sonido.width, rect_boton_sonido.y + rect_boton_sonido.height), 4)

   display.update()

#pendiente con:
#la musica de ultimo
#los fantasmas como que se vuelven gafos

quit()
