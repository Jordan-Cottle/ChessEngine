import re
from Pieces import Pawn, Rook, Knight, Bishop, Queen, King
from random import choice

notation = '(?P<title>[PpRrNnBbQqKk])?(?P<pos>[a-h][1-8])(?P<suffix>[x+#o0=])?'

class Player:

    def __init__(self, color, pieces, board, enemy = None):
        self.color = color
        self.board = board
        self.enemy = enemy

        self.king = None
        self.pieces = []
        for piece in pieces:
            match = re.match(notation, piece)
            title = match.group('title')
            pos = match.group('pos')
            if title is None:
                self.pieces.append(Pawn(self, pos, board))
            else:
                if title in 'Rr':
                    self.pieces.append(Rook(self, pos, board))
                elif title in 'Nn':
                    self.pieces.append(Knight(self, pos, board))
                elif title in 'Bb':
                    self.pieces.append(Bishop(self, pos, board))
                elif title in 'Qq':
                    self.pieces.append(Queen(self, pos, board))
                elif title in 'Kk':
                    self.pieces.append(King(self, pos, board))
                    self.king = self.pieces[-1]

    def test(self, move):
        start_score = self.score - self.enemy.score

        self.board.move(move)
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