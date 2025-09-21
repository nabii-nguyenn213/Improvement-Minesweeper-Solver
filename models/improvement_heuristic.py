import numpy as np
import time

HIDDEN_CELL = -0.5
FLAG_CELL = -1  

class Improvement_Heuristic: 
    
    def __init__(self): 
        self.done = []
        self.t = 1
        self.times = 0
        self.longest_time_solve = 0
    
    def reset(self): 
        self.done = []
        self.t = 1
        self.times = 0
        self.longest_time_solve = 0
    
    def get_avg_time_solve(self): 
        print(f"Average time solve {(self.times/self.t):.2f} seconds")
        return 
    
    def get_longest_time_solve(self):
        print("LONGEST TIME SOLVE (HEURISTIC) :", self.longest_time_solve)
        return  
        
    def border_board(self, current_board): 
        return np.pad(current_board, pad_width=((1, 1), (1, 1)), mode="constant", constant_values=10)

    def find_unsolved_cell(self, current_board): 
        padded = self.border_board(current_board)
        H, W = padded.shape
        board_copy = padded.copy()
        unsolved_cell = []

        for i in range(1, H - 1):
            for j in range(1, W - 1):
                if (i, j) in self.done: continue
                region = board_copy[i-1:i+2, j-1:j+2]    
                if self._all_hidden(region) : continue
                if self._contain_hidden(region):
                    if region[1, 1] != HIDDEN_CELL and region[1, 1] != FLAG_CELL:
                        unsolved_cell.append((i-1, j-1))

        return unsolved_cell
        
    def _contain_hidden(self, region): 
        return (region == HIDDEN_CELL).any()
    
    def _all_hidden(self, region): 
        return np.all(region == HIDDEN_CELL)

    def flag(self, region): 
        neg_count = np.count_nonzero(region < 0) 
        if neg_count == region[1, 1]: 
            return [tuple(idx) for idx in np.argwhere(region == HIDDEN_CELL)]
        return None
        
    def safe(self, region): 
        flag_count = np.count_nonzero(region == FLAG_CELL)
        # True -> open all the hidden, else do nothing
        if flag_count == region[1, 1]: 
            return [tuple(idx) for idx in np.argwhere(region == HIDDEN_CELL)]
        return None
    
    def solve(self, current_board):
        self.start = time.time()
        padded = self.border_board(current_board)
        H, W = padded.shape
        
        flags = []
        safes = []

        board_copy = padded.copy()
        self.t += 1
        
        for i in range(1, H - 1):
            for j in range(1, W - 1):
                if (i, j) in self.done: continue
                region = board_copy[i-1:i+2, j-1:j+2]    
                if self._all_hidden(region) : continue
                if self._contain_hidden(region):
                    # === FLAG RULE ===
                    flag_coords = self.flag(region)
                    if flag_coords is not None:
                        for (r, c) in flag_coords: 
                            gr, gc = r + i - 1, c + j - 1
                            if board_copy[gr, gc] == HIDDEN_CELL:
                                board_copy[gr, gc] = FLAG_CELL
                                flags.append((gr - 1, gc - 1))  # shift back to original board

                    # === SAFE RULE ===
                    safe_coords = self.safe(region)
                    if safe_coords is not None:
                        for (r, c) in safe_coords:
                            gr, gc = r + i - 1, c + j - 1
                            if board_copy[gr, gc] == HIDDEN_CELL:
                                safes.append((gr - 1, gc - 1))  # shift back to original board
                else : 
                    self.done.append((i, j))

        self.end = time.time()
        self.longest_time_solve = max(self.longest_time_solve, (self.end - self.start))
        self.times += (self.end - self.start)

        return safes, flags
