from models.improvement_heuristic import HIDDEN_CELL, FLAG_CELL, Improvement_Heuristic
import numpy as np 
from display.display_board import *
import os 

class Enhanced_Heuristic(): 

    def get_info(self, current_board, unsolved_cell): 
        mine_coors = []
        mine_count = []
        center = []

        for (r, c) in unsolved_cell: 
            region = current_board[r - 1: r + 2, c - 1: c + 2]

            remaining_mine = int(region[1, 1] - np.count_nonzero(region == FLAG_CELL))

            mine_coord = []
            
            for i, j in [tuple(idx) for idx in np.argwhere(region == HIDDEN_CELL)]: 
                mine_coord.append((int(i + r - 2), int(j + c - 2)))

            mine_coors.append(mine_coord)
            mine_count.append(remaining_mine)
            center.append(int(region[1, 1]))
        return mine_coors, mine_count, center

    def solve(self, current_board, unsolved_cell): 

        current_board_copy = np.pad(current_board, pad_width = ((1, 1), (1, 1)), mode = "constant", constant_values = 10)
        safes = [] 
        mines = []

        coord_may_mine, mine_count, center = self.get_info(current_board_copy, unsolved_cell)

        for i in range(len(coord_may_mine)):
            for j in range(len(coord_may_mine)): 
                if i == j: continue

                store_ = []
                # i se xet xem co nhung thang nao la tap con cua no 
                if all(item in coord_may_mine[i] for item in coord_may_mine[j]): 
                    if mine_count[i] == mine_count[j]: 
                        for (r, c) in coord_may_mine[i] : 
                            if (r, c) not in safes and (r, c) not in coord_may_mine[j] : 
                                safes.append((r, c))
                    elif mine_count[i] + mine_count[j] == center[i]: 
                        for (r, c) in coord_may_mine[i]: 
                            if (r, c) not in mines and (r, c) not in coord_may_mine[j]: 
                                mines.append((r, c))
                    else : 
                        store_.append(j)

            if store_ != []: 
                z = []
                total_mine = 0
                for k in store_ : 
                    for (r, c) in coord_may_mine[k]: 
                        if (r, c) not in z : 
                            z.append((r, c))
                        total_mine += mine_count[k]
                if total_mine == center[i]: 
                    for (r, c) in coord_may_mine[i]: 
                        if (r, c) not in safes and (r, c) not in z: 
                            safes.append((r, c))
                    

        # print("COORD MAY MINE: ", coord_may_mine)
        # print("SAFE :", safes)
        # print("MINES", mines)
        return safes, mines

if __name__ == "__main__": 
    h = Improvement_Heuristic()
    random_range = len(os.listdir('./data/intermediate'))
    random_idx = np.random.randint(1, random_range)
    print('TEST BOARD NUMBER:', random_idx)
    test = np.load(f'./data/intermediate/{random_idx}.npy')
    print()
    unsolved_cell = h.find_unsolved_cell(test)
    unsolved_cell = [(r + 1, c + 1) for (r, c) in unsolved_cell]
    print("RUN SOLVER :")

    solver = Enhanced_Heuristic()
    safes, mines = solver.solve(test, unsolved_cell)
    display(test, safes, mines, True)
