import pisqpipe as pp
from pisqpipe import DEBUG_EVAL


# ================================ start of player ================================  
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


# ================================ start of board ================================  
from copy import deepcopy
from math import ceil
from sys import stdout
from typing import List, Tuple

# from players import player

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
				stdout.write(convert_player_char(coord))
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
		if not (is_valid(p) and p == self._next_player):
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


# ================================ start of training_data ================================  
import glob
import pickle
from os.path import isfile
from sys import argv
from typing import List, Tuple

# from gomokuapp.board import Board, BoardStruct, MovesStruct

"""
Training data is represented as a list of moves/boards, and the winner for that game.
"""
TrainingDataStruct = Tuple[List[BoardStruct], int]

_TRAINING_DATA_FILES = glob.glob("../resources/training/fast_training_data/*.psq")[:3700]
_TRAINING_DATA_FILES += glob.glob("../resources/training/more_fast_training_data/*.psq")[:2800]
_TRAINING_DATA_FILES += glob.glob("../resources/training/even_more_fast_training_data/*.psq")[:4000]
_TRAINING_DATA_FILES += glob.glob("../resources/training/training_data_max/*.psq")[:33000]
_TRAINING_DATA_FILES += glob.glob("../resources/training/training_data_harry/*.psq")[-27000:]
_TRAINING_DATA_FILES += glob.glob("../resources/training/training_data_mcmc/*.psq")
_TRAINING_DATA_FILES += glob.glob("../resources/training/training_data_march/*.psq")

_TEST_DATA_FILES = glob.glob("../resources/training/fast_training_data/*.psq")[-2500:]
_TEST_DATA_FILES += glob.glob("../resources/training/more_fast_training_data/*.psq")[-1400:]
_TEST_DATA_FILES += glob.glob("../resources/training/even_more_fast_training_data/*.psq")[-2000:]
_TEST_DATA_FILES += glob.glob("../resources/training/training_data_harry/*.psq")[:5000]


_TRAINING_DATA_SAVE_PATH = "neuralnetwork/save_data/training_data.pckl"
_TESTING_DATA_SAVE_PATH = "neuralnetwork/save_data/testing_data.pckl"


def check_source(lines):
	return len(lines[0]) > 6


def parse_training_file(path: str) -> MovesStruct:
	with open(path) as f:
		ls = f.readlines()

	# Check the format of the file being parsed
	# True: Original format
	# False: Faster, dumber format

	original_source = check_source(ls)

	ls = [l.strip() for l in ls]
	if original_source:
		ls = ls[1:-3]
		ls = [l.split(',')[:2] for l in ls]
	else:
		ls = ls[:-19]
		ls = [l.split(",") for l in ls]

	return [(int(m[0]) - 1, int(m[1]) - 1) for m in ls]


def simulate(moves: MovesStruct, should_print: bool = False) -> TrainingDataStruct:
	board = Board()
	all_boards = [board.get_board()]
	p = -1
	for x, y in moves:
		assert board.move(x, y, p)
		all_boards.append(board.get_board())
		if should_print:
			board.print_board()
		winner, _ = board.decide_winner()
		if winner != 0:
			return all_boards, winner
		p = -p
	raise ValueError('Winner still not determined after all moves have been made.')


def process_training_data(paths: List[str], should_print=False):
	training_data = []
	training_data_processed_count = 0
	for path in paths:
		training_data_processed_count = training_data_processed_count + 1
		if training_data_processed_count % 500 == 0:
			print ("Processed " + str(training_data_processed_count) + "/" + str(len(paths)))
		path_data = []
		if should_print:
			print('processing file', path)
		moves = parse_training_file(path)
		try:
			boards, winner = simulate(moves, should_print=should_print)
			path_data.extend((b, winner) for b in boards)
		except ValueError as error:
			print("Warning: Training data not interpretable: %s. Error: %s" % (path, error))
			continue
		if not path_data:
			print("Can't read/find file ", path)
		else:
			training_data.append(path_data)
	return training_data


def split_list_into_n_lists(list, n):
	return [list[i::n] for i in range(n)]


def merge_lists_into_one_list(list_one, list_two):
	return [j for i in zip(list_one, list_two) for j in i]


def _save_data(file_path: str, data: List[TrainingDataStruct]) -> None:
	"""
	Takes a list of pre-parsed training data, and stores it at the given path, for quicker access.

	:param file_path:
	:return:
	"""
	lists = split_list_into_n_lists(data, 2)
	data1 = lists[0]
	data2 = lists[1]
	file1 = open(file_path, 'wb')
	pickle.dump(data1, file1)
	file1.close()
	file2 = open(file_path + "2", 'wb')
	pickle.dump(data2, file2)
	file2.close()


def _load_data(file_path: str) -> List[TrainingDataStruct]:
	"""
	Takes a file path, and returns the list of training data stored there.

	:param file_path:
	:return:
	"""
	f1 = open(file_path, 'rb')
	data1 = pickle.load(f1)
	f1.close()
	f2 = open(file_path + "2", 'rb')
	data2 = pickle.load(f2)
	f2.close()
	data = merge_lists_into_one_list(data1, data2)
	return data


def _load_or_parse_data(parse_paths: List[str], save_path: str, file_count: int = None) -> List[TrainingDataStruct]:
	"""
	If the given save path already exists, attempts to extract a list of training data from it.
	Otherwise, the parse paths are used to generate data, which is stored at the given save path, and then returned.

	The file count is ignored when saving data.
	This also means that all of the files given by parse_paths will be parsed.

	:param parse_paths: A list of file paths for training data to be parsed.
	:param save_path: A path that may or may not contain pre-parsed training data; written to, in the latter case.
	:param file_count: The amount of training data to return.
	:return: Parsed training data, one way or another.
	"""
	running_on_raptor = True  # False
	if isfile(save_path) or not running_on_raptor:
		data = _load_data(save_path)
	else:
		data = process_training_data(parse_paths)
		if not running_on_raptor:
			_save_data(save_path, data)

	if file_count is None:
		return data
	return data[:file_count]


def get_training_data(file_count: int = None):
	return _load_or_parse_data(_TRAINING_DATA_FILES, _TRAINING_DATA_SAVE_PATH, file_count)


def get_test_data(file_count: int = None):
	return _load_or_parse_data(_TEST_DATA_FILES, _TESTING_DATA_SAVE_PATH, file_count)


# if __name__ == '__main__':
# 	if len(argv) > 1:
# 		process_training_data(argv[1:], should_print=True)
# 	else:
# 		process_training_data(_TRAINING_DATA_FILES, should_print=True)


# ================================ start of neural_network ================================  
import os
import random
import sys
from random import randrange
from typing import List
from datetime import datetime, timedelta

import numpy
import tensorflow as tf
from tensorflow import Session
from tensorflow.python.framework.errors import NotFoundError

# from gomokuapp.board import BOARD_SIZE
# from neuralnetwork.training_data import get_training_data, get_test_data

# ---FILE BASED CONSTANTS---
DEBUG_PRINT_SIZE = 5
'''
	It's very possible the program will crash if you decrease NUMBER_OF_BATCHES due to an out of memory.
	This is because NUMBER_OF_BATCHES is how many times the total training/testing data is split into separate batches,
	so the lower the number the larger the batch amount.

	Decrease NUMBER_OF_BATCHES_TO_TRAIN_ON if you don't wish to train on every batch.
	NUMBER_OF_BATCHES_TO_TRAIN_ON should be no larger than NUMBER_OF_BATCHES
'''
NUMBER_OF_BATCHES = 500
NUMBER_OF_BATCHES_TO_TRAIN_ON = NUMBER_OF_BATCHES
# This is how many times each batch will be trained on
TRAINING_ITERATIONS = 1

MODEL_SAVE_FILE_PATH = "neuralnetwork/save_data/models/model.ckpt"
GRAPH_LOGS_SAVE_FILE_PATH = "neuralnetwork/save_data/logs/"

# ---HYPER PARAMETERS ---
LEARNING_RATE = 0.01

# The rate at which neurons are kept after learning
KEEP_SOME_PROBABILITY = 0.5
KEEP_ALL_PROBABILITY = 1.0

# Setting the below to None means load all of them
TRAINING_DATA_FILE_COUNT = None
TEST_DATA_FILE_COUNT = None

# --- LAYER/WEIGHT/BIAS CONSTANTS---
INPUT_SIZE = BOARD_SIZE ** 2
OUTPUT_SIZE = 2
HEURISTIC_SIZE = 1
CONV_SIZE = 15
CONV_WEIGHT_1_INPUT_CHANNELS = 1
CONV_WEIGHT_1_FEATURES = 12
CONV_WEIGHT_2_FEATURES = 14
# POOL MULTIPLICATION SIZE = 5 BECAUSE IT REPRESENTS BOARD_SIZE / 4 CAUSE WE DO 2x2 POOLING
POOL_MULTIPLICATION_SIZE = 5
CONV_2_OUTPUT_SIZE = POOL_MULTIPLICATION_SIZE * POOL_MULTIPLICATION_SIZE * CONV_WEIGHT_2_FEATURES
FC_LAYER_1_WEIGHTS = CONV_WEIGHT_2_FEATURES * 16
STRIDE_SIZE = 1  # this probably won't need changing
COLOUR_CHANNELS_USED = 1  # We are not feeding our network a colour image so this is always 1
HEURISTIC_2_IN_A_ROW_MULTIPLIER = 3
HEURISTIC_3_IN_A_ROW_MULTIPLIER = 15
HEURISTIC_4_IN_A_ROW_MULTIPLIER = 50


def get_weight_variable(shape):
	return tf.Variable(tf.truncated_normal(shape, stddev=0.1))


def get_bias_variable(shape):
	return tf.Variable(tf.constant(0.1, shape=shape))


'''
	This only works on batched_inputs
'''


def one_hot_input_batch(input_batch):
	one_hotted_input_batch = []
	for board in input_batch:
		one_hotted_move = []
		for row in board:
			for cell in row:
				one_hotted_move.append(cell)
		one_hotted_input_batch.append(one_hotted_move)
	return one_hotted_input_batch


'''
	returns the training data in a batch format which can be argmaxed by tensorflow
'''


def convert_training_to_batch(training_data, number_of_batches):
	train_input = []
	train_output = []
	heuristics = []
	batched_count = 0
	for i in range(len(training_data)):
		batched_count = batched_count + 1
		if i % 500 == 0:
			print(str(batched_count) + "/" + str(len(training_data)) + " batched so far")
		for j in range(len(training_data[i])):
			# if the move number is less than 5 and the game lasts more than 5 moves don't bother
			if not (j < 5 < len(training_data[i])):
				heuristic_ = get_number_in_a_row_heuristic_for_move(training_data[i][j][0])
				# if heuristic_ != [0] * len(heuristic_):
				if heuristic_ != 0:
					train_input.append(training_data[i][j][0])
					# If training_data[i][j][1] == -1 then an argmax function would identify the first index 0 as the highest
					# If training_data[i][j][1] == 1 then the argmax function would identify index 1 as the highest
					# Our nn just has to mimic this
					train_output.append([0, training_data[i][j][1]])
					heuristics.append([heuristic_])
	train_input, train_output, heuristics = shuffle_lists_together(train_input, train_output, heuristics)
	if number_of_batches == 1:
		return [train_input], [train_output], [heuristics]
	else:
		return nn_split_list_into_n_lists(train_input, number_of_batches), nn_split_list_into_n_lists(train_output, number_of_batches), nn_split_list_into_n_lists(
			heuristics, number_of_batches)


def shuffle_lists_together(train_input, train_output, heuristics):
	list_to_shuffle = list(zip(train_input, train_output, heuristics))
	random.shuffle(list_to_shuffle)
	# [:] means the result will be put into lists not tuples
	train_input[:], train_output[:], heuristics[:] = zip(*list_to_shuffle)
	return train_input, train_output, heuristics


def nn_split_list_into_n_lists(list, n):
	return [list[i::n] for i in range(n)]


def conv2d(image, weights):
	return tf.nn.conv2d(image, weights, strides=[STRIDE_SIZE, STRIDE_SIZE, STRIDE_SIZE, STRIDE_SIZE], padding='SAME')


def pool2x2(conv_image):
	return tf.nn.avg_pool(conv_image, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')


def restore(sess: Session, file_path: str):
	saver = tf.train.Saver()

	try:
		saver.restore(sess, file_path)
	except NotFoundError as e:
		print('Could not load a TensorFlow model from \'%s\' because none was found.' % file_path, file=sys.stderr)
		print('Current dir: %s' % os.path.abspath('.'), file=sys.stderr)
		raise e


def save_network_weights(sess: Session, file_path: str, overwrite: bool = False) -> bool:
	file_exists = os.path.exists(file_path)

	if file_exists and not overwrite:
		return True

	if not file_exists:
		dir_path = os.path.dirname(file_path)
		dir_exists = os.path.exists(dir_path)
		if not dir_exists:
			os.makedirs(dir_path)

	saver = tf.train.Saver()

	save_path = saver.save(sess, file_path)
	print('TensorFlow model saved in file: %s' % save_path)


def network_layers(training_input, heuristic, keep_prob):
	conv_weights1 = get_weight_variable([CONV_SIZE, CONV_SIZE, CONV_WEIGHT_1_INPUT_CHANNELS, CONV_WEIGHT_1_FEATURES])
	conv_bias1 = get_bias_variable([CONV_WEIGHT_1_FEATURES])

	input_image = tf.reshape(training_input, [-1, BOARD_SIZE, BOARD_SIZE, COLOUR_CHANNELS_USED])

	convolution1 = tf.nn.tanh(conv2d(input_image, conv_weights1) + conv_bias1)
	pool1 = pool2x2(convolution1)

	conv_weights2 = get_weight_variable([CONV_SIZE, CONV_SIZE, CONV_WEIGHT_1_FEATURES, CONV_WEIGHT_2_FEATURES])
	conv_bias2 = get_bias_variable([CONV_WEIGHT_2_FEATURES])

	convolution2 = tf.nn.tanh(conv2d(pool1, conv_weights2) + conv_bias2)
	pool2 = pool2x2(convolution2)

	fully_connected_weights1 = get_weight_variable([CONV_2_OUTPUT_SIZE, FC_LAYER_1_WEIGHTS])
	fully_connected_bias1 = get_bias_variable([FC_LAYER_1_WEIGHTS])

	pool2_flat = tf.reshape(pool2, [-1, CONV_2_OUTPUT_SIZE])
	fully_connected_output1 = tf.nn.tanh(tf.matmul(pool2_flat, fully_connected_weights1) + fully_connected_bias1)

	fully_connected1_drop = tf.nn.dropout(fully_connected_output1, keep_prob)

	heuristic_layer_weights = get_weight_variable([HEURISTIC_SIZE, FC_LAYER_1_WEIGHTS])
	heuristic_layer_bias = get_bias_variable([FC_LAYER_1_WEIGHTS])

	heuristic_layer_output = tf.nn.dropout(
		tf.nn.tanh(tf.matmul(heuristic, heuristic_layer_weights) + heuristic_layer_bias), keep_prob)

	# plus FC_LAYER_1_WEIGHTS because it has to account for the size of the output of the heuristic layer getting concatted to it later
	fully_connected_weights2 = get_weight_variable([FC_LAYER_1_WEIGHTS + FC_LAYER_1_WEIGHTS, OUTPUT_SIZE])
	fully_connected_bias2 = get_bias_variable([OUTPUT_SIZE])

	fully_connected_drop_output_with_heuristic = tf.concat(1, [fully_connected1_drop, heuristic_layer_output])
	tf_output = tf.nn.softmax(
		tf.matmul(fully_connected_drop_output_with_heuristic, fully_connected_weights2) + fully_connected_bias2)
	return tf_output, convolution1, convolution2, pool2


def evaluate_network_layers(tf_output, training_output, global_step):
	cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(tf_output, training_output))

	train_step = tf.train.AdamOptimizer(LEARNING_RATE).minimize(cross_entropy, global_step=global_step)

	correct_prediction = tf.equal(tf.argmax(tf.nn.softmax(tf_output), 1), tf.argmax(training_output, 1))

	accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

	return cross_entropy, train_step, accuracy


def init_sess_and_variables():
	sess = tf.InteractiveSession()

	# This is necessary to ensure compatibility with two different versions of tensorflow (windows and ubuntu)
	try:
		sess.run(tf.global_variables_initializer())
	except AttributeError:
		sess.run(tf.initialize_all_variables())

	return sess


def restore_session_if_needed(sess, should_use_save_data):
	print("---")
	if should_use_save_data:
		restore(sess, MODEL_SAVE_FILE_PATH)
		print("TensorFlow model loaded from last session.")
	else:
		print("Previous save data not loaded! If you wish to load the previous save data run: python3 neural_network_main.py True")
	print("---")


def init_feed_dict(train_input_batch, train_output_batch, train_heuristics, training_input, test_input_batch, test_output_batch, test_heuristics, training_output, keep_prob, heuristic):
	feed_dict_train = []
	feed_dict_train_keep_all = []
	feed_dict_test = []
	for i in range(NUMBER_OF_BATCHES):
		train_input_batch[i] = one_hot_input_batch(train_input_batch[i])
		test_input_batch[i] = one_hot_input_batch(test_input_batch[i])
		feed_dict_train.append({training_input: train_input_batch[i], training_output: train_output_batch[i], keep_prob: KEEP_SOME_PROBABILITY, heuristic: train_heuristics[i]})
		feed_dict_train_keep_all.append({training_input: train_input_batch[i], training_output: train_output_batch[i], keep_prob: KEEP_ALL_PROBABILITY, heuristic: train_heuristics[i]})
		feed_dict_test.append({training_input: test_input_batch[i], training_output: test_output_batch[i], keep_prob: KEEP_ALL_PROBABILITY, heuristic: test_heuristics[i]})
	return feed_dict_train, feed_dict_train_keep_all, feed_dict_test


def neural_network_test_loop(sess, accuracy, feed_dict_test, feed_dict_train_keep_all):
	training_accuracy = []
	testing_accuracy = []
	for i in range(NUMBER_OF_BATCHES_TO_TRAIN_ON):
		training_accuracy.append(sess.run(accuracy, feed_dict=feed_dict_train_keep_all[i]))
		testing_accuracy.append(sess.run(accuracy, feed_dict=feed_dict_test[i]))
	training_average = sum(training_accuracy) / len(training_accuracy)
	testing_average = sum(testing_accuracy) / len(testing_accuracy)
	print_accuracy_percentage(training_average, testing_average)


def init_nn_variables_and_placeholders():
	training_input = tf.placeholder(tf.float32, [None, INPUT_SIZE])
	heuristic = tf.placeholder(tf.float32, [None, HEURISTIC_SIZE])
	keep_prob = tf.placeholder(tf.float32)
	training_output = tf.placeholder(tf.float32, [None, OUTPUT_SIZE])
	global_step = tf.Variable(0, trainable=False)
	return training_input, heuristic, keep_prob, training_output, global_step


def compare_data(data):
	without_dupes = []
	data_count = len(data)
	print("Data count: %s" % data_count)
	for d in data:
		if d not in without_dupes:
			without_dupes.append(d)
	without_dupes_count = len(without_dupes)
	print("without_dupes count: %s" % without_dupes_count)
	if data_count > without_dupes_count:
		no_of_dupes = data_count - without_dupes_count
		print("Data has %s duplicates!" % no_of_dupes)
		print("This is %s%% of the data." % ((no_of_dupes / data_count) * 100))


def neural_network_train(should_use_save_data):
	duplicate_testing = False  # True if want to test for duplicates
	print("Convolutional Neural Network training beginning...")
	print("Loading training and testing data...")
	training_data = get_training_data(TRAINING_DATA_FILE_COUNT)
	testing_data = get_test_data(TEST_DATA_FILE_COUNT)
	print("Training and testing data loaded!")

	if duplicate_testing:
		print("Training data has %s files" % (len(training_data)))
		print("Examining training data for duplicates...")
		compare_data(training_data)
		print("Testing data has %s files" % (len(testing_data)))
		print("Examining testing data for duplicates...")
		compare_data(testing_data)

	training_input, heuristic, keep_prob, training_output, global_step = init_nn_variables_and_placeholders()

	tf_output, convolution1, convolution2, pool2 = network_layers(training_input, heuristic, keep_prob)

	cross_entropy, train_step, accuracy = evaluate_network_layers(tf_output, training_output, global_step)

	sess = init_sess_and_variables()

	restore_session_if_needed(sess, should_use_save_data)

	print("Batching inputs and setting up variables and heuristics...")
	train_input_batch, train_output_batch, train_heuristics = convert_training_to_batch(training_data, NUMBER_OF_BATCHES)
	test_input_batch, test_output_batch, test_heuristics = convert_training_to_batch(testing_data, NUMBER_OF_BATCHES)
	feed_dict_train, feed_dict_train_keep_all, feed_dict_test = init_feed_dict(train_input_batch, train_output_batch, train_heuristics, training_input, test_input_batch, test_output_batch, test_heuristics, training_output, keep_prob, heuristic)

	print("Network training starting!")
	for j in range(TRAINING_ITERATIONS):
		for i in range(NUMBER_OF_BATCHES_TO_TRAIN_ON):
			print("-")
			print("Batch number: " + str(i + 1) + "/" + str(NUMBER_OF_BATCHES_TO_TRAIN_ON) + " Training step: " + str(
				j + 1) + "/" + str(TRAINING_ITERATIONS) + " Global step: " + str(sess.run(global_step)))
			entropy, _, train_step_accuracy, h, to, c1, c2, p2 = sess.run(
				[cross_entropy, train_step, accuracy, heuristic, training_output, convolution1, convolution2, pool2],
				feed_dict=feed_dict_train[i])
			print("Entropy: " + str(entropy))
			print("Training Step Result Accuracy: " + str(train_step_accuracy))
			# print(h[0])
			# print(to[0])
			# print(c1[0][0])
			# print("--")
			# print(c2[0][0])
			# print("--")
			# print(p2[0])
			train_input_batch[i], train_output_batch[i], train_heuristics[i] = shuffle_lists_together(
				train_input_batch[i], train_output_batch[i], train_heuristics[i])
			feed_dict_train[i] = {training_input: train_input_batch[i], training_output: train_output_batch[i], keep_prob: KEEP_SOME_PROBABILITY, heuristic: train_heuristics[i]}
		if j % 10 == 0:
			print("Testing Accuracy on random testing batch: " + str(
				sess.run(accuracy, feed_dict=random.choice(feed_dict_test))))

	debug_outputs = sess.run(tf_output, feed_dict=feed_dict_train_keep_all[0])
	print_debug_outputs(DEBUG_PRINT_SIZE, train_output_batch[0], debug_outputs)

	print("NN training complete, moving on to testing.")

	neural_network_test_loop(sess, accuracy, feed_dict_test, feed_dict_train_keep_all)

	save_network_weights(sess, MODEL_SAVE_FILE_PATH, True)


def print_debug_outputs(amount, train_output_batch, debug_outputs):
	print("---")
	print("Debugging/printing random outputs from tensorflow compared to the actual outputs...")
	for i in range(amount):
		random_move_index = randrange(0, len(train_output_batch))
		print("index of move in output array: " + str(random_move_index))
		print("tf output: " + str(debug_outputs[random_move_index]))
		print("Actual output: " + str(train_output_batch[random_move_index]))
	print("---")


def print_accuracy_percentage(training_accuracy, testing_accuracy):
	training_accuracy = "%.2f" % (training_accuracy * 100)
	testing_accuracy = "%.2f" % (testing_accuracy * 100)
	print("-----")
	print("Training Accuracy: " + str(training_accuracy) + "%")
	print("Testing Accuracy: " + str(testing_accuracy) + "%")
	print("-----")


def get_number_in_a_row_heuristic_for_move(move):
	"""
		return [
			# Player -1
				Amount of 2 in a row, Amount of 3 in a row, Amount of 4 in a row,
			# Player 1
				Amount of 2 in a row, Amount of 3 in a row, Amount of 4 in a row
			]
		]
	"""

	player_counts = [[0] * 3 for _ in range(2)]

	for f, m in [
		(count_in_a_row_horizontally_and_vertically, move),
		(count_in_a_row_diagonally, move),
	]:
		for p in range(2):
			tplayer_count = f(m, (p * 2) - 1)
			player_counts[p] = [x + y for x, y in zip(player_counts[p], tplayer_count)]

	sum_heuristic = 0
	sum_heuristic -= player_counts[0][0] * HEURISTIC_2_IN_A_ROW_MULTIPLIER
	sum_heuristic -= player_counts[0][1] * HEURISTIC_3_IN_A_ROW_MULTIPLIER
	sum_heuristic -= player_counts[0][2] * HEURISTIC_4_IN_A_ROW_MULTIPLIER
	sum_heuristic += player_counts[1][0] * HEURISTIC_2_IN_A_ROW_MULTIPLIER
	sum_heuristic += player_counts[1][1] * HEURISTIC_3_IN_A_ROW_MULTIPLIER
	sum_heuristic += player_counts[1][2] * HEURISTIC_4_IN_A_ROW_MULTIPLIER
	return sum_heuristic


# return player_counts[0] + player_counts[1]

def count_in_a_row_horizontally(move, player: int) -> List[int]:
	counts = [0] * 3
	for row in move:
		in_a_row_count = 0
		for cell_index in range(len(row)):
			if player == row[cell_index]:
				in_a_row_count += 1
			else:
				if 2 <= in_a_row_count <= 4:
					'''
					The below code is used for testing, i'm commiting it currently because I want to be 100% it works and i'm not yet
					print(row)
					print("cell_index: "+ str(cell_index))
					print("row count: " + str(in_a_row_count))
					print(row[(cell_index-1)-in_a_row_count])
					print((cell_index-1)-in_a_row_count)
					print(row[cell_index-1])
					print(row[cell_index])

					test this with the command:
					python3 -c 'import neural_network; print(neural_network.count_in_a_row_horizontally([[1,1,0,1,1], [0,0,0,0,0]], 1))'
					'''
					if (cell_index - 1) - in_a_row_count < 0:
						if row[cell_index] == 0:
							counts[in_a_row_count - 2] += 1
					elif (row[(cell_index - 1) - in_a_row_count] == 0) and (row[cell_index] == 0):
						counts[in_a_row_count - 2] += 1
				in_a_row_count = 0
		if 2 <= in_a_row_count <= 4:
			'''
			print(row)
			print("cell_index: "+ str(cell_index))
			print("row count: " + str(in_a_row_count))
			print(row[(cell_index)-in_a_row_count])
			print((cell_index)-in_a_row_count)
			print(row[cell_index])
			'''
			if row[cell_index - in_a_row_count] == 0:
				counts[in_a_row_count - 2] += 1

	return counts


def count_in_a_row_horizontally_and_vertically(move, player: int) -> List[int]:
	rotated_move = [[i[j] for i in move] for j in range(len(move[0]))]
	counts = [0] * 3
	for row, column in zip(move, rotated_move):
		in_a_row_count_horizontal = 0
		in_a_row_count_vertical = 0
		for cell_index_horizontal, cell_index_vertical in zip(range(len(row)), range(len(column))):
			if player == row[cell_index_horizontal]:
				in_a_row_count_horizontal += 1
			else:
				if 2 <= in_a_row_count_horizontal <= 4:
					if (cell_index_horizontal - 1) - in_a_row_count_horizontal < 0:
						if row[cell_index_horizontal] == 0:
							counts[in_a_row_count_horizontal - 2] += 1
					elif (row[(cell_index_horizontal - 1) - in_a_row_count_horizontal] == 0) and (
								row[cell_index_horizontal] == 0):
						counts[in_a_row_count_horizontal - 2] += 1
				in_a_row_count_horizontal = 0
			if player == column[cell_index_vertical]:
				in_a_row_count_vertical += 1
			else:
				if 2 <= in_a_row_count_vertical <= 4:
					if (cell_index_vertical - 1) - in_a_row_count_vertical < 0:
						if column[cell_index_vertical] == 0:
							counts[in_a_row_count_vertical - 2] += 1
					elif (column[(cell_index_vertical - 1) - in_a_row_count_vertical] == 0) and (
								column[cell_index_vertical] == 0):
						counts[in_a_row_count_vertical - 2] += 1
					in_a_row_count_vertical = 0
		if 2 <= in_a_row_count_horizontal <= 4:
			if row[cell_index_horizontal - in_a_row_count_horizontal] == 0:
				counts[in_a_row_count_horizontal - 2] += 1
		if 2 <= in_a_row_count_vertical <= 4:
			if column[cell_index_vertical - in_a_row_count_vertical] == 0:
				counts[in_a_row_count_vertical - 2] += 1

	return counts


def count_in_a_row_diagonally(move, player):
	move_array = numpy.asarray(move)

	'''
		I referenced code from this stack-overflow answer in order to get a list of all the diagonals in a 2D numpy array
		http://stackoverflow.com/a/6313414/4204337
	'''
	diagonals = [move_array[::-1, :].diagonal(i) for i in range(-move_array.shape[0] + 1, move_array.shape[1])]
	# get diagonals from the other direction
	diagonals.extend(move_array.diagonal(i) for i in range(move_array.shape[1] - 1, -move_array.shape[0], -1))

	all_diagonals_in_move = [n.tolist() for n in diagonals]

	return count_in_a_row_horizontally(all_diagonals_in_move, player)

def print_use_output(winner, output):
	print([winner, max(output)])


def get_failed_predictions():
	print("Checking Neural Network for Failed Predictions:")
	training_input, heuristic, keep_prob, tf_output, sess = setup_network()
	failed_predictions = []
	testing_data = get_test_data(TEST_DATA_FILE_COUNT)
	for game in testing_data:
		winner_of_game = game[0][1]
		for move in game:
			print(move[0])
			winner_from_network = use_network(move[0], training_input, heuristic, keep_prob, tf_output, sess, winner_of_game)  # , winner_of_game
			if winner_from_network != winner_of_game:
				failed_predictions.append(move)
	print("Failed Predictions:")
	with open("save_data/failed_predictions/failed_predictions.txt", 'w') as file_handler:
		for prediction in failed_predictions:
			print(prediction)
			file_handler.write("{}\n".format(prediction))


def reset_default_graph():
	tf.reset_default_graph()

def setup_network():
	training_input, heuristic, keep_prob, _, _ = init_nn_variables_and_placeholders()
	tf_output, _, _, _ = network_layers(training_input, heuristic, keep_prob)
	sess = init_sess_and_variables()
	restore(sess, MODEL_SAVE_FILE_PATH)
	return training_input, heuristic, keep_prob, tf_output, sess


def use_network(input, training_input, heuristic, keep_prob, tf_output, sess, player):
	test_input = [input]
	test_input_batch = one_hot_input_batch(test_input)
	heuristic_ = get_number_in_a_row_heuristic_for_move(input)
	feed_dict_test = {training_input: test_input_batch, keep_prob: KEEP_ALL_PROBABILITY, heuristic: [[heuristic_]]}
	output = sess.run(tf.nn.softmax(tf_output), feed_dict=feed_dict_test)[0]

	return output[int((player + 1)/2)]


# if __name__ == '__main__':
# 	get_failed_predictions()


# ================================ start of monte_carlo ================================  
import math
import random
from copy import deepcopy
from datetime import datetime, timedelta
from typing import List
from numpy.random import choice

# from gomokuapp.board import BOARD_SIZE
# from gomokuapp.board import Board, MoveStruct
# from neuralnetwork.neural_network import setup_network, use_network, reset_default_graph


class Neural_Network:
	def __init__(self):
		self.training_input, self.heuristic, self.keep_prob, self.tf_output, self.sess = setup_network()

	def nn(self, board: Board, player) -> float:
		return use_network(board.get_board(), self.training_input, self.heuristic, self.keep_prob, self.tf_output,
		                   self.sess, player)

	'''
		This resets the tensorflow graph and keeps it running at 0.01 seconds per use.
		If this isn't called after at least every 200 calls the time per use for the nn will increase with each call.
	'''
	def clear_garbage_from_nn(self):
		reset_default_graph()
		self.training_input, self.heuristic, self.keep_prob, self.tf_output, self.sess = setup_network()


nodes_created = 0

class Node:
# <<<<<<< HEAD
	# DEFAULT_DEPTH = 0
	# DEFAULT_BREADTH = 4
# =======
	DEFAULT_DEPTH = 1
	DEFAULT_BREADTH = 1
# >>>>>>> 8543d584518b4ed9d95ac3dfac1e6821a56a3e19
	DEFAULT_TIME_SECONDS = 5
	WIN_VALUE = 1

	"""
	Represents a move that can be made, how good that move is, and what moves can be made after it.
	"""
	def __init__(self, move: MoveStruct, board: Board, neural_network: Neural_Network, player_for_computer: int):
		global nodes_created
		nodes_created += 1
		self._explore_count = 1
		self.children = []
		self.x, self.y = move
		self._board = board
		self.neural_network = neural_network
		self.player = self.get_player_of_node()
		self.player_for_computer = player_for_computer

		# Value between -1 and 1, where 1 means we've won, and -1 means we've lost.
		self._default_value = self.WIN_VALUE if self.is_winning_move() else self.neural_network.nn(self._board, self.player)
		self._default_value = self.negate_score_for_opponent_node(self._default_value)
		self.value = self._default_value

	def is_winning_move(self) -> bool:
		return self._board.decide_winner()[0] is not 0

	def get_player_of_node(self) -> int:
		# - because the board will have the player which is about to move not the player for which this node belongs
		return -self._board.get_next_player()

	def get_move(self) -> MoveStruct:
		return self.x, self.y

	def explore(self):
		self._explore_count += 1
		player_to_move = self._board.get_next_player()
		played_moves = self._board.get_played_moves()
		moves = self.get_playable_moves(played_moves)
		# print("Exploring %r,%r: %r" % (self.x, self.y, moves))
		for x, y in moves:
			# print(x,y,self.player_to_move)
			assert self._board.move(x, y, player_to_move)
			child = self.create_child_node(x, y)
			self.children.append(child)
			reversed_move = self._board.reverse_move()
			assert reversed_move == (x, y, player_to_move), "%r vs %r" % (reversed_move, (x, y, player_to_move))
		# print(self.debug_nn_outputs)

		self.children = sorted(self.children, key=lambda child: child.value, reverse=True)

	def create_child_node(self, x: int, y: int) -> "Node":
		next_board = deepcopy(self._board)
		child = Node((x, y), next_board, self.neural_network, self.player_for_computer)
		return child

	def _monte_carlo_score(self, child: "Node") -> float:
		value = child.value
		node_count = child._explore_count
		total_count = sum(c._explore_count for c in self.children)
		score = value + (2 * math.log(total_count) / node_count) ** 0.5
		# print("Monte carlo score: (%r) (%r)" % (child, score))
		return score

	def _select_children(self, children: List["Node"]) -> List["Node"]:
		return sorted(children, key=self._monte_carlo_score, reverse=True)

	def get_play(self, depth: int = DEFAULT_DEPTH, breadth: int = DEFAULT_BREADTH, time_seconds: int = DEFAULT_TIME_SECONDS) -> "Node":
		global nodes_created
		start_time = datetime.utcnow()
		while (datetime.utcnow() - start_time) < timedelta(seconds=time_seconds):
			nodes_created = 0
			self.neural_network.clear_garbage_from_nn()
# <<<<<<< HEAD
		# 	child = self.select(depth, breadth)
		# for kid in self.children:
		# 	print(kid.value)
		# 	print(kid.x)
		# 	print(kid.y)
		# 	print("-")
		# print(child.value)
		# print(child.x)
		# print(child.y)
		# # print(datetime.utcnow() - start_time)
		# return child
# =======
			self.select(depth, breadth)
			winning = sorted(self.children, key=lambda c:c.value)[-1]
			# print("%r, Time: %ds, Nodes: %r" % (winning._board.get_last_move(), (datetime.utcnow() - start_time).seconds, nodes_created))
			# print()
		print("Making move %r: %ds" % (winning._board.get_last_move(), (datetime.utcnow() - start_time).seconds))
		return winning
# >>>>>>> 8543d584518b4ed9d95ac3dfac1e6821a56a3e19

	def select(self, depth: int = DEFAULT_DEPTH, breadth: int = DEFAULT_BREADTH) -> "Node":
		if len(self.children) == 0:
			depth -= 1
			self.explore()

		winning_node = self.check_for_winning_node()
		if winning_node is not None:
			return winning_node

		children_to_explore = self._select_children(self.children)[:breadth]
		if depth > 0:
			for child in children_to_explore:
				child.select(depth)

		self.add_child_scores_to_value()

# <<<<<<< HEAD
		# children_to_explore = sorted(children_to_explore, key=lambda child: child.get_value(), reverse=True)
		# print("whores")
		# print(self.x)
		# print(self.y)
		# print("[")
		# for kid in children_to_explore:
		# 	print(kid.value)
		# print("]")
# =======
		children_to_explore = sorted(children_to_explore, key=lambda child: child.value, reverse=True)
# >>>>>>> 8543d584518b4ed9d95ac3dfac1e6821a56a3e19
		return children_to_explore[0] if children_to_explore else None

	def negate_score_for_opponent_node(self, v: int) -> int:
		if self.player != self.player_for_computer:
			return -v
		return v

	def add_child_scores_to_value(self):
# <<<<<<< HEAD
		# self.value = self.set_default_value()
		# self.value = ((self.value * 0.5) + (sum(c.value for c in self.children) * 0.5)) / (len(self.children) + 1)
		# self.negate_score_for_opponent_node()
# =======
		self.value = (self._default_value + sum(c.value for c in self.children)) / (len(self.children) + 1)
		self.value = self.negate_score_for_opponent_node(self.value)
# >>>>>>> 8543d584518b4ed9d95ac3dfac1e6821a56a3e19

	def check_for_winning_node(self) -> "Node":
		for child in self.children:
			if child.value == self.WIN_VALUE:
				return child

	def get_playable_moves(self, played_moves: list) -> list:
		# print(played_moves)
		if len(played_moves) > 0:
			moves = self.get_adjacent_moves(played_moves)
		else:
			# Todo: Replace with a better selection method.
			# Computer goes first so try from 10 random moves. Will most likely want to change at some point
			moves = self.pick_from_random()
		return moves

	def get_adjacent_moves(self, played_moves: list) -> set:
		adjacent_moves = []
		for move in played_moves:
			x = move[0]
			y = move[1]
			go_up = (x, y - 1)
			go_up_right = (x - 1, y - 1)
			go_right = (x - 1, y)
			go_down_right = (x - 1, y + 1)
			go_down = (x, y + 1)
			go_down_left = (x + 1, y + 1)
			go_left = (x + 1, y)
			go_up_left = (x + 1, y - 1)
			adjacent_moves.extend(
				(go_up, go_up_right, go_right, go_down_right, go_down, go_down_left, go_left, go_up_left))
		adjacent_moves = filter(lambda move: move not in played_moves and self.valid_coordinate(move), adjacent_moves)
		adjacent_moves = set(adjacent_moves)
		return adjacent_moves

	def valid_coordinate(self, move: MoveStruct) -> bool:
		return all(map(lambda x: 0 <= x < BOARD_SIZE, move))

	def pick_from_random(self) -> list:
		random_moves = []
		for i in range(0, 10):
			x = random.randint(0, BOARD_SIZE - 1)
			y = random.randint(0, BOARD_SIZE - 1)
			random_moves.append((x, y))
		return random_moves

	def __str__(self):
		return (self.x, self.y).__str__()


# ================================ start of computer ================================  
"""
Contains the logic required to run the bot against a board, and make a move.
"""
from copy import deepcopy

# from gomokuapp.board import Board, MoveStruct
# from players.player import INT_PLAYER_1, INT_PLAYER_2
# from treesearch import monte_carlo as mc
# from treesearch.monte_carlo import Neural_Network

# Change to True to produce heatmap PDFs
# GEN_GRAPH = False

# if GEN_GRAPH:
# 	from graph_main import use_graph_gen

class Computer:
	def __init__(self):
		self.neural_network = Neural_Network()
		self.node = None
		self.player_int = 0

	def make_move(self, brd: Board) -> MoveStruct:
		if self.is_new_game():
			self.set_player_number_for_computer(brd)
			self.create_node(brd)
		else:
			last_move = brd.get_last_move()
			assert last_move is not None, "Expected to have received a move but was None"
			node_found = self.update_node_to_child(last_move)
			if not node_found:
				self.create_node(brd, last_move)

		# if GEN_GRAPH:
		# 	use_graph_gen(self.node._board, self.neural_network)

		self.node = self.node.get_play()
		x, y = self.node.get_move()

		return x, y

	def is_new_game(self) -> bool:
		return self.node is None

	def create_node(self, brd: Board, move: MoveStruct = (None, None)):
		board = deepcopy(brd)
		self.node = Node(move, board, self.neural_network, self.player_int)

	def set_player_number_for_computer(self, board: Board):
		if board.get_last_move() is None:
			self.player_int = INT_PLAYER_1
		else:
			self.player_int = INT_PLAYER_2

	def update_node_to_child(self, last_move: MoveStruct) -> bool:
		for child in self.node.children:
			if child.get_move() == last_move:
				self.node = child
				return True
		return False


# ================================ start of source code ================================  

__author__ = "Jan Stránský (https://github.com/stranskyjan/pbrain-pyrandom), Modified for AlphaGomoku"

pp.infotext = 'name="AI-Gomoku", author="Shihan Ran", version="1.0", country="China"'


MAX_BOARD = 100
board = Board()

COMPUTER = Computer()


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
	COMPUTER = Computer()
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
