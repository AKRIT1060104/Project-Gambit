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
			
	def get_piece_colour(self,row,column):
			piece_colour = None 
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
	
	def make_move(self,move):
			target_piece = self.get_piece(move.from_row,move.from_col)
			target_piece_colour = self.get_piece_colour(move.from_row,move.from_col)
			if target_piece == self.EMPTY or [move.to_row,move.to_col] == [move.from_row,move.from_col]:
				return False
			if self.who_to_move != target_piece_colour or target_piece_colour == None:
				return False
			else:
				self.move_history.append(move)
				move.captured_piece = self.board[move.to_row][move.to_col]
				move.moving_piece = target_piece
				self.board[move.to_row][move.to_col] = target_piece
				self.board[move.from_row][move.from_col] = self.EMPTY
				
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
				self.board[history.from_row][history.from_col] = history.moving_piece
				self.board[history.to_row][history.to_col] = history.captured_piece
				self.move_history.pop()
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
						
						#knight moves
						if self.get_piece_type(indx_row,indx_col) == "N":
							moves.extend(self.knight_moves(indx_row,indx_col))
						if self.get_piece_type(indx_row,indx_col) == "K":
							moves.extend(self.king_moves(indx_row,indx_col))
						

							
							

			
											
			return moves								
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

	def king_moves(self,row,col):
		moves = []
		offsets = [(1, 0),(-1, 0),(0, 1),(0, -1),(1, 1),(1, -1),(-1, 1),(-1,-1)]
	
		for o_row, o_col in offsets:
			to_row = row + o_row
			to_col = col + o_col
		
			if 0 <= to_row < 8 and 0<= to_col <8:
				if self.get_piece_colour(to_row,to_col) != self.who_to_move:
					
					moves.append(Move(row,col,to_row,to_col))	
					
		return moves

	#bishop move gen
	def bishop_move (self,row,col):
			moves = []
							
						
						
						
					
				
				
				
			

			
#MOVE CLASS EXPLICITLY FOR STORAGE OF MOVE AND PIECE CAPTURE HISTORY			
class Move:
	def __init__(self,from_row,from_col,to_row,to_col):
			self.from_row = from_row
			self.from_col = from_col
			self.to_row = to_row
			self.to_col = to_col	
			self.captured_piece = None
			self.moving_piece = None
	def __repr__(self):
        	return (
            f"Move(({self.from_row}, {self.from_col})"
            f" -> ({self.to_row}, {self.to_col}))"
        )
			
					
		
							   
game = Chessboard()
#print(game.get_piece_colour(3,3))
#print(game.get_piece(0,3))
move = Move(7,1,3,3)
move2 = Move(1,0,5,3)
move3 = Move(6,3,4,3)
#game.make_move(move)
#game.make_move(move2)
#game.make_move(move3)
#game.display_board()
#print(game.who_to_move)

game.undo_move()
game.undo_move()
game.undo_move()
game.display_board()
print(game.who_to_move)
print(game.get_piece_type(7,1))
print(game.pseudo_move_generator())

game.make_move(move)
game.display_board()
game.make_move(game.pseudo_move_generator()[0])
game.make_move(game.pseudo_move_generator()[0])
game.display_board()

#for i in range(10):
#	game.make_move(game.	pseudo_move_generator()[0])
#	game.make_move(game.pseudo_move_generator()[0])
#	game.display_board()




	
