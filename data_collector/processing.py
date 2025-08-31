import numpy as np

# CELL VALUES
BORDER_CELL = -10
HIDDEN_CELL = -0.5
FLAG_CELL = -1

def extract_feature(partial_board):
    padded_partial_board = np.pad(partial_board, pad_width=2, mode='constant', constant_values=BORDER_CELL)
    features = np.zeros((partial_board.shape[0]*partial_board.shape[1], 27), dtype=np.float32)
    for r in range(partial_board.shape[0]):
        for c in range(partial_board.shape[1]):
            features[r*partial_board.shape[1] + c, 0] = partial_board[r, c] # Value of the cell
            
            neighbors = np.zeros(24, dtype=np.float32)
            num_hidden = 0
            num_flags = 0
            current_ = 0
            for i in range(-2, 3):
                for j in range(-2, 3):
                    if i == 0 and j == 0:
                        continue
                    neighbors[current_] = padded_partial_board[r + i + 1, c + j + 1]
                    if padded_partial_board[r + i + 1, c + j + 1] == HIDDEN_CELL:
                        num_hidden += 1
                    elif padded_partial_board[r + i + 1, c + j + 1] == FLAG_CELL:
                        num_flags += 1
                    current_ += 1
            features[r*partial_board.shape[1] + c, 1:25] = neighbors # Values of the neighbors    
            features[r*partial_board.shape[1] + c, 25] = num_hidden # Number of hidden cells around
            features[r*partial_board.shape[1] + c, 26] = num_flags # Number of flags around
    return features