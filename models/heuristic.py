import numpy as np

# ! Constants
HIDDEN_CELL = -0.5
FLAG_CELL = -1
MINE_CELL = -2
BORDER_CELL = -10

class Heuristic:
    def __init__(self, board):
        self.board = board
        
    def find_mine(self):
        mines = []
        for row in range(self.board.shape[0]):
            for col in range(self.board.shape[1]):
                num_hidden = 0
                num_revealed = 0
                num_flags_around = 0
                if self.board[row, col] <= 0:
                    continue
                for r in range(max(0, row - 1), min(self.board.shape[0] - 1, row + 1) + 1):
                    for c in range(max(0, col - 1), min(self.board.shape[1] - 1, col + 1) + 1):
                        if r == row and c == col:
                            continue
                        if self.board[r, c] == HIDDEN_CELL:
                            num_hidden += 1
                        elif self.board[r, c] == FLAG_CELL:
                            num_flags_around += 1
                        elif self.board[r, c] >= 0:
                            num_revealed += 1                
                if num_hidden + num_flags_around == self.board[row, col]:
                    for r in range(max(0, row - 1), min(self.board.shape[0] - 1, row + 1) + 1):
                        for c in range(max(0, col - 1), min(self.board.shape[1] - 1, col + 1) + 1):
                            if r == row and c == col: 
                                continue
                            if self.board[r, c] == HIDDEN_CELL:
                                mines.append((r, c))
        return mines
    
    def find_safe(self):
        safes = []
        for row in range(self.board.shape[0]):
            for col in range(self.board.shape[1]):
                num_hidden = 0
                num_revealed = 0
                num_flags_around = 0
                if self.board[row, col] <= 0:
                    continue
                for r in range(max(0, row - 1), min(self.board.shape[0] - 1, row + 1) + 1):
                    for c in range(max(0, col - 1), min(self.board.shape[1] - 1, col + 1) + 1):
                        if r == row and c == col:
                            continue
                        if self.board[r, c] == HIDDEN_CELL:
                            num_hidden += 1
                        elif self.board[r, c] == FLAG_CELL:
                            num_flags_around += 1
                        elif self.board[r, c] >= 0:
                            num_revealed += 1                
                if num_flags_around == self.board[row, col]:
                    for r in range(max(0, row - 1), min(self.board.shape[0] - 1, row + 1) + 1):
                        for c in range(max(0, col - 1), min(self.board.shape[1] - 1, col + 1) + 1):
                            if r == row and c == col: 
                                continue
                            if self.board[r, c] == HIDDEN_CELL:
                                safes.append((r, c))
        return safes
    
    def solve(self):
        safes = self.find_safe()
        mines = self.find_mine()
        return safes, mines