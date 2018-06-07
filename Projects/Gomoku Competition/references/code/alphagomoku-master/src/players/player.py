"""
The player is represented by an int.
-1:	Player 1
0:	Not occupied.
1:	Player 2
"""

CHAR_PLAYER_1 = 'X'
CHAR_PLAYER_2 = 'Y'
# Char that represents unclaimed territory.
CHAR_NEUTRAL = '-'
PLAYER_CODES = [CHAR_PLAYER_1, CHAR_NEUTRAL, CHAR_PLAYER_2]

# TODO: Think about incorporating the use of these constants more throughout the project.
INT_PLAYER_1 = -1
INT_PLAYER_2 = 1


def is_valid(player: int) -> bool:
	"""
	:param player: integer representing the player.
	:return: True if int between -1 and 1, False otherwise.
	"""
	return isinstance(player, int) and -1 <= player <= 1


def convert_player_char(player: int) -> str:
	assert is_valid(player), "Invalid board cell contents"
	return PLAYER_CODES[player + 1]


def get_player_string(player: int) -> str:
	assert is_valid(player) and player != 0, "Invalid player code"
	if player == -1:
		return "Player 1"
	elif player == 1:
		return "Player 2"
