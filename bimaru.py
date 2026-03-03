import pygame
import sys

pygame.init()
DISPLAYSURF = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Bimaru")

unbekannt = 0
wasser = 1
schiff = 2

class Feld():
    def __init__(self, status=unbekannt):
        self.status = status


reihen = 10
spalten = 10
board = [[Feld() for _ in range(spalten)] for _ in range(reihen)]

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

            pygame.draw.rect(DISPLAYSURF, color, (j*50, i*50, 50, 50), 0)


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    DISPLAYSURF.fill((255, 255, 255))
    draw_board(DISPLAYSURF)
    pygame.display.update()
