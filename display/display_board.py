import numpy as np
import pygame
import sys

# Constants

HIDDEN_CELL = -0.5
MINE_CELL = -2
FLAG_CELL = -1
CELL_SIZE = 40 

# Color
HIDDEN_COLOR = (150, 150, 150)  
FLAG_COLOR = (200, 50, 50) 
BOMB_COLOR = (0, 0, 0) 
OPEN_COLOR = (255, 255, 255)  
LINE_COLOR = (0, 0, 0)  
SAFE_COLOR = (0, 255, 0)  

def draw_grid(grid, GRID_SIZE, screen, font, offset_x, safe=None, mine = None, axis = False ):
    if not axis: 
        for y in range(GRID_SIZE[1]):
            for x in range(GRID_SIZE[0]):
                value = grid[y, x]
                rect = pygame.Rect(x * CELL_SIZE + offset_x, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                
                if safe and (y, x) in safe:
                    pygame.draw.rect(screen, SAFE_COLOR, rect)
                elif value == HIDDEN_CELL:
                    pygame.draw.rect(screen, HIDDEN_COLOR, rect)
                elif value == FLAG_CELL:
                    pygame.draw.rect(screen, FLAG_COLOR, rect)
                elif mine and (y, x) in mine:
                    pygame.draw.rect(screen, BOMB_COLOR, rect)
                else:
                    pygame.draw.rect(screen, OPEN_COLOR, rect)
                    if value > 0:
                        text = font.render(str(int(value)), True, (0, 0, 0))
                        screen.blit(text, (x * CELL_SIZE + 12 + offset_x, y * CELL_SIZE + 8))
                pygame.draw.rect(screen, LINE_COLOR, rect, 1)
    else : 
       for y in range(GRID_SIZE[1] + 1):
            if y == GRID_SIZE[1]: 
                for x in range(GRID_SIZE[0]): 
                    
                    rect = pygame.Rect(x * CELL_SIZE + offset_x, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(screen, (255, 255, 255), rect)
                    text = font.render(str(int(x)), True, (0, 0, 0))
                    screen.blit(text, (x * CELL_SIZE + 12 + offset_x, y * CELL_SIZE+ 8))
            else: 
                for x in range(GRID_SIZE[0] + 1):
                    if x == GRID_SIZE[0]: 
                        rect = pygame.Rect(x * CELL_SIZE + offset_x, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        pygame.draw.rect(screen, (255, 255, 255), rect)
                        text = font.render(str(int(y)), True, (0, 0, 0))
                        screen.blit(text, (x * CELL_SIZE + 12 + offset_x, y * CELL_SIZE+ 8))

                    else: 
                        value = grid[y, x]
                        rect = pygame.Rect(x * CELL_SIZE + offset_x, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        
                        if safe and (y, x) in safe:
                            pygame.draw.rect(screen, SAFE_COLOR, rect)
                        elif value == HIDDEN_CELL:
                            pygame.draw.rect(screen, HIDDEN_COLOR, rect)
                        elif value == FLAG_CELL:
                            pygame.draw.rect(screen, FLAG_COLOR, rect)
                        elif mine and (y, x) in mine:
                            pygame.draw.rect(screen, BOMB_COLOR, rect)
                        else:
                            pygame.draw.rect(screen, OPEN_COLOR, rect)
                            if value > 0:
                                text = font.render(str(int(value)), True, (0, 0, 0))
                                screen.blit(text, (x * CELL_SIZE + 12 + offset_x, y * CELL_SIZE + 8))
                        pygame.draw.rect(screen, LINE_COLOR, rect, 1)


def display(board, safe = None, mine = None, axis = False ): 
    nrow, ncol = board.shape
    GRID_SIZE = (ncol, nrow) 
    if not axis : 
        WIDTH, HEIGHT = GRID_SIZE[0] * CELL_SIZE  + 20, GRID_SIZE[1] * CELL_SIZE  
    else: 
        WIDTH, HEIGHT = (GRID_SIZE[0] + 1) * CELL_SIZE  + 20, (GRID_SIZE[1] + 1) * CELL_SIZE  
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Minesweeper Visualizer")
    font = pygame.font.Font(None, 30)


    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Close window
                running = False

        # Fill screen with a color (RGB)
        screen.fill((255, 255, 255))  
        draw_grid(board, GRID_SIZE, screen, font, offset_x=0, safe = safe, mine = mine, axis = axis)
        pygame.display.flip()

    # Quit Pygame
    pygame.quit()
    sys.exit()
