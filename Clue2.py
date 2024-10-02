import pygame
import random

# Inicializamos pygame y la música
pygame.init()
pygame.mixer.init()

# Cargar música de fondo
pygame.mixer.music.load('musica_fondo.mp3')
pygame.mixer.music.play(-1)  # -1 para que la música se reproduzca en bucle

# Tamaño de la ventana
ANCHO = 800
ALTO = 800
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Simulación de Clue")

# Cargar imagen del tablero
tablero_img = pygame.image.load('fondo_tablero.png')
tablero_img = pygame.transform.scale(tablero_img, (ANCHO, ALTO))

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (255, 0, 0)
AZUL = (0, 0, 255)
VERDE = (0, 255, 0)

# Fuentes
fuente = pygame.font.SysFont(None, 30)

# Cartas
sospechosos = ['Miss Scarlet', 'Professor Plum', 'Mrs Peacock', 'Reverend Green', 'Colonel Mustard', 'Mrs White']
armas = ['Cuchillo', 'Revolver', 'Cuerda', 'Veneno', 'Candelabro', 'Llave Inglesa']
habitaciones = ['Cocina', 'Comedor', 'Conservatorio', 'Sala de Billar', 'Biblioteca', 'Estudio', 'Vestíbulo', 'Salón', 'Sala de Baile']

# Solución
asesino_solucion = random.choice(sospechosos)
arma_solucion = random.choice(armas)
habitacion_solucion = random.choice(habitaciones)

cartas_totales = sospechosos + armas + habitaciones
cartas_disponibles = [c for c in cartas_totales if c != asesino_solucion and c != arma_solucion and c != habitacion_solucion]

# Repartimos las cartas entre los jugadores
random.shuffle(cartas_disponibles)
jugadores = 6  # Incrementamos el número de jugadores

cartas_por_jugador = len(cartas_disponibles) // jugadores
jugador_cartas = [cartas_disponibles[i * cartas_por_jugador:(i + 1) * cartas_por_jugador] for i in range(jugadores)]

# Base de Conocimiento (qué cartas tienen los jugadores)
base_conocimiento = {
    f'Jugador{i + 1}': jugador_cartas[i] for i in range(jugadores)
}
base_conocimiento['Solucion'] = None

# Variables del estado del juego
jugador_actual = 1
fase = "turno"  # "turno", "sugerencia", "resultado"
sugerencia = {'sospechoso': None, 'arma': None, 'habitacion': None}
respuesta_sugerencia = None
ganador = None

# Función para mostrar las pistas más detalladas
def mostrar_pistas_completas():
    pista = []
    
    for sospechoso in sospechosos:
        jugadores_con_carta = [f'Jugador{i + 1}' for i in range(jugadores) if sospechoso in jugador_cartas[i]]
        if jugadores_con_carta:
            pista.append(f'{sospechoso} lo tiene: {", ".join(jugadores_con_carta)}')
        else:
            pista.append(f'{sospechoso} puede ser el culpable.')

    for arma in armas:
        jugadores_con_carta = [f'Jugador{i + 1}' for i in range(jugadores) if arma in jugador_cartas[i]]
        if jugadores_con_carta:
            pista.append(f'{arma} lo tiene: {", ".join(jugadores_con_carta)}')
        else:
            pista.append(f'{arma} podría ser el arma utilizada.')

    for habitacion in habitaciones:
        jugadores_con_carta = [f'Jugador{i + 1}' for i in range(jugadores) if habitacion in jugador_cartas[i]]
        if jugadores_con_carta:
            pista.append(f'{habitacion} la tiene: {", ".join(jugadores_con_carta)}')
        else:
            pista.append(f'El crimen podría haber ocurrido en la {habitacion}.')
    
    return pista

# Función para mostrar las cartas que el jugador posee
def mostrar_cartas_jugador(jugador_cartas):
    texto_cartas = "Tienes las siguientes cartas: "
    for carta in jugador_cartas:
        texto_cartas += f"{carta}, "
    return texto_cartas[:-2]  # Quitar la última coma y espacio

# Función de inferencia para deducir la solución
def inferir_solucion():
    posibles_asesinos = set(sospechosos) - set.union(*[set(cartas) for cartas in jugador_cartas])
    posibles_armas = set(armas) - set.union(*[set(cartas) for cartas in jugador_cartas])
    posibles_habitaciones = set(habitaciones) - set.union(*[set(cartas) for cartas in jugador_cartas])

    if len(posibles_asesinos) == 1 and len(posibles_armas) == 1 and len(posibles_habitaciones) == 1:
        base_conocimiento['Solucion'] = (list(posibles_asesinos)[0], list(posibles_armas)[0], list(posibles_habitaciones)[0])
        return True
    return False

# Función para realizar una sugerencia en el juego
def sugerir(sospechoso, arma, habitacion):
    respuesta = None
    # Los otros jugadores responden a la sugerencia si tienen alguna carta que coincide
    for i in range(1, jugadores):
        if sospechoso in jugador_cartas[i] or arma in jugador_cartas[i] or habitacion in jugador_cartas[i]:
            respuesta = f'Jugador{i + 1} tiene una de las cartas sugeridas.'
            break
    if not respuesta:
        respuesta = 'Ningún jugador tiene las cartas sugeridas.'
    return respuesta

# Función para manejar sugerencias del jugador
def manejar_sugerencia():
    global respuesta_sugerencia
    respuesta_sugerencia = sugerir(sugerencia['sospechoso'], sugerencia['arma'], sugerencia['habitacion'])

# Función para dibujar el menú y el tablero
def dibujar_menu():
    ventana.fill(BLANCO)
    ventana.blit(tablero_img, (0, 0))  # Dibujar tablero como fondo
    
    titulo = fuente.render("Simulación de Clue", True, NEGRO)
    ventana.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 50))
    
    # Botones
    pygame.draw.rect(ventana, VERDE, (300, 150, 200, 50))  # Botón de Pistas
    texto_pistas = fuente.render("Mostrar Pistas", True, NEGRO)
    ventana.blit(texto_pistas, (ANCHO//2 - texto_pistas.get_width()//2, 160))
    
    pygame.draw.rect(ventana, ROJO, (300, 250, 200, 50))  # Botón de Inferir
    texto_inferir = fuente.render("Inferir Solución", True, NEGRO)
    ventana.blit(texto_inferir, (ANCHO//2 - texto_inferir.get_width()//2, 260))
    
    pygame.draw.rect(ventana, AZUL, (300, 350, 200, 50))  # Botón de Sugerir
    texto_sugerir = fuente.render("Hacer Sugerencia", True, NEGRO)
    ventana.blit(texto_sugerir, (ANCHO//2 - texto_sugerir.get_width()//2, 360))
    
    pygame.draw.rect(ventana, AZUL, (300, 450, 200, 50))  # Botón de Salir
    texto_salir = fuente.render("Salir", True, NEGRO)
    ventana.blit(texto_salir, (ANCHO//2 - texto_salir.get_width()//2, 460))
    
    pygame.display.update()

# Función principal
def juego():
    corriendo = True
    global fase, sugerencia, respuesta_sugerencia
    while corriendo:
        dibujar_menu()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            
            if evento.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                
                # Botón de Pistas
                if 300 <= x <= 500 and 150 <= y <= 200:
                    pistas = mostrar_pistas_completas()
                    ventana.fill(BLANCO)
                    ventana.blit(tablero_img, (0, 0))  # Mantener el tablero visible
                    for i, pista in enumerate(pistas):
                        texto_pista = fuente.render(pista, True, BLANCO)
                        ventana.blit(texto_pista, (50, 100 + i * 40))
                    pygame.display.update()
                    pygame.time.wait(5000)
                
                # Botón de Inferir Solución
                if 300 <= x <= 500 and 250 <= y <= 300:
                    solucion_encontrada = inferir_solucion()
                    ventana.fill(BLANCO)
                    ventana.blit(tablero_img, (0, 0))  # Mantener el tablero visible
                    if solucion_encontrada:
                        asesino, arma, habitacion = base_conocimiento['Solucion']
                        texto_solucion = fuente.render(f"¡El asesino es {asesino}, con el {arma}, en la {habitacion}!", True, NEGRO)
                    else:
                        texto_solucion = fuente.render("Aún no se puede inferir la solución.", True, BLANCO)
                    ventana.blit(texto_solucion, (50, 100))
                    pygame.display.update()
                    pygame.time.wait(5000)
                
                # Botón de Sugerir
                if 300 <= x <= 500 and 350 <= y <= 400:
                    # Aquí manejar la sugerencia del jugador
                    sugerencia = {'sospechoso': 'Miss Scarlet', 'arma': 'Cuchillo', 'habitacion': 'Biblioteca'}
                    manejar_sugerencia()
                    ventana.fill(BLANCO)
                    ventana.blit(tablero_img, (0, 0))  # Mantener el tablero visible
                    texto_respuesta = fuente.render(respuesta_sugerencia, True, NEGRO)
                    ventana.blit(texto_respuesta, (50, 100))
                    pygame.display.update()
                    pygame.time.wait(5000)
                
                # Botón de Salir
                if 300 <= x <= 500 and 450 <= y <= 500:
                    corriendo = False
    
    pygame.quit()

# Ejecutar el juego
juego()
