import time
import statistics
from board import Chessboard
from engine import Engine

#ai genrated script didnt wanna waste time on thiss 

FEN = "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1"
SEARCH_DEPTH = 3   # raise to 4 if it finishes quickly
PERFT_DEPTH = 4    # start position: should give 197281 nodes
RUNS = 3


def bench_perft():
    game = Chessboard()
    start = time.perf_counter()
    nodes = game.perft(PERFT_DEPTH)
    elapsed = time.perf_counter() - start
    print(f"perft({PERFT_DEPTH}): {nodes} nodes, {elapsed:.2f}s, {nodes / elapsed:,.0f} nodes/s")


def bench_search():
    rates = []
    for i in range(RUNS):
        game = Chessboard()
        game.load_fen(FEN)
        engine = Engine(depth=SEARCH_DEPTH)

        start = time.perf_counter()
        engine.get_best_move(game, SEARCH_DEPTH)
        elapsed = time.perf_counter() - start

        nps = engine.nodes_searched / elapsed
        rates.append(nps)
        print(f"search run {i + 1}: {engine.nodes_searched} nodes, {elapsed:.2f}s, {nps:,.0f} nodes/s")

    print(f"median search speed: {statistics.median(rates):,.0f} nodes/s")


if __name__ == "__main__":
    bench_perft()
    bench_search()