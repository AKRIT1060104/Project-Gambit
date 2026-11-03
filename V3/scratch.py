from board import Chessboard

print("starting")

tests = [
	("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1", 3),
	("8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1", 4),
	("n1n5/PPPk4/8/8/8/8/4Kppp/5N1N b - - 0 1", 3),
]

for fen, depth in tests:
	game = Chessboard()
	game.load_fen(fen)
	game.hash_check(depth)
	print("ok:", fen[:20])

print("all ok")