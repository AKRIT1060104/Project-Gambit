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
	
	
	def __init__(self):
		self.who_to_move = "WHITE"
		self.move_history = []
		#castling rights/flags
		self.castling_rights = {"WK": True, "WQ": True, "BK": True,"BQ": True}
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
			
	#Helper methods
	
				
				
	def get_piece_colour(self,row,column):
			piece_colour = self.EMPTY
			if self.board[row][column][0] == "w":
				piece_colour = "WHITE"
			
			elif self.board[row][column][0] == "b":
				piece_colour = "BLACK"
			else:
				pass
			return piece_colour
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
		self.castling_rights.update(WK=False,WQ=False,BK=False,BQ=False)
		self.en_passant_square = None
		
		self.who_to_move = "WHITE"
		self.move_history =[]
		for i,j in enumerate(self.board):
			for k,l in enumerate(j):
				self.board[i][k] = self.EMPTY
				
	def place_piece(self,row,col,piece):
		self.board[row][col] = piece
	
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
					self.board[row_indx][col] = colour_letter + charac.upper()
					col += 1
			#whos turn
			if side == "w": self.who_to_move = "WHITE"
			else: self.who_to_move = "BLACK"
			
			#castling rights
			for ch in castling:
					if ch == "K":
						self.castling_rights["WK"] = True
					if ch == "k":
						self.castling_rights["BK"] = True
					if ch == "Q":
						self.castling_rights["WQ"] = True
					if ch == "q":
						self.castling_rights["BQ"] = True
		#enpassant
		if enpassant == "-":
			self.en_passant_square = None
		else:
			col = ord(enpassant[0]) - ord("a")
			row = 8 - int(enpassant[1])
			self.en_passant_square = (row,col)
		
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

		print("Total:",sum(results.values()))		
#finds the king and gives the row,col
	def find_king(self,colour):
		for row,i in enumerate(self.board):
			for col,element in enumerate(i):
				if self.get_piece_type(row,col) == "K" and self.get_piece_colour(row,col) == colour:
					return row,col
					
	#checks if a square is attacked and can my king move there
	def is_attacked(self,square):
		for move in self.pseudo_move_generator():
			if (move.to_row ,move.to_col) == square:
				return True
		return False
		
		#checks if a square is attacked by a colour (works on empty squares too)
	def square_attacked(self,row,col,by_colour):
		knight_offsets = [(2, 1),(2, -1),(-2, 1),(-2, -1),(1, 2),(1, -2),(-1, 2),(-1,-2)]
		king_offsets = [(1, 0),(-1, 0),(0, 1),(0, -1),(1, 1),(1, -1),(-1, 1),(-1,-1)]
		bishop_offsets = [(1, 1),(1, -1),(-1, 1),(-1,-1)]
		rook_offsets = [(1, 0),(-1, 0),(0, 1),(0,-1)]
		
		#knights
		for dr,dc in knight_offsets:
			r, c = row + dr, col + dc
			if 0 <= r < 8 and 0 <= c < 8:
				if self.get_piece_type(r,c) == "N" and self.get_piece_colour(r,c) == by_colour:
					return True
		
		#king
		for dr,dc in king_offsets:
			r, c = row + dr, col + dc
			if 0 <= r < 8 and 0 <= c < 8:
				if self.get_piece_type(r,c) == "K" and self.get_piece_colour(r,c) == by_colour:
					return True
		
		#pawns
		if by_colour == "WHITE":
			pawn_row = row + 1
		else:
			pawn_row = row - 1
		
		for side in [-1, 1]:
			c = col + side
			if 0 <= pawn_row < 8 and 0 <= c < 8:
				if self.get_piece_type(pawn_row,c) == "P" and self.get_piece_colour(pawn_row,c) == by_colour:
					return True
		
		#straight lines (rook or queen)
		for dr,dc in rook_offsets:
			r, c = row + dr, col + dc
			while 0 <= r < 8 and 0 <= c < 8 and self.get_piece_type(r,c) == self.EMPTY:
				r += dr
				c += dc
			if 0 <= r < 8 and 0 <= c < 8:
				if self.get_piece_colour(r,c) == by_colour and self.get_piece_type(r,c) in ("R","Q"):
					return True
		
		#diagonals (bishop or queen)
		for dr,dc in bishop_offsets:
			r, c = row + dr, col + dc
			while 0 <= r < 8 and 0 <= c < 8 and self.get_piece_type(r,c) == self.EMPTY:
				r += dr
				c += dc
			if 0 <= r < 8 and 0 <= c < 8:
				if self.get_piece_colour(r,c) == by_colour and self.get_piece_type(r,c) in ("B","Q"):
					return True
		
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
		if moves:
			if self.is_in_check(self.who_to_move):
				return "check"
			return "playing"
		if self.is_in_check(self.who_to_move):
			return "checkmate"
		return "stalemate"
				
		
		
#move logic
	
	def make_move(self,move):
			target_piece = self.get_piece(move.from_row,move.from_col)
			target_piece_colour = self.get_piece_colour(move.from_row,move.from_col)
			
			#special moves saves 
			move.saved_rights = self.castling_rights.copy()
			move.saved_enpassant = self.en_passant_square
			
			if target_piece == self.EMPTY or [move.to_row,move.to_col] == [move.from_row,move.from_col]:
				return False
			elif self.who_to_move != target_piece_colour:
				return False
			else:
				self.move_history.append(move)
				move.captured_piece = self.board[move.to_row][move.to_col]
				#enpassant capture
				if move.is_enpassant:
					move.captured_piece = self.board[move.from_row][move.to_col]
					self.board[move.from_row][move.to_col] = self.EMPTY
					self.board[move.from_row][move.from_col] = self.EMPTY
				else:
					move.captured_piece = self.board[move.to_row][move.to_col]
				move.moving_piece = target_piece
				self.board[move.to_row][move.to_col] = target_piece
				self.board[move.from_row][move.from_col] = self.EMPTY
				
				#priomotion 
				if move.promotion != None:
					self.board[move.to_row][move.to_col] = move.promotion
				
				#castling
				if target_piece[1] == "K":
					#Rook moves for castling
					if move.is_castle:
						row = move.from_row
						if move.to_col == 6: #kingside
							self.board[row][7] = self.EMPTY
							self.board[row][5] = target_piece_colour[0].lower()+ "R"
						else: #queenside
							self.board[row][0] = self.EMPTY
							self.board[row][3] = target_piece_colour[0].lower()+"R"
						
							
					
					if target_piece_colour == "WHITE":
						self.castling_rights.update(WK=False,WQ=False)
					else:
						self.castling_rights.update(BK=False,BQ=False)
				#each corner belongs to exactly one castling right
				corner_rights = {(7,7):"WK",(7,0):"WQ",(0,7):"BK",(0,0):"BQ"}
				
				for corner,right in corner_rights.items():
					if (move.from_row,move.from_col) == corner or (move.to_row,move.to_col) == corner:
						self.castling_rights[right] = False
						
						
				#enpassant
				if target_piece[1] == "P" and abs(move.from_row-move.to_row) == 2:
					row_between = (move.from_row+move.to_row) // 2
					self.en_passant_square = (row_between,move.from_col)
				else:
					self.en_passant_square = None
				

				
				if target_piece_colour == "WHITE":
					self.who_to_move = 'BLACK'
				else:
					self.who_to_move = "WHITE"
				return True
				
	def undo_move(self):
			if self.move_history == []:
				return False
			else:
				history = self.move_history[-1]
				target_piece_colour = history.moving_piece
				self.board[history.from_row][history.from_col] = history.moving_piece
				self.board[history.to_row][history.to_col] = history.captured_piece
				self.move_history.pop()
				
				#undo special moves flags
				self.castling_rights = history.saved_rights.copy()
				self.en_passant_square = history.saved_enpassant
				
				if history.is_castle:
						row = history.from_row
						if history.to_col == 6: #kingside
							self.board[row][5] = self.EMPTY
							self.board[row][7] = target_piece_colour[0].lower()+ "R"
						else: #queenside
							self.board[row][3] = self.EMPTY
							self.board[row][0] = target_piece_colour[0].lower()+"R"
				#enpassant
				if history.is_enpassant:
					self.board[history.to_row][history.to_col] = self.EMPTY
					self.board[history.from_row][history.to_col] = history.captured_piece
				
			
				if self.who_to_move == "WHITE":
					self.who_to_move = "BLACK"
				else:
					self.who_to_move = "WHITE"
				return True
			
	
	
	def pseudo_move_generator(self):
			moves = []
			
			for indx_row,row in enumerate(self.board):
				for indx_col,col_element in enumerate(row):
					if self.get_piece_colour(indx_row,indx_col) != self.who_to_move or col_element == self.EMPTY:
						continue
						
					else:
						piece_type = self.get_piece_type(indx_row,indx_col)
						piece_colour = self.get_piece_colour(indx_row,indx_col)
						
						#knight moves
						if piece_type == "N":
							moves.extend(self.knight_moves(indx_row,indx_col))
						elif piece_type == "K":
							moves.extend(self.king_moves(indx_row,indx_col))
						elif piece_type == "B":
							moves.extend(self.bishop_moves(indx_row,indx_col))
						elif piece_type == "Q":
							moves.extend(self.queen_moves(indx_row,indx_col))
						elif piece_type == "R":
							moves.extend(self.rook_moves(indx_row,indx_col))
						elif piece_type == "P":
							moves.extend(self.pawn_moves(indx_row,indx_col))
			return moves
							
						
#legal move generator
	def legal_moves(self):
		legal_moves = []
		mover = self.who_to_move
		if mover == "WHITE":
			enemy = "BLACK"
		else:
			enemy = "WHITE"
		for move in self.pseudo_move_generator():
			self.make_move(move)
			king_row,king_col = self.find_king(mover)
			if not self.square_attacked(king_row,king_col,enemy):
				legal_moves.append(move)
			self.undo_move()
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
			moves = []
			offsets = [(1, 1),(1, -1),(-1, 1),(-1,-1)]

			for o_row,o_col in offsets:
				to_row = row + o_row
				to_col = col + o_col

				while 0 <= to_row < 8 and 0<= to_col <8:
					piece_colour = self.get_piece_colour(to_row,to_col)
					if piece_colour == self.who_to_move:
						break
					elif piece_colour == self.EMPTY:
						moves.append(Move(row,col,to_row,to_col))
					else:
						moves.append(Move(row,col,to_row,to_col))
						break
					to_row += o_row
					to_col += o_col
			return moves
	#rook move gen
	def rook_moves (self,row,col):
			moves = []
			offsets = [(1, 0),(-1, 0),(0, 1),(0,-1)]

			for o_row,o_col in offsets:
				to_row = row + o_row
				to_col = col + o_col

				while 0 <= to_row < 8 and 0<= to_col <8:
					piece_colour = self.get_piece_colour(to_row,to_col)
					if piece_colour == self.who_to_move:
						break
					elif piece_colour == self.EMPTY:
						moves.append(Move(row,col,to_row,to_col))
					else:
						moves.append(Move(row,col,to_row,to_col))
						break
					to_row += o_row
					to_col += o_col
			return moves
	#queen move gen
	def queen_moves (self,row,col):
			moves = []
			offsets = [(1, 0),(-1, 0),(0, 1),(0, -1),(1, 1),(1, -1),(-1, 1),(-1,-1)]

			for o_row,o_col in offsets:
				to_row = row + o_row
				to_col = col + o_col

				while 0 <= to_row < 8 and 0<= to_col <8:
					piece_colour = self.get_piece_colour(to_row,to_col)
					if piece_colour == self.who_to_move:
						break
					elif piece_colour == self.EMPTY:
						moves.append(Move(row,col,to_row,to_col))
					else:
						moves.append(Move(row,col,to_row,to_col))
						break
					to_row += o_row
					to_col += o_col
			return moves
	
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
			prefix = "W"
			rook = "wR"
		else:
			enemy = "WHITE"
			home_row = 0
			prefix = "B"
			rook = "bR"
		if (row,col) != (home_row,4): return moves
		if self.square_attacked(home_row,4,enemy): return moves
		
		# one entry per side. Each says:
   	 # which right, where the rook starts, which columns must be empty,
    	# which columns the king passes or lands on (must be safe), king's target column
		options = [(prefix + "K", 7 , [5, 6], [5, 6], 6),
						   (prefix + "Q", 0 , [1, 2, 3],[3, 2], 2)]
		for (right,rook_col,empty_col,safe_col,king_to) in options:
				if self.castling_rights[right] == False: continue
				if self.board[home_row][rook_col] != rook: continue
				if any(self.board[home_row][c] != self.EMPTY for c in empty_col): continue
				if any(self.square_attacked(home_row,c,enemy) for c in safe_col): continue
				moves.append(Move(home_row,4,home_row,king_to,is_castle=True))
		return moves
				
								
											
														
																	
																				
																							
																													
#MOVE CLASS EXPLICITLY FOR STORAGE OF MOVE AND PIECE CAPTURE HISTORY			
class Move:
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
	def __repr__(self):
	           return (f"Move(({self.from_row}, {self.from_col})"
	           f" -> ({self.to_row}, {self.to_col},{self.promotion}))"
	           )
