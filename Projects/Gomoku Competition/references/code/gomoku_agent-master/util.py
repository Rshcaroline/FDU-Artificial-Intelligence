
def prettyPrint(board):
	chessSize = len(board)
	output = ""
	for i in range(chessSize):
		if i != 0:
			for j in range(chessSize):
				output = output + '----'
			output = output + '\n'
		for j in range(chessSize):
			if j == 0:
				output = output + '|'
			if board[i][j] == 1:
				output = output + ' x |'
			elif board[i][j] == 2:
				output = output + ' o |'
			else:
				output = output + '   |'
		output = output + '\n'
	print output