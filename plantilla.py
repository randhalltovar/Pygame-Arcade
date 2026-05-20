from pygame import *
import random
import math

# INICIALIZACIÓN
init()
font.init()
mixer.init()

# CONFIGURACIÓN Y CONSTANTES
ANCHO, ALTO = 800, 600
FPS = 60
TITULO = 'Pac-Man'

COLOR_FONDO = (13, 13, 13)
CIAN_NEON = (0, 255, 255)
BLANCO = (255, 255, 255)
AMARILLO = (255, 255, 0)
AZUL_PALIDO = (173, 216, 230)
ROJO = (255, 0, 0)

FILAS = 20
COLUMNAS = 20
TAM_CELDA = 25 

MARGEN_X = (ANCHO - (COLUMNAS * TAM_CELDA)) // 2
MARGEN_Y = 90

vidas = 3
puntaje = 0
sonido_activo = True
estado_juego = "MENU" 

modo_huida = False
tiempo_huida_restante = 0

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
    [1,2,2,2,2,0,0,1,4,4,4,4,1,0,0,2,2,2,2,1],
    [1,1,1,1,2,1,0,1,1,1,1,1,1,0,1,2,1,1,1,1],
    [0,0,0,1,2,1,0,0,0,0,0,0,0,0,1,2,1,0,0,0],
    [1,1,1,1,2,1,2,1,1,1,1,1,1,2,1,2,1,1,1,1],
    [1,3,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,3,1],
    [1,2,1,1,2,1,1,1,2,1,1,2,1,1,1,2,1,1,2,1],
    [1,2,2,1,2,2,2,2,2,0,0,2,2,2,2,2,1,2,2,1],
    [1,1,2,1,2,1,2,1,1,1,1,1,1,2,1,2,1,2,1,1],
    [1,2,2,2,2,1,2,2,2,1,1,2,2,2,1,2,2,2,2,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

def generar_mapa():
    return [fila[:] for fila in MATRIZ_LABERINTO]

mapa_actual = generar_mapa()

fuente_titulo = font.SysFont('Arial', 55, bold=True)
fuente_interfaz = font.SysFont('Arial', 25, bold=True)

try:
    img_bocina = transform.scale(image.load("bocina.png"), (40, 40))
except:
    img_bocina = Surface((40, 40), SRCALPHA)
    img_bocina.fill((0, 200, 0))
    draw.polygon(img_bocina, BLANCO, [(10, 15), (20, 15), (30, 5), (30, 35), (20, 25), (10, 25)])

try:
    mixer.music.load("Fondo.mp3")
    mixer.music.play(-1)
except:
    print("Advertencia: No se encontró el archivo Fondo.mp3 en el directorio.")

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

class GameSprite(sprite.Sprite):
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
    def __init__(self, x_matriz, y_matriz):
        super().__init__(None, x_matriz, y_matriz)

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

        draw.circle(surface, AMARILLO, (centro_x, centro_y), radio)
        draw.circle(surface, (0, 0, 0), (centro_x - 4, centro_y - 3), 2)
        draw.circle(surface, (0, 0, 0), (centro_x + 4, centro_y - 3), 2)
        rect_sonrisa = Rect(centro_x - 4, centro_y - 2, 10, 8)
        draw.arc(surface, (0, 0, 0), rect_sonrisa, math.pi, 2 * math.pi, 2)

class Enemy(GameSprite):
    def __init__(self, superficie_img, x_matriz, y_matriz, tipo, img_normal, max_cooldown):
        super().__init__(superficie_img, x_matriz, y_matriz)
        self.tipo = tipo
        self.img_normal = img_normal
        self.cooldown_movimiento = 0
        self.max_cooldown = max_cooldown
        self.last_grid_x = x_matriz
        self.last_grid_y = y_matriz
        
    def update(self, player_x, player_y):
        self.cooldown_movimiento += 1
        if self.cooldown_movimiento < self.max_cooldown: 
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
                    if (nx, ny) != (self.last_grid_x, self.last_grid_y):
                        movimientos.append((nx, ny))
        
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

window = display.set_mode((ANCHO, ALTO))
display.set_caption(TITULO)
reloj = time.Clock()

player = Player(1, 18)

fantasmas = [
    Enemy(img_rojo, 9, 9, "Perseguidor", img_rojo, 12),
    Enemy(img_rosa, 10, 9, "Predicador", img_rosa, 15),
    Enemy(img_cian, 9, 10, "Flanqueador", img_cian, 18),
    Enemy(img_naranja, 10, 10, "Errático", img_naranja, 21)
]

rect_menu_jugar = Rect(ANCHO // 2 - 100, 300, 200, 50)
rect_menu_salir = Rect(ANCHO // 2 - 100, 380, 200, 50)
rect_pantalla_accion = Rect(ANCHO // 2 - 100, 330, 200, 50)
rect_boton_sonido = Rect(ANCHO - 60, ALTO - 60, 40, 40)

run = True

while run:
    tiempo_delta = reloj.tick(FPS)
    window.fill(COLOR_FONDO)
    
    for e in event.get():
        if e.type == QUIT:
            run = False
            
        if e.type == MOUSEBUTTONDOWN:
            pos_raton = e.pos
            if estado_juego == "MENU":
                if rect_menu_jugar.collidepoint(pos_raton):
                    mapa_actual = generar_mapa()
                    vidas = 3
                    puntaje = 0
                    modo_huida = False
                    player.grid_x, player.grid_y = 1, 18
                    player.actualizar_posicion_real()
                    for f_item in fantasmas:
                        f_item.grid_x, f_item.grid_y = 9, 9
                        f_item.last_grid_x, f_item.last_grid_y = 9, 9
                        f_item.actualizar_posicion_real()
                    estado_juego = "JUEGO"
                elif rect_menu_salir.collidepoint(pos_raton):
                    run = False
            
            elif estado_juego in ["GAME_OVER", "VICTORIA"]:
                if rect_pantalla_accion.collidepoint(pos_raton):
                    estado_juego = "MENU"
            
            if rect_boton_sonido.collidepoint(pos_raton):
                sonido_activo = not sonido_activo
                if sonido_activo:
                    mixer.music.unpause()
                else:
                    mixer.music.pause()

        if e.type == KEYDOWN and estado_juego == "JUEGO":
            if e.key == K_LEFT:
                player.mover(-1, 0)
            elif e.key == K_RIGHT:
                player.mover(1, 0)
            elif e.key == K_UP:
                player.mover(0, -1)
            elif e.key == K_DOWN:
                player.mover(0, 1)

    if estado_juego == "MENU":
        texto_sombra = fuente_titulo.render("PAC-MAN ARCADE", True, (100, 100, 0))
        window.blit(texto_sombra, (ANCHO // 2 - texto_sombra.get_width() // 2 + 4, 84))
        texto_titulo_menu = fuente_titulo.render("PAC-MAN ARCADE", True, AMARILLO)
        window.blit(texto_titulo_menu, (ANCHO // 2 - texto_titulo_menu.get_width() // 2, 80))

        draw.circle(window, AMARILLO, (ANCHO // 2 - 100, 220), 10)
        window.blit(img_rojo, (ANCHO // 2 - 60, 210))
        window.blit(img_rosa, (ANCHO // 2 - 20, 210))
        window.blit(img_cian, (ANCHO // 2 + 20, 210))
        window.blit(img_naranja, (ANCHO // 2 + 60, 210))
        
        draw.rect(window, CIAN_NEON, rect_menu_jugar, 2)
        texto_jugar = fuente_interfaz.render("JUGAR", True, BLANCO)
        window.blit(texto_jugar, (rect_menu_jugar.x + (rect_menu_jugar.width - texto_jugar.get_width()) // 2, rect_menu_jugar.y + 10))
        
        draw.rect(window, CIAN_NEON, rect_menu_salir, 2)
        texto_salir = fuente_interfaz.render("SALIR", True, BLANCO)
        window.blit(texto_salir, (rect_menu_salir.x + (rect_menu_salir.width - texto_salir.get_width()) // 2, rect_menu_salir.y + 10))

    elif estado_juego == "JUEGO":
        if modo_huida:
            tiempo_huida_restante -= tiempo_delta
            if tiempo_huida_restante <= 0:
                modo_huida = False

        texto_vidas = fuente_interfaz.render("VIDAS: ", True, BLANCO)
        window.blit(texto_vidas, (50, 35))
        for i in range(vidas):
            window.blit(img_corazon, (135 + (i * 25), 40))
            
        texto_puntaje = fuente_interfaz.render(f"PUNTAJE: {puntaje}", True, AMARILLO)
        window.blit(texto_puntaje, (320, 35))
            
        if modo_huida:
            texto_timer = fuente_interfaz.render(f"Poder: {int(tiempo_huida_restante/1000)}s", True, AZUL_PALIDO)
            window.blit(texto_timer, (610, 35))

        for f in range(FILAS):
            for c in range(COLUMNAS):
                celda = mapa_actual[f][c]
                pos_celda_x = MARGEN_X + c * TAM_CELDA
                pos_celda_y = MARGEN_Y + f * TAM_CELDA
                
                if celda == 1:
                    draw.rect(window, CIAN_NEON, (pos_celda_x, pos_celda_y, TAM_CELDA, TAM_CELDA), 1)
                elif celda == 2:
                    draw.circle(window, AMARILLO, (pos_celda_x + TAM_CELDA // 2, pos_celda_y + TAM_CELDA // 2), 3)
                elif celda == 3:
                    draw.circle(window, BLANCO, (pos_celda_x + TAM_CELDA // 2, pos_celda_y + TAM_CELDA // 2), 7)

        celda_actual_tipo = mapa_actual[player.grid_y][player.grid_x]
        if celda_actual_tipo == 2:
            mapa_actual[player.grid_y][player.grid_x] = 0
            puntaje += 10
        elif celda_actual_tipo == 3:
            mapa_actual[player.grid_y][player.grid_x] = 0
            puntaje += 50
            modo_huida = True
            tiempo_huida_restante = 30000 

        monedas_restantes = sum(fila.count(2) + fila.count(3) for fila in mapa_actual)
        if monedas_restantes == 0:
            estado_juego = "VICTORIA"

        for fantasma in fantasmas:
            fantasma.update(player.grid_x, player.grid_y)
            fantasma.reset(window)
            
            if (fantasma.grid_x == player.grid_x and fantasma.grid_y == player.grid_y) or fantasma.rect.colliderect(player.rect):
                if modo_huida:
                    fantasma.grid_x, fantasma.grid_y = 9, 9
                    fantasma.last_grid_x, fantasma.last_grid_y = 9, 9
                    fantasma.actualizar_posicion_real()
                    puntaje += 200
                else:
                    vidas -= 1
                    player.grid_x, player.grid_y = 1, 18 
                    player.actualizar_posicion_real()
                    for f_item in fantasmas:
                        f_item.grid_x, f_item.grid_y = 9, 9
                        f_item.last_grid_x, f_item.last_grid_y = 9, 9
                        f_item.actualizar_posicion_real()
                        
                    if vidas <= 0:
                        estado_juego = "GAME_OVER"
                    break

        player.reset(window)

    elif estado_juego == "GAME_OVER":
        texto_derrota = fuente_titulo.render("GAME OVER", True, ROJO)
        window.blit(texto_derrota, (ANCHO // 2 - texto_derrota.get_width() // 2, 200))
        
        draw.rect(window, ROJO, rect_pantalla_accion, 2)
        texto_reintentar = fuente_interfaz.render("REINTENTAR", True, BLANCO)
        window.blit(texto_reintentar, (rect_pantalla_accion.x + (rect_pantalla_accion.width - texto_reintentar.get_width()) // 2, rect_pantalla_accion.y + 10))

    elif estado_juego == "VICTORIA":
        texto_ganas = fuente_titulo.render("¡HAS GANADO!", True, AMARILLO)
        window.blit(texto_ganas, (ANCHO // 2 - texto_ganas.get_width() // 2, 200))
        
        draw.rect(window, AMARILLO, rect_pantalla_accion, 2)
        texto_menu = fuente_interfaz.render("OTRA VEZ", True, BLANCO)
        window.blit(texto_menu, (rect_pantalla_accion.x + (rect_pantalla_accion.width - texto_menu.get_width()) // 2, rect_pantalla_accion.y + 10))

    window.blit(img_bocina, (rect_boton_sonido.x, rect_boton_sonido.y))
    if not sonido_activo:
        draw.line(window, ROJO, (rect_boton_sonido.x, rect_boton_sonido.y), 
                  (rect_boton_sonido.x + rect_boton_sonido.width, rect_boton_sonido.y + rect_boton_sonido.height), 4)

    display.update()

quit()
