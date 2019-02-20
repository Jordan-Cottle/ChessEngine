from random import choice
import re

mode = 'watch'  # test, play, watch, custom, random, soloLearn

"""
Write a chess engine that implements all the chess rules, evaluates the chessboard and generates optimal moves for a
 given board set. 

The program should read the chessboard data from the input provided as a list of piece positions. For example "Ra4, Ne7,
 f3" means Rook on a4, Knight on e7 and Pawn on f3. The notation uses one-letter abbreviations of pieces: K (King),
  Q (Queen), N (Knight), R (Rook), B (Bishop), Pawn abbreviation may be skipped.

Output the generated moves including the following abbreviations: "x" if there is a capture, for example, Bxe4 means
 Bishop moved and captured the piece on e4. The sequence O-O indicates kingside castling; queenside castling is
 indicated by the sequence O-O-O. Pawn promotions are noted by appending = to the destination square, followed by the
  piece the pawn is promoted to (e8=Q, pawn moved to e8 and promoted to Queen). If the move is a checking move, + is
   also appended; if the move is a checkmating move, # is appended instead, for example, e8=Q#.
"""

notation = '(?P<title>[PpRrNnBbQqKk])?(?P<pos>[a-h][1-8])(?P<suffix>[x+#o0=])?'

#Values used for random piece generation, remove a title, rank, or file to remove them from a randomly generated board state (king is always included)
titles = 'prnbq'
files = 'abcdefgh'
ranks = '12345678'

numPieces = 4


def get_move(player):
    piece = chess[input('Enter the position of the piece you\'d like to move: ')]
    while piece not in player.pieces or len(piece.moves) == 0:
        print('Invalid Piece')
        piece = chess[input('Enter the position of the piece you\'d like to move: ')]

    print(f'{piece} can move to: ', end='')
    for move in piece.moves:
        if move.kind != 'cover':
            print(move.position, end=' ')
    print()

    move = Move(piece, input(f'Enter the position you would like to move {piece} to: '))
    while move not in piece.moves:
        print('Invalid Move')
        print(piece.moved)
        print(f'{piece} can move to {piece.moves}')
        move = Move(piece, input(f'Enter the position you would like to move {piece} to: '))

    return move


class File:
    files = list('__abcdefgh__')

    def __init__(self, file):
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


class Move:

    def __init__(self, piece, note):
        self.piece = piece
        self.start = piece.position

        match = re.match(notation, note)

        self.position = match.group('pos')
        suffix = match.group('suffix')

        if suffix is None:
            self.kind = 'move'
            self.suffix = ''

        elif suffix == 'x':
            self.cap = chess[self.position]
            self.kind = 'cap'
            self.suffix = suffix

        elif suffix == 'o':
            self.kind = 'cover'
            self.covered = chess[self.position]
            self.suffix = suffix

        elif suffix == '0':
            self.kind = 'castling'
            if piece.file == 'a':
                self.suffix = '0-0-0'
            elif piece.file == 'h':
                self.suffix = '0-0'

        elif suffix == '=':
            self.kind = 'promote'
            self.suffix = '=Q'

    def reverse(self):
        if self.kind == 'promote':
            self.piece.player.pieces.remove(chess[self.position])
            self.piece.player.pieces.append(self.piece)
            chess.remove(chess[self.position])
            chess.add(self.piece)
            chess.move(Move(self.piece, f'{self.start}'))
        else:
            chess.move(Move(self.piece, f'{self.start}'))
            if self.kind == 'cap':
                chess.add(self.cap)
                self.piece.enemy.pieces.append(self.cap)

    def __str__(self):
        return f'{self.piece.title}{self.position}{self.suffix}'

    def __repr__(self):
        return f'{self.piece}->{self.position}'

    def __hash__(self):
        file = self.position[0]
        rank = self.position[1]
        return (File.files.index(file) * 10) + int(rank)

    def __eq__(self, other):
        if type(other) == Move:
            return self.position == other.position
        elif type(other) == str:
            return self.position == other
        else:
            raise NotImplementedError


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
        if move.kind in ('move', 'check', 'check-mate'):
            self.add(piece)
        elif move.kind == 'cap':
            self[move.position].capture()
            self.add(move.piece)

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


class Piece:
    def __init__(self, color, role, position):
        self.color = color
        self.role = role
        self.position = position
        self.file = File(position[0])
        self.rank = int(position[1])
        self.start = position

    @property
    def moved(self):
        if self.start == self.position:
            return False
        else:
            return True

    @property
    def player(self):
        if self.color == 'White':
            return white
        elif self.color == 'Black':
            return black

    @property
    def enemy(self):
        if self.color == 'White':
            return black
        elif self.color == 'Black':
            return white

    def move(self, move):
        self.position = move.position
        self.file = File(move.position[0])
        self.rank = int(move.position[1])

    def capture(self):
        if self.color == 'White':
            white.pieces.remove(self)
        elif self.color == 'Black':
            black.pieces.remove(self)

    @property
    def title(self):
        if self.role == 'Knight':
            if self.color == 'White':
                return 'N'
            elif self.color == 'Black':
                return 'n'
        else:
            if self.color == 'White':
                return self.role[0].upper()
            elif self.color == 'Black':
                return self.role[0].lower()

    @property
    def check(self):
        if self.position in self.enemy.checks:
            return True
        else:
            return False

    @property
    def checked_by(self):
        checked_by = []
        if self.check:
            for move in self.enemy.checks:
                if move.cap == self:
                    checked_by.append(move.piece)

        return checked_by

    @property
    def covered_by(self):
        covered_by = []
        for move in self.player.covers:
            if move.covered == self:
                covered_by.append(move.piece)

        return covered_by

    @property
    def covered(self):
        if len(self.covered_by) == 0:
            return False
        else:
            return True

    @property
    def score(self):
        points = self._score

        if self.check:
            if not self.covered:
                points = 0
            else:  # self.covered;
                points -= self.points - min([checker.points for checker in self.checked_by])
                for move in self.moves:
                    if move in self.enemy.king.moves:
                        points += 1
        else:
            for move in self.moves:
                if move in self.enemy.king.moves and self.covered:
                    points += 1.5

                points += .06

        return points

    def __str__(self):
        if self.role == 'Pawn':
            return f'{self.position}'
        else:
            return f'{self.title}{self.position}'

    def __repr__(self):
        return f'{self.color} {self.role} at {self.position}'


class Pawn(Piece):

    def __init__(self, color, position):
        super(Pawn, self).__init__(color, 'Pawn', position)
        self.points = 1

    def promote(self):
        queen = Queen(self.color, self.position)
        chess.remove(self)
        chess.add(queen)
        self.player.pieces.remove(self)
        self.player.pieces.append(queen)
        return queen

    @property
    def moves(self):
        if self.position is None:
            return []

        moves = []
        if self.color == 'White':
            forward = f'{self.file}{self.rank + 1}'
            dash = f'{self.file}{self.rank + 2}'
            attack_r = f'{self.file + 1}{self.rank + 1}'
            attack_l = f'{self.file - 1}{self.rank + 1}'
        else:  # self.color == 'Black':
            forward = f'{self.file}{self.rank - 1}'
            dash = f'{self.file}{self.rank - 2}'
            attack_r = f'{self.file - 1}{self.rank - 1}'
            attack_l = f'{self.file + 1}{self.rank - 1}'

        if chess[forward] is None:
            if (self.color == 'White' and self.rank == 7) or (self.color == 'Black' and self.rank == 2):
                moves.append(Move(self,forward + '=Q'))
            else:
                moves.append(Move(self, forward))
        if not self.moved and (chess[forward] is None and chess[dash] is None):
            moves.append(Move(self, dash))

        diag = chess[attack_r]
        if diag is not None and diag != 'border':
            if diag.color != self.color:
                moves.append(Move(self, attack_r + 'x'))
            else:
                moves.append(Move(self, attack_r + 'o'))

        diag = chess[attack_l]
        if diag is not None and diag != 'border':
            if diag.color != self.color:
                moves.append(Move(self, attack_l + 'x'))
            else:
                moves.append(Move(self, attack_l + 'o'))

        return moves

    @property
    def score(self):
        score = self.points
        if self.color == 'White':
            score += self.rank / 4
        elif self.color == 'Black':
            score += (8 - self.rank) / 4

        if self.check:
            if not self.covered:
                score /= 2
            if self.covered:
                score += 1

        if self.moves == []:
            score -= 1

        return score


class Knight(Piece):

    def __init__(self, color, position):
        super(Knight, self).__init__(color, 'Knight', position)
        self.points = 3

    @property
    def moves(self):
        if self.position is None:
            return []

        moves = [(2, 1), (-2, 1), (2, -1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        valid_moves = []
        for move in moves:
            move = f'{self.file + move[0]}{self.rank + move[1]}'
            end = chess[move]
            if end is None:
                valid_moves.append(Move(self, move))
            elif end != 'border':
                if end.color != self.color:
                    valid_moves.append(Move(self, move + 'x'))
                else:
                    valid_moves.append(Move(self, move + 'o'))

        return valid_moves

    @property
    def _score(self):
        score = self.points

        return score


class Rook(Piece):

    def __init__(self, color, position):
        super(Rook, self).__init__(color, 'Rook', position)
        self.points = 5

    @property
    def moves(self):
        if self.position is None:
            return []

        directions = ((1, 0), (-1, 0), (0, 1), (0, -1))
        valid_moves = []

        for direction in directions:
            for distance in range(1, 9):
                move = f'{self.file + (direction[0] * distance)}{self.rank + (direction[1] * distance)}'
                end = chess[move]
                if end is None:
                    valid_moves.append(Move(self, move))
                elif end == 'border':
                    break  # End of the line, check next direction
                else:
                    if end.color == self.color:
                        valid_moves.append(Move(self, move + 'o'))
                        break  # Can't jump over own color
                    elif end.color != self.color:
                        valid_moves.append(Move(self, move + 'x'))
                        break  # Can't move past opponent's piece
                    else:
                        print(f'Somehow you broke something in {self}')

        return valid_moves

    @property
    def _score(self):
        score = self.points
        length = len(self.moves)

        score += .05 * length

        return score


class Bishop(Piece):

    def __init__(self, color, position):
        super(Bishop, self).__init__(color, 'Bishop', position)
        self.points = 3

    @property
    def moves(self):
        if self.position is None:
            return []

        directions = ((1, 1), (1, -1), (-1, 1), (-1, -1))
        valid_moves = []

        for direction in directions:
            for distance in range(1, 9):
                move = f'{self.file + (direction[0] * distance)}{self.rank + (direction[1] * distance)}'
                end = chess[move]
                if end is None:
                    valid_moves.append(Move(self, move))
                elif end == 'border':
                    break  # End of the line, check next direction
                else:
                    if end.color == self.color:
                        valid_moves.append(Move(self, move + 'o'))
                        break  # Can't jump over own color
                    elif end.color != self.color:
                        valid_moves.append(Move(self, move + 'x'))
                        break  # Can't move past opponent's piece
                    else:
                        print(f'Somehow you broke something in {self}')

        return valid_moves

    @property
    def _score(self):
        score = self.points

        return score


class Queen(Piece):

    def __init__(self, color, position):
        super(Queen, self).__init__(color, 'Queen', position)
        self.points = 9

    @property
    def moves(self):
        if self.position is None:
            return []
        directions = ((1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1))
        valid_moves = []

        for direction in directions:
            for distance in range(1, 9):
                move = f'{self.file + (direction[0] * distance)}{self.rank + (direction[1] * distance)}'
                end = chess[move]
                if end is None:
                    valid_moves.append(Move(self, move))
                elif end == 'border':
                    break  # End of the line, check next direction
                else:
                    if end.color == self.color:
                        valid_moves.append(Move(self, move + 'o'))
                        break  # Can't jump over own color
                    elif end.color != self.color:
                        valid_moves.append(Move(self, move + 'x'))
                        break  # Can't move past opponent's piece
                    else:
                        print(f'Somehow you broke something in {self}')

        return valid_moves

    @property
    def _score(self):
        score = self.points

        return score


class King(Piece):

    def __init__(self, color, position):
        super(King, self).__init__(color, 'King', position)
        self.points = 15

    @property
    def moves(self):
        if self.position is None:
            return []
        directions = ((1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1))
        valid_moves = []

        for direction in directions:
            move = f'{self.file + direction[0]}{self.rank + direction[1]}'
            end = chess[move]
            if end is None:
                valid_moves.append(Move(self, move))
            elif end == 'border':
                continue
            else:
                if end.color == self.color:
                    valid_moves.append(Move(self, move + 'o'))
                elif end.color != self.color:
                    valid_moves.append(Move(self, move + 'x'))

                else:
                    print(f'Somehow you broke something in {self}')

        return valid_moves

    @property
    def score(self):
        length = len(self.moves)

        score = self.points
        for move in self.moves:
            if move in self.enemy.moves:
                score -= self.points / length

        if self.check:
            score -= 100

        return score


class Player:

    def __init__(self, color, pieces):
        self.color = color
        self.pieces = []
        self.king = None
        for piece in pieces:
            match = re.match(notation, piece)
            title = match.group('title')
            pos = match.group('pos')
            if title is None:
                self.pieces.append(Pawn(self.color, pos))
            else:
                if title in 'Rr':
                    self.pieces.append(Rook(self.color, pos))
                elif title in 'Nn':
                    self.pieces.append(Knight(self.color, pos))
                elif title in 'Bb':
                    self.pieces.append(Bishop(self.color, pos))
                elif title in 'Qq':
                    self.pieces.append(Queen(self.color, pos))
                elif title in 'Kk':
                    self.pieces.append(King(self.color, pos))
                    self.king = self.pieces[-1]

    def test(self, move):
        global chess

        start_score = self.score - self.enemy.score

        chess.move(move)
        moves = [move]

        score = self.score - self.enemy.score

        if self.enemy.king.check:
            if move.piece.check and not move.piece.covered:
                score -= 10
            else:
                score += 5

        if move.kind == 'cap':
            if move.cap.score <= move.cap.points:
                score += move.cap.points

        for piece in self.pieces:
            score += piece.score - piece.points

        moves.reverse()
        for move in moves:
            move.reverse()

        return score - start_score

    def best_move(self):
        best_moves = []
        best_score = -1000
        for move in self.moves:
            if move.kind == 'cover':
                continue
            score = self.test(move)
            if score > best_score:
                best_moves = [move]
                best_score = score
            elif score == best_score:
                best_moves += [move]

        best = choice(best_moves)
        return best

    @property
    def enemy(self):
        if self.color == 'White':
            return black
        elif self.color == 'Black':
            return white

    @property
    def moves(self):
        available_moves = []
        for piece in self.pieces:
            available_moves += piece.moves
        return available_moves

    @property
    def checks(self):
        checks = []
        for move in self.moves:
            if move.kind == 'cap':
                checks.append(move)

        return checks

    @property
    def covers(self):
        covering_moves = []
        for move in self.moves:
            if move.kind == 'cover':
                covering_moves += [move]

        return covering_moves

    @property
    def score(self):
        score = 0
        for piece in self.pieces:
            score += piece.points

        return score


chess = Board()
board = chess.board

if mode == 'play':
    whitePieces = ['a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2', 'Ra1', 'Nb1', 'Bc1', 'Qd1', 'Ke1', 'Bf1', 'Ng1',
                   'Rh1']
    blackPieces = ['a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7', 'Ra8', 'Nb8', 'Bc8', 'Qd8', 'Ke8', 'Bf8', 'Ng8',
                   'Rh8']

    white = Player('White', whitePieces)
    black = Player('Black', blackPieces)

    players = (white, black)
    for player in players:
        for piece_ in player.pieces:
            chess.add(piece_)

    print(chess)

    gameOn = True

    while gameOn:
        if white.king.check:
            print('White king in check!')
        white_move = white.best_move()
        print(f'White chooses {white_move}')
        chess.move(white_move)
        print(chess)
        if white.king.check:
            gameOn = False
            print('Black wins!')
            break

        if black.king.check:
            print('Black king in check!')
        print(f'AI recommends {black.best_move()}')
        chess.move(get_move(black))
        print(chess)
        if black.king.check:
            gameOn = False
            print('White wins!')

elif mode == 'watch':
    whitePieces = ['a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2', 'Ra1', 'Nb1', 'Bc1', 'Qd1', 'Ke1', 'Bf1', 'Ng1',
                   'Rh1']
    blackPieces = ['a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7', 'Ra8', 'Nb8', 'Bc8', 'Qd8', 'Ke8', 'Bf8', 'Ng8',
                   'Rh8']

    white = Player('White', whitePieces)
    black = Player('Black', blackPieces)

    players = (white, black)
    for player in players:
        for piece_ in player.pieces:
            chess.add(piece_)

    print(chess)

    gameOn = True
    count = 0
    while gameOn:
        if white.king.check:
            print('White king in check!')
        white_move = white.best_move()
        if white_move.kind == 'cap':
            count = 0
        else:
            count += 1

        print(f'White chooses {white_move}: {white.test(white_move)}')
        chess.move(white_move)

        print(chess)
        if white.king.check:
            gameOn = False
            print('Black wins!')
            break

        if black.king.check:
            print('Black king in check!')
        black_move = black.best_move()
        if black_move.kind == 'cap':
            count = 0
        else:
            count += 1

        print(f'Black chooses {black_move}: {black.test(black_move)}')
        chess.move(black_move)
        print(chess)
        if black.king.check:
            gameOn = False
            print('White wins!')

        if count > 25:
            gameOn = False
            print('Draw game!')

elif mode == 'test':
    def show():
        for player in players:
            print(player.score)


    whitePieces = ['ka1', 'g7']
    blackPieces = ['ka8', 'rc4']

    white = Player('White', whitePieces)
    black = Player('Black', blackPieces)

    players = (white, black)
    for player in players:
        for piece_ in player.pieces:
            chess.add(piece_)

    print(chess)

    show()
    chess.move(Move(black.pieces[1], 'rc3'))
    print(chess)

    show()
    chess.move(Move(black.pieces[1], 'rb3'))
    print(chess)

    show()
    print(white.test(Move(white.pieces[1], 'g8=Q')))
    chess.move(white.best_move())
    print(chess)

    chess.move(black.best_move())
    print(chess)

    chess.move(white.best_move())
    print(chess)

elif mode == 'custom':
    whitePieces = input("Enter the white pieces: ").split(' ')
    blackPieces = input("Enter the black pieces: ").split(' ')

    white = Player('White', whitePieces)
    black = Player('Black', blackPieces)

    players = (white, black)
    for player in players:
        for piece_ in player.pieces:
            chess.add(piece_)

    print(chess)

elif mode == 'random':
    whitePieces = [f'{choice(titles)}{choice(files)}{choice(ranks)}' for _ in range(numPieces)] + [
        f'k{choice(files)}{choice(ranks)}']
    blackPieces = [f'{choice(titles)}{choice(files)}{choice(ranks)}' for _ in range(numPieces)] + [
        f'k{choice(files)}{choice(ranks)}']

    white = Player('White', whitePieces)
    black = Player('Black', blackPieces)

    players = (white, black)
    for player in players:
        for piece_ in player.pieces:
            chess.add(piece_)

    print(chess)

elif mode == 'soloLearn':
    try:
        whitePieces = input("Enter the white pieces: ").split(' ')
        print(whitePieces)
        blackPieces = input("Enter the black pieces: ").split(' ')
        print(blackPieces)

        if(len(whitePieces) < 2 or len(blackPieces) < 2):
            raise EOFError  # hot fix to also handle blank input in normal environment
    except EOFError:
        print() # corrects missing endline when no pieces are input
        whitePieces = [f'{choice(titles)}{choice(files)}{choice(ranks)}' for _ in range(numPieces)] + [
            f'k{choice(files)}{choice(ranks)}']
        blackPieces = [f'{choice(titles)}{choice(files)}{choice(ranks)}' for _ in range(numPieces)] + [
            f'k{choice(files)}{choice(ranks)}']
        

    white = Player('White', whitePieces)
    if white.king is None:
        print("White king missing, creating one at default starting position")
        white.king = King('White', 'e1')
        white.pieces.append(white.king)

    black = Player('Black', blackPieces)
    if black.king is None:
        print("Black king missing, creating one at default starting position")
        black.king = King('Black', 'e8')
        black.pieces.append(black.king)

    players = (white, black)
    for player in players:
        for piece_ in player.pieces:
            chess.add(piece_)

    print(chess)
    for i in range(3):
        if white.king.check:
            print('White king in check!')
    
        white_move = white.best_move()
        print(f"White's best move is {white_move}")
        chess.move(white_move)
        print(chess)
    
        if black.king.check:
            print('Black king in check!')
    
        black_move = black.best_move()
        print(f"Black's best move is {black_move}")
        chess.move(black_move)
        print(chess)
