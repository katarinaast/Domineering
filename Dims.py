class Dims:
    def __init__(self, num):
        self.WIDTH = 500        # window width
        self.HEIGHT = 500       # window height
        self.num = num          # num of rows and cols (square table)
        self.rows = num         #
        self.cols = num         # 
        self.dim = num + 2      # number of cells in each row/column (2 for text)
        self.cell_size = self.WIDTH // self.dim  # size of each cell in px
        self.piece_long = 2 * self.cell_size - 2 *(self.cell_size // 10)    # length/height of tile (longer length)
        self.piece_short = self.cell_size - 2 *(self.cell_size // 10)       # length/height of tile (shorter length)
        self.piece_offset = self.cell_size // 10



