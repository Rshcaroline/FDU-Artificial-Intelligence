from typing import Callable

from gomokuapp.gomoku import Gomoku
from players import human, computer

"""
Represents the different types of player we can have as a tuple.
In the format {user input: (type description, type function)}

User input char: What we expect the user to input in order to tell us what type to use.
Type description: A simple description of what kind of player this type represents.
The type function is the function that should be called in order to get a move from the player.
"""
COMPUTER = computer.Computer()
PLAYER_TYPES = {
	'c': ('A computer', COMPUTER.make_move),
	'h': ('Manual input from (supposedly) a human', human.make_move),
}

ENUMERATE_TYPE_MESSAGE = '\r\nTypes include %s: ' % [(k, PLAYER_TYPES[k][0]) for k in PLAYER_TYPES]

"""
Format string for the first console prompt for a player type.
0: An integer representing the player we want a type for.
"""
PLAYER_TYPE_PROMPT_INITIAL = "Who should player %d be?" + ENUMERATE_TYPE_MESSAGE
"""
Format string for any repeat console prompts for a player type.
0: A string representing the last response from the console.
"""
PLAYER_TYPE_PROMPT_REPEAT = "'%s' is not a valid opponent." + ENUMERATE_TYPE_MESSAGE


def prompt_player_type(player: int) -> Callable:
	"""
	Prompts the console for the given player type.
	Allows the user to choose who plays who (c vs c, p vs c, etc.)
	:param player: The player we're asking for.
	:return: 'c' for 'computer', or 'h' for 'human'
	"""
	player_type = input(PLAYER_TYPE_PROMPT_INITIAL % player)
	while player_type not in PLAYER_TYPES:
		player_type = input(PLAYER_TYPE_PROMPT_REPEAT % player_type)
	return PLAYER_TYPES[player_type][1]


def play_game() -> None:
	players = {
		-1: prompt_player_type(1),
		1: prompt_player_type(2)
	}
	player = -1
	won = False
	while not won:
		x_coordinate, y_coordinate = players[player](gomoku.board)
		if gomoku.make_move(x_coordinate, y_coordinate, player):
			won = gomoku.check_for_winner()
			player = -player
		else:
			print("Error making move it may be invalid, please check again!")


if __name__ == '__main__':
	gomoku = Gomoku()
	play_game()
