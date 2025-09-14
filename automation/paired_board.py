from selenium import webdriver
from selenium.webdriver.common.by import By
import tkinter as tk
import numpy as np
from models.improvement_heuristic import Improvement_Heuristic
import time
import pygame
import os
os.environ["SDL_VIDEO_WINDOW_POS"] = "20, 50"

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


game_level = input("SELECT LEVEL (BEGINNER/INTERMEDIATE/EXPERT): ")
game_level = game_level.lower()

while game_level not in ['beginner', 'intermediate', 'expert']:
    print("INVALID GAME MODE!")
    game_level = input("SELECT LEVEL (BEGINNER/INTERMEDIATE/EXPERT): ")


root = tk.Tk()
root.withdraw()
screen_width = root.winfo_screenwidth()

options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--incognito")

driver = webdriver.Chrome(options=options)
driver.set_window_size(800, 800)
driver.set_window_position(screen_width-800, 10)
driver.set_page_load_timeout(30)

minesweeper_url = f'https://minesweeperonline.com/#{game_level}'
driver.execute_script(f'window.open("{minesweeper_url}")', 'blank')
driver.switch_to.window(driver.window_handles[-1])
time.sleep(2)

if game_level == 'beginner': 
    total_cell = 9*9
    nrow, ncol = (9, 9)
elif game_level == 'intermediate': 
    total_cell = 16*16
    nrow, ncol = (16, 16)
else: 
    total_cell = 16*30
    nrow, ncol = (16, 30)
    
GRID_SIZE = (ncol, nrow) 
WIDTH, HEIGHT = GRID_SIZE[0] * CELL_SIZE  + 20, GRID_SIZE[1] * CELL_SIZE  

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minesweeper Visualizer")
font = pygame.font.Font(None, 30)


def draw_grid(grid, offset_x, safe=None):
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
            elif value == -2:
                pygame.draw.rect(screen, BOMB_COLOR, rect)
            else:
                pygame.draw.rect(screen, OPEN_COLOR, rect)
                if value > 0:
                    text = font.render(str(int(value)), True, (0, 0, 0))
                    screen.blit(text, (x * CELL_SIZE + 12 + offset_x, y * CELL_SIZE + 8))
            pygame.draw.rect(screen, LINE_COLOR, rect, 1)

def get_current_board():
    current_board = np.zeros((nrow, ncol), dtype=object)
    for r in range(nrow):
        for c in range(ncol):
            grid_id = f'//*[@id="{r+1}_{c+1}"]'
            grid = driver.find_element(By.XPATH, grid_id)
            get_current_state = grid.get_attribute("class")
            if get_current_state == 'square bombflagged':
                current_board[r, c] = FLAG_CELL
            elif get_current_state == 'square blank':
                current_board[r, c] = HIDDEN_CELL
            elif get_current_state == 'square bombdeath':
                current_board[r, c] = MINE_CELL
            else:
                number = float(get_current_state[-1])
                current_board[r, c] = number
    return current_board

def reset_board():
    resetid = '//*[@id="face"]'
    resetButton = driver.find_element(By.XPATH, resetid)
    resetButton.click()
    time.sleep(1)
    
def game_over():
    face_id = '//*[@id="face"]'
    face = driver.find_element(By.XPATH, face_id)
    get_current_state = face.get_attribute("class")
    # ! when lose the class will be : "facedead"
    # ! otherwise "facewin"
    if get_current_state == 'facedead':
        return -1
    if get_current_state == 'facewin': 
        return 1
    return 0

def heuristic_solve(heuristic, current_board): 
    safes, mines = heuristic.solve(current_board)
    return safes, mines 

def update_current(current_board, mines):
    for r, c in mines : 
        current_board[r, c] = FLAG_CELL
    return current_board

def paired_board(current_board, offset_x, safe): 
    screen.fill((255, 255, 255))   
    draw_grid(current_board, offset_x=offset_x, safe=safe)
    pygame.display.flip()
        
def play():
    heuristic = Improvement_Heuristic()
    done = game_over()
    flag_coords = []
    while done == 0:
        current_board = get_current_board()
        current_board = update_current(current_board=current_board, mines=flag_coords)
        safes, mines = heuristic_solve(heuristic=heuristic, current_board=current_board)
        safes = None if safes == [] else safes
        for r, c in mines: 
            if (r, c) not in flag_coords:
                flag_coords.append((r, c))
        current_board = update_current(current_board=current_board, mines=flag_coords)
        paired_board(current_board=current_board, offset_x=0, safe=safes)
        done = game_over()
    if done == 1: 
        print("Win")
        total_win += 1
    elif done == -1 :
        print("Lose") 
    print()
    pygame.quit()
    
play()
