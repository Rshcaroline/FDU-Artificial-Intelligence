import re


class StringParser:
	def __init__(self):
		self.game = None
		self.user_input = None

	"""
		"Brain" refers to the Neural Network/application.
		"Manager" refers to the third-party brokering the games.
	"""

	def read(self, command: str) -> None:
		if command == "START 20":
			"""
			When it receives this command (99% of the time it will be 20, but not always),
			the brain will create a new board of whatever size is defined in the command,
			then respond "OK".
			If the brain doesn't like the size, respond with "ERROR". There can be a message
			after that. The manager can try other sizes, or it can display a message to the
			user. Respond OK if the board is initialized successfully.
			The brain will respond with "OK" if the board initialises correctly.
			The brain will respond with "ERROR" (and an optional message) if it does not.
			"""
			if self.game is not None:
				print("ERROR")
			print("OK")
		# self.game = Gomoku()
		if re.search('START', command):
			print("ERROR")
		if command == "BEGIN":
			"""
			After receiving a START command and initiating the board, "BEGIN" states that the
			brain gets the first move.
			The brain will respond with the X and Y coordinates of its move.

			The difference between BEGIN and TURN is simply:
				BEGIN states that the AI is taking the first turn
				TURN states that a move has just been taken, and that a new space must be acknowledged by the AI
			"""
			"""
			DUMMY CODE
			string array of size 2 is populated by x and y coordinate of AI's move
			AI acknowledges move by adding it to its own board
			AI sends move to manager
			"""
			"""self.game.make_move(10,12)"""
			print("10,12")
		if re.search('TURN\s', command):
			"""
			X and Y represent the X and Y coordinates of the opponent's move.
			The brain will respond with the X and Y coordinates of its move.
			"""
			"""
			DUMMY CODE
			AI adds opponents move to own board by reading in
			string array of size 2 is populated by x and y coordinate of AI's move
			AI acknowledges move by adding it to its own board
			AI sends move to manager
			"""
			"""
			First: Sorry
			Second: Here's how it reads the inputs...
				First, it sees if the opponent's y-coordinate move is 2 digits long or not. It will adjust
				how far away from the end of the string it will look in order to find the x coordinate.
				This is because it needs to avoid reading the comma in as a number. I threw in a
				Try-Catch-like thing because someone's gonna say TURN hello,goodbye or some garbage.
			"""
			try:
				two_digit_x_coord = re.search('\s[0-9][0-9],', command)
				two_digit_y_coord = re.search(',[0-9][0-9]', command)
				if two_digit_y_coord:
					opponent_y_coord = (command[len(command) - 2]) + (command[len(command) - 1])
					if two_digit_x_coord:
						opponent_x_coord = (command[len(command) - 5]) + (command[len(command) - 4])
					else:
						opponent_x_coord = (command[len(command) - 4])
				else:
					opponent_y_coord = (command[len(command) - 1])
					if two_digit_x_coord:
						opponent_x_coord = (command[len(command) - 4]) + (command[len(command) - 3])
					else:
						opponent_x_coord = (command[len(command) - 3])
				print(str(opponent_x_coord) + "," + str(opponent_y_coord))
				"""self.game.make_move(opponent_x_coord, opponent_y_coord, 0)"""
			except RuntimeError:
				print("ERROR")

		if command == "BOARD":
			"""
			"BOARD" creates a new match, but with the potential to set the board to however the
			manager wishes it to be. After receiving the command, new lines will be of format
			"X,Y,[Player (1/2)]", until it sends "DONE".
			The brain will then answer with the coordinates of its next move.
			Manager:
				BOARD
				10,10,1
				10,11,2
				9,10,1
				DONE
			Brain:
				9,9
			(This assumes the brain is player 2 I assume)
			PS: Moves aren't necessarily sent in the order they were played in, unless using Renju rules.
			"""
		if command == "INFO [key] [value]":
			"""
		"INFO" sends the brain some information about the game so everyone knows the rules.
		For instance, "INTO timeout_match 300000" sets the time limit for the whole match
		to be 300,000 milliseconds, or about 5 minutes.
		Full key of INFO commands:
		timeout_turn  - time limit for each move (milliseconds, 0=play as fast as possible)
		timeout_match - time limit of a whole match (milliseconds, 0=no limit)
		max_memory    - memory limit (bytes, 0=no limit)
		time_left     - remaining time limit of a whole match (milliseconds)
		game_type     - 0=opponent is human, 1=opponent is brain, 2=tournament, 3=network tournament
		rule          - bit-mask or sum of 1=exactly five in a row win, 2=continuous game, 4=renju
		evaluate      - coordinates X,Y representing current position of the mouse cursor
		folder        - folder for persistent files [Used to determine a folder for persistent data.
						Because this folder is common for all the brains, the brain must create
						its own sub-folder with a name exactly matching the brain's name. If the manager
						never sends a folder command, then the brain cannot save permanent files.]
		Manager:
			INFO timeout_milliseconds 300000
		Brain:
			<no answer expected, just store the value somewhere>
		"""
		if command == "END":
			"""
			The brain is not expected to answer to this instruction, but rather to delete all of its temporary files.
			"""
		if command == "ABOUT":
			"""
			In the format key="value", the brain replies with some details about itself.
			Manager:
				ABOUT
			Brain:
				name="GroupProjectNN", version="1.0", author="#Banterbury", country="UK"
			"""
			print("name=\"GroupProjectNN\", version=\"0.1\", author=\"Alpha Gomoku\", country=\"UK\"")


if __name__ == "__main__":
	parser = StringParser()
	while True:
		user_input = input("")
		parser.read(user_input)
