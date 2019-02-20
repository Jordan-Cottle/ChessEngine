import re
from abc import abstractmethod, ABC

from Board import File

notation = '(?P<title>[PpRrNnBbQqKk])?(?P<pos>[a-h][1-8])(?P<suffix>[x+#o0=])?'

class Move:
    def __init__(self, piece, note, board):
        self.piece = piece
        self.start = piece.position
        self.board = board

        match = re.match(notation, note)

        self.position = match.group('pos')
        suffix = match.group('suffix')

        if suffix is None:
            self.kind = 'move'
            self.suffix = ''

        elif suffix == 'x':
            self.cap = self.board[self.position]
            self.kind = 'cap'
            self.suffix = suffix

        elif suffix == 'o':
            self.kind = 'cover'
            self.covered = self.board[self.position]
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
            self.piece.player.pieces.remove(self.board[self.position])
            self.piece.player.pieces.append(self.piece)
            self.board.remove(self.board[self.position])
            self.board.add(self.piece)
            self.board.move(Move(self.piece, f'{self.start}', self.board))
        else:
            self.board.move(Move(self.piece, f'{self.start}', self.board))
            if self.kind == 'cap':
                self.board.add(self.cap)
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





class Piece(ABC):
    def __init__(self, player, role, position, board, points):
        self.player = player
        self.color = player.color
        self.role = role
        self.position = position
        self.board = board
        self.file = File(position[0])
        self.rank = int(position[1])
        self.start = position
        self.points = points

    @property
    def moved(self):
        if self.start == self.position:
            return False
        else:
            return True

    @property
    def enemy(self):
        return self.player.enemy

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
        points = self.points

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

    @property    
    @abstractmethod
    def moves(self):
        raise NotImplementedError

    def move(self, move):
        self.position = move.position
        self.file = File(move.position[0])
        self.rank = int(move.position[1])

    def capture(self):
        self.player.pieces.remove(self)

    def __str__(self):
        if self.role == 'Pawn':
            return f'{self.position}'
        else:
            return f'{self.title}{self.position}'

    def __repr__(self):
        return f'{self.color} {self.role} at {self.position}'


class Pawn(Piece):

    def __init__(self, player, position, board):
        super(Pawn, self).__init__(player, 'Pawn', position, board, 1)

    def promote(self):
        queen = Queen(self.color, self.position, self.board)
        self.board.remove(self)
        self.board.add(queen)
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

        if self.board[forward] is None:
            if (self.color == 'White' and self.rank == 7) or (self.color == 'Black' and self.rank == 2):
                moves.append(Move(self,forward + '=Q', self.board))
            else:
                moves.append(Move(self, forward, self.board))
        if not self.moved and (self.board[forward] is None and self.board[dash] is None):
            moves.append(Move(self, dash, self.board))

        diag = self.board[attack_r]
        if diag is not None and diag != 'border':
            if diag.color != self.color:
                moves.append(Move(self, attack_r + 'x', self.board))
            else:
                moves.append(Move(self, attack_r + 'o', self.board))

        diag = self.board[attack_l]
        if diag is not None and diag != 'border':
            if diag.color != self.color:
                moves.append(Move(self, attack_l + 'x', self.board))
            else:
                moves.append(Move(self, attack_l + 'o', self.board))

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

    def __init__(self, color, position, board):
        super(Knight, self).__init__(color, 'Knight', position, board, 3)

    @property
    def moves(self):
        if self.position is None:
            return []

        moves = [(2, 1), (-2, 1), (2, -1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        valid_moves = []
        for move in moves:
            move = f'{self.file + move[0]}{self.rank + move[1]}'
            end = self.board[move]
            if end is None:
                valid_moves.append(Move(self, move, self.board))
            elif end != 'border':
                if end.color != self.color:
                    valid_moves.append(Move(self, move + 'x', self.board))
                else:
                    valid_moves.append(Move(self, move + 'o', self.board))

        return valid_moves

    @property
    def _score(self):
        score = self.points

        return score


class Rook(Piece):

    def __init__(self, color, position, board):
        super(Rook, self).__init__(color, 'Rook', position, board, 5)

    @property
    def moves(self):
        if self.position is None:
            return []

        directions = ((1, 0), (-1, 0), (0, 1), (0, -1))
        valid_moves = []

        for direction in directions:
            for distance in range(1, 9):
                move = f'{self.file + (direction[0] * distance)}{self.rank + (direction[1] * distance)}'
                end = self.board[move]
                if end is None:
                    valid_moves.append(Move(self, move, self.board))
                elif end == 'border':
                    break  # End of the line, check next direction
                else:
                    if end.color == self.color:
                        valid_moves.append(Move(self, move + 'o', self.board))
                        break  # Can't jump over own color
                    elif end.color != self.color:
                        valid_moves.append(Move(self, move + 'x', self.board))
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

    def __init__(self, color, position, board):
        super(Bishop, self).__init__(color, 'Bishop', position, board, 3)

    @property
    def moves(self):
        if self.position is None:
            return []

        directions = ((1, 1), (1, -1), (-1, 1), (-1, -1))
        valid_moves = []

        for direction in directions:
            for distance in range(1, 9):
                move = f'{self.file + (direction[0] * distance)}{self.rank + (direction[1] * distance)}'
                end = self.board[move]
                if end is None:
                    valid_moves.append(Move(self, move, self.board))
                elif end == 'border':
                    break  # End of the line, check next direction
                else:
                    if end.color == self.color:
                        valid_moves.append(Move(self, move + 'o', self.board))
                        break  # Can't jump over own color
                    elif end.color != self.color:
                        valid_moves.append(Move(self, move + 'x', self.board))
                        break  # Can't move past opponent's piece
                    else:
                        print(f'Somehow you broke something in {self}')

        return valid_moves

    @property
    def _score(self):
        score = self.points

        return score


class Queen(Piece):

    def __init__(self, color, position, board):
        super(Queen, self).__init__(color, 'Queen', position, board, 9)

    @property
    def moves(self):
        if self.position is None:
            return []
        directions = ((1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1))
        valid_moves = []

        for direction in directions:
            for distance in range(1, 9):
                move = f'{self.file + (direction[0] * distance)}{self.rank + (direction[1] * distance)}'
                end = self.board[move]
                if end is None:
                    valid_moves.append(Move(self, move, self.board))
                elif end == 'border':
                    break  # End of the line, check next direction
                else:
                    if end.color == self.color:
                        valid_moves.append(Move(self, move + 'o', self.board))
                        break  # Can't jump over own color
                    elif end.color != self.color:
                        valid_moves.append(Move(self, move + 'x', self.board))
                        break  # Can't move past opponent's piece
                    else:
                        print(f'Somehow you broke something in {self}')

        return valid_moves

    @property
    def _score(self):
        score = self.points

        return score


class King(Piece):

    def __init__(self, color, position, board):
        super(King, self).__init__(color, 'King', position, board, 15)

    @property
    def moves(self):
        if self.position is None:
            return []
        directions = ((1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1))
        valid_moves = []

        for direction in directions:
            move = f'{self.file + direction[0]}{self.rank + direction[1]}'
            end = self.board[move]
            if end is None:
                valid_moves.append(Move(self, move, self.board))
            elif end == 'border':
                continue
            else:
                if end.color == self.color:
                    valid_moves.append(Move(self, move + 'o', self.board))
                elif end.color != self.color:
                    valid_moves.append(Move(self, move + 'x', self.board))

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