#!/bin/pypy3
import json
import unittest

import chessy
import perft


class TestStringMethods(unittest.TestCase):
    
    def test_perft_positions(self):
        with open(__file__.replace(".py", ".json")) as f:
            positions = json.load(f)
        for pos in positions:
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

if __name__ == '__main__':
    unittest.main()