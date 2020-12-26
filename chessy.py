#!/bin/pypy3
"""
A silly chessengine.
"""
import re
import random
from typing import NamedTuple, Tuple, List, Dict, Set

# Board coordinates for reference
# 0,     1,  2,    3,  4,    5,   6,   7,	
# 16,   17,  18,  19,  20,  21,  22,  23,	
# 32,   33,  34,  35,  36,  37,  38,  39,	
# 48,   49,  50,  51,  52,  53,  54,  55,	
# 64,   65,  66,  67,  68,  69,  70,  71,	
# 80,   81,  82,  83,  84,  85,  86,  87,	
# 96,   97,  98,  99, 100, 101, 102, 103,	
# 112, 113, 114, 115, 116, 117, 118, 119,

COLOUR = [w, b] = [0b0100_0000, 0b1000_0000]
PLAYER_BITS = 0b1100_0000
CASTLE = [wOO, wOOO, bOO, bOOO, OO, OOO, wc, bc] = [
    0b0001, 0b0010, 0b0100, 0b1000, 0b0101, 0b1010, 0b0011, 0b1100]

PIECE_TYPES = [P, R, N, B, Q, K] = [
    0b0001, 0b0010, 0b0100, 0b1000, 0b0001_0000, 0b0010_0000]

SLIDER_PIECE = R | B | Q

PIECES = [wP, wR, wN, wB, wQ, wK, 
          bP, bR, bN, bB, bQ, bK] = [
              p | c for c in COLOUR for p in PIECE_TYPES]

FLAGS = [attacked_square, attacked_piece, unsafe_square,
         pinned_piece, enpasant_square] = [0b0001, 0b0010, 0b0100, 0b01000, 0b10000]

PIECE_NOTATION = {"p": bP, "r": bR, "n": bN, "b": bB, "q": bQ, "k": bK,
                  "P": wP, "R": wR, "N": wN, "B": wB, "Q": wQ, "K": wK}
PIECE_ENCODING = {bP: "p", bR: "r", bN: "n", bB: "b", bQ: "q", bK: "k",
                  wP: "P", wR: "R", wN: "N", wB :"B", wQ: "Q", wK: "K"}
PROMOTE_PIECE = {"r": R, "q": Q, "b": B, "n": N, "R": R, "Q": Q, "B": B, "N": N}
PROMOTE_PIECE_ENCODING = {R: "r", Q: "q", B: "b", N: "n"}

BOARD_NOTATION = [ 
    "a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8", "","","","","","","","",
    "a7", "b7", "c7", "d7", "e7", "f7", "g7", "h7", "","","","","","","","",
    "a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6", "","","","","","","","",
    "a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5", "","","","","","","","",
    "a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4", "","","","","","","","",
    "a3", "b3", "c3", "d3", "e3", "f3", "g3", "h3", "","","","","","","","",
    "a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2", "","","","","","","","",
    "a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1", "","","","","","","","",]

OFF_THE_BOARD = len(BOARD_NOTATION)

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

PIECE_SYMBOLS = {wP: '♙', wR: '♖', wN: '♘', wB: '♗', wQ: '♕', wK: '♔', 
                 bP: '♟︎', bR: '♜', bN: '♞', bB: '♝', bQ: '♛', bK: '♚',
                 0:  ' '}

directions = [north, east, south, west] = -16, 1, 16, -1

MOVE_VECTORS = {
    bP: [south+west, south,  south+east],
    wP: [north+west, north,  north+east],
    bR: [north, east, south, west],
    wR: [north, east, south, west],
    bN: [north+north+east, north+north+west, north+east+east, north+west+west,
         south+south+east, south+south+west, south+east+east, south+west+west,],
    wN: [north+north+east, north+north+west, north+east+east, north+west+west,
         south+south+east, south+south+west, south+east+east, south+west+west,],
    bB: [north+west, north+east, south+west, south+east],
    wB: [north+west, north+east, south+west, south+east],
    bQ: [north+west, north+east, south+west, south+east, north, east, south, west],
    wQ: [north+west, north+east, south+west, south+east, north, east, south, west],
    bK: [north+west, north+east, south+west, south+east, north, east, south, west],
    wK: [north+west, north+east, south+west, south+east, north, east, south, west],}


# Piece and square evaluation from Simplified Evaluation by Tomasz Michniewski 
# https://www.chessprogramming.org/Simplified_Evaluation_Function
PIECE_VALUE = { K: 20_000,
                Q:    900,
                R:    500,
                B:    330,
                N:    320,
                P:    100, 
                0:      0,}

OFF_0x88_BOARD = (0,) * 8

PIECE_SQUARE_BONUS = {
    P: (( 0,  0,  0,  0,  0,  0,  0,  0),
        (50, 50, 50, 50, 50, 50, 50, 50),
        (10, 10, 20, 30, 30, 20, 10, 10),
        ( 5,  5, 10, 25, 25, 10,  5,  5),
        ( 0,  0,  0, 20, 20,  0,  0,  0),
        ( 5, -5,-10,  0,  0,-10, -5,  5),
        ( 5, 10, 10,-20,-20, 10, 10,  5),
        ( 0,  0,  0,  0,  0,  0,  0,  0)),

    N: ((-50,-40,-30,-30,-30,-30,-40,-50),
        (-40,-20,  0,  0,  0,  0,-20,-40),
        (-30,  0, 10, 15, 15, 10,  0,-30),
        (-30,  5, 15, 20, 20, 15,  5,-30),
        (-30,  0, 15, 20, 20, 15,  0,-30),
        (-30,  5, 10, 15, 15, 10,  5,-30),
        (-40,-20,  0,  5,  5,  0,-20,-40),
        (-50,-40,-30,-30,-30,-30,-40,-50)),

    B: ((-20,-10,-10,-10,-10,-10,-10,-20),
        (-10,  0,  0,  0,  0,  0,  0,-10),
        (-10,  0,  5, 10, 10,  5,  0,-10),
        (-10,  5,  5, 10, 10,  5,  5,-10),
        (-10,  0, 10, 10, 10, 10,  0,-10),
        (-10, 10, 10, 10, 10, 10, 10,-10),
        (-10,  5,  0,  0,  0,  0,  5,-10),
        (-20,-10,-10,-10,-10,-10,-10,-20)),

    R: ((  0,  0,  0,  0,  0,  0,  0,  0),
        (  5, 10, 10, 10, 10, 10, 10,  5),
        ( -5,  0,  0,  0,  0,  0,  0, -5),
        ( -5,  0,  0,  0,  0,  0,  0, -5),
        ( -5,  0,  0,  0,  0,  0,  0, -5),
        ( -5,  0,  0,  0,  0,  0,  0, -5),
        ( -5,  0,  0,  0,  0,  0,  0, -5),
        (  0,  0,  0,  5,  5,  0,  0,  0)),

    Q: ((-20,-10,-10, -5, -5,-10,-10,-20),
        (-10,  0,  0,  0,  0,  0,  0,-10),
        (-10,  0,  5,  5,  5,  5,  0,-10),
        ( -5,  0,  5,  5,  5,  5,  0, -5),
        (  0,  0,  5,  5,  5,  5,  0, -5),
        (-10,  5,  5,  5,  5,  5,  0,-10),
        (-10,  0,  5,  0,  0,  0,  0,-10),
        (-20,-10,-10, -5, -5,-10,-10,-20)),

    K: ((-30,-40,-40,-50,-50,-40,-40,-30),
        (-30,-40,-40,-50,-50,-40,-40,-30),
        (-30,-40,-40,-50,-50,-40,-40,-30),
        (-30,-40,-40,-50,-50,-40,-40,-30),
        (-20,-30,-30,-40,-40,-30,-30,-20),
        (-10,-20,-20,-20,-20,-20,-20,-10),
        ( 20, 20,  0,  0,  0,  0, 20, 20),
        ( 20, 30, 10,  0,  0, 10, 30, 20)), }
    
King_endgame = ((-50,-40,-30,-20,-20,-30,-40,-50),
                (-30,-20,-10,  0,  0,-10,-20,-30),
                (-30,-10, 20, 30, 30, 20,-10,-30),
                (-30,-10, 30, 40, 40, 30,-10,-30),
                (-30,-10, 30, 40, 40, 30,-10,-30),
                (-30,-10, 20, 30, 30, 20,-10,-30),
                (-30,-30,  0,  0,  0,  0,-30,-30),
                (-50,-30,-30,-30,-30,-30,-30,-50),) 

PIECE_SQUARE_VALUE = {
    k | p: tuple((s + PIECE_VALUE[k]) * (1 if p == w else -1)
        for r in (v if p == w else reversed(v))
        for s in r + OFF_0x88_BOARD)
    for k,v in PIECE_SQUARE_BONUS.items()
    for p in COLOUR
}

PIECE_SQUARE_VALUE[0] = (0,) * 128

board_t = List[int]
class GameState(NamedTuple):
    board: board_t
    player: int
    castle: int
    ep: int
    pawnmove: int
    num_moves: int
    last_moved_piece: int
    captured_piece: int
    moved_from_square: int
    moved_to_square: int


ENDC = '\033[0m'
WHITE = '\033[38;5;0;48;5;15m'
BLACK = '\033[38;5;0;48;5;250m'
def draw_board(board: board_t) -> None:
    print()
    for r in range(8):
        print(f"  {8 - r}", end="  ")
        for c in range(8):
            square = r << 4 | c
            piece = board[square]
            color =  WHITE if (r + c) % 2 == 0 else BLACK
            print(f"{color}{PIECE_SYMBOLS[piece]} {ENDC}", end="")
        print()
        if r == 7:
            print(f"\n     a b c d e f g h", end="\n\n")    


def king_in_check_through_square(state: GameState, square: int) -> bool:
    other_player = state.player ^ PLAYER_BITS
    for dir_one, dir_two in ((north+west, south+east), 
                             (north+east, south+west),
                             (north, south), 
                             (east, west)):
        lookup_dir_one = lookup_dir_two = square
        king_found = False
        slider_found = False
        while True:
            lookup_dir_one += dir_one

            if lookup_dir_one & 0x88: break
            piece = state.board[lookup_dir_one]
            if piece & state.player: 
                king_found = piece & K > 0
                break
            elif piece & other_player:
                slider_found = piece & SLIDER_PIECE > 0 and dir_two in MOVE_VECTORS[piece]
                break

        while True:
            lookup_dir_two += dir_two
            if lookup_dir_two & 0x88: break
            piece = state.board[lookup_dir_two]
            if piece & state.player: 
                king_found = piece & K > 0
                break
            elif piece & other_player:
                slider_found = piece & SLIDER_PIECE > 0 and dir_two in MOVE_VECTORS[piece]
                break
        if king_found and slider_found:
            return True
    return False


def generate_new_state(state: GameState, from_square: int, to_square: int, 
        ep_capture_square:int=OFF_THE_BOARD, ep_square:int=OFF_THE_BOARD, 
        castle:int=0, pawn_promote:int=0) -> GameState:
    new_board = [*state.board]
    player = state.player ^ PLAYER_BITS
    
    if player & w:
        num_moves = state.num_moves + 1
    else:
        num_moves = state.num_moves
    
    if new_board[from_square] & P or new_board[to_square]:
        pawnmove = 0
    else:
        pawnmove = state.pawnmove + 1
    
    captured_piece = new_board[to_square]
    last_moved_piece = new_board[from_square]
    moved_from_square = from_square
    moved_to_square = to_square

    new_board[from_square], new_board[to_square] = 0, new_board[from_square]

    # PROMOTION
    if pawn_promote:
        new_board[to_square] = pawn_promote | state.player
    
    if ep_capture_square < len(new_board):
        new_board[ep_capture_square] = 0

    new_castle = state.castle & ~castle
    if castle:
        if castle == wOOO:
            new_board[115], new_board[112] = wR, 0
            new_castle = state.castle & ~wc        
        elif castle == wOO:
            new_board[117], new_board[119] = wR, 0
            new_castle = state.castle & ~wc
        elif castle & bOO and not(castle & bOOO):
            new_board[5], new_board[7] = bR, 0
            new_castle = state.castle & ~bc
        elif castle & bOOO and not(castle & bOO):
            new_board[3], new_board[0] = bR, 0
            new_castle = state.castle & ~bc
            
    if new_castle:
        if new_castle & wOOO and new_board[112] != wR:
            new_castle &= ~wOOO
        if new_castle & wOO and new_board[119] != wR:
            new_castle &= ~wOO
        if new_castle & bOOO and new_board[0] != bR:
            new_castle &= ~bOOO
        if new_castle & bOO and new_board[7] != bR:
            new_castle &= ~bOO

    return GameState(new_board, player, new_castle, 
        ep_square, pawnmove, num_moves, last_moved_piece, 
        captured_piece, moved_from_square, moved_to_square)


def generate_move_validation_state(state: GameState, new_squares: List[Tuple[int, int]]) -> GameState:
    new_board = [*state.board]
    for s, v in new_squares:
        new_board[s] = v
    return state._replace(board=new_board)


def move_generation(state: GameState) -> Dict[Tuple[int, ...], GameState]:
    generated_moves: Dict[Tuple[int, ...], GameState] = {}
    flags_board = [0] * len(state.board)
    
    other_player = state.player ^ PLAYER_BITS
    checking_squares: Set[int] = set()
    pinned_pieces: Dict[int, List[int]] = {}
    unsafe_squares: Set[int] = set()
    double_check = False
    check = False
    for square in range(128):
        if square & 0x88: continue 
        piece = state.board[square]
        if not piece & other_player: continue

        for m in MOVE_VECTORS[piece]:
            if piece & P and m in (north, south): continue

            att_sqr = square
            attack_list = [att_sqr]
            possible_pin = None
            while True:
                att_sqr += m
                if att_sqr & 0x88: break 
                if state.board[att_sqr] & other_player: 
                    if not possible_pin:
                        unsafe_squares.add(att_sqr)
                    break
                    
                attack_list.append(att_sqr)
                if state.board[att_sqr] & state.player:
                    if state.board[att_sqr] & K:
                        if possible_pin:
                            pinned_pieces[possible_pin] = attack_list[:-1]
                            break
                        else:
                            if check:
                                double_check = True
                            else:
                                checking_squares = set(attack_list)
                                check = True
                    else:
                        if possible_pin: break
                        possible_pin = att_sqr
                if not possible_pin:
                    unsafe_squares.add(att_sqr)

                if not piece & SLIDER_PIECE: break

    for square in range(128):
        if square & 0x88: continue 
        piece = state.board[square]
        if not piece & state.player: continue

        pinned = square in pinned_pieces
        pinned_allowed_move = pinned_pieces.get(square, [])

        # DOUBLE CHECK ONLY KING MOVES
        if double_check and not(piece & K): continue

        for m in MOVE_VECTORS[piece]:
            att_sqr = square
            while True:
                att_sqr += m
                if att_sqr & 0x88: break 
                if pinned and (att_sqr not in pinned_allowed_move): break
                if state.board[att_sqr] & state.player: break

                # PAWN RULES
                if piece & P:
                    new_piece = piece
                    
                    
                    if m in (north, south):
                        if state.board[att_sqr] & other_player:
                            break
                        # NORMAL MOVE
                        if not check or att_sqr in checking_squares:
                            if att_sqr <= 7 or att_sqr >= 112:
                                for promote_to in (Q, R, B, N):
                                    generated_moves[(square, att_sqr, promote_to)] = generate_new_state(
                                        state, from_square=square, to_square=att_sqr, pawn_promote=promote_to)
                            else:
                                generated_moves[(square, att_sqr)] = generate_new_state(
                                            state, from_square=square, to_square=att_sqr)
                        # DOUBLE MOVE FROM INITIAL POSITION
                        if (state.player & w and 96 <= square <= 103) or (
                            state.player & b and 16 <= square <= 23):
                            double_move = att_sqr + m
                                    
                            if not state.board[double_move]:
                                if not check or double_move in checking_squares:
                                    generated_moves[(square, double_move)] = generate_new_state(
                                        state, from_square=square, to_square=double_move, ep_square=att_sqr)

                    else:
                        # ENPASSANT CAPTURE
                        if att_sqr == state.ep:
                            ep_capture_square = state.ep + (south if state.player & w else north)   
                            if not check or att_sqr in checking_squares or ep_capture_square in checking_squares:

                                validate_state = generate_move_validation_state(state, 
                                        new_squares=[(square, 0), (att_sqr, new_piece), (ep_capture_square, 0)])
                                if not king_in_check_through_square(validate_state, ep_capture_square):
                                    generated_moves[(square, att_sqr)] = generate_new_state(
                                        state, from_square=square, to_square=att_sqr, ep_capture_square=ep_capture_square)

                        # CAPTURE
                        elif state.board[att_sqr] & other_player:
                            if not check or att_sqr in checking_squares:
                                if att_sqr <= 7 or att_sqr >= 112:
                                    for promote_to in (Q, R, B, N):
                                        generated_moves[(square, att_sqr, promote_to)] = generate_new_state(
                                            state, from_square=square, to_square=att_sqr, pawn_promote=promote_to)
                                else:
                                    generated_moves[(square, att_sqr)] = generate_new_state(
                                            state, from_square=square, to_square=att_sqr)
                
                #KING RULES
                elif piece & K:
                    #CASTLE
                    castlemask = wc if state.player & w else bc
                    can_castle = state.castle & castlemask
                    if not (check or double_check) and can_castle:
                        double_move = att_sqr + m
                        if m == east and can_castle & OO:
                            if not (state.board[att_sqr] | state.board[double_move]
                                ) and (att_sqr not in unsafe_squares and double_move not in unsafe_squares):
                                generated_moves[(square, double_move)] = generate_new_state(state, 
                                    from_square=square, to_square=double_move, castle=can_castle&OO)

                        elif m == west and can_castle & OOO:
                            tripple_move = double_move + m
                            if not (state.board[att_sqr] | state.board[double_move] | state.board[tripple_move]
                                ) and (att_sqr not in unsafe_squares and double_move not in unsafe_squares):
                                generated_moves[(square, double_move)] = generate_new_state(state, 
                                    from_square=square, to_square=double_move, castle=can_castle&OOO)
                    
                    if not att_sqr in unsafe_squares:
                        generated_moves[(square, att_sqr)] = generate_new_state(state, 
                            from_square=square, to_square=att_sqr, castle=castlemask)

                else:
                    if not check or att_sqr in checking_squares:
                        generated_moves[(square, att_sqr)] = generate_new_state(state, 
                            from_square=square, to_square=att_sqr)

                if state.board[att_sqr] & other_player: break
                if not piece & SLIDER_PIECE: break

    return generated_moves


searched = 0
MATE = 2 * PIECE_VALUE[K]
ALPHABETA = 99999999999999

def search(state: GameState, depth: int, print_status: bool = False):
    global searched
    searched = 0
    next_states: List[GameState] = sorted(move_generation(state).values(), 
                         key=move_order_value, reverse=True)
    # move_scores = {}
    alpha = -ALPHABETA
    beta = ALPHABETA
    num_moves = len(next_states)
    best_move = None
    for i, ns in enumerate(next_states):
        if print_status:
            print(f"\rThinking of move {i+1:>3}/{num_moves}, depth = {depth}", end= "")
        score = alphabeta(ns, depth - 1, alpha, beta, ns.player == w)
        # move_scores[score] = move_scores.get(score, []) + [ns]
        if state.player == w:
            if score > alpha:
                alpha = score
                best_move = ns
        else:
            if score < beta:
                beta = score
                best_move = ns
        if print_status:
            print(f", best score = {alpha if state.player == w else beta: <20}", end="")
    if print_status:
        print("\n")
    print("Searched", searched)
    
    # best_moves = move_scores.get(beta, [])
    return best_move #random.choice(best_moves) if best_moves else None


def move_order_value(state: GameState) -> int:
    moved_piece = state.last_moved_piece
    captured_piece = state.captured_piece
    pos_matrix = PIECE_SQUARE_VALUE[moved_piece]
    
    improvement = abs(pos_matrix[state.moved_to_square] - pos_matrix[state.moved_from_square])
    capture_value = PIECE_VALUE[captured_piece & ~PLAYER_BITS]
    return improvement + capture_value


def alphabeta(state, depth, alpha, beta, maximizingPlayer):
    next_states = move_generation(state).values()
    next_states = sorted(next_states, key=move_order_value, reverse=True)
    if depth == 0 or len(next_states) == 0:
        global searched
        searched += 1
        return evaluate(state, next_states, depth)

    if maximizingPlayer:
        value = -ALPHABETA
        for ns in next_states:
            value = max(value, alphabeta(ns, depth - 1, alpha, beta, False))
            alpha = max(alpha, value)
            if alpha >= beta: break
        return value
    else:
        value = ALPHABETA
        for ns in next_states:
            value = min(value, alphabeta(ns, depth - 1, alpha, beta, True))
            beta = min(beta, value)
            if beta <= alpha: break
        return value

MOBILITY_SCORE = PIECE_VALUE[P] // 10
PAWN_PUNISH = PIECE_VALUE[P] // 2
def evaluate(state: GameState, next_states, depth) -> int:
    position_value = 0
    other_player = state.player ^ PLAYER_BITS
    white_pawn_files = [0] * 8
    black_pawn_files = [0] * 8
    if len(next_states) == 0:
        king_square = 0
        for square in range(128):
            if square & 0x88: continue 
            piece = state.board[square]
            if piece & K and piece & state.player: 
                king_square = square
                break
        
        # check by night.
        for m in MOVE_VECTORS[wN]:
            if king_square + m & 0x88: continue
            nightmove = state.board[king_square + m]
            if nightmove & N and nightmove & other_player:
                return MATE * (-1 if state.player == w else 1) * depth
        
        for dir_one, dir_two in ((north+west, south+east), 
                                 (north+east, south+west),
                                 (north, south), 
                                 (east, west),
                                 (south+east, north+west), 
                                 (south+west, north+east),
                                 (south, north), 
                                 (west, east)):
            att_sqr = king_square
            while True:
                att_sqr += dir_one
                if att_sqr & 0x88: break 
                piece = state.board[att_sqr]
                if piece & state.player: break
                if piece & other_player:
                    if piece & P: 
                        if dir_one in (north, south, east, west): break
                        if dir_two in MOVE_VECTORS[piece] and dir_two + att_sqr == king_square:
                            return MATE * (-1 if state.player == w else 1)  * depth
                    if piece & N: break
                    if piece & K: break
                    if dir_two in MOVE_VECTORS[piece]:
                        return MATE * (-1 if state.player == w else 1)  * depth
        # not mate
        return 0                  

    for square in range(128):
        if square & 0x88: continue 
        piece = state.board[square]
        if piece == 0: continue
        if piece & P:
            if piece & w:
                white_pawn_files[square & 0b111] += 1
            else:
                black_pawn_files[square & 0b111] += 1
        position_value += PIECE_SQUARE_VALUE[piece][square]

    # punish doubled pawns
    position_value -= sum(i for i in white_pawn_files if i > 1) * PAWN_PUNISH
    position_value += sum(i for i in black_pawn_files if i > 1) * PAWN_PUNISH

    # punish isolated pawns
    if white_pawn_files[0] > 0 and white_pawn_files[1] == 0:
        position_value -= white_pawn_files[0] * PAWN_PUNISH
    if black_pawn_files[0] > 0 and black_pawn_files[1] == 0:
        position_value += black_pawn_files[0] * PAWN_PUNISH
    if white_pawn_files[7] > 0 and white_pawn_files[6] == 0:
        position_value -= white_pawn_files[7] * PAWN_PUNISH
    if black_pawn_files[7] > 0 and black_pawn_files[6] == 0:
        position_value += black_pawn_files[7] * PAWN_PUNISH
    for i, j, k in zip(white_pawn_files, white_pawn_files[1:], white_pawn_files[2:]):
        if i == 0 and j > 0 and k == 0:
            position_value += i * PAWN_PUNISH
    for i, j, k in zip(black_pawn_files, black_pawn_files[1:], black_pawn_files[2:]):
        if i == 0 and j > 0 and k == 0:
            position_value += i * PAWN_PUNISH

    # punish blocked pawns

    # revard mobility
    position_value += len(next_states) * MOBILITY_SCORE * (
        -1 if state.player & b else 1)
    other_side = state._replace(player=state.player^PLAYER_BITS)
    position_value += len(move_generation(other_side).values()) * MOBILITY_SCORE * (
        1 if state.player & b else -1)
    return position_value


def parse_FEN(fen_string: str) -> GameState:
    board, player, castle, ep, *moves = fen_string.strip().split()
    if len(moves) < 2:
        pawnmove = num_moves = 0
    else:
        pawnmove = int(moves[0])
        num_moves = int(moves[1])

    parsed_board = []
    for r in board.split("/"):
        for c in r:
            if c.isdigit():
                parsed_board.extend([0] * int(c))
            elif c in PIECE_NOTATION:
                parsed_board.append(PIECE_NOTATION[c])
            else:
                raise Exception(f"ERROR: illegal symbol in FEN notation: {c}")
        parsed_board.extend([0] * 8)
    
    if player not in "wb":
        raise Exception(f"ERROR: illegal player symbol in FEN notation: {player}")

    try:
        ep_square = BOARD_NOTATION.index(ep)
    except ValueError:
        ep_square = OFF_THE_BOARD
    
    castle_bin = 0b0
    if parsed_board[116] == wK:
        if "K" in castle and parsed_board[119] == wR:
            castle_bin |= wOO
        if "Q" in castle and parsed_board[112] == wR:
            castle_bin |= wOOO
    if parsed_board[4] == bK:
        if "k" in castle and parsed_board[7] == bR:
            castle_bin |= bOO
        if "q" in castle and parsed_board[0] == bR:
            castle_bin |= bOOO
        
    return GameState(parsed_board, w if player == "w" else b, 
                 castle_bin, ep_square, pawnmove, num_moves, 0, 0, 0, 0)


def to_fen(state: GameState) -> str:
    string_builder: List[str] = []
    for r in range(8):
        num_empty = 0
        for c in range(8):
            piece = PIECE_ENCODING.get(state.board[r << 4 | c], "")
            if piece:
                if num_empty > 0:
                    string_builder.append(str(num_empty))
                    num_empty = 0
            else:
                num_empty += 1
            string_builder.append(piece)
        if num_empty > 0: 
            string_builder.append(str(num_empty))
        if r < 7:
            string_builder.append("/")
    string_builder.append(f" {'w' if state.player & w else 'b'} ")
    if state.castle:
        string_builder.append("K" if state.castle & wOO else "")
        string_builder.append("Q" if state.castle & wOOO else "")
        string_builder.append("k" if state.castle & bOO else "")
        string_builder.append("q" if state.castle & bOOO else "")
    else:
        string_builder.append("-")
    string_builder.append(" ")
    if state.ep != OFF_THE_BOARD:
        string_builder.append(BOARD_NOTATION[state.ep])
    else: 
        string_builder.append("-")
    string_builder.append(f" {state.pawnmove} {state.num_moves}")
    return "".join(string_builder)


def parse_move_input(move: str) -> Tuple[int, ...]:
    match = re.match("^([a-hA-H][1-8])([a-hA-H][1-8])([QRBNqrbn])?$", move.replace(" ", ""))
    if not match:
        return OFF_THE_BOARD, OFF_THE_BOARD
    f, t = match.group(1,2)
    try:
        if match.group(3):
            return (BOARD_NOTATION.index(f.lower()), 
                    BOARD_NOTATION.index(t.lower()),
                    PROMOTE_PIECE[match.group(3)])
        else:
            return (BOARD_NOTATION.index(f.lower()), BOARD_NOTATION.index(t.lower()))
    except ValueError:
        return (OFF_THE_BOARD, OFF_THE_BOARD)


def main(state: GameState) -> None:
    while True:
        draw_board(state.board)
        moves = move_generation(state)
        if not moves:
            print("You lost :-(")
            break

        while True:
            move = parse_move_input(input("Enter move: "))
            if move in moves:
                state = moves[move]
                break
            else:
                print("Enter moves in from to square form. eg. e2e4, promotion append q b r n eg. e7e8q")
        draw_board(state.board)
        
        state = search(state, 6, print_status=True)
        if not state:
            print("You win :-)")
            break

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        fen = sys.argv[1]
    else:
        fen = STARTING_FEN
    state = parse_FEN(fen)
    main(state)