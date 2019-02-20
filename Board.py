class Board:
    """Use to manage pieces on the game board"""

    def __init__(self):
        empty = {-1: 'border', 0: 'border', 1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None,
                 9: 'border', 10: 'border'}
        self.board = {File('a'): empty.copy(), File('b'): empty.copy(), File('c'): empty.copy(),
                      File('d'): empty.copy(), File('e'): empty.copy(), File('f'): empty.copy(),
                      File('g'): empty.copy(), File('h'): empty.copy(), File('_'): {i: 'border' for i in range(-1, 11)}}

    def add(self, piece):
        self.board[piece.file][piece.rank] = piece

    def remove(self, piece):
        self.board[piece.file][piece.rank] = None

    def move(self, move):
        piece = move.piece

        self.remove(piece)
        piece.move(move)
 
        if move.kind == 'cap':
            self[move.position].capture()
            self.add(move.piece)
        else:
            self.add(piece)

        if move.kind == 'promote':
            piece.promote()

    def __str__(self):
        files = 'abcdefgh'
        string = []
        for rank in range(8, 0, -1):
            lst = [f'{rank} ']  # print(rank, end=' |')
            for file in files:
                if self[f'{file}{rank}'] is None:
                    lst.append(' ')  # print(' |', end='')
                else:
                    lst.append(f'{self[f"{file}{rank}"].title}')  # print(f'{self[f"{file}{rank}"].title}|', end='')
            string.append('|'.join(lst))
        string.append('   a b c d e f g h')
        string = '|\n'.join(string)
        return string

    def __getitem__(self, index):
        try:
            return self.board[File(index[0])][int(index[1:])]
        except KeyError:
            print('KeyError')
            return None


class File:
    """
    Used to track the files (rank/file) of the chess board.
    
    Used primarily to simplify numeric operations with the file while still maintaining the character representation
    """

    files = '__abcdefgh__'

    def __init__(self, file):
        """
        Stores a character that can be easily added to and subtracted from
        
        file: the character corresponding to the the file of the board
        """

        self.file = file

    def __add__(self, other):
        f_int = File.files.index(self.file)
        return File(File.files[f_int + other])

    def __sub__(self, other):
        f_int = File.files.index(self.file)
        return File(File.files[f_int - other])

    def __str__(self):
        return self.file

    def __repr__(self):
        return self.file

    def __hash__(self):
        return File.files.index(self.file)

    def __eq__(self, other):
        if type(other) == File:
            return self.file == other.file
        elif type(other) == str:
            return self.file == other
        else:
            raise NotImplementedError