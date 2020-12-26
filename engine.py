"""
This class stores all the information about the current gamestate. It will also determine 
all the valid moves for the current state + MoveLog
"""
class GameState(object):
    """docstring for GameState"""
    def __init__(self):
        self.board = [
        ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
        ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
        ["--", "--", "--", "--", "--", "--", "--", "--"],
        ["--", "--", "--", "--", "--", "--", "--", "--"],
        ["--", "--", "--", "--", "--", "--", "--", "--"],
        ["--", "--", "--", "--", "--", "--", "--", "--"],
        ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
        ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveGeneratingFunctions = {
                                        "p": self.generate_pawn_moves, 
                                        "R": self.generate_rook_moves,
                                        "N": self.generate_knight_moves,
                                        "B": self.generate_bishop_moves,
                                        "Q": self.generate_queen_moves,
                                        "K": self.generate_king_moves
                                        }
        self.directions = {'orth': [(1, 0), (0, 1), (-1, 0), (0, -1)], 'diag': [(1, 1), (-1, 1), (1, -1), (-1, -1)]} # all directions
        self.whiteToMove = True #s tore whos turn it is
        self.moveLog = [] # store the moves. Also needs to store all the captured and moved pieces.

        self.enpassantSq = ()
        
        # castling rights
        self.wks = True 
        self.wqs = True
        self.bks = True
        self.bqs = True

        self.castleRightsLog = [[self.wks, self.wqs, self.bks, self.bqs]]

        self.whitheKingSq = [7, 4] # store the position of the white King 
        self.blackKingSq = [0, 4] # store the position of the black King

        self.checkmate = False
        self.stalemate = False


    def make_move(self, move):
        # Use this to only execute the move
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.movedPiece
        self.whiteToMove = not self.whiteToMove

        if move.movedPiece == "wK":
            self.whitheKingSq = [move.endRow, move.endCol]
        if move.movedPiece== "bK":
            self.blackKingSq = [move.endRow, move.endCol]

        if move.is_promotion:
            self.board[move.endRow][move.endCol] = move.movedPiece[0] + "Q"

        if move.movedPiece[1] == "p" and abs(move.startRow - move.endRow) == 2:
            self.enpassantSq = ((move.endRow + move.startRow)//2, move.endCol)
        else:
            self.enpassantSq = ()

        if move.is_enpassant: 
            self.board[move.startRow][move.endCol] = "--"
            # print(move.get_chess_notation())
        if move.is_castle:
            if move.endCol - move.startCol == 2: # kingside
                self.board[move.startRow][move.endCol-1] = self.board[move.startRow][7]
                self.board[move.startRow][7] = "--"
            else:
                self.board[move.startRow][move.endCol+1] = self.board[move.startRow][0]
                self.board[move.startRow][0] = "--"


        # print(self.castleRightsLog)
        self.update_castling_rights(move)
        self.castleRightsLog.append([self.wks, self.wqs, self.bks, self.bqs])


        self.moveLog.append(move)

    def undo_move(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.movedPiece
            self.board[move.endRow][move.endCol] = move.capturedPiece
            self.whiteToMove = not self.whiteToMove

            if move.movedPiece == "wK":
                self.whitheKingSq = [move.startRow, move.startCol]
            elif move.movedPiece == "bK":
                self.blackKingSq = [move.startRow, move.startCol]
            if move.is_enpassant: 
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.capturedPiece
                self.enpassantSq = (move.endRow, move.endCol)
            if move.movedPiece[1] == "p" and abs(move.startRow - move.endRow) == 2:
                self.enpassantSq = ()
            if move.is_castle:
                if move.endCol - move.startCol == 2: # kingside
                    self.board[move.startRow][7] = self.board[move.startRow][move.endCol-1]
                    self.board[move.startRow][move.endCol-1] = "--"
                else: # queenside
                    self.board[move.startRow][0] = self.board[move.startRow][move.endCol+1]
                    self.board[move.startRow][move.endCol+1] = "--"

            self.castleRightsLog.pop()
            self.wks, self.wqs, self.bks, self.bqs = self.castleRightsLog[-1]

    def update_castling_rights(self, move):
        if move.movedPiece == 'wK':
            self.wks = False
            self.wqs = False 
        elif move.movedPiece == 'bK':
            self.bks = False
            self.bqs = False 
        elif move.movedPiece == 'wR':
            if move.startRow == 7:
                if move.startCol == 7:
                    self.wks = False
                elif move.startCol == 0:
                    self.wqs = False
        elif move.movedPiece == 'bR':
            if move.startRow == 0:
                if move.startCol == 7:
                    self.bks = False
                elif move.startCol == 0:
                    self.bqs = False

    def in_check(self):
        if self.whiteToMove:
            return self.square_under_attack(self.whitheKingSq[0], self.whitheKingSq[1])
        elif not self.whiteToMove:
            return self.square_under_attack(self.blackKingSq[0], self.blackKingSq[1])

    def square_under_attack(self, row, col):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.get_all_possible_moves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == row and move.endCol == col:
                return True
        return False

    def get_all_possible_moves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board)):
                color = self.board[row][col][0]
                if (self.whiteToMove and color == "w") or (not self.whiteToMove and color == "b"):
                    piece = self.board[row][col][1]
                    '''
                    We check for all the pieces and generate its move according to its position
                    '''
                    self.moveGeneratingFunctions[piece](row, col, moves)
        return moves

    def get_all_valid_moves(self):
        tempEnpassantSq = self.enpassantSq
        tempCastleRights = [self.wks, self.wqs, self.bks, self.bqs]
        validMoves = self.get_all_possible_moves()
        if self.whiteToMove:
            castleMoves = self.get_castling_moves(self.whitheKingSq[0], self.whitheKingSq[1], validMoves)
        else:
            castleMoves = self.get_castling_moves(self.blackKingSq[0], self.blackKingSq[1], validMoves)
        for i in range(len(validMoves)-1, -1, -1):
            self.make_move(validMoves[i])
            self.whiteToMove = not self.whiteToMove
            if self.in_check():
                validMoves.remove(validMoves[i])
            self.whiteToMove = not self.whiteToMove
            self.undo_move()
        if len(validMoves) == 0:
            if self.in_check():
                self.checkmate = True
                print('CHECKMATE')
            else:
                self.stalemate = True
                print('DRAW')
        else:
            self.checkmate = False
            self.stalemate = False
        self.enpassantSq = tempEnpassantSq
        self.wks, self.wqs, self.bks, self.bqs = tempCastleRights
        return validMoves

    def generate_pawn_moves(self, row, col, moves):
        # move by using (0, 1), (1, 0) ...
        if self.whiteToMove:
            if self.board[row - 1][col] == "--": # one square move
                moves.append(Move((row, col), (row - 1, col), self.board))
                if row == 6 and self.board[row - 2][col] == "--": # two square move
                    moves.append(Move((row, col), (row - 2, col), self.board))

            if col - 1 >= 0: # capture to the left
                if self.board[row - 1][col - 1][0] == "b":
                    moves.append(Move((row, col), (row - 1, col - 1), self.board)) 
                # enpassant move
                elif self.enpassantSq == (row-1, col-1):
                    moves.append(Move((row, col), (row - 1, col - 1), self.board, is_enpassant=True)) 


            if col + 1 <= 7: # capture to the right
                if self.board[row - 1][col + 1][0] == "b":
                    moves.append(Move((row, col), (row - 1, col + 1), self.board)) 
                elif self.enpassantSq == (row-1, col+1):
                    moves.append(Move((row, col), (row - 1, col + 1), self.board, is_enpassant=True)) 


        elif not self.whiteToMove:
            if self.board[row + 1][col] == "--": # one square move
                moves.append(Move((row, col), (row + 1, col), self.board))
                if row == 1 and self.board[row + 2][col] == "--": # two square move
                    moves.append(Move((row, col), (row + 2, col), self.board))  

            if col - 1 >= 0:
                if self.board[row + 1][col - 1][0] == "w":
                    moves.append(Move((row, col), (row + 1, col - 1), self.board)) 
                elif self.enpassantSq == (row+1, col-1):
                    moves.append(Move((row, col), (row + 1, col - 1), self.board, is_enpassant=True))  

            if col + 1 <= 7:
                if self.board[row + 1][col + 1][0] == "w":
                    moves.append(Move((row, col), (row + 1, col + 1), self.board)) 
                elif self.enpassantSq == (row+1, col+1):
                    moves.append(Move((row, col), (row + 1, col + 1), self.board, is_enpassant=True)) 

    def generate_rook_moves(self, row, col, moves):
        if self.whiteToMove:
            for d in self.directions['orth']:
                endSq = tuple(map(lambda x, y: x + y, (row, col), d))
                while 0 <= endSq[0] <= 7 and 0 <= endSq[1] <= 7 and self.board[endSq[0]][endSq[1]][0] != "w":
                    if self.board[endSq[0]][endSq[1]] == "--":
                        moves.append(Move((row, col), endSq, self.board))
                    if self.board[endSq[0]][endSq[1]][0] == "b":
                        moves.append(Move((row, col), endSq, self.board))
                        break
                    endSq = tuple(map(lambda x, y: x + y, endSq, d))

        if not self.whiteToMove:
            for d in self.directions['orth']:
                endSq = tuple(map(lambda x, y: x + y, (row, col), d))
                while 0 <= endSq[0] <= 7 and 0 <= endSq[1] <= 7 and self.board[endSq[0]][endSq[1]][0] != "b":
                    if self.board[endSq[0]][endSq[1]] == "--":
                        moves.append(Move((row, col), endSq, self.board))
                    if self.board[endSq[0]][endSq[1]][0] == "w":
                        moves.append(Move((row, col), endSq, self.board))
                        break
                    endSq = tuple(map(lambda x, y: x + y, endSq, d))


    def generate_knight_moves(self, row, col, moves):
        '''
        We have a maximum of eight squares we can end up in using the knight
        '''
        SqOne = [row - 2, col - 1]
        SqTwo = [row - 2, col + 1]
        SqThree = [row - 1, col - 2]
        SqFour= [row - 1, col + 2]
        SqFive = [row + 2, col - 1]
        SqSix = [row + 2, col + 1]
        SqSeven = [row + 1, col - 2]
        SqEight = [row + 1, col + 2]
        Squares = [SqOne, SqTwo, SqThree, SqFour, SqFive, SqSix, SqSeven, SqEight]
        for Sq in Squares.copy():
            if (Sq[0]<0 or Sq[0]>7):
                Squares.remove(Sq)
            elif (Sq[1]<0 or Sq[1]>7):
                Squares.remove(Sq)
        for Sq in Squares:
            if self.whiteToMove and (self.board[Sq[0]][Sq[1]] == "--" or self.board[Sq[0]][Sq[1]][0] == "b"):
                moves.append(Move((row, col), (Sq[0], Sq[1]), self.board))
            elif not self.whiteToMove and (self.board[Sq[0]][Sq[1]] == "--" or self.board[Sq[0]][Sq[1]][0] == "w"):
                moves.append(Move((row, col), (Sq[0], Sq[1]), self.board))               

    def generate_bishop_moves(self, row, col, moves):
        if self.whiteToMove:
            for d in self.directions['diag']:
                endSq = tuple(map(lambda x, y: x + y, (row, col), d))
                while 0 <= endSq[0] <= 7 and 0 <= endSq[1] <= 7 and self.board[endSq[0]][endSq[1]][0] != "w":
                    if self.board[endSq[0]][endSq[1]] == "--":
                        moves.append(Move((row, col), endSq, self.board))
                    if self.board[endSq[0]][endSq[1]][0] == "b":
                        moves.append(Move((row, col), endSq, self.board))
                        break
                    endSq = tuple(map(lambda x, y: x + y, endSq, d))
        if not self.whiteToMove:
            for d in self.directions['diag']:
                endSq = tuple(map(lambda x, y: x + y, (row, col), d))
                while 0 <= endSq[0] <= 7 and 0 <= endSq[1] <= 7 and self.board[endSq[0]][endSq[1]][0] != "b":
                    if self.board[endSq[0]][endSq[1]] == "--":
                        moves.append(Move((row, col), endSq, self.board))
                    if self.board[endSq[0]][endSq[1]][0] == "w":
                        moves.append(Move((row, col), endSq, self.board))
                        break
                    endSq = tuple(map(lambda x, y: x + y, endSq, d))
       
    def generate_queen_moves(self, row, col, moves):
        if self.whiteToMove:
            for d in self.directions['diag'] + self.directions['orth']:
                endSq = tuple(map(lambda x, y: x + y, (row, col), d))
                while 0 <= endSq[0] <= 7 and 0 <= endSq[1] <= 7 and self.board[endSq[0]][endSq[1]][0] != "w":
                    if self.board[endSq[0]][endSq[1]] == "--":
                        moves.append(Move((row, col), endSq, self.board))
                    if self.board[endSq[0]][endSq[1]][0] == "b":
                        moves.append(Move((row, col), endSq, self.board))
                        break
                    endSq = tuple(map(lambda x, y: x + y, endSq, d))
        if not self.whiteToMove:
            for d in self.directions['diag'] + self.directions['orth']:
                endSq = tuple(map(lambda x, y: x + y, (row, col), d))
                while 0 <= endSq[0] <= 7 and 0 <= endSq[1] <= 7 and self.board[endSq[0]][endSq[1]][0] != "b":
                    if self.board[endSq[0]][endSq[1]] == "--":
                        moves.append(Move((row, col), endSq, self.board))
                    if self.board[endSq[0]][endSq[1]][0] == "w":
                        moves.append(Move((row, col), endSq, self.board))
                        break
                    endSq = tuple(map(lambda x, y: x + y, endSq, d))

    def generate_king_moves(self, row, col, moves):
        if self.whiteToMove:
            for d in self.directions['diag'] + self.directions['orth']:
                endSq = tuple(map(lambda x, y: x + y, (row, col), d))
                if 0 <= endSq[0] <= 7 and 0 <= endSq[1] <= 7 and self.board[endSq[0]][endSq[1]][0] != "w":
                    if self.board[endSq[0]][endSq[1]] == "--":
                        moves.append(Move((row, col), endSq, self.board))
                    if self.board[endSq[0]][endSq[1]][0] == "b":
                        moves.append(Move((row, col), endSq, self.board))
            # castling
            # if self.wks and not self.in_check():
            #   if not self.square_under_attack(7, 5) and not self.square_under_attack(7, 6):
            #       moves.append(Move((row, col), (row, col+2), self.board, is_castle=True))
            # if self.wqs and not self.in_check():
            #   if not self.square_under_attack(7, 1) and not self.square_under_attack(7, 2) and not self.square_under_attack(7, 3):
            #       moves.append(Move((row, col), (row, col-2), self.board, is_castle=True))

        if not self.whiteToMove:
            for d in self.directions['diag'] + self.directions['orth']:
                endSq = tuple(map(lambda x, y: x + y, (row, col), d))
                if 0 <= endSq[0] <= 7 and 0 <= endSq[1] <= 7 and self.board[endSq[0]][endSq[1]][0] != "b":
                    if self.board[endSq[0]][endSq[1]] == "--":
                        moves.append(Move((row, col), endSq, self.board))
                    if self.board[endSq[0]][endSq[1]][0] == "w":
                        moves.append(Move((row, col), endSq, self.board))   

    def get_castling_moves(self, r, c, moves):
        if self.square_under_attack(r, c):
            return
        if (self.whiteToMove and self.wks) or (not self.whiteToMove and self.bks):
            self.get_king_side_castling_moves(r, c, moves)
        if (self.whiteToMove and self.wqs) or (not self.whiteToMove and self.bqs):
            self.get_queen_side_castling_moves(r, c, moves)

    def get_king_side_castling_moves(self, r, c, moves):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if not self.square_under_attack(r, c+1) and not self.square_under_attack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, is_castle=True))

    def get_queen_side_castling_moves(self, r, c, moves):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--":
            if not self.square_under_attack(r, c-1) and not self.square_under_attack(r, c-2) and not self.square_under_attack(r, c-3):
                moves.append(Move((r, c), (r, c-2), self.board, is_castle=True))


    # def is_castling_possible():
    #   if self.wks:
    #       if self.board[7][5] == "--" and self.board[7][6] == "--":
    #           if not self.square_under_attack(7, 4) and not self.square_under_attack(7, 5) and not self.square_under_attack(7, 6):
    #               return True
    #   elif self.wqs:  
    #       if self.board[7][1] == "--" and self.board[7][2] == "--" and self.board[7][3] == "--":
    #           if not self.square_under_attack(7, 1) and not self.square_under_attack(7, 2) and not self.square_under_attack(7, 3) and not self.square_under_attack(7, 4):
    #               return True

class Move(object):
    """docstring for Move"""
    # map keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                    "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                    "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    # pieceToPoints = {"p": 1, "R": 5, "N": 3, "B": 3, "Q": 9, "K": 4}

    def __init__(self, startSQ, endSQ, board, is_promotion=False, is_enpassant=False, is_castle=False):
        self.pieceToPoints = {"p": 1, "R": 5, "N": 3, "B": 3, "Q": 9, "K": 4}
        self.startRow = startSQ[0]
        self.startCol = startSQ[1]
        self.endRow = endSQ[0]
        self.endCol = endSQ[1]
        self.movedPiece = board[self.startRow][self.startCol]
        self.capturedPiece = board[self.endRow][self.endCol] # this becomes empty if we do an enpassant move
        self.moveId = self.startRow * 1000 + self.startCol * 100 +\
                    self.endRow * 10 + self.endCol * 1

        self.is_promotion = is_promotion
        self.is_promotion = (self.movedPiece[1] == "p" and (self.endRow == 0 or self.endRow == 7))

        self.is_enpassant = is_enpassant
        if self.is_enpassant:
            self.capturedPiece = "bp" if self.movedPiece == "wp" else "wp" 

        self.is_castle = is_castle
            

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveId == other.moveId
        return False

    def get_chess_notation(self): # prototype
        return self.get_rank_file(self.startRow, self.startCol) + self.get_rank_file(self.endRow, self.endCol)

    def get_rank_file(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]


                        




        
