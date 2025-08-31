import pygame
import numpy as np
import random

# Constants
CELL_SIZE = 40 
GRID_SIZE = (9, 9) 
WIDTH, HEIGHT = GRID_SIZE[0] * CELL_SIZE  + 20, GRID_SIZE[1] * CELL_SIZE  

# Color
HIDDEN_COLOR = (150, 150, 150)  
FLAG_COLOR = (200, 50, 50) 
BOMB_COLOR = (0, 0, 0) 
OPEN_COLOR = (255, 255, 255)  
LINE_COLOR = (0, 0, 0)  
SAFE_COLOR = (0, 255, 0)  

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minesweeper Visualizer")
font = pygame.font.Font(None, 30)

dataset_dir = './dataset/beginner/1.npy'
total_board = np.load(dataset_dir)
idx = random.randint(0, total_board.shape[-1])
grid = total_board[:, :, idx]

def draw_grid(grid, offset_x, safe=None):
    for y in range(GRID_SIZE[1]):
        for x in range(GRID_SIZE[0]):
            value = grid[y, x]
            rect = pygame.Rect(x * CELL_SIZE + offset_x, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            
            if safe and (y, x) in safe:
                pygame.draw.rect(screen, SAFE_COLOR, rect)
            elif value == -0.5:
                pygame.draw.rect(screen, HIDDEN_COLOR, rect)
            elif value == -1:
                pygame.draw.rect(screen, FLAG_COLOR, rect)
            elif value == -2:
                pygame.draw.rect(screen, BOMB_COLOR, rect)
            else:
                pygame.draw.rect(screen, OPEN_COLOR, rect)
                if value > 0:
                    text = font.render(str(int(value)), True, (0, 0, 0))
                    screen.blit(text, (x * CELL_SIZE + 12 + offset_x, y * CELL_SIZE + 8))
            
            pygame.draw.rect(screen, LINE_COLOR, rect, 1)

def main():
    running = True

    while running:
        screen.fill((255, 255, 255))
        draw_grid(grid, 0) 
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    pygame.quit()

if __name__ == "__main__":
    main()

