import random

PIECES = ("wP", "wN", "wB", "wR", "wQ", "wK","bP", "bN", "bB", "bR", "bQ", "bK",)

#bits for clasting
WK_BIT = 1 #0001
WQ_BIT = 2 #0010
BK_BIT = 4 #0100
BQ_BIT = 8 #1000
ALL_CASTLE_BIT = 15 #1111

#Zobrist hash table
_rng = random.Random(161416) #for module use so _

#zpiece[piece][row][col] to 64 bit int
Z_PIECE = {
	p: [[_rng.getrandbits(64) for _ in range(8)] for _ in range(8)] 
	for p in PIECES
	}
	
Z_CASTLE = [_rng.getrandbits(64) for _ in range(16)]
Z_EP = [[_rng.getrandbits(64) for _ in range(8)]for _ in range(8)]
Z_SIDE = _rng.getrandbits(64)

#updating castle mask 

CASTLE_MASK = [[ALL_CASTLE_BIT for _ in range(8)]for _ in range(8)] #creates a 8x8 grid with all 15 ie 1111 in binary

CASTLE_MASK[7][7] &= ~WK_BIT # h1 rook
CASTLE_MASK[7][0] &= ~WQ_BIT # a1 rook
CASTLE_MASK[7][4] &= ~(WK_BIT | WQ_BIT)# e1 king
CASTLE_MASK[0][7] &= ~BK_BIT # h8 rook
CASTLE_MASK[0][0] &= ~BQ_BIT  # a8 rook
CASTLE_MASK[0][4] &= ~(BK_BIT | BQ_BIT)# e8 king

# --- 3. PRE-COMPUTED ATTACK & RAY TABLES (Step 4) ---
_KNIGHT_OFFSETS = ((2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2))
_KING_OFFSETS   = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))
_ROOK_OFFSETS     = ((1, 0), (-1, 0), (0, 1), (0, -1))
_BISHOP_OFFSETS   = ((1, 1), (1, -1), (-1, 1), (-1, -1))

KNIGHT_TARGETS = [[() for _ in range(8)] for _ in range(8)]
KING_TARGETS   = [[() for _ in range(8)] for _ in range(8)]
ROOK_RAYS      = [[() for _ in range(8)] for _ in range(8)]
BISHOP_RAYS    = [[() for _ in range(8)] for _ in range(8)]
QUEEN_RAYS     = [[() for _ in range(8)] for _ in range(8)]

PAWN_ATTACKER = {
	"WHITE" : [[() for _ in range(8)]for _ in range(8)],
	"BLACK" : [[() for _ in range(8)]for _ in range(8)]
}

STRAIGHT_DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1)) #orthogonal btw
GAY_DIRS   = ((1, 1), (1, -1), (-1, 1), (-1, -1)) #diagonal btw

for r in range(8):
	for c in range(8):
		#tuple for each PIECE move available so we can have faster hash gen cause we can use moves to just calculate hash faster than recaling it
		KNIGHT_TARGETS[r][c] = tuple((r+dr,c+dc)for dr,dc in _KNIGHT_OFFSETS
		if 0 <= r + dr < 8 and 0 <= c + dc < 8 
	) 
		KING_TARGETS[r][c] = tuple((r+dr,c+dc)for dr,dc in _KING_OFFSETS
		if 0 <= r + dr < 8 and 0 <= c + dc < 8 
	)
		PAWN_ATTACKER["WHITE"][r][c] = tuple((r+1,c+dc) for dc in (-1, 1)
		if 0 <= r + 1 < 8 and 0 <= c + dc < 8 
	)
		PAWN_ATTACKER["BLACK"][r][c] = tuple((r-1,c+dc) for dc in (-1, 1)
		if 0 <= r + 1 < 8 and 0 <= c + dc < 8 
	)
		#for sliding pieces
		r_rays = []
		for dr,dc in _ROOK_OFFSETS:
			ray = []
			nr, nc = r+dr,c+dc
			while 0 <= nr < 8 and 0 <= nc < 8 :
				ray.append((nr,nc))
				nr += dr
				nc += dc
				
			if ray:
				r_rays.append(tuple(ray))
					
		ROOK_RAYS[r][c] = tuple(r_rays)
		
		b_rays = []
		for dr,dc in _BISHOP_OFFSETS:
			ray = []
			nr, nc = r+dr,c+dc
			while 0 <= nr < 8 and 0 <= nc < 8 :
				ray.append((nr,nc))
				nr += dr
				nc += dc
				
			if ray:
				b_rays.append(tuple(ray))
					
		BISHOP_RAYS[r][c] = tuple(b_rays)
		QUEEN_RAYS[r][c] = BISHOP_RAYS[r][c] + ROOK_RAYS[r][c]
		
		
#compute the hash using everthibg we have 
def compute_hash(game):
	h = 0
	board = game.board
	empty = game.EMPTY
	
	for r in range(8):
		row = board[r]
		
		for c in range(8):
			piece = row[c]
			
			if piece != empty:
				h ^= Z_PIECE[piece][r][c]
				
		
	h ^= Z_CASTLE[game.castling_rights]
	
	if game.en_passant_square != None:
		er,ec = game.en_passant_square
		
		h ^= Z_EP[er][ec]
	if game.who_to_move == "BLACK":
		h ^= Z_SIDE
		
	return(h)
				

		
	
	




