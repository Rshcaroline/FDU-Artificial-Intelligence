from gomokuapp.board import Board
from players import player


def print_winning_message(winner: int, winning_moves: list) -> None:
	print(player.get_player_string(winner) + " has won using the following moves: ")
	for move in winning_moves:
		print("(" + str(move[0] + 1) + ", " + str(move[1] + 1) + ")")


class Gomoku:
	board = Board()

	def make_move(self, x: int, y: int, player: int) -> bool:
		if self.board.move(x, y, player):
			self.board.print_board()
			return True
		return False

	def check_for_winner(self) -> bool:
		winning_data = self.board.decide_winner()

		if winning_data[1] is None:
			return False

		winner, winning_moves = winning_data
		print_winning_message(winner, winning_moves)
		return True
