#!/bin/pypy3
import chessy


def num_moves_tree(state, depth, i=0, l=[]):
    sub_moves = chessy.move_generation(state).values()
    if i >= len(l):
        l.append(0)
    l[i] += len(sub_moves)
    if depth == i + 1:
        return l
    for s in sub_moves:
        l = num_moves_tree(s, depth, i+1, l)
    return l


def perft(depth, splitdepth=0, fenstring=chessy.STARTING_FEN):
    state = chessy.parse_FEN(fen)
    chessy.draw_board(state.board)
    moves = num_moves_tree(state, depth)
    print(moves)
    # for i in range():
    #     print(i, moves[i])

def num_moves(state, num_iterations):
    if num_iterations <= 0:
        return 1
    if num_iterations == 1:
        return len(chessy.move_generation(state).values())
    num = 0
    for s in chessy.move_generation(state).values():
        num += num_moves(s, num_iterations - 1)
    return num


def perftree(depth, splitdepth=0, fenstring=chessy.STARTING_FEN, movelist=None):
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
    if len(sys.argv) < 3 or not sys.argv[1].isdigit():
        print("Usage is: python perft.py <depth> <FEN string> <movelist>")
        exit(1)
    movelist = None
    if len(sys.argv) == 4 and sys.argv[3]:
        movelist = sys.argv[3].split()

    perftree(int(sys.argv[1]), fenstring=sys.argv[2], movelist=movelist)