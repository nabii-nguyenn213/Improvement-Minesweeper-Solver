from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import tkinter as tk
import numpy as np
from models.heuristic import Heuristic
from models.improvement_heuristic import Improvement_Heuristic
import joblib
import time
from data_collector.processing import extract_feature
import os

HIDDEN_CELL = -0.5
MINE_CELL = -2
FLAG_CELL = -1


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
    num_mines = 10
    stop_threshold = 0.65
elif game_level == 'intermediate': 
    total_cell = 16*16
    nrow, ncol = (16, 16)
    num_mines = 40
    stop_threshold = 0.7
else: 
    total_cell = 16*30
    nrow, ncol = (16, 30)
    num_mines = 99
    stop_threshold = 0.8

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

def number_of_cell_hidden(current_board):    
    current_hidden = 0
    for r in range(len(current_board)): 
        for c in range(len(current_board[r])): 
            if current_board[r, c] == HIDDEN_CELL: 
                current_hidden += 1
    
    return current_hidden

def pre_opening_move(): 
    return nrow//2, ncol//2

def update_current_board(current_board, mines): 
    for r, c in mines:
        current_board[r, c] = FLAG_CELL
    return current_board

def open_all(current_board): 
    for r in range(len(current_board)): 
        for c in range(len(current_board[r])): 
            if current_board[r, c] == HIDDEN_CELL: 
                cell_id = f'//*[@id="{r+1}_{c+1}"]'
                cell = driver.find_element(By.XPATH, cell_id)
                cell.click()
        
def play():
    if game_level == 'beginner': 
        number_of_time_playing = 100
    elif game_level == 'intermediate': 
        number_of_time_playing = 50
    else: 
        number_of_time_playing = 100
    
    total_win = 0    
    
    heuristic = Improvement_Heuristic()
    
    board_solved_proportion = []
    
    for _ in range(number_of_time_playing):
        # time.sleep(1)
        print(f'Game {_ + 1} :', end=" ")
        start = time.time()
        heuristic.reset()
        
        flag_coords = []
        
        pre_opening = pre_opening_move()
        if pre_opening != None: 
            cell_id = f'//*[@id="{pre_opening[0] + 1}_{pre_opening[1] + 1}"]'
            cell = driver.find_element(By.XPATH, cell_id)
            cell.click()
        
        done = game_over()

        while done == 0:
            # time.sleep(1)
            current_board = get_current_board()
            current_board = update_current_board(current_board, flag_coords)
            if len(flag_coords) == num_mines: 
                open_all(current_board=current_board)
            safes, mines = heuristic_solve(heuristic=heuristic, current_board=current_board)
            if safes == [] and mines == []:
                print("HEURISTIC STUCK")
                time.sleep(5)
                number_cell_hidden = number_of_cell_hidden(current_board)
                print("Board solved : ", (total_cell - number_cell_hidden)/total_cell , "%")
                board_solved_proportion.append((total_cell - number_cell_hidden)/total_cell)
                break
            else:
                if safes:
                    for r, c in safes:
                        cell_id = f'//*[@id="{r+1}_{c+1}"]'
                        cell = driver.find_element(By.XPATH, cell_id)
                        cell.click()
                if mines:
                    for r, c in mines: 
                        if (r, c) not in flag_coords: 
                            flag_coords.append((r, c))

            done = game_over()
        end = time.time()
        reset_board() 
        
        if done == 1: 
            print("Win")
            total_win += 1
        elif done == -1 :
            print("Lose") 
        elapsed = end-start
        print(f"TIME PLAYED : {elapsed:.2f} seconds.")
        heuristic.get_longest_time_solve()
        print()
        
    print("Percentage =", total_win/number_of_time_playing)
    print("Mean percentage =", sum(board_solved_proportion)/len(board_solved_proportion))
    
play()
