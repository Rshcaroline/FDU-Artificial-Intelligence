from copy import deepcopy
from math import ceil
from sys import stdout
from typing import List, Tuple

from players import player

"""
A row consists of a list of players.
"""
ColStruct = List[int]

"""
A board consists of a list of rows.
The board is navigated with [x][y] coordinates.
"""
BoardStruct = List[ColStruct]

"""
Moves are represented as a tuple of x and y coords.
"""
MoveStruct = Tuple[int, int]

MovesStruct = List[MoveStruct]

BOARD_SIZE = 20
# The number of pieces that are required to be in a row to win.
COUNT_NEEDED = 5


class Board:
	def __init__(self, board_struct: BoardStruct = None):
		if board_struct is not None:
			self._init_from_board_struct(board_struct)
			return
		self._board = [[0 for j in range(BOARD_SIZE)] for i in range(BOARD_SIZE)]
		self._next_player = -1
		self._winner = 0
		self._winning_moves = None
		self._moves = []
		self.player_minus_one_moves = []
		self.player_one_moves = []

	def _init_from_board_struct(self, board_struct: BoardStruct):
		"""
		Simulates the board as though all moves were being played from left to right, bottom to top.
		"""
		self.__init__()
		next_player = 0
		for x in range(BOARD_SIZE):
			for y in range(BOARD_SIZE):
				p = board_struct[x][y]
				if p != 0:
					next_player += p

					self._next_player = p
					assert self.move(x, y, p)
		if next_player == 0:
			self._next_player = -1
		else:
			self._next_player = 1

	def print_board(self):
		coords = range(BOARD_SIZE)
		for y in reversed(coords):
			for x in coords:
				coord = self._board[x][y]
				stdout.write(player.convert_player_char(coord))
			print()
		print()

	def decide_winner(self):
		return self._winner, self._winning_moves

	def _decide_winner_line(self, x: int, y: int, dx: int, dy: int) -> Tuple[int, MovesStruct or None]:
		"""
		Counts the number of spaces in a line belonging to the player in the given space.
		So if board[x][y] belongs to player 1, dx = 1, and dy = 0,
		then this function will search the horizontal line for consecutive player 1 spaces from board[x][y].
		"""
		p = self._board[x][y]
		count = 1
		moves = [(x, y)]
		for d in [-1, 1]:
			tx = x + dx * d
			ty = y + dy * d
			while check_coords(tx, ty) and self._board[tx][ty] == p:
				moves.append((tx, ty))
				count += 1
				if count == COUNT_NEEDED:
					return p, moves
				tx += dx * d
				ty += dy * d
		return 0, None

	def _decide_winner(self, x: int, y: int) -> None:
		"""
		Decides if there is a winner using the provided coords.
		If there is a winner, _winner and _winning_moves are set accordingly.
		:param x: X coord.
		:param y: Y coord.
		"""
		for step in [(1, 0), (0, 1), (1, 1), (1, -1)]:

			winner, moves = self._decide_winner_line(x, y, step[0], step[1])
			if winner != 0:
				self._winner = winner
				self._winning_moves = moves

	def move(self, x: int, y: int, p: int) -> bool:
		"""
		:param x: The x coordinate to move to.
		:param y: The y coordinate to move to.
		:param p: The player.
		:return: True if move successful, False if move invalid.
		"""
		if self._winner != 0 or self._board[x][y] != 0:
			return False

		'''
		p == self._next_player is needed because:
			* The next_player isn't being updated correctly. 
			* Somewhere the move method is being called with an incorrect player
		'''
		if not (player.is_valid(p) and p == self._next_player):
			return False

		self._next_player = -p
		if p == 1:
			self.player_one_moves.append((x,y))
		elif p == -1:
			self.player_minus_one_moves.append((x,y))
		self._moves.append((x, y))
		self._board[x][y] = p
		self._decide_winner(x, y)
		return True

	def reverse_move(self) -> Tuple[int, int, int]:
		"""
		Reverts a move, as though it had never been played.
		:return: x, y, player.
		"""
		assert len(self._moves) > 0
		x, y = self._moves.pop()
		p = self._board[x][y]
		self._board[x][y] = 0
		self._next_player = p
		if self._winner != 0:
			self._winner = 0
			self._winning_moves = None
		return x, y, p

	def get_last_move(self) -> Tuple[int, int] or None:
		if len(self._moves) == 0:
			return None
		return self._moves[-1]

	def get_next_player(self) -> int:
		return self._next_player

	def get_played_moves(self) -> list:
		return self._moves

	#def get_played_moves(self, player):
	#	if player == -1:
	#		return self.player_minus_one_moves
	#	elif player == 1:
	#		return self.player_one_moves

	def get_board(self) -> BoardStruct:
		"""
		:return: A deep copy of the board 2D array.
		"""
		return deepcopy(self._board)

	def get_possible_moves(self) -> List[Tuple[int, int]]:
		"""
		Returns a list of Board instances representing the state of the board after a possible move has been made.
		"""
		if self._winner != 0:
			return []

		if len(self._moves) == 0:
			return [(x, y) for y in range(ceil(BOARD_SIZE / 2)) for x in range(ceil(BOARD_SIZE / 2))]

		moves = [(x, y) for y in range(BOARD_SIZE) for x in range(BOARD_SIZE) if self._board[x][y] == 0]
		return moves


def check_coords(x: int, y: int) -> bool:
	return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE
