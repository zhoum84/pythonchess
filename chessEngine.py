# Runs the chess game, stores the info
class GameState():
    def __init__(self):
        self.board=[
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.move_functions = {'p' : self.get_pawn_moves, 'R' : self.get_rook_moves, 'N' : self.get_knight_moves, 
                               'B' : self.get_bishop_moves, 'Q' : self.get_queen_moves, 'K' : self.get_king_moves
                               }
        self.white_to_move = True
        self.move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.in_check = False
        self.pins = []
        self.checks = []
        self.enpassant = () #square where enpassant can occur


    def make_move(self, move):
        self.board[move.start_row][move.start_column] = '--'
        self.board[move.end_row][move.end_column] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        if move.piece_moved == "wK":
            self.white_king_location = (move.end_row, move.end_column)
        elif move.piece_moved == "bK":
            self.black_king_location = (move.end_row, move.end_column)
        
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_column] = move.piece_moved[0] + 'Q'
        elif move.is_enpassant:
            self.board[move.start_row][move.end_column] = "--"
        
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
            self.enpassant = ((move.start_row + move.end_row)//2, (move.end_column + move.start_column)//2)
        else:
            self.enpassant = ()

                
    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_column] = move.piece_moved
            self.board[move.end_row][move.end_column] = move.piece_captured
            self.white_to_move = not self.white_to_move
            if move.piece_moved == "wK":
                self.white_king_location = (move.start_row, move.start_column)
            elif move.piece_moved == "bK":
                self.black_king_location = (move.start_row, move.start_column)

            if move.is_enpassant:
                self.board[move.end_row][move.end_column] = '--'
                self.board[move.start_row][move.end_column] = move.piece_captured
                self.enpassant = (move.end_row, move.end_column)
            if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
                self.enpassant = ()

    # considers check
    def get_valid_moves(self):
        temp_enpassant = self.enpassant
        moves = []
        self.in_check, self.pins, self.checks = self.check_for_pins_and_checks()

        if self.white_to_move:
            king_row = self.white_king_location[0]
            king_col = self.white_king_location[1]
        else:
            king_row = self.black_king_location[0]
            king_col = self.black_king_location[1]

        if self.in_check: 
            if len(self.checks) == 1:
                moves = self.get_possible_moves()
                check = self.checks[0]
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col]
                valid_squares = []
                if piece_checking[1] == 'N':
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i)
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and check_col:
                            break
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].piece_moved[1] != 'K':
                        if not (moves[i].end_row, moves[i].end_column) in valid_squares:
                            moves.remove(moves[i])
            else:
                self.get_king_moves(king_row, king_col, moves)
        else:
            moves = self.get_possible_moves()
        
        #saves the enpassant
        self.enpassant = temp_enpassant 
        return moves

    def check_for_pins_and_checks(self):
        pins = []
        checks = []
        in_check = False
        if self.white_to_move:
            enemy_color = 'b'
            ally_color = 'w'
            start_row = self.white_king_location[0]
            start_column = self.white_king_location[1]
        else:
            enemy_color = 'w'
            ally_color = 'b'
            start_row = self.black_king_location[0]
            start_column = self.black_king_location[1]
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = ()
            for i in range(1, 8):
                end_row = start_row + d[0] * i
                end_col = start_column + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] == 'K':
                        if possible_pin == ():
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else:
                            break
                    elif end_piece[0] == enemy_color:
                        type = end_piece[1]
                        if (0 <= j <= 3 and type == 'R') \
                            or (4 <= j <= 7 and type == 'B') \
                            or (i == 1 and type == 'p' and ((enemy_color == 'w' and 6 <= j <= 7) or (enemy_color == 'b' and 4 <= j <= 5)))\
                            or (type == 'Q') or (i == 1 and type == 'K'):
                            if possible_pin == ():
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else:
                                pins.append(possible_pin)
                                break
                        else:
                            break
        knight_moves = ((-1, 2), (2, -1), (1, 2), (2, 1), (-1, -2), (-2, 1), (1, -2), (-2, -1))
        for moves in knight_moves:
            end_row = start_row + moves[0]
            end_col = start_column + moves[1]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == "N":  # enemy knight attacking a king
                    in_check = True
                    checks.append((end_row, end_col, moves[0], moves[1]))
        return in_check, pins, checks


        
    # does not consider check
    def get_possible_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn =='w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves)
        return moves

    def get_pawn_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()

        for i in range(len(self.pins) -1, -1 , -1):
            if self.pins[i][0] == r and self.pins[i][1] ==  c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.white_to_move: 
            if self.board[r - 1][c] == "--":
                if not piece_pinned or pin_direction == (-1, 0):
                    moves.append(Move((r, c), (r - 1, c), self.board))
                    if r == 6 and self.board[r-2][c] == "--":
                        moves.append(Move((r, c), (r-2, c), self.board)) 
           
            if c - 1 >= 0:
                if self.board[r-1][c-1][0] == 'b':
                    if not piece_pinned or pin_direction == (-1, -1):
                        moves.append(Move((r, c), (r-1, c-1), self.board)) 
                elif (r - 1, c - 1) == self.enpassant:
                    moves.append(Move((r, c), (r-1, c-1), self.board, enpassant_possible = True)) 

            if c + 1 <= 7:
                if self.board[r-1][c+1][0] == 'b':
                    if not piece_pinned or pin_direction == (-1, 1):
                        moves.append(Move((r, c), (r - 1, c + 1), self.board)) 
                elif (r - 1, c + 1) == self.enpassant:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, enpassant_possible = True)) 

        else: 
            if self.board[r + 1][c] == "--":
                if not piece_pinned or pin_direction == (1, 0):
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    if r == 1 and self.board[r + 2][c] == "--":
                        moves.append(Move((r, c), (r + 2, c), self.board)) 
          
            if c - 1 >= 0:
                if self.board[r+1][c-1][0] == 'w':
                    if not piece_pinned or pin_direction == (1, -1):
                        moves.append(Move((r, c), (r + 1, c - 1), self.board)) 
                elif (r + 1, c - 1) == self.enpassant:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, enpassant_possible = True)) 

            if c + 1 <= 7:
                if self.board[r+1][c+1][0] == 'w':
                    if not piece_pinned or pin_direction == (1, 1):
                        moves.append(Move((r, c), (r + 1, c + 1), self.board)) 
                elif (r + 1, c + 1) == self.enpassant:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, enpassant_possible = True)) 



    def get_rook_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = 'b' if self.white_to_move else 'w'
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break

        for d in directions: 
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break
                        else:
                            break
                else:
                    break
    
    def get_knight_moves(self, r, c, moves):
        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break
        
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        enemy_color = 'b' if self.white_to_move else 'w'
        for m in knight_moves: 
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if(end_piece[0] =='-' or end_piece[0] == enemy_color):
                        moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_bishop_moves(self, r, c, moves):

        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break
                        else:
                            break 
                else:
                    break


    def get_queen_moves(self, r, c, moves):
        self.get_bishop_moves(r, c, moves)
        self.get_rook_moves(r, c, moves)
    
    def get_king_moves(self, r, c, moves):
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        enemy_color = 'b' if self.white_to_move else 'w'
        for i in range(8):
            end_row = r + row_moves[i]
            end_col = c + col_moves[i]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if(end_piece[0] =='-' or end_piece[0] == enemy_color):
                    if enemy_color == 'b':
                        self.white_king_location = (end_row, end_col)
                    else:
                        self.black_king_location = (end_row, end_col)
                    in_check, pins, checks = self.check_for_pins_and_checks()
                    if not in_check:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    if enemy_color == 'b':
                        self.white_king_location = (r, c)
                    else:
                        self.black_king_location = (r, c)

class Move():

    ranks_to_rows = {"1" : 7, "2" : 6, "3" : 5, "4" : 4,
                     "5" : 3, "6" : 2, "7" : 1, "8" : 0}
    rows_to_ranks = {v : k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a" : 0, "b" : 1, "c" : 2, "d" : 3,
                     "e" : 4, "f" : 5, "g" : 6, "h" : 7}
    cols_to_files = {v : k for k, v in files_to_cols.items()} 

    def __init__(self, start, end, board, enpassant_possible = False):
        self.start_row = start[0]
        self.start_column = start[1]
        self.end_row = end[0]
        self.end_column = end[1]
        self.piece_moved = board[self.start_row][self.start_column]
        self.piece_captured = board[self.end_row][self.end_column]
        
        self.is_pawn_promotion = (self.piece_moved == "wp" and self.end_row == 0) or (self.piece_moved == "bp" and self.end_row == 7)

        self.is_enpassant = enpassant_possible

        if self.is_enpassant:
            self.piece_captured = 'wp' if self.piece_moved == 'bp' else 'bp'

        self.move_id = self.start_row * 1000 + self.start_column * 100 + self.end_row * 10 + self.end_column 

    def __eq__ (self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_column) + self.get_rank_file(self.end_row, self.end_column)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]
    

