import pygame
import sys
from pathlib import Path
from board import Chessboard

pygame.init()
SQUARE_SIZE = 130
BOARD_SIZE = SQUARE_SIZE * 8
screen = pygame.display.set_mode((BOARD_SIZE,BOARD_SIZE))
pygame.display.set_caption("PROJECT GAMBIT")

LIGHT = (240, 217, 181)
DARK = (181, 136, 99)

ASSET_DIR = Path(__file__).resolve().parent / "chessAssets"

#----load images------
PIECES = [
    "wK", "wQ", "wR", "wB", "wN", "wP",
    "bK", "bQ", "bR", "bB", "bN", "bP",
]
images = {}

for piece in PIECES:
	path = str(ASSET_DIR / f"{piece}.png")
	image = pygame.image.load(str(path)).convert_alpha()
	
	pygame.transform.smoothscale(image,(SQUARE_SIZE-10,SQUARE_SIZE-10))
	images[piece] = image


game = Chessboard()


def draw_board():
	checked_king = king_check_square()
	for row in range(8):
		for col in range(8):
			colour = (LIGHT if (row+col)%2 == 0
			else DARK)
			x = col * SQUARE_SIZE
			y = row * SQUARE_SIZE
			
			pygame.draw.rect(screen,colour,(x,y,SQUARE_SIZE,SQUARE_SIZE))
			#draw last move highlight
			if last_move != None:
				start = (last_move.from_row,last_move.from_col)
				end = (last_move.to_row,last_move.to_col)
				
				if (row,col) == start or (row,col) == end:
					screen.blit(last_move_overlay,(x,y))
			#check highlight draw
			if (row,col) == checked_king:
				screen.blit(check_overlay,(x,y))
			#draw the pieces
			piece = game.board[row][col]
			if piece != game.EMPTY:
				image = images[piece]
				
				rect = image.get_rect(center=(x + SQUARE_SIZE//2,y+SQUARE_SIZE//2))
				screen.blit(image,rect)
#gives selected piece moves
def piece_moves_gen(row,col):
	all_legal_moves = game.legal_moves()
	piece_moves = []
	for move in all_legal_moves:
		if (move.from_row,move.from_col) == (row,col):
			piece_moves.append(move)
	return piece_moves
#takes piece moves and gives destination row col 
def destination_squares(piece_moves):
	destination = []
	for move in piece_moves:
		destination.append((move.to_row,move.to_col))
	return destination
def draw_move_indicator():
	transparent_surface = pygame.Surface((BOARD_SIZE,BOARD_SIZE),pygame.SRCALPHA)
	for row,col in destinations:
		x = col * SQUARE_SIZE + SQUARE_SIZE//2
		y = row * SQUARE_SIZE + SQUARE_SIZE//2
		
		if game.get_piece(row,col) == game.EMPTY:
			pygame.draw.circle(transparent_surface,(0,0,0,110),(x,y),20)
		else:
			pygame.draw.circle(transparent_surface,(0,0,0,110),(x,y),SQUARE_SIZE//2 - 5,6)
	screen.blit(transparent_surface,(0,0))

def king_check_square():
	if game.is_in_check(game.who_to_move):
		return game.find_king(game.who_to_move)
	return None
	
			
		

selected_square = None
piece_moves = []
destinations = []
#lastmove highlight variables
last_move_overlay = pygame.Surface((SQUARE_SIZE,SQUARE_SIZE),pygame.SRCALPHA)
last_move_overlay.fill((255,230,0,85))
check_overlay = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
check_overlay.fill((220, 40, 40, 100))
last_move = None

game_status = 'playing'
running = True
clock = pygame.time.Clock()
while running:
		events_list = pygame.event.get()
		for events in events_list:
			if events.type == pygame.MOUSEBUTTONDOWN:
				mouse_x,mouse_y = events.pos
				row = mouse_y // 130
				col = mouse_x// 130
				
				clicked_piece = game.get_piece(row,col)
				if selected_square == None:
					if clicked_piece != game.EMPTY and game.get_piece_colour(row,col) == game.who_to_move:
						selected_square = (row,col)
						piece_moves = piece_moves_gen(row,col)
						destinations = destination_squares(piece_moves)
						print(f"selectedsquare {selected_square}, legal moves{destinations}")
				else:
						chosen_move = None
						for move in piece_moves:
							if (move.to_row,move.to_col) == (row,col):
								chosen_move = move
								break
						if chosen_move != None:
							last_move = chosen_move
							game.make_move(chosen_move)
							game_status = game.game_status()
							print(game_status)
							selected_square = None
							piece_moves = []
							destinations = []
						elif clicked_piece != game.EMPTY and game.get_piece_colour(row,col) ==game.who_to_move:
							selected_square = (row,col)
							piece_moves = piece_moves_gen(row,col)
							destinations = destination_squares(piece_moves)
						else:
							selected_square = None
							piece_moves = []
							destinations = []
			if events.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
		screen.fill((0,0,0))
		draw_board()
		draw_move_indicator()
		pygame.display.update()
		clock.tick(60)
		
	