import pygame as p
import CE

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


def load_images():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = CE.game_stater()
    move_made = False
    animated = False
    load_images()
    running = True
    sq_selcted = ()
    player_clicks = []
    game_over = False
    while running:
        check_moves = gs.king_is_not_in_check_moves()
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.KEYDOWN:
                if e.key == p.K_c:
                    gs.make_move(gs.random_move())
                elif e.key == p.K_z:
                    gs.undo_move()
                    animated = False
                    game_over = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sq_selcted == (row, col):
                        sq_selcted = ()
                        player_clicks = []
                    else:
                        sq_selcted = (row, col)
                        player_clicks.append(sq_selcted)
                    if len(player_clicks) == 2:
                        move = CE.Move(player_clicks[0], player_clicks[1], gs.board)
                        for i in range(len(check_moves)):
                            if move == check_moves[i]:
                                gs.make_move(move)
                                move_made = True
                                animated = True
                                sq_selcted = ()
                                player_clicks = []
                        if not move_made:
                            player_clicks = [sq_selcted]

        if move_made:
            if animated:
                animated_move(gs.move_log[-1], screen, gs.board, clock)
            check_moves = gs.king_is_not_in_check_moves()
            move_made = False

        draw_game_state(screen, gs, check_moves, sq_selcted)

        if gs.check_mate:
            game_over = True
            if gs.white_move:
                draw_text(screen, "black wins by Checkmate")
            else:
                draw_text(screen, "white wins by Checkmate")
        elif gs.stal_mate:
            game_over = True
            draw_text(screen, "it is a stale mate")

        clock.tick(MAX_FPS)
        p.display.flip()


def high_light_squares(screen, gs, king_is_not_in_check_moves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == ("w" if gs.white_move else "b"):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color("blue"))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            s.fill(p.Color("yellow"))
            for move in king_is_not_in_check_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (SQ_SIZE*move.end_col, SQ_SIZE*move.end_row))


def draw_game_state(screen, gs, king_is_not_in_check_moves, sq_selected):
    draw_board(screen)
    high_light_squares(screen, gs, king_is_not_in_check_moves, sq_selected)
    draw_pieces(screen, gs.board)


def draw_board(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def animated_move(move, screen, board, clock):
    global colors
    d_r = move.end_row - move.start_row
    d_c = move.end_col - move.start_col
    frame_per_square = 8
    frame_count = (abs(d_r) + abs(d_c)) * frame_per_square
    for frame in range(frame_count + 1):
        r, c = (move.start_row + d_r * frame/frame_count, move.start_col+d_c* frame/frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        color = colors [(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col*SQ_SIZE, move.end_row*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)
        if move.piece_captured != "--":
            screen.blit(IMAGES[move.piece_captured], end_square)
        screen.blit(IMAGES[move.piece_moved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def draw_text(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    text_obj = font.render(text, 0, p.Color("Gray"))
    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - text_obj.get_width()/2,HEIGHT/2 - text_obj.get_height()/2)
    screen.blit(text_obj, text_location)
    text_obj = font.render(text, 0, p.Color("Black"))
    screen.blit(text_obj, text_location.move(2, 2))

if __name__ == "__main__":
    main()
