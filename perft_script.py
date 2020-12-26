#! /bin/pypy3
import subprocess
import sys

OKGREEN = '\033[92m'
FAIL = '\033[91m'
ENDC = '\033[0m'

stockfish = subprocess.Popen("stockfish", 
    stdin=subprocess.PIPE, 
    stdout=subprocess.PIPE, 
    stderr=subprocess.STDOUT,
    bufsize=1, universal_newlines=True)
stockfish.stdout.readline()

def read_stdout(engine, terminates_with):
    out = []
    while True:
        line = engine.stdout.readline().strip()
        if line:
            out.append(line)
        if line.startswith(terminates_with):
            break
    return out

move_list = []
fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
depth = 1

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("enter perft script")
        exit()
    script = sys.argv[1].split()

    while True:
        cmd, *args = input("cmd> ").strip().split(" ", 1)
        if cmd == "fen":
            if args:
                move_list = []
                fen = args[0].strip()
            else:
                print(fen)

        elif cmd in ("h", "help"):
            pass
        
        elif cmd == "move":
            if args:
                move_list.append(args[0].strip())
            else:
                print(move_list)
        
        elif cmd == "pop":
            move_list.pop()

        elif cmd == "root":
            move_list = []
        
        elif cmd == "depth":
            if args:
                depth = int(args[0].strip())
            else:
                print(depth)
        
        elif cmd in ("q", "quit"):
            exit()
        
        elif cmd == "diff":
            stockfish.stdin.write(f"position fen {fen}")
            if move_list:
                stockfish.stdin.write(f" moves {' '.join(move_list)}")
            stockfish.stdin.write(f"\n")
            stockfish.stdin.write(f"go perft {depth}\n")
            stockfish_nodes = read_stdout(stockfish, "Nodes searched: ")
            stockfish_nodes = dict(tuple(n.split(": ")) for n in stockfish_nodes[:-1])
            
            runscript = [*script]
            runscript.extend(
                [f"{depth}", f"{fen}", ' '.join(move_list) if move_list else ""])
            perft = subprocess.run(runscript,
                capture_output=True, universal_newlines=True)
            capture = perft.stdout.splitlines()
            perft_nodes = dict(tuple(n.split()) for n in capture[:-2])
            searched = sorted(perft_nodes.keys() | stockfish_nodes.keys())
            i = j = 0
            for node in searched:
                n = perft_nodes.get(node, "")
                s = stockfish_nodes.get(node, "")
                if s != n:
                    print(f"{FAIL}{node}\t{s}\t{n}{ENDC}")
                else:
                    print(f"{OKGREEN}{node}\t{s}\t{n}{ENDC}")
            
            tot_stockfish = sum(int(i) for i in stockfish_nodes.values())
            tot_perft_nodes= sum(int (i) for i in perft_nodes.values())
            print(f"\n{FAIL if tot_stockfish != tot_perft_nodes else OKGREEN}"
                  f"Total\t{tot_stockfish}\t{tot_perft_nodes}{ENDC}")