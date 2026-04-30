import pygame
import sys
import random
import math

PALABRAS = ["SILLON", "PRISMA", "COMIDA", "MORRON", "ESTADO"]

PALABRAS = [p for p in PALABRAS if len(p) == 6]

if not PALABRAS:
    PALABRAS = ["SILLON", "PRISMA", "COMIDA", "MORRON", "ESTADO"]

# --- COLORES FESTIVOS ---
COLOR_FONDO       = (20, 10, 40)
COLOR_CELDA       = (40, 25, 70)
COLOR_BORDE       = (100, 80, 150)
COLOR_TEXTO       = (255, 245, 220)
COLOR_CORRECTO    = (80, 200, 120)
COLOR_PRESENTE    = (255, 190, 50)
COLOR_AUSENTE     = (80, 70, 100)
COLOR_TECLADO_BG  = (55, 40, 90)
COLOR_TITULO      = (255, 100, 180)
COLOR_HINT        = (200, 160, 255)

LETRAS_VALIDAS = "QWERTYUIOPASDFGHJKLZXCVBNM"

pygame.init()

ANCHO, ALTO = 550, 700
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Carldle")

# Cargar imagen al tamaño completo de la ventana
imagen_ganador = pygame.image.load("invitation.png")
imagen_ganador = pygame.transform.scale(imagen_ganador, (ANCHO, ALTO))

# Fuentes
try:
    fuente_titulo = pygame.font.SysFont("helvetica", 38, bold=True)
    fuente_celda  = pygame.font.SysFont("helvetica", 36, bold=True)
    fuente_tecla  = pygame.font.SysFont("helvetica", 18, bold=True)
    fuente_msg    = pygame.font.SysFont("helvetica", 22, bold=True)
    fuente_sub    = pygame.font.SysFont("helvetica", 16)
except:
    fuente_titulo = pygame.font.SysFont(None, 38)
    fuente_celda  = pygame.font.SysFont(None, 36)
    fuente_tecla  = pygame.font.SysFont(None, 18)
    fuente_msg    = pygame.font.SysFont(None, 22)
    fuente_sub    = pygame.font.SysFont(None, 16)

# --- CONFETTI ---
class Confetti:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.randint(0, ANCHO)
        self.y = random.randint(-50, -5)
        self.color = random.choice([
            (255, 100, 180), (100, 220, 255), (255, 220, 50),
            (120, 255, 150), (200, 130, 255), (255, 150, 80)
        ])
        self.size = random.randint(6, 14)
        self.speed = random.uniform(2, 5)
        self.wobble = random.uniform(-1.5, 1.5)
        self.angle = random.uniform(0, 360)
        self.rot_speed = random.uniform(-4, 4)

    def update(self):
        self.y += self.speed
        self.x += self.wobble
        self.angle += self.rot_speed
        if self.y > ALTO + 20:
            self.reset()

    def draw(self, surf):
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(s, self.color, (0, 0, self.size, self.size))
        rotated = pygame.transform.rotate(s, self.angle)
        surf.blit(rotated, (int(self.x), int(self.y)))

confettis = [Confetti() for _ in range(80)]
mostrar_confetti = False

def nuevo_juego():
    return {
        "palabra": random.choice(PALABRAS),
        "intentos": [],
        "intento_actual": "",
        "max_intentos": 6,
        "ganado": False,
        "perdido": False,
        "mensaje": "",
        "mensaje_timer": 0,
        "colores_teclado": {},
        "shake": False,
        "shake_timer": 0,
        "ganado_timer": 0,
    }

estado = nuevo_juego()

CELDA_TAM = 58
CELDA_GAP = 6
FILAS = 6
COLS = 6
GRILLA_W = COLS * CELDA_TAM + (COLS - 1) * CELDA_GAP
GRILLA_X = (ANCHO - GRILLA_W) // 2
GRILLA_Y = 120

TECLADO_Y = GRILLA_Y + FILAS * (CELDA_TAM + CELDA_GAP) + 20
FILA1 = list("QWERTYUIOP")
FILA2 = list("ASDFGHJKL")
FILA3 = list("ZXCVBNM")
TECLA_W, TECLA_H = 40, 36
TECLA_GAP = 4

def pos_grilla(fila, col):
    x = GRILLA_X + col * (CELDA_TAM + CELDA_GAP)
    y = GRILLA_Y + fila * (CELDA_TAM + CELDA_GAP)
    return x, y

def evaluar(intento, palabra):
    resultado = ['ausente'] * 6
    conteo = {}
    for c in palabra:
        conteo[c] = conteo.get(c, 0) + 1
    for i in range(6):
        if intento[i] == palabra[i]:
            resultado[i] = 'correcto'
            conteo[intento[i]] -= 1
    for i in range(6):
        if resultado[i] != 'correcto' and intento[i] in conteo and conteo[intento[i]] > 0:
            resultado[i] = 'presente'
            conteo[intento[i]] -= 1
    return resultado

def color_estado(estado_letra):
    if estado_letra == 'correcto':
        return COLOR_CORRECTO
    elif estado_letra == 'presente':
        return COLOR_PRESENTE
    else:
        return COLOR_AUSENTE

def dibujar_celda(surf, x, y, letra, estado_letra=None, activa=False, shake_offset=0):
    rect = pygame.Rect(x + shake_offset, y, CELDA_TAM, CELDA_TAM)
    if estado_letra:
        color_fondo = color_estado(estado_letra)
        color_borde = color_fondo
    elif activa:
        color_fondo = COLOR_CELDA
        color_borde = COLOR_TITULO
    else:
        color_fondo = COLOR_CELDA
        color_borde = COLOR_BORDE
    pygame.draw.rect(surf, color_fondo, rect, border_radius=10)
    pygame.draw.rect(surf, color_borde, rect, 3, border_radius=10)
    if letra:
        txt = fuente_celda.render(letra, True, COLOR_TEXTO)
        surf.blit(txt, txt.get_rect(center=rect.center))

def dibujar_teclado(surf, colores):
    filas = [FILA1, FILA2, FILA3]
    for f_idx, fila in enumerate(filas):
        total_w = len(fila) * TECLA_W + (len(fila) - 1) * TECLA_GAP
        x_start = (ANCHO - total_w) // 2
        y = TECLADO_Y + f_idx * (TECLA_H + TECLA_GAP)
        for i, letra in enumerate(fila):
            x = x_start + i * (TECLA_W + TECLA_GAP)
            rect = pygame.Rect(x, y, TECLA_W, TECLA_H)
            color = colores.get(letra, COLOR_TECLADO_BG)
            pygame.draw.rect(surf, color, rect, border_radius=8)
            pygame.draw.rect(surf, COLOR_BORDE, rect, 2, border_radius=8)
            txt = fuente_tecla.render(letra, True, COLOR_TEXTO)
            surf.blit(txt, txt.get_rect(center=rect.center))

def dibujar_fondo_festivo(surf, t):
    surf.fill(COLOR_FONDO)
    for i in range(6):
        angulo = t * 0.3 + i * math.pi / 3
        cx = ANCHO // 2 + int(math.cos(angulo) * 280)
        cy = ALTO // 2 + int(math.sin(angulo) * 220)
        color = [
            (255, 80, 150, 18), (80, 200, 255, 18),
            (255, 200, 50, 18), (150, 80, 255, 18),
            (80, 255, 150, 18), (255, 130, 80, 18),
        ][i]
        s = pygame.Surface((200, 200), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (100, 100), 100)
        surf.blit(s, (cx - 100, cy - 100))

reloj = pygame.time.Clock()
t = 0

corriendo = True
while corriendo:
    dt = reloj.tick(60)
    t += 0.02

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            corriendo = False

        if event.type == pygame.KEYDOWN:
            if not estado["ganado"] and not estado["perdido"]:
                if event.key == pygame.K_BACKSPACE:
                    estado["intento_actual"] = estado["intento_actual"][:-1]

                elif event.key == pygame.K_RETURN:
                    intento = estado["intento_actual"]
                    if len(intento) < 6:
                        estado["mensaje"] = "¡Faltan letras!"
                        estado["mensaje_timer"] = 120
                        estado["shake"] = True
                        estado["shake_timer"] = 20
                    else:
                        resultado = evaluar(intento, estado["palabra"])
                        estado["intentos"].append((intento, resultado))
                        estado["intento_actual"] = ""

                        prioridad = {'correcto': 3, 'presente': 2, 'ausente': 1}
                        for i, letra in enumerate(intento):
                            est = resultado[i]
                            actual = estado["colores_teclado"].get(letra)
                            if actual is None or prioridad[est] > prioridad.get(
                                {COLOR_CORRECTO: 'correcto', COLOR_PRESENTE: 'presente',
                                 COLOR_AUSENTE: 'ausente'}.get(actual, 'ausente'), 0):
                                estado["colores_teclado"][letra] = color_estado(est)

                        if intento == estado["palabra"]:
                            estado["ganado_timer"] = 30
                            mostrar_confetti = True
                        elif len(estado["intentos"]) >= estado["max_intentos"]:
                            estado["perdido"] = True
                            estado["mensaje"] = f"Era {estado['palabra']}, COMO NO LA SACASTE"
                            estado["mensaje_timer"] = 9999

                elif event.unicode.upper() in LETRAS_VALIDAS and len(estado["intento_actual"]) < 6:
                    estado["intento_actual"] += event.unicode.upper()

            if event.key == pygame.K_r and (estado["ganado"] or estado["perdido"]):
                estado = nuevo_juego()
                mostrar_confetti = False

    if estado["ganado_timer"] > 0:
        estado["ganado_timer"] -= 1
    if estado["ganado_timer"] == 1:
        estado["ganado"] = True

    if estado["mensaje_timer"] > 0:
        estado["mensaje_timer"] -= 1

    # --- DIBUJAR ---
    if estado["ganado"]:
        # Pantalla completa con la imagen de invitación y confetti encima
        pantalla.blit(imagen_ganador, (0, 0))
        for c in confettis:
            c.update()
            c.draw(pantalla)
    else:
        dibujar_fondo_festivo(pantalla, t)

        titulo = fuente_titulo.render("Carldle", True, COLOR_TITULO)
        pantalla.blit(titulo, titulo.get_rect(centerx=ANCHO // 2, y=18))

        sub = fuente_sub.render("el que no la saca no come torta", True, COLOR_HINT)
        pantalla.blit(sub, sub.get_rect(centerx=ANCHO // 2, y=68))

        shake_offset = 0
        if estado["shake"]:
            shake_offset = random.randint(-5, 5)

        for fila in range(FILAS):
            for col in range(COLS):
                x, y = pos_grilla(fila, col)
                if fila < len(estado["intentos"]):
                    intento_str, resultado = estado["intentos"][fila]
                    letra = intento_str[col] if col < len(intento_str) else ""
                    est = resultado[col]
                    dibujar_celda(pantalla, x, y, letra, est)
                elif fila == len(estado["intentos"]) and not estado["perdido"]:
                    letra = estado["intento_actual"][col] if col < len(estado["intento_actual"]) else ""
                    dibujar_celda(pantalla, x, y, letra, activa=True, shake_offset=shake_offset)
                else:
                    dibujar_celda(pantalla, x, y, "")

        # Teclado
        dibujar_teclado(pantalla, estado["colores_teclado"])

        # Mensaje de error o derrota
        if estado["mensaje"] and estado["mensaje_timer"] > 0:
            color_msg = COLOR_TITULO if estado["ganado"] else COLOR_PRESENTE
            msg = fuente_msg.render(estado["mensaje"], True, color_msg)
            msg_rect = msg.get_rect(centerx=ANCHO // 2, y=TECLADO_Y + 3 * (TECLA_H + TECLA_GAP) + 12)
            pygame.draw.rect(pantalla, (30, 15, 55), msg_rect.inflate(20, 12), border_radius=10)
            pantalla.blit(msg, msg_rect)

        if estado["perdido"]:
            hint = fuente_sub.render("Presioná R para tratar de vuelta", True, COLOR_HINT)
            pantalla.blit(hint, hint.get_rect(centerx=ANCHO // 2, y=TECLADO_Y + 3 * (TECLA_H + TECLA_GAP) + 45))

    pygame.display.flip()

pygame.quit()
sys.exit()