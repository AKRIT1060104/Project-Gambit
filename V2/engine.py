from eval import evaluate_relative,PIECE_VALUE
import random

#-----the search-------
MATE = 100000
INF = 10000000 #10 milli

class Engine:
	
	def __init__(self,depth=3):
		self.default_depth = depth
		self.nodes_searched = 0
		
		self.contempt = 25
		self.root_colour = "BLACK"
		
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
		
	def get_draw_score(self,game):
		return -self.contempt if self.root_colour == game.who_to_move else self.contempt
		
	def quiescence(self,game,alpha,beta,ply,q_depth = 0):
		
		in_check = game.is_in_check(game.who_to_move)
		side = game.who_to_move
		enemy = "WHITE" if side == "BLACK" else "BLACK"
		self.nodes_searched += 1
		if q_depth >= 12:
				return alpha
		
	
		
		if not in_check:
			stand_pat = evaluate_relative(game)
			
			if stand_pat >= beta: #position too good for them to allow that move
				return beta
				
			if stand_pat > alpha:
				alpha = stand_pat
				
				
		legal_moves_found = False
		
		if in_check:
			moves = game.pseudo_move_generator()
		else:
			moves = game.capture_moves()
		
		moves.sort(key=lambda m: self.score_moves(game,m,ply), reverse=True)
		kr, kc = game.find_king(side)
		for move in moves:
			if not in_check and move.promotion is None:
				victim = game.board[move.to_row][move.to_col]
				gain = PIECE_VALUE[victim[1]] if victim != game.EMPTY else 100
				if stand_pat + gain + 200 < alpha:
					continue
					
			fr,fc = move.from_row, move.from_col
			is_king_move = (fr, fc) == (kr, kc)
			aligned = (fr == kr) or (fc == kc) or (abs(fr - kr) == abs(fc - kc))
			needs_test = in_check or is_king_move or aligned or move.is_enpassant
			game.make_move(move)
			if needs_test:
				kr2, kc2 = game.find_king(side)      # moved if it's a king move
				if game.square_attacked(kr2, kc2, enemy):
					game.undo_move()
					
					continue	
			legal_moves_found = True
			
			score = -self.quiescence(game, -beta, -alpha, ply=ply+1,q_depth=q_depth + 1)
			game.undo_move()
			
			
			if score >= beta:
				return beta
			if score > alpha:
				alpha = score
				
		if in_check and not legal_moves_found:
			return -MATE + ply
			
				
		return alpha
			
	def nega_Max(self,game,depth,alpha,beta,ply):
		
		self.nodes_searched += 1
		
		if ply > 0:
			if game.halfmove_clock >= 100 or game.repitition(count=2) or game.is_insufficient_material():
				return self.get_draw_score(game)
			
		# keep searchibg if in check
		in_check = game.is_in_check(game.who_to_move)
		side = game.who_to_move
		enemy = "WHITE" if side == "BLACK" else "BLACK"
		if in_check and ply < 12:
			depth += 1
		if depth == 0:
			return self.quiescence(game, alpha, beta, ply)
		
		moves = game.pseudo_move_generator()
		#sorts the moves in decending order of their score		
		moves.sort(key=lambda m: self.score_moves(game,m,ply), reverse=True)
		
		legal_count = 0
		best_score = -INF
		
		
		kr ,kc = game.find_king(side)
		for move in moves:
			fr,fc = move.from_row, move.from_col
			is_king_move = (fr, fc) == (kr, kc)
			aligned = (fr == kr) or (fc == kc) or (abs(fr - kr) == abs(fc - kc))
			needs_test = in_check or is_king_move or aligned or move.is_enpassant
			game.make_move(move)
			if needs_test:
				kr2, kc2 = game.find_king(side)      # moved if it's a king move
				if game.square_attacked(kr2, kc2, enemy):
					game.undo_move()
					
					continue	
			legal_count += 1
			score = -self.nega_Max(game,depth-1,-beta , -alpha , ply+1)
			game.undo_move()
			if score > best_score:
				best_score = score
			if score > alpha:
				alpha = score
			if alpha >= beta:
				break
		if legal_count == 0:
			if in_check:
				return -MATE + ply #checkmate closer ply = faster mate
			return self.get_draw_score(game) #stalemate
				#because negamax works on the principle that score(a) = -score(b) so after one move it should flip to the opponent side so the negative sign
			
			
		return best_score
		
	def get_best_move(self,game,depth=None):
		
		if depth == None:
			depth = self.default_depth
		
		self.nodes_searched = 0
		self.root_colour = game.who_to_move
		
		
		
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
