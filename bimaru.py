import pygame
import sys
import random

pygame.init()
DISPLAYSURF = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Bimaru")

unbekannt = 0
wasser = 1
schiff = 2
treffer = 3
feldgroesse = 50

start = 0
end = None

font = pygame.font.SysFont(None, 36)
clicks = 0

class Feld():
    def __init__(self, status=unbekannt):
        self.status = status
        self.schiff = None
        self.hit = False

class Schiff():
    def __init__(self, laenge, felder):
        self.laenge = laenge
        self.felder = felder
        self.treffer = set()
    
    def versenkt(self):
        return len(self.treffer) == self.laenge


reihen = 12
spalten = 12
board = [[Feld() for _ in range(spalten)] for _ in range(reihen)]

def in_bound(x, y):
    return 0 <= x < reihen and 0 <= y < spalten

def kann_platzieren(felder):
    felder_set = set(felder)

    for x, y in felder:
        if not in_bound(x, y):
            return False
        if board[x][y].status != unbekannt:
            return False

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in felder_set:
                    continue
                if in_bound(nx, ny) and board[nx][ny].status == schiff:
                    return False
    
    return True

def platzieren_schiff(x, y, laenge, horizontal):
    felder = []
    for k in range(laenge):
        if horizontal:
            felder.append((x, y + k))
        else:
            felder.append((x + k, y))

    if not kann_platzieren(felder):
        return None

    neues_schiff = Schiff(laenge, felder)

    for fx, fy in felder:
        board[fx][fy].status = schiff
        board[fx][fy].schiff = neues_schiff

    return neues_schiff

def platziere_zufaellige_flotte():
    schiffe = []
    flotten_laengen = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]

    for laenge in flotten_laengen:
        platziert = False

        while not platziert:
            horizontal = random.choice([True, False])

            if horizontal:
                x = random.randint(0, reihen - 1)
                y = random.randint(0, spalten - laenge)
            else:
                x = random.randint(0, reihen - laenge)
                y = random.randint(0, spalten - 1)

            neues_schiff = platzieren_schiff(x, y, laenge, horizontal)

            if neues_schiff:
                schiffe.append(neues_schiff)
                platziert = True

    return schiffe

schiffe = platziere_zufaellige_flotte()

def start_timer():
    global start, end
    start = pygame.time.get_ticks()
    end = None

def stop_timer():
    global end
    if end == None:
        end = pygame.time.get_ticks()
    return end

def alles_versenkt():
    for schiff in schiffe:
        if not schiff.versenkt():
            return False
    return True

def vergangene_zeit():
    if end is None:
        return (pygame.time.get_ticks() - start) / 1000
    else:
        return (end - start) / 1000
    

def abschiessen(x, y):
    global clicks
    spalte = x // feldgroesse
    reihe = y // feldgroesse

    if not in_bound(reihe, spalte):
        return

    feld = board[reihe][spalte]

    if feld.hit:
        return
    
    clicks = clicks + 1
    feld.hit = True

    if feld.status == schiff:
        feld.status = treffer
        feld.schiff.treffer.add((reihe, spalte))
    elif feld.status == treffer:
        feld.status = treffer
    else:
        feld.status = wasser

    if alles_versenkt():
        stop_timer()

def restart():
    global board, schiffe, clicks
    board = [[Feld() for _ in range(spalten)] for _ in range(reihen)]
    schiffe = platziere_zufaellige_flotte()
    clicks = 0
    start_timer()   


def draw_board(surface):
    for i in range(reihen):
        for j in range(spalten):
            status = board[i][j].status
            
            if status == unbekannt:
                color = (200, 200, 200)
            elif status == wasser:
                color = (0, 0, 255)
            elif status == schiff:
                color = (255, 0, 0)
            elif status == treffer:
                color = (0, 255, 0)

            pygame.draw.rect(DISPLAYSURF, color, (j*50, i*50, 50, 50), 0)
            pygame.draw.rect(surface, (0, 0, 0), (j * 50, i * 50, 50, 50), 1)

    text = font.render(f"clicks: {clicks}", True, (0, 0, 0))
    zeit = font.render(f"zeit: {vergangene_zeit()} s", True, (0, 0, 0))
    DISPLAYSURF.blit(text, (610, 10))
    DISPLAYSURF.blit(zeit, (610, 50))

start_timer()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = pygame.mouse.get_pos()
            abschiessen(x, y)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                restart()
    
    DISPLAYSURF.fill((255, 255, 255))
    draw_board(DISPLAYSURF)
    pygame.display.update()
