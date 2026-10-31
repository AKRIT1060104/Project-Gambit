from eval import evaluate_relative,PIECE_VALUE
import random

#-----the search-------
MATE = 100000
INF = 10000000 #10 milli

class Engine:
	
	def __init__(self,depth=3):
		self.default_depth = depth
		self.nodes_searched = 0
		
		#for future purpose
		self.killer_moves = [[None , None] for _ in range(64)]
		self.transposition_table = {}
		
	def score_moves(self,game,move,ply=0):
		
		# for priotorizing mvv-lva (most valuable victim and least valuable attacker)
		score = 0
		
		target_piece = game.board[move.to_row][move.to_col]
		moving_piece = game.board[move.from_row][move.from_col]
		
		if target_piece != game.EMPTY:
			victim_val= PIECE_VALUE[target_piece[1]]
			attacker_val = PIECE_VALUE[moving_piece[1]]
			
			score += 10000 + (victim_val * 10 ) - attacker_val
		
		elif move.is_enpassant:
			score += 10000 + (PIECE_VALUE["P"] * 10)  - PIECE_VALUE["P"]
		
		if move.promotion != None:
			score += 8000 + PIECE_VALUE[move.promotion[1]]
			
		return score
			
	def nega_Max(self,game,depth,alpha,beta,ply):
		
		self.nodes_searched += 1
		
		if depth == 0:
			return evaluate_relative(game)
		
		moves = game.legal_moves()
		
		if not moves:
			if game.is_in_check(game.who_to_move):
				return -MATE + ply #checkmate closer ply = faster mate
			return 0 #stalemate
		
		#sorts the moves in decending order of their score		
		moves.sort(key=lambda m: self.score_moves(game,m,ply), reverse=True)
		
		best_score = -INF
		
		for move in moves:
			game.make_move(move)
			
			#because negamax works on the principle that score(a) = -score(b) so after one move it should flip to the opponent side so the negative sign
			score = -self.nega_Max(game,depth-1,-beta , -alpha , ply+1)
			game.undo_move()
			if score > best_score:
				best_score = score
			if score > alpha:
				alpha = score
			if alpha >= beta:
				break
			
		return best_score
		
	def get_best_move(self,game,depth=None):
		
		if depth == None:
			depth = self.default_depth
		
		self.nodes_searched = 0
		
		legal = game.legal_moves()
		
		if not legal:
			return None
			
		legal.sort(key=lambda m: self.score_moves(game,m,ply=0), reverse=True)
		best_moves = []
		best_score = -INF
		alpha = -INF
		beta = INF
		
		for move in legal:
			game.make_move(move)
			alpha = best_score -1
			score = -self.nega_Max(game,depth - 1 , -beta, -alpha , ply=1)
			game.undo_move()
			
			if score > best_score:
				best_score = score
				best_moves = [move]
				
			elif score == best_score:
				best_moves.append(move)
				
			#alpha = max(alpha,best_score)
			
		#looks at captures in equal moves and picks those 
		captures = [m for m in best_moves if game.board[m.to_row][m.to_col] != game.EMPTY or m.is_enpassant]
		if captures:
			return random.choice(captures)
		
		return random.choice(best_moves)
