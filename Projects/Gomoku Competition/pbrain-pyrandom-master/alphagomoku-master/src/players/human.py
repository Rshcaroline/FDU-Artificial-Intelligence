"""
Contains the logic to get the next move from the user.
"""
import re

from gomokuapp.board import Board
from players.player import get_player_string


def validate_input(move: str) -> bool:
	pattern = re.compile('([1-9]|1[0-9]|20),([1-9]|1[0-9]|20)')
	return pattern.match(move) is not None


def make_move(brd: Board) -> (int, int):
	player = brd.get_next_player()
	while True:
		move = input("Type your move " + get_player_string(player) + " (X,Y): ")
		if validate_input(move):
			break
		print("Invalid move.")

	coordinates = move.split(",")
	x = int(coordinates[0]) - 1
	y = int(coordinates[1]) - 1
	return x, y
