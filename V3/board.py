from zobrist_hash import (Z_PIECE, Z_CASTLE, Z_EP, Z_SIDE, CASTLE_MASK,compute_hash, WK_BIT, WQ_BIT, BK_BIT, BQ_BIT)
from tables import KNIGHT_TARGETS, KING_TARGETS, ROOK_RAYS, BISHOP_RAYS, QUEEN_RAYS,PAWN_ATTACKER
from eval import PSQT,evaluate


class Chessboard:
	EMPTY = 'O'
	
	WHITE_ROOK = "wR"
	WHITE_KNIGHT = "wN"
	WHITE_BISHOP = "wB"
	WHITE_QUEEN = "wQ"
	WHITE_KING = "wK"
	WHITE_PAWN = "wP"
	
	BLACK_ROOK = "bR"
	BLACK_KNIGHT = "bN"
	BLACK_BISHOP = "bB"
	BLACK_QUEEN = "bQ"
	BLACK_KING = "bK"
	BLACK_PAWN = "bP"
	
	#sliding pieces offsets
	KNIGHT_OFFSETS = ((2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2))
	KING_OFFSETS   = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))
	BISHOP_OFFSETS = ((1, 1), (1, -1), (-1, 1), (-1, -1))
	ROOK_OFFSETS   = ((1, 0), (-1, 0), (0, 1), (0, -1))
	CORNER_RIGHTS  = {(7, 7): "WK", (7, 0): "WQ", (0, 7): "BK", (0, 0): "BQ"}
	
	
	def __init__(self):
		self.who_to_move = "WHITE"
		self.move_history = []
		
		#kings square cache
		self.white_king_square = (7,4)
		self.black_king_square = (0,4)
		
		#castling rights/flags
		self.castling_rights = 15
		
		
		
		#W/B is the colour and K/Q is kingside or queen side
		
		#en passant flags
		self.en_passant_square = None

		self.board = [[self.EMPTY for _ in range(8)]for _ in range (8)]
		#white side
		self.board[7][0]= self.WHITE_ROOK
		self.board[7][7]= self.WHITE_ROOK
		self.board[7][1]= self.WHITE_KNIGHT
		self.board[7][6]= self.WHITE_KNIGHT
		self.board[7][2]= self.WHITE_BISHOP
		self.board[7][5]= self.WHITE_BISHOP
		self.board[7][3]= self.WHITE_QUEEN
		self.board[7][4]= self.WHITE_KING
		for _ in range(8):
			self.board[6][_] = self.WHITE_PAWN
		#black side 
		self.board[0][0]= self.BLACK_ROOK
		self.board[0][7]= self.BLACK_ROOK
		self.board[0][1]= self.BLACK_KNIGHT
		self.board[0][6]= self.BLACK_KNIGHT
		self.board[0][2]= self.BLACK_BISHOP
		self.board[0][5]= self.BLACK_BISHOP
		self.board[0][3]= self.BLACK_QUEEN
		self.board[0][4]= self.BLACK_KING
		for _ in range(8):
			self.board[1][_] = self.BLACK_PAWN
			
		#halfmove clock
		self.halfmove_clock = 0
		self.state_history = [self.get_state_key()]
		
		self.hash = compute_hash(self)
		self.eval_score = evaluate(self)
		self.state_history = [self.hash]
	#Helper methods
	
				
				
	def get_piece_colour(self, row, column):
		p = self.board[row][column]
		if p == self.EMPTY:
			return self.EMPTY
		return "WHITE" if p[0] == "w" else "BLACK"
	def get_piece(self,row,column):
			piece_type = None
			if self.board[row][column][0] == self.EMPTY:
				piece_type = self.EMPTY
			else:
				piece_type = self.board[row][column]
			return piece_type
	def get_piece_type(self,row,column):
			piece_type = None
			if self.board[row][column][0] == self.EMPTY:
				piece_type = self.EMPTY
			else:
				piece_type = self.board[row][column][1]
			return piece_type
			
	#displays the board
	def display_board(self):
		for i , row in enumerate(self.board):
			#makes it align using piece:2 makes sure each elemnt has a padding of 2 
			print(f"{8-i}  " + "  ".join(f"{piece:2}"for piece in row))
		print("\n","   a   b   c   d   e   f   g   h")
	
	def clear_board(self):
		self.castling_rights = 0
		self.en_passant_square = None
		
		self.who_to_move = "WHITE"
		self.move_history =[]
		
		self.halfmove_clock = 0
		self.eval_score = 0
		self.state_history = []
		for i,j in enumerate(self.board):
			for k,l in enumerate(j):
				self.board[i][k] = self.EMPTY
				
	def place_piece(self,row,col,piece):
		self.board[row][col] = piece
		
		#updates the kings position
		if piece == self.WHITE_KING:
			self.white_king_square = (row,col)
		elif piece == self.BLACK_KING:
			self.black_king_square = (row,col)
	
	def load_fen(self,fen):
		self.clear_board()
		parts = fen.split()
		placement = parts[0]
		side = parts[1]
		castling = parts[2]
		enpassant = parts[3]
		
		#pieces
		rows = placement.split("/")
		for row_indx, row_element in enumerate(rows):
			col = 0
			for charac in row_element:
				if charac.isdigit():
					col = col + int(charac)
				else:
					colour_letter = "w" if charac.isupper() else "b"
					piece = colour_letter + charac.upper()
					self.board[row_indx][col] = piece
					
					if piece == self.WHITE_KING:
						self.white_king_square = (row_indx,col)
					elif piece == self.BLACK_KING:
						self.black_king_square = (row_indx,col)
					col += 1
		#whos turn
		if side == "w": self.who_to_move = "WHITE"
		else: self.who_to_move = "BLACK"
			
		#castling rights
		for ch in castling:
				if ch == "K":
						self.castling_rights |= WK_BIT
				if ch == "k":
						self.castling_rights |= BK_BIT
				if ch == "Q":
						self.castling_rights |= WQ_BIT
				if ch == "q":
						self.castling_rights |= BQ_BIT
		#enpassant
		if enpassant == "-":
			self.en_passant_square = None
		else:
			col = ord(enpassant[0]) - ord("a")
			row = 8 - int(enpassant[1])
			self.en_passant_square = (row,col)
			
		#halfmove clock
		self.halfmove_clock = int(parts[4]) if len(parts)>4 else 0
		self.hash = compute_hash(self)
		self.eval_score = evaluate(self)
		self.state_history = [self.hash]
		
	def divide_perft(self,depth):
		results = {}

		for move in self.legal_moves():
			from_square = (
				chr(move.from_col + ord("a")) +
				str(8 - move.from_row)
			)
			to_square = (
				chr(move.to_col + ord("a")) +
				str(8 - move.to_row)
			)

			move_name = from_square + to_square

			if move.promotion is not None:
				move_name += move.promotion[1].lower()

			self.make_move(move)
			results[move_name] = self.perft(depth-1)
			self.undo_move()

		for move,nodes in sorted(results.items()):
			print(f"{move}: {nodes}")

		print("Total:",sum(results.values()))
#finds the king and gives the row,col
	def find_king(self,colour):
		if colour == "WHITE":
			return self.white_king_square
		return self.black_king_square
					
		#checks if a square is attacked by a colour (works on empty squares too)
	def square_attacked(self,row,col,by_colour):
		board = self.board
		empty = self.EMPTY
		
		p = "w" if by_colour == "WHITE" else 'b'
		N = p + "N"
		K = p + "K"
		P = p + "P"
		R = p + "R"
		B = p + "B"
		Q = p + "Q"
		
		#knights
		for r,c in KNIGHT_TARGETS[row][col]:
			if board[r][c] == N:
				return True
		#kings
		for r,c in KING_TARGETS[row][col]:
			if board[r][c] == K:
				return True
		#pawns
		for r,c in PAWN_ATTACKER[by_colour][row][col]:
			if board[r][c] == P:
				return True
				
		#rooks and queen
		for ray in ROOK_RAYS[row][col]:
			for r , c in ray:
				piece = board[r][c]
				
				if piece == empty:
					continue
				if piece == R or piece == Q:
					return True
				break
		#bishop and queen 
		for ray in BISHOP_RAYS[row][col]:
			for r , c in ray:
				piece = board[r][c]
				if piece == B or piece == Q:
					return True
				if piece != empty:
					break
				
		return False
		
#perft test
	def perft(self,depth):
		if depth == 0:
			return 1
		total = 0
		for move in self.legal_moves():
			self.make_move(move)
			total += self.perft(depth-1)
			self.undo_move()
		return total

	def is_in_check(self,colour):
		king_row,king_col = self.find_king(colour)
		
		enemy = "BLACK" if colour == "WHITE" else "WHITE"
		
		return self.square_attacked(king_row,king_col,enemy)
	
	def game_status(self):
		
		moves = self.legal_moves()
		in_check = self.is_in_check(self.who_to_move)
		if not moves:
			if in_check:
				return "checkmate"
			else:
				return "stalemate"
		if self.halfmove_clock >= 100:
			return "draw_50_moves"
		if self.repitition(count=3):
			return "draw_by_repition"
		if self.is_insufficient_material():
			return "draw_insufficient_material"
		if moves:
			if in_check:
				return "check"
			return "playing" 

		
	def clone(self):
		new_game = Chessboard.__new__(Chessboard)
		new_game.board = [row.copy() for row in self.board]
		new_game.who_to_move = self.who_to_move
		new_game.move_history = self.move_history.copy()
		new_game.castling_rights = self.castling_rights
		new_game.en_passant_square = self.en_passant_square
		new_game.white_king_square = self.white_king_square
		new_game.black_king_square = self.black_king_square
		new_game.halfmove_clock = self.halfmove_clock
		new_game.hash = self.hash
		new_game.eval_score = self.eval_score
		new_game.state_history = self.state_history.copy()
		
		
		return new_game
		
	def hash_check(self, depth):
		if depth == 0: return
		for m in self.legal_moves():
			self.make_move(m)
			assert self.hash == compute_hash(self), m
			self.hash_check(depth-1)
			self.undo_move()
		assert self.hash == compute_hash(self)
		
	def sliding_moves(self,row,col,rays,piece,me):
			board = self.board
			moves=[]
			
			for ray in rays:
				for tr,tc in ray:
					target = board[tr][tc]
					
					if target == self.EMPTY:
						moves.append(Move(row,col,tr,tc))
						continue
					if target[0] != me:
						moves.append(Move(row,col,tr,tc))
						
					break
			return moves
						
			
	def get_state_key(self):
		board_tuple = tuple(tuple(row) for row in self.board)
		
		return (board_tuple, self.who_to_move, self.castling_rights, self.en_passant_square)
		
	
	def repitition(self,count=3):
		current_key = self.state_history[-1]
		if len(self.state_history) < count:
			return False
		start_idx = max(0, len(self.state_history)- 1 - self.halfmove_clock)
		hits = 0
		for i in range(len(self.state_history)-1,start_idx -1 , -2):
			if self.state_history[i] == current_key:
				hits += 1
				if hits >= count:
					return True
		return False
		
		
	def is_insufficient_material(self):
		bishops = []
		knights = {"w": 0, "b": 0}

		for r in range(8):
			for c in range(8):
				p = self.board[r][c]

				if p == self.EMPTY or p[1] == "K":
					continue

				if p[1] in ("P", "R", "Q"):
					return False

				if p[1] == "B":
					bishops.append((r + c) % 2)

				elif p[1] == "N":
					knights[p[0]] += 1

		total_knights = knights["w"] + knights["b"]

		# Bare kings or just one minor piece
		if total_knights + len(bishops) <= 1:
			return True

		# All bishops occupy the same square colour,
		# with no knights present.
		if total_knights == 0 and len(set(bishops)) == 1:
			return True

		# Two knights belonging to the same side
		# against a bare king.h
		if (total_knights == 2 and
			len(bishops) == 0 and
			2 in knights.values()):
			return True

		return False
		
				
		
		
#move logic
	
	def make_move(self, move):
		board = self.board
		empty = self.EMPTY

		fr = move.from_row
		fc = move.from_col
		tr = move.to_row
		tc = move.to_col

		p = board[fr][fc]
		mover_char = "w" if self.who_to_move == "WHITE" else "b"

		if p == empty or p[0] != mover_char or (fr == tr and fc == tc):
			return False

		is_pawn = p[1] == "P"
		is_king = p[1] == "K"
		is_ep = move.is_enpassant
		is_castle = move.is_castle

		target = board[tr][tc]
		captured = board[fr][tc] if is_ep else target
		placed = move.promotion if move.promotion else p
		rook = mover_char + "R" if is_castle else None

		move.saved_rights = self.castling_rights
		move.saved_enpassant = self.en_passant_square
		move.saved_halfmove_clock = self.halfmove_clock
		move.saved_hash = self.hash
		move.saved_eval = self.eval_score

		move.captured_piece = captured
		move.moving_piece = p

		self.move_history.append(move)

		if is_pawn or target != empty or is_ep:
			self.halfmove_clock = 0
		else:
			self.halfmove_clock += 1

		board[fr][fc] = empty

		if is_ep:
			board[fr][tc] = empty

		board[tr][tc] = placed

		if is_king:
			if mover_char == "w":
				self.white_king_square = (tr, tc)
			else:
				self.black_king_square = (tr, tc)

			if is_castle:
				if tc == 6:
					r_from, r_to = 7, 5
				else:
					r_from, r_to = 0, 3

				board[fr][r_from] = empty
				board[fr][r_to] = rook

		self.castling_rights &= (
			CASTLE_MASK[fr][fc] & CASTLE_MASK[tr][tc]
		)

		if is_pawn and abs(fr - tr) == 2:
			self.en_passant_square = ((fr + tr) // 2, fc)
		else:
			self.en_passant_square = None

		self.who_to_move = "BLACK" if mover_char == "w" else "WHITE"

		# Zobrist hash
		z_piece = Z_PIECE
		z_from = z_piece[p]
		z_placed = z_piece[placed]

		h = move.saved_hash ^ Z_SIDE
		h ^= Z_CASTLE[move.saved_rights] ^ Z_CASTLE[self.castling_rights]

		if move.saved_enpassant is not None:
			er, ec = move.saved_enpassant
			h ^= Z_EP[er][ec]

		if self.en_passant_square is not None:
			er, ec = self.en_passant_square
			h ^= Z_EP[er][ec]

		h ^= z_from[fr][fc]
		h ^= z_placed[tr][tc]

		if captured != empty:
			z_captured = z_piece[captured]

			if is_ep:
				h ^= z_captured[fr][tc]
			else:
				h ^= z_captured[tr][tc]

		if is_castle:
			h ^= z_piece[rook][fr][r_from]
			h ^= z_piece[rook][fr][r_to]

		self.hash = h
		self.state_history.append(h)

		# Incremental evaluation
		psqt = PSQT

		score = move.saved_eval
		score -= psqt[p][fr][fc]
		score += psqt[placed][tr][tc]

		if captured != empty:
			if is_ep:
				score -= psqt[captured][fr][tc]
			else:
				score -= psqt[captured][tr][tc]

		if is_castle:
			score -= psqt[rook][fr][r_from]
			score += psqt[rook][fr][r_to]

		self.eval_score = score

		return True
				
	def undo_move(self):
		if not self.move_history:
			return False

		history = self.move_history[-1]

		board = self.board
		empty = self.EMPTY

		fr = history.from_row
		fc = history.from_col
		tr = history.to_row
		tc = history.to_col

		p = history.moving_piece
		captured = history.captured_piece

		is_ep = history.is_enpassant
		is_castle = history.is_castle

		board[fr][fc] = p
		board[tr][tc] = captured

		self.move_history.pop()

		if p == self.WHITE_KING:
			self.white_king_square = (fr, fc)
		elif p == self.BLACK_KING:
			self.black_king_square = (fr, fc)

		if is_castle:
			rook = p[0] + "R"

			if tc == 6:
				r_from, r_to = 5, 7
			else:
				r_from, r_to = 3, 0

			board[fr][r_from] = empty
			board[fr][r_to] = rook

		if is_ep:
			board[tr][tc] = empty
			board[fr][tc] = captured

		self.castling_rights = history.saved_rights
		self.en_passant_square = history.saved_enpassant
		self.hash = history.saved_hash
		self.halfmove_clock = history.saved_halfmove_clock
		self.eval_score = history.saved_eval

		self.who_to_move = (
			"BLACK" if self.who_to_move == "WHITE" else "WHITE"
		)

		self.state_history.pop()

		return True
			
	
	
	def pseudo_move_generator(self):
		moves = []
		board = self.board
		empty = self.EMPTY

		white = self.who_to_move == "WHITE"
		me = "w" if white else "b"
		enemy = "b" if white else "w"

		for r, row in enumerate(board):
			for c, piece in enumerate(row):

				if piece[0] != me:
					continue

				kind = piece[1]

				# KNIGHT
				if kind == "N":
					for tr, tc in KNIGHT_TARGETS[r][c]:
						if board[tr][tc][0] != me:
							moves.append(Move(r, c, tr, tc))

				# KING
				elif kind == "K":
					for tr, tc in KING_TARGETS[r][c]:
						if board[tr][tc][0] != me:
							moves.append(Move(r, c, tr, tc))

					moves.extend(self.castle_moves(r, c))

				# PAWN
				elif kind == "P":

					direction = -1 if white else 1
					start_row = 6 if white else 1
					last_row = 0 if white else 7

					one_step = r + direction

					if 0 <= one_step < 8:

						# Forward movement
						if board[one_step][c] == empty:

							if one_step == last_row:
								for promotion in ("Q", "R", "B", "N"):
									moves.append(
										Move(r, c, one_step, c,
											promotion=me + promotion)
									)
							else:
								moves.append(Move(r, c, one_step, c))

							# Double movement
							two_step = r + 2 * direction

							if r == start_row and board[two_step][c] == empty:
								moves.append(Move(r, c, two_step, c))

						# Captures and en passant
						for dc in (-1, 1):
							cap_col = c + dc

							if not 0 <= cap_col < 8:
								continue

							target = board[one_step][cap_col]

							if target != empty and target[0] == enemy:

								if one_step == last_row:
									for promotion in ("Q", "R", "B", "N"):
										moves.append(
											Move(r, c, one_step, cap_col,
												promotion=me + promotion)
										)
								else:
									moves.append(
										Move(r, c, one_step, cap_col)
									)

							# En passant
							if (one_step, cap_col) == self.en_passant_square:
								moves.append(
									Move(r, c, one_step, cap_col,
										is_enpassant=True)
								)

				# SLIDING PIECES
				else:

					if kind == "B":
						rays = BISHOP_RAYS[r][c]

					elif kind == "R":
						rays = ROOK_RAYS[r][c]

					elif kind == "Q":
						rays = QUEEN_RAYS[r][c]

					else:
						continue

					for ray in rays:
						for tr, tc in ray:

							target = board[tr][tc]

							if target == empty:
								moves.append(Move(r, c, tr, tc))
								continue

							if target[0] == enemy:
								moves.append(Move(r, c, tr, tc))

							break

		return moves
					
					
							
						
#legal move generator
	def legal_moves(self):
		legal_moves = []
		moves = self.pseudo_move_generator()
		side = self.who_to_move
		in_check = self.is_in_check(side)

		enemy = "WHITE" if side == "BLACK" else "BLACK"
		kr, kc = self.find_king(side)

		for move in moves:
			fr, fc = move.from_row, move.from_col
			is_king_move = (fr, fc) == (kr, kc)
			aligned = (fr == kr) or (fc == kc) or (abs(fr - kr) == abs(fc - kc))
			needs_test = in_check or is_king_move or aligned or move.is_enpassant

			self.make_move(move)

			illegal = False

			if needs_test:
				kr2, kc2 = self.find_king(side)
				illegal = self.square_attacked(kr2, kc2, enemy)

			self.undo_move()

			if not illegal:
				legal_moves.append(move)

		return legal_moves
	#knight move gen
	def knight_moves(self,row,col):
		moves = []
		offsets = [(2, 1),(2, -1),(-2, 1),(-2, -1),(1, 2),(1, -2),(-1, 2),(-1,-2)]

		for o_row, o_col in offsets:
			to_row = row + o_row
			to_col = col + o_col

			if 0 <= to_row < 8 and 0<= to_col <8:
				if self.get_piece_colour(to_row,to_col) != self.who_to_move:

					moves.append(Move(row,col,to_row,to_col))

		return moves
		
#function that returns all capture moves
	def capture_moves(self):
		moves = []
		board = self.board
		EMPTY = self.EMPTY
		colour = self.who_to_move
		
		if colour == "WHITE":
			me,enemy = "w" , "b"
			direction,last_row = -1,0
		else:
			me,enemy = "b" , "w"
			direction,last_row = 1,7
		ep = self.en_passant_square
		
		for r in range(8):
			row = board[r]
			for c in range(8):
				p = row[c]
				
				if p[0] != me:
					continue
				t = p[1]
				if t == "N" or t == "K":
					targets = KNIGHT_TARGETS[r][c] if t == "N" else KING_TARGETS[r][c]
					for tr,tc in targets:
						if board[tr][tc][0] == enemy:
							moves.append(Move(r,c,tr,tc))
				elif t == "P":
					tr = r + direction
					if not (0 <= tr < 8):
						continue
					for dc in (-1, 1):
						tc = c + dc
						if 0 <= tc < 8:
							if board[tr][tc][0] == enemy:
								moves.extend(self.add_pawn_moves(r, c, tr, tc, last_row, colour))
							elif ep == (tr, tc):
								moves.append(Move(r, c, tr, tc, is_enpassant=True))
					if tr == last_row and board[tr][c] == EMPTY:
						moves.append(Move(r, c, tr, c, promotion=me + "Q"))
				else:
					if t == "B":
						rays = BISHOP_RAYS[r][c]
					elif t == "R":
						rays = ROOK_RAYS[r][c]
					else:
						rays = QUEEN_RAYS[r][c]
					for ray in rays:
						for tr, tc in ray:
							q = board[tr][tc]
							if q == EMPTY:
								continue
							if q[0] == enemy:
								moves.append(Move(r, c, tr, tc))
							break
		return moves

			
		

	#king move gen
	def king_moves(self,row,col):
		moves = []
		offsets = [(1, 0),(-1, 0),(0, 1),(0, -1),(1, 1),(1, -1),(-1, 1),(-1,-1)]

		for o_row, o_col in offsets:
			to_row = row + o_row
			to_col = col + o_col

			if 0 <= to_row < 8 and 0<= to_col <8:
				if self.get_piece_colour(to_row,to_col) != self.who_to_move:

					moves.append(Move(row,col,to_row,to_col))
		moves.extend(self.castle_moves(row,col))
		return moves

	#bishop move gen
	def bishop_moves (self,row,col):
		return self.sliding_moves(row,col,self.BISHOP_OFFSETS)
	#rook move gen
	def rook_moves (self,row,col):

		return self.sliding_moves(row,col,self.ROOK_OFFSETS)
	#queen move gen
	def queen_moves (self,row,col):
		return self.sliding_moves(row,col,self.KING_OFFSETS)
	#white pawn move gen
	def add_pawn_moves(self,row,col,to_row,to_col,last_row,colour):
		moves = []
		if to_row == last_row:
			for piece_letter in ["Q", "R", "B", "N"]:
				promotion_piece = colour[0].lower() + piece_letter
				moves.append(Move(row,col,to_row,to_col,promotion=promotion_piece))
		else:
			moves.append(Move(row,col,to_row,to_col))
		return moves
	
	def pawn_moves(self,row,col):
			moves =[]
			pawn_colour = self.get_piece_colour(row,col)
			
			if pawn_colour == "WHITE":
				direction = -1
				start_row = 6
				enemy = "BLACK"
				last_row = 0
			else:
				direction = 1
				start_row = 1
				enemy = "WHITE"
				last_row = 7
			
			#forward movement and double movement
			to_row = row + direction
			if 0 <= to_row < 8:
				if self.get_piece_type(to_row,col) == self.EMPTY:
						moves.extend(self.add_pawn_moves(row,col,to_row,col,last_row,pawn_colour))
						double_to_row = row + 2 * direction
						if row == start_row and self.get_piece_type(double_to_row,col) == self.EMPTY:
							moves.extend(self.add_pawn_moves(row,col,double_to_row,col,last_row,pawn_colour))

								
			
			#capture logic
			for diagonal in (1,-1):
				cap_row = row + direction
				cap_col = col + diagonal
				if 0<= cap_row <8 and 0<= cap_col <8:
					if self.get_piece_colour(cap_row,cap_col) == enemy:
						moves.extend(self.add_pawn_moves(row,col,cap_row,cap_col,last_row,pawn_colour))
						
					#enpassant
					if (cap_row,cap_col) == self.en_passant_square:
						moves.append(Move(row,col,cap_row,cap_col,is_enpassant=True))

			return moves
			 
	#castling move gen
	def castle_moves(self,row,col):
		moves =[]
		colour = self.who_to_move
		
		if colour == "WHITE":
			enemy = "BLACK"
			home_row = 7
			rook = "wR"
			k_bit = WK_BIT
			q_bit = WQ_BIT
		else:
			enemy = "WHITE"
			home_row = 0
			rook = "bR"
			k_bit = BK_BIT
			q_bit = BQ_BIT
		if (row,col) != (home_row,4): return moves
		if self.square_attacked(home_row,4,enemy): return moves
		# one entry per side. Each says:
		# which right (bit), where the rook starts, which columns must be empty,
		# which columns the king passes or lands on (must be safe), king's target column
		options = [(k_bit, 7, [5, 6], [5, 6], 6),
				   (q_bit, 0, [1, 2, 3], [3, 2], 2)]
		for (right,rook_col,empty_col,safe_col,king_to) in options:
				if not (self.castling_rights & right): continue
				if self.board[home_row][rook_col] != rook: continue
				if any(self.board[home_row][c] != self.EMPTY for c in empty_col): continue
				if any(self.square_attacked(home_row,c,enemy) for c in safe_col): continue
				moves.append(Move(home_row,4,home_row,king_to,is_castle=True))
		return moves
				
								
											
														
																	
																				
																							
																													
#MOVE CLASS EXPLICITLY FOR STORAGE OF MOVE AND PIECE CAPTURE HISTORY			
class Move:
	__slots__ = (
		"from_row", "from_col",
		"to_row", "to_col",
		"captured_piece", "moving_piece",
		"promotion", "is_castle",
		"saved_rights", "saved_enpassant",
		"is_enpassant", "saved_halfmove_clock",
		"saved_hash", "saved_eval"
	)
	def __init__(self,from_row,from_col,to_row,to_col,promotion=None,is_castle=False,is_enpassant=False):
			self.from_row = from_row
			self.from_col = from_col
			self.to_row = to_row
			self.to_col = to_col	
			self.captured_piece = None
			self.moving_piece = None
			self.promotion = promotion
			self.is_castle = is_castle
			self.saved_rights = None
			self.saved_enpassant = None
			self.is_enpassant = is_enpassant
			self.saved_halfmove_clock = 0
			self.saved_hash = 0
			self.saved_eval = 0
	def __repr__(self):
	           return (f"Move(({self.from_row}, {self.from_col})"
	           f" -> ({self.to_row}, {self.to_col},{self.promotion}))"
	           )
	def __eq__(self,other):
		if not isinstance(other,Move):
			return False
		return(self.from_row == other.from_row and self.from_col == other.from_col and self.to_row == other.to_row and self.to_col == other.to_col and self.promotion == other.promotion)
