from pygame import *

# 1. INICIALIZACIÓN
init()
font.init()
mixer.init()

# 2. CONFIGURACIÓN Y CONSTANTES
# Es recomendable usar nombres descriptivos para facilitar el mantenimiento
ANCHO, ALTO = 800, 600
FPS = 60
TITULO = 'Plantilla Base Pygame'
COLOR_FONDO = (30, 30, 30) # Un gris oscuro para no cansar la vista

# 3. DEFINICIÓN DE CLASES
class GameSprite(sprite.Sprite):
    """Clase base para todos los objetos visuales del juego."""
    def __init__(self, sprite_img, x, y, w, h, speed):
        super().__init__()
        self.image = transform.scale(image.load(sprite_img), (w, h))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed

    def reset(self, surface):
        """Dibuja el sprite en su posición actual."""
        surface.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    """Clase para el personaje controlado por el usuario."""
    def update(self):
        keys = key.get_pressed()
        # Movimiento Horizontal
        if keys[K_a] and self.rect.x > 0:
            self.rect.x -= self.speed
        if keys[K_d] and self.rect.x < ANCHO - self.rect.width:
            self.rect.x += self.speed
        
        # Movimiento Vertical (Recordar: Y crece hacia abajo)
        if keys[K_w] and self.rect.y > 0:
            self.rect.y -= self.speed
        if keys[K_s] and self.rect.y < ALTO - self.rect.height:
            self.rect.y += self.speed

class Enemy(GameSprite):
    """Clase para obstáculos o enemigos con movimiento automático."""
    def update(self):
        # Implementar IA simple o patrullaje aquí
        self.rect.y += self.speed
        if self.rect.y > ALTO:
            self.rect.y = -50 # Reaparece arriba

# 4. INSTANCIACIÓN DE OBJETOS
window = display.set_mode((ANCHO, ALTO))
display.set_caption(TITULO)
reloj = time.Clock()

# Aquí se crearían los grupos de sprites y objetos individuales
# player = Player('hero.png', 50, ALTO - 100, 80, 100, 5)
# enemies = sprite.Group()

# 5. CICLO PRINCIPAL (GAME LOOP)
run = True
finish = False # Variable para controlar estados (Ej: Pantalla de Game Over)

while run:
    # --- A. Gestión de Eventos ---
    for e in event.get():
        if e.type == QUIT:
            run = False
        
        # Reinicio del juego con una tecla
        if e.type == KEYDOWN:
            if e.key == K_r:
                finish = False
                # Aquí se debería resetear la posición de los objetos

    # --- B. Lógica del Juego (Solo si no ha terminado) ---
    if not finish:
        window.fill(COLOR_FONDO)

        # Actualizar posiciones
        # player.update()
        # enemies.update()

        # Dibujar elementos
        # player.reset(window)
        # enemies.draw(window)

        # Ejemplo de condición de fin
        # if sprite.spritecollide(player, enemies, False):
        #     finish = True

    # --- C. Actualización de Pantalla ---
    display.update()
    reloj.tick(FPS)

# Al salir del ciclo, cerrar recursos
quit()
