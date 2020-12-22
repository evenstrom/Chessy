#!/bin/pypy3
import chessy


def num_moves(state, num_iterations):
    if num_iterations <= 0:
        return 1
    if num_iterations == 1:
        return len(chessy.move_generation(state).values())
    num = 0
    for s in chessy.move_generation(state).values():
        num += num_moves(s, num_iterations - 1)
    return num


def perft(depth, fenstring, movelist):
    state = chessy.parse_FEN(fenstring)
    if movelist:
        for m in movelist:
            move = chessy.parse_move_input(m)
            moves = chessy.move_generation(state)
            state = moves[move]
    total = 0
    for m, s in chessy.move_generation(state).items():
        f,t,*p = m
        print(chessy.BOARD_NOTATION[f] + chessy.BOARD_NOTATION[t], end="")
        if p:
            print(chessy.PROMOTE_PIECE_ENCODING[p[0]], end="")
        moves = num_moves(s, depth - 1)
        total += moves
        print(f" {moves}")
    print(f"\n{total}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2 or not sys.argv[1].isdigit():
        print("Usage is: python perft.py <depth> [<FEN string>] [<movelist>]")
        exit(1)
    try:
        fen = sys.argv[2]
    except IndexError:
        fen = chessy.STARTING_FEN

    movelist = None
    if len(sys.argv) == 4 and sys.argv[3]:
        movelist = sys.argv[3].split()

    perft(int(sys.argv[1]), fenstring=fen, movelist=movelist)