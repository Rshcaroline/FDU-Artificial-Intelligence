import pisqpipe as pp
from gomokuapp.board import Board
from pisqpipe import DEBUG_EVAL
from players import computer

__author__ = "Jan Stránský (https://github.com/stranskyjan/pbrain-pyrandom), Modified for AlphaGomoku"

pp.infotext = 'name="AI-Gomoku", author="Shihan Ran", version="1.0", country="China"'


MAX_BOARD = 100
board = Board()

COMPUTER = computer.Computer()


def brain_init():
	if pp.width < 5 or pp.height < 5:
		pp.pipeOut("ERROR size of the board")
		return
	if pp.width > MAX_BOARD or pp.height > MAX_BOARD:
		pp.pipeOut("ERROR Maximal board size is {}".format(MAX_BOARD))
		return
	pp.pipeOut("OK")


def brain_restart():
	global board, COMPUTER
	board = Board()
	COMPUTER = computer.Computer()
	pp.pipeOut("OK")


def isFree(x, y):
	return x >= 0 and pp.width > 0 <= y < pp.height and board.get_board()[x][y] == 0


def brain_my(x, y):
	if isFree(x, y):
		board.move(x, y, board.get_next_player())
	else:
		pp.pipeOut("ERROR my move [{},{}]".format(x, y))


def brain_opponents(x, y):
	if isFree(x, y):
		board.move(x, y, board.get_next_player())
	else:
		pp.pipeOut("ERROR opponents's move [{},{}]".format(x, y))


def brain_block(x, y):
	if isFree(x, y):
		board.move(x, y, board.get_next_player())
	else:
		pp.pipeOut("ERROR winning move [{},{}]".format(x, y))


def brain_takeback(x, y):
	if x >= 0 and pp.width > 0 <= y < pp.height and board.get_board()[x][y] != 0:
		board.reverse_move()
		return 0
	return 2


def brain_turn():
	if pp.terminateAI:
		return
	i = 0
	while True:
		x, y = COMPUTER.make_move(board)
		i += 1
		if pp.terminateAI:
			return
		if isFree(x, y):
			break
	if i > 1:
		pp.pipeOut("DEBUG {} coordinates didn't hit an empty field".format(i))
	pp.do_mymove(x, y)


def brain_end():
	pass


def brain_about():
	pp.pipeOut(pp.infotext)


if DEBUG_EVAL:
	import win32gui

	def brain_eval(x, y):
		# TODO check if it works as expected
		wnd = win32gui.GetForegroundWindow()
		dc = win32gui.GetDC(wnd)
		rc = win32gui.GetClientRect(wnd)
		c = str(board.get_board()[x][y])
		win32gui.ExtTextOut(dc, rc[2] - 15, 3, 0, None, c, ())
		win32gui.ReleaseDC(wnd, dc)


# overwrites information about a game
# The board has 20x20 squares
pp.width, pp.height = 20, 20
# 15 seconds per move, 90 seconds per match for maximum
# time for one turn in milliseconds
pp.info_timeout_turn = 15000
# total time for a game
pp.info_timeout_match = 90000
# 0: human opponent, 1: AI opponent, 2: tournament, 3: network tournament
pp.info_game_type = 1
# 0: five or more stones win, 1: exactly five stones win
pp.info_exact5 = 0
# 0: gomoku, 1: renju
pp.info_renju = 0


# "overwrites" functions in pisqpipe module
pp.brain_init = brain_init
pp.brain_restart = brain_restart
pp.brain_my = brain_my
pp.brain_opponents = brain_opponents
pp.brain_block = brain_block
pp.brain_takeback = brain_takeback
pp.brain_turn = brain_turn
pp.brain_end = brain_end
pp.brain_about = brain_about
if DEBUG_EVAL:
	pp.brain_eval = brain_eval


def main():
	pp.main()


if __name__ == "__main__":
	main()
