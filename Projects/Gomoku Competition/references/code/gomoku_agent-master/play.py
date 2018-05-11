import game
import util
import time

iteration = 20
numberWin = [0, 0]
numSteps = [[0 for i in range(iteration)] for i in range(0, 2)]
boardSize = 6

for i in range(0, iteration):
	newGame = game.Gomoku(boardSize)
	# print "start a new Gomoku game with board size %dx%d"%(boardSize, boardSize)

	baselinePolicy = game.BaselinePolicy()
	randomPolicy = game.RandomPolicy()
	minimaxPolicy = game.MinimaxPolicy()
	time_to_move = [[], []]
	while (newGame.isEnd() < 0):
		nextPlayer = newGame.nextPlayer
		start = time.time()
		if (nextPlayer == 1):
			# action = randomPolicy.getNextAction(newGame)			
			action = minimaxPolicy.getNextAction(newGame)
			# print "player 1 selects ", action
		else:
			# action = randomPolicy.getNextAction(newGame)
			action = baselinePolicy.getNextAction(newGame)
			# print "player 2 selects ", action
		# print time.time() - start
		time_to_move[nextPlayer - 1].append(time.time() - start)
		# print "player %d places on (%d, %d)"%(nextPlayer, action[0], action[1])
		newGame.updateBoard(action)
	losePlayer, totalStep0, totalStep1 = newGame.currentGame()
	winPlayer = 2 if losePlayer == 1 else 1
	totalStep = (totalStep0, totalStep1)
	if newGame.isEnd() != 0:
		numberWin[winPlayer-1] += 1
		numSteps[winPlayer-1][i] = totalStep[winPlayer-1]
		print '#### player %d wins' %winPlayer, 'last move: ', newGame.lastMove
	else:
		print 'break even!'
	util.prettyPrint(newGame.chessBoard)

print "player 1 wins %d times, the average number of steps to win is %f, the average time to think is %f "%(numberWin[0], \
	1.0*sum(numSteps[0])/numberWin[0] if numberWin[0] != 0 else float('inf'), sum(time_to_move[0]) / len(time_to_move[0]))
print "player 2 wins %d times, the average number of steps to win is %f, the average time to think is %f "%(numberWin[1], \
	1.0*sum(numSteps[1])/numberWin[1] if numberWin[1] != 0 else float('inf'), sum(time_to_move[1]) / len(time_to_move[1]))

	# if newGame.isEnd() == 0:
	# 	print "break even!"
	# else:
	# 	print "Game ends! player %d wins in %d steps"%(winPlayer, totalStep[winPlayer - 1])
	# for i in range(0, boardSize):
	# 	print newGame.chessBoard[i]

