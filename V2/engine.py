from eval import evaluate
import random

#-----the search-------
MATE = 100000
INF = float("inf")


def minimax(game,depth,alpha,beta):
	
	if depth == 0:
		return evaluate(game.board)
	
		
		
	moves = game.legal_moves()
	
	
	
	if not moves:
		if game.is_in_check(game.who_to_move):
			if game.who_to_move == "WHITE": return -MATE - depth
			else: return +MATE + depth
		return 0
		
	
	
	
	if game.who_to_move == "WHITE":
		best = -float("inf")
		for move in moves:
			game.make_move(move)
			best = max(best,minimax(game,depth - 1,alpha,beta))
			alpha = max(best,alpha)
			game.undo_move()
			if alpha >= beta:
				break
		return best
	else:
		best = float("inf")
		for move in moves:
			game.make_move(move)
			best = min(best,minimax(game,depth - 1,alpha,beta))
			beta = min(best,beta)
			game.undo_move()
			if alpha >= beta:
				break
		return best

def best_move(game,depth):
	best_moves = []
	mover = game.who_to_move
	best_score = (-float("inf") if mover == "WHITE" else float("inf"))
	
	legal = game.legal_moves()
	if not legal:
		return None
	for move in game.legal_moves():
		game.make_move(move)
		score = minimax(game,depth-1,-INF,INF)
		game.undo_move()
		if mover == "WHITE":
			if score > best_score:
				best_score = score
				best_moves = [move]
			elif score == best_score:
				best_moves.append(move)
			
		else:
			if score < best_score:
				best_score = score
				best_moves = [move]
			elif score == best_score:
				best_moves.append(move)
				
		#looks at captures in equal moves and picks those 
	captures = [m for m in best_moves if game.board[m.to_row][m.to_col] != game.EMPTY]
	if captures:
		return random.choice(captures)
	
	return random.choice(best_moves)


	
		

			
	