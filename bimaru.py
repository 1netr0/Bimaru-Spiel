import pygame
import sys
import random

pygame.init()
DISPLAYSURF = pygame.display.set_mode((800, 700))
pygame.display.set_caption("Bimaru")

unbekannt = 0
wasser = 1
schiff = 2
treffer = 3
versenkt = 4
markiert_wasser = 5
markiert_schiff = 6
feldgroesse = 50


schwierigkeitsstufen = [
    ("Leicht",     6,  6,  [3, 2, 1, 1],                        70),
    ("Mittel",     8,  8,  [3, 2, 2, 1, 1, 1],                  60),
    ("Schwer",     10, 10, [4, 3, 3, 2, 2, 2, 1, 1, 1, 1],      50),
    ("Experte",    12, 12, [5, 4, 3, 3, 2, 2, 2, 1, 1, 1, 1],   42),
]

reihen = 12
spalten = 12
flotten_laengen = [5, 4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
feldgroesse = 42
spiel_laeuft = False

start = 0
end = None

font = pygame.font.SysFont(None, 36)
clicks = 0

class Feld():
    def __init__(self, status=unbekannt):
        self.status = status
        self.schiff = None
        self.hit = False
        self.markierung = None

class Schiff():
    def __init__(self, laenge, felder):
        self.laenge = laenge
        self.felder = felder
        self.treffer = set()
    
    def versenkt(self):
        return len(self.treffer) == self.laenge


board = [[Feld() for _ in range(spalten)] for _ in range(reihen)]
schiffe = []

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
    spalte = (x - 40) // feldgroesse
    reihe = (y - 40) // feldgroesse

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

        if feld.schiff.versenkt():
            for fx, fy in feld.schiff.felder:
                board[fx][fy].status = versenkt

    elif feld.status == treffer:
        feld.status = treffer
    else:
        feld.status = wasser

    if alles_versenkt():
        stop_timer()

def markieren(x, y):
    spalte = (x - 40) // feldgroesse
    reihe = (y - 40) // feldgroesse

    if not in_bound(reihe, spalte):
        return
    
    feld = board[reihe][spalte]

    if feld.hit:
        return
    
    if feld.markierung is None:
        feld.markierung = markiert_wasser
    elif feld.markierung == markiert_wasser:
        feld.markierung = markiert_schiff
    else:
        feld.markierung = None

def neue_runde(stufe_index):
    global board, schiffe, clicks, reihen, spalten, flotten_laengen, feldgroesse, spiel_laeuft
    _, r, s, fl, fg = schwierigkeitsstufen[stufe_index]
    reihen = r
    spalten = s
    flotten_laengen = fl
    feldgroesse = fg

    board = [[Feld() for _ in range(spalten)] for _ in range(reihen)]
    schiffe = platziere_zufaellige_flotte()
    clicks = 0
    spiel_laeuft = True
    start_timer()

def restart():
    global spiel_laeuft
    spiel_laeuft = False

def schiffe_spalten(spalte):
    return sum(1 for reihe in range(reihen)
               if board[reihe][spalte].status == schiff and not board[reihe][spalte].hit)

def schiffe_reihen(reihe):
    return sum(1 for spalte in range(spalten)
               if board[reihe][spalte].status == schiff and not board[reihe][spalte].hit)


def draw_menu(surface):
    sw, sh = surface.get_size()
    surface.fill((15, 25, 50))

    font_titel = pygame.font.SysFont(None, 72)
    font_sub   = pygame.font.SysFont(None, 30)

    titel = font_titel.render("BIMARU", True, (255, 255, 255))
    sub   = font_sub.render("Schwierigkeitsstufe wählen", True, (120, 160, 220))
    surface.blit(titel, titel.get_rect(center=(sw // 2, 110)))
    surface.blit(sub,   sub.get_rect(center=(sw // 2, 170)))

    btn_rects = []
    btn_w, btn_h = 340, 72
    spacing = 20
    total_h = len(schwierigkeitsstufen) * (btn_h + spacing) - spacing
    start_y = (sh - total_h) // 2 + 60

    farben = [
        ((50, 180, 90),  (30, 130, 60)),   
        ((60, 140, 220), (30, 90, 170)),   
        ((220, 150, 30), (160, 100, 10)),  
        ((210, 50,  50), (150, 20, 20)),   
    ]

    beschreibungen = [
        "6×6  ·  4 Schiffe",
        "8×8  ·  6 Schiffe",
        "10×10  ·  10 Schiffe",
        "12×12  ·  11 Schiffe",
    ]

    for i, (name, *_) in enumerate(schwierigkeitsstufen):
        bx = (sw - btn_w) // 2
        by = start_y + i * (btn_h + spacing)
        rect = pygame.Rect(bx, by, btn_w, btn_h)
        btn_rects.append(rect)

        farbe, _ = farben[i]

        pygame.draw.rect(surface, farbe, rect, border_radius=12)

        fn = pygame.font.SysFont(None, 38)
        fd = pygame.font.SysFont(None, 24)
        t_name = fn.render(name, True, (255, 255, 255))
        t_desc = fd.render(beschreibungen[i], True, (220, 220, 220))
        surface.blit(t_name, t_name.get_rect(center=(sw // 2, by + btn_h // 2 - 10)))
        surface.blit(t_desc, t_desc.get_rect(center=(sw // 2, by + btn_h // 2 + 18)))

    hint = font_sub.render("M = Markieren  ·  R = Hauptmenü", True, (70, 100, 150))
    surface.blit(hint, hint.get_rect(center=(sw // 2, sh - 30)))

    return btn_rects

def draw_gewonnen_overlay(surface):
    screen_w, screen_h = surface.get_size()
 

    overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    surface.blit(overlay, (0, 0))
 

    box_w, box_h = 360, 160
    box_x = (screen_w - box_w) // 2
    box_y = (screen_h - box_h) // 2
 

    pygame.draw.rect(surface, (30, 30, 30), (box_x + 4, box_y + 4, box_w, box_h), border_radius=12)

    pygame.draw.rect(surface, (255, 255, 255), (box_x, box_y, box_w, box_h), border_radius=12)

    pygame.draw.rect(surface, (0, 180, 80), (box_x, box_y, box_w, box_h), 3, border_radius=12)
 
    font_gross = pygame.font.SysFont(None, 42)
    font_klein = pygame.font.SysFont(None, 30)
 
    zeile1 = font_gross.render("Bimaru gelöst!", True, (0, 140, 60))
    zeile2 = font_klein.render(f"Klicks: {clicks}   Zeit: {vergangene_zeit():.1f} s", True, (60, 60, 60))
    zeile3 = font_klein.render("R drücken für das Hauptmenü", True, (120, 120, 120))
 
    surface.blit(zeile1, zeile1.get_rect(center=(screen_w // 2, box_y + 45)))
    surface.blit(zeile2, zeile2.get_rect(center=(screen_w // 2, box_y + 90)))
    surface.blit(zeile3, zeile3.get_rect(center=(screen_w // 2, box_y + 125)))



def draw_board(surface):
    for i in range(reihen):
        for j in range(spalten):
            feld = board[i][j]
            status = feld.status
            
            if status == unbekannt:
                color = (200, 200, 200)
            elif status == wasser:
                color = (0, 0, 255)
            elif status == schiff:
                color = (200, 200, 200)
            elif status == treffer:
                color = (255, 255, 0)
            elif status == versenkt:
                color = (0, 255, 0)
            else:
                color = (200, 200, 200)

            pygame.draw.rect(DISPLAYSURF, color, (40 + j * feldgroesse, 40 + i*feldgroesse, feldgroesse, feldgroesse), 0)
            pygame.draw.rect(surface, (0, 0, 0), (40 + j * feldgroesse, 40 + i * feldgroesse, feldgroesse, feldgroesse), 1)


            if not feld.hit:
                cx = 40 + j * feldgroesse + feldgroesse // 2
                cy = 40 + i * feldgroesse + feldgroesse // 2
                if feld.markierung == markiert_wasser:
                    sym = pygame.font.SysFont(None, 28).render("~", True, (0, 0, 150))
                    DISPLAYSURF.blit(sym, sym.get_rect(center=(cx, cy)))
                elif feld.markierung == markiert_schiff:
                    sym = pygame.font.SysFont(None, 28).render("X", True, (60, 60, 60))
                    DISPLAYSURF.blit(sym, sym.get_rect(center=(cx, cy)))

    text = font.render(f"clicks: {clicks}", True, (0, 0, 0))
    zeit = font.render(f"zeit: {vergangene_zeit()} s", True, (0, 0, 0))
    DISPLAYSURF.blit(text, (spalten * feldgroesse + 50, 10))
    DISPLAYSURF.blit(zeit, (spalten * feldgroesse + 50, 50))

    for j in range(spalten):
        anzahl = schiffe_spalten(j)
        text = font.render(str(anzahl), True, (0, 0, 0))
        text_rect = text.get_rect(center=(40 + j * feldgroesse + feldgroesse / 2, 20))
        DISPLAYSURF.blit(text, text_rect)

    for i in range(reihen):
        anzahl = schiffe_reihen(i)
        text = font.render(str(anzahl), True, (0, 0, 0))
        text_rect = text.get_rect(center=(20 , 40 + i * feldgroesse + feldgroesse / 2))
        DISPLAYSURF.blit(text, text_rect) 

start_timer()

while True:
    mx, my = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


        if not spiel_laeuft:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(menu_btn_rects if 'menu_btn_rects' in dir() else []):
                    if rect.collidepoint(mx, my):
                        neue_runde(i)


        else:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not alles_versenkt():
                    abschiessen(mx, my)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    if not alles_versenkt():
                        markieren(mx, my)
                if event.key == pygame.K_r:
                    restart()
    
    DISPLAYSURF.fill((255, 255, 255))

    if not spiel_laeuft:
        menu_btn_rects = draw_menu(DISPLAYSURF)
    else:
        draw_board(DISPLAYSURF)
        if alles_versenkt():
            draw_gewonnen_overlay(DISPLAYSURF)

    pygame.display.update()
