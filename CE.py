import random


class game_stater:
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.move_functions = {"p": self.get_pawn_moves, "R": self.get_rook_moves, "B": self.get_bishop_moves,
                               "N": self.get_knight_moves, "Q": self.get_queen_moves, "K": self.get_king_moves}
        self.white_move = True
        self.move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (1, 4)
        self.check_mate = False
        self.stal_mate = False
        self.castling = Castling(True, True, True, True)
        self.castling_log = [Castling(self.castling.wks, self.castling.wqs,
                                      self.castling.bks, self.castling.bqs)]

    def clone_board(self):
        return self.board

    def make_move(self, move):
        if move == 0:
            return
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_move = not self.white_move
        if move.piece_moved == "wK":
            self.white_king_location = (move.end_row, move.end_col)
        if move.piece_moved == "bK":
            self.black_king_location = (move.end_row, move.end_col)

        if move.is_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + "Q"

        self.update_castling(move)
        self.castling_log.append(Castling(self.castling.wks, self.castling.wqs,
                                          self.castling.bks, self.castling.bqs))

        if move.end_col - move.start_col == 2 and move.piece_moved[1] == "K":
            self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]
            self.board[move.end_row][move.end_col + 1] = '--'
        elif move.start_col - move.end_col == 2 and move.piece_moved[1] == "K":
            self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]
            self.board[move.end_row][move.end_col - 2] = '--'

    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_move = not self.white_move
            if move.piece_moved == "wK":
                self.white_king_location = (move.start_row, move.start_col)
            if move.piece_moved == "bK":
                self.black_king_location = (move.start_row, move.start_col)
            if move.end_col - move.start_col == 2 and move.piece_moved[1] == "K":
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                self.board[move.end_row][move.end_col - 1] = '--'
            elif move.start_col - move.end_col == 2 and move.piece_moved[1] == "K":
                self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = '--'
            self.castling_log.pop()
            self.castling.wks = self.castling_log[-1].wks
            self.castling.wqs = self.castling_log[-1].wqs
            self.castling.bks = self.castling_log[-1].bks
            self.castling.bqs = self.castling_log[-1].bqs
            self.check_mate = False
            self.stal_mate = False

    def update_castling(self, move):
        if move.piece_moved == "wK":
            self.castling.wks = False
            self.castling.wqs = False
        elif move.piece_moved == "bK":
            self.castling.bqs = False
            self.castling.bks = False
        elif move.piece_moved == "wR":
            if move.start_row == 7:
                if move.start_col == 0:
                    self.castling.wqs = False
                elif move.start_col == 7:
                    self.castling.wks = False
        elif move.piece_moved == "bR":
            if move.start_row == 0:
                if move.start_col == 0:
                    self.castling.wqs = False
                elif move.start_col == 7:
                    self.castling.wks = False
        if move.end_col == 7 and move.end_row == 7:
            self.castling.wks = False
        elif move.end_col == 0 and move.end_row == 7:
            self.castling.wqs = False
        elif move.end_col == 7 and move.end_row == 0:
            self.castling.bks = False
        elif move.end_col == 0 and move.end_row == 0:
            self.castling.bqs = False

    def king_is_not_in_check_moves(self):
        moves = self.get_all_possible_moves()
        temp_castle_moves = Castling(self.castling.wks, self.castling.wqs, self.castling.bks, self.castling.bqs)
        if self.white_move:
            self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves)
        else:
            self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves)
        for i in range(len(moves) - 1, -1, -1):
            self.make_move(moves[i])
            self.white_move = not self.white_move
            if self.in_check():
                moves.remove(moves[i])
            self.white_move = not self.white_move
            self.undo_move()
        if len(moves) == 0:
            if self.in_check():
                self.check_mate = True
            else:
                self.stal_mate = True
        else:
            self.stal_mate = False
            self.check_mate = False
        self.castling = temp_castle_moves
        return moves

    def in_check(self):
        if self.white_move:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])

    def square_under_attack(self, row, col):
        self.white_move = not self.white_move
        opp_moves = self.get_all_possible_moves()
        self.white_move = not self.white_move
        for move in opp_moves:
            if move.end_row == row and move.end_col == col:
                return True
        return False

    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == "w" and self.white_move) or (turn == "b" and not self.white_move):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves)
        return moves

    def get_pawn_moves(self, r, c, moves):
        if self.white_move:
            if self.board[r - 1][c] == "--":
                moves.append(Move((r, c), (r - 1, c), self.board))
                if (r == 6) and (self.board[r - 2][c] == "--"):
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r - 1][c - 1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
            if c + 1 <= 7:
                if self.board[r - 1][c + 1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
        else:
            if self.board[r + 1][c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board))
                if (r == 1) and (self.board[r + 2][c] == "--"):
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
            if c + 1 <= 7:
                if self.board[r + 1][c + 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))

    def get_rook_moves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = "b" if self.white_move else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
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

    def get_bishop_moves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = "b" if self.white_move else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
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
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        ally_color = "w" if self.white_move else "b"
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_queen_moves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = "b" if self.white_move else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
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

    def get_king_moves(self, r, c, moves):
        king_moves = ((-1, -1), (-1, 0), (-1, 1), (0, 1), (1, -1), (1, 0), (1, 1), (0, -1))
        ally_color = "w" if self.white_move else "b"
        for i in range(8):
            end_row = r + king_moves[i][0]
            end_col = c + king_moves[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_castle_moves(self, r, c, moves):
        if self.square_under_attack(r, c):
            return
        if (self.white_move and self.castling.wks) or (not self.white_move and self.castling.bks):
            self.get_king_side(r, c, moves)
        if (self.white_move and self.castling.wqs) or (not self.white_move and self.castling.bqs):
            self.get_qeen_side(r, c, moves)

    def get_king_side(self, r, c, moves):
        if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":
            if not self.square_under_attack(r, c + 1) and not self.square_under_attack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, True))

    def get_qeen_side(self, r, c, moves):
        if self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--":
            if not self.square_under_attack(r, c - 1) and not self.square_under_attack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, True))

    def random_move(self):
        if len(game_stater.king_is_not_in_check_moves(self)) == 0:
            return 0
        moves = game_stater.king_is_not_in_check_moves(self)
        return random.choice(moves)


class Move:
    ranks_to_row = {"1": 7, "2": 6, "3": 5, "4": 4,
                    "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_row.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, castle=False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.is_promotion = False
        self.is_castle = castle
        self.is_promotion = (self.piece_moved == "wp" and self.end_row == 0) or (self.piece_moved == "bp" and self.end_row == 7)

        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def get_chess_notation(self):
        return self.get_rank_files(self.start_row, self.start_col) + self.get_rank_files(self.end_row, self.end_col)

    def get_rank_files(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]


class Castling:
    def __init__(self, wks, wqs, bks, bqs):
        self.wks = wks
        self.wqs = wqs
        self.bks = bks
        self.bqs = bqs
