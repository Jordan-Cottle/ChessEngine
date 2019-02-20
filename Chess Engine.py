import re
from random import choice
from Board import Board
from Player import Player
from Pieces import Move, King


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

    move = Move(piece, input(f'Enter the position you would like to move {piece} to: '), player.board)
    while move not in piece.moves:
        print('Invalid Move')
        print(piece.moved)
        print(f'{piece} can move to {piece.moves}')
        move = Move(piece, input(f'Enter the position you would like to move {piece} to: '), player.board)

    return move


chess = Board()

if mode == 'play':
    whitePieces = ['a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2', 'Ra1', 'Nb1', 'Bc1', 'Qd1', 'Ke1', 'Bf1', 'Ng1',
                   'Rh1']
    blackPieces = ['a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7', 'Ra8', 'Nb8', 'Bc8', 'Qd8', 'Ke8', 'Bf8', 'Ng8',
                   'Rh8']

    white = Player('White', whitePieces, chess)
    black = Player('Black', blackPieces, chess, white)

    #manually set white's enemy since black didn't exist when white was created
    white.enemy = black

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

    white = Player('White', whitePieces, chess)
    black = Player('Black', blackPieces, chess, white)

    #manually set white's enemy since black didn't exist when white was created
    white.enemy = black

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
    def showScore():
        for player in players:
            print(player.score)


    whitePieces = ['ka1', 'g7']
    blackPieces = ['ka8', 'rc4']

    white = Player('White', whitePieces, chess)
    black = Player('Black', blackPieces, chess, white)

    #manually set white's enemy since black didn't exist when white was created
    white.enemy = black

    players = (white, black)
    for player in players:
        for piece_ in player.pieces:
            chess.add(piece_)

    print(chess)

    showScore()
    chess.move(Move(black.pieces[1], 'rc3', chess))
    print(chess)

    showScore()
    chess.move(Move(black.pieces[1], 'rb3', chess))
    print(chess)

    showScore()
    print(white.test(Move(white.pieces[1], 'g8=Q', chess)))
    chess.move(white.best_move())
    print(chess)

    chess.move(black.best_move())
    print(chess)

    chess.move(white.best_move())
    print(chess)

elif mode == 'custom':
    whitePieces = input("Enter the white pieces: ").split(' ')
    blackPieces = input("Enter the black pieces: ").split(' ')

    white = Player('White', whitePieces, chess)
    black = Player('Black', blackPieces, chess, white)

    #manually set white's enemy since black didn't exist when white was created
    white.enemy = black

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

    white = Player('White', whitePieces, chess)
    black = Player('Black', blackPieces, chess, white)

    #manually set white's enemy since black didn't exist when white was created
    white.enemy = black

    players = (white, black)
    for player in players:
        for piece_ in player.pieces:
            chess.add(piece_)

    print(chess)

elif mode == 'soloLearn':  #run a time-sensitive demo example, with automatically generated input if none is given
    try:
        whitePieces = input("Enter the white pieces: ").split(' ')
        print(whitePieces)
        blackPieces = input("Enter the black pieces: ").split(' ')
        print(blackPieces)
    except EOFError:
        print() # corrects missing endline when no pieces are input
        whitePieces = [f'{choice(titles)}{choice(files)}{choice(ranks)}' for _ in range(numPieces)] + [
            f'k{choice(files)}{choice(ranks)}']
        blackPieces = [f'{choice(titles)}{choice(files)}{choice(ranks)}' for _ in range(numPieces)] + [
            f'k{choice(files)}{choice(ranks)}']
        

    white = Player('White', whitePieces, chess)
    if white.king is None:
        print("White king missing, creating one at default starting position")
        white.king = King('White', 'e1', white.board)
        white.pieces.append(white.king)

    black = Player('Black', blackPieces, chess, white)
    if black.king is None:
        print("Black king missing, creating one at default starting position")
        black.king = King('Black', 'e8', black.board)
        black.pieces.append(black.king)

    #manually set white's enemy since black didn't exist when white was created
    white.enemy = black
    
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
