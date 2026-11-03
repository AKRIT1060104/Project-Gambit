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
		if 0 <= r - 1 < 8 and 0 <= c + dc < 8 
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