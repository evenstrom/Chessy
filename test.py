#!/bin/pypy3
import json
import unittest

import chessy
import perft


class TestChessy(unittest.TestCase):
    
    def test_perft_positions(self):
        with open(__file__.replace(".py", ".json")) as f:
            positions = json.load(f)
        for pos in positions:
            if not pos["type"] == "perf_test": continue
            with self.subTest(pos=pos):
                print(pos["fen"])
                print(f"depth: {pos['depth']}, expected number of nodes: {pos['nodes']}")
                state = chessy.parse_FEN(pos["fen"])
                chessy.draw_board(state.board)
                perft_result = perft.num_moves(state, pos["depth"])
                if pos["nodes"] != perft_result:
                    print(f"Error produced {perft_result} nodes")
                else:
                    print("Success!\n")
                self.assertEqual(perft_result, pos["nodes"])
    
    def test_tactics_4_moves_or_less(self):
        with open(__file__.replace(".py", ".json")) as f:
            positions = json.load(f)
        for pos in positions:
            if pos["type"] != "tactics_test": continue
            depth = pos["depth"]
            if depth > 4: continue

            fens = pos["fen"]
            results = pos["result"]
            print(pos["source"])
            print(pos["name"])
            for f, r in zip(fens, results):
                with self.subTest(f=f):
                    state = chessy.parse_FEN(f)
                    expects_state = chessy.parse_FEN(r)
                    res = chessy.search(state, depth, True)
                    res_fen = chessy.to_fen(res)
                    if res_fen != r:
                        chessy.draw_board(expects_state.board)
                        chessy.draw_board(res.board)
                    self.assertEqual(res_fen, r)
                depth -= 2

    def test_tactics_4_to_6_moves(self):
        with open(__file__.replace(".py", ".json")) as f:
            positions = json.load(f)
        for pos in positions:
            if pos["type"] != "tactics_test": continue
            depth = pos["depth"]
            if not 4 < depth <= 6: continue

            fens = pos["fen"]
            results = pos["result"]
            print(pos["source"])
            print(pos["name"])
            for f, r in zip(fens, results):
                with self.subTest(f=f):
                    state = chessy.parse_FEN(f)
                    expects_state = chessy.parse_FEN(r)
                    res = chessy.search(state, depth, True)
                    res_fen = chessy.to_fen(res)
                    if res_fen != r:
                        chessy.draw_board(expects_state.board)
                        chessy.draw_board(res.board)
                    self.assertEqual(res_fen, r)
                depth -= 2
if __name__ == '__main__':
    unittest.main()