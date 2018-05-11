##############################
## test cases for sanity check
##############################

import game, util

def SanityCheckEvaluationFunction():
	chessBoardSize = 6
	print "create a new chess board: "
	newGame = game.Gomoku(chessBoardSize)

	moves = [(1,2), (3,1), (2,2), (4,1), (4,2), (5,1), (5,2), (3,4), (3,3)]
	for m in moves:
		newGame.updateBoard(m)
		# print "action: ", m, "winningCount = ", newGame.winningCount
	value = game.evaluate(newGame, 1)
	util.prettyPrint(newGame.chessBoard)
	assert(value == 17) # window count = {1: 6, 2: 2, 3: 1, 4: 1}
	print "pass test for evaluation function"

SanityCheckEvaluationFunction()

def SanityCheckRevertFunction():
	chessBoardSize = 4
	newGame = game.Gomoku(chessBoardSize)
	actions = [(0,2), (1,3), (2,0), (1,1)]
	for a in actions:
		newGame.updateBoard(a)
		util.prettyPrint(newGame.chessBoard)
		print '----------------------------------------------------------------------'
	actions = actions[::-1]
	actions.append((-1,-1))
	for i in range(1, len(actions)):
		newGame.revert(actions[i])
		util.prettyPrint(newGame.chessBoard)
		print '----------------------------------------------------------------------'

SanityCheckRevertFunction()

def SanityCheckIsEnd():
	chessBoardSize = 7
	newGame = game.Gomoku(chessBoardSize)
	newGame.updateBoard((3, 3))
	newGame.updateBoard((1, 4))
	newGame.updateBoard((2, 2))
	newGame.updateBoard((1, 1))
	newGame.updateBoard((4, 0))
	newGame.updateBoard((5, 0))
	newGame.updateBoard((4, 5))
	newGame.updateBoard((2, 5))
	newGame.updateBoard((4, 2))
	newGame.updateBoard((5, 2))
	newGame.updateBoard((4, 3))
	newGame.updateBoard((3, 2))
	newGame.updateBoard((2, 3))
	newGame.updateBoard((1, 3))
	newGame.updateBoard((0, 1))
	newGame.updateBoard((5, 3))
	newGame.updateBoard((2, 4))
	newGame.updateBoard((2, 1))
	newGame.updateBoard((5, 1))
	assert(newGame.isEnd() == -1)

SanityCheckIsEnd()






