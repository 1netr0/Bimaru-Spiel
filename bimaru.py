import pygame
import sys

pygame.init()
DISPLAYSURF = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Bimaru")

unbekannt = 0
wasser = 1
schiff = 2

reihen = 10
spalten = 10
board = [[unbekannt for _ in range(spalten)] for _ in range(reihen)]

def draw_board(surface):
    for i in range(reihen):
        for j in range(spalten):
            if board[i][j] == unbekannt:
                color = (200, 200, 200)
            elif board[i][j] == wasser:
                color = (0, 0, 255)
            elif board[i][j] == schiff:
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
