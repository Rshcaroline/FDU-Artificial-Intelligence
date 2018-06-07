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

from gomokuapp.board import BOARD_SIZE
from neuralnetwork.training_data import get_training_data, get_test_data

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
		return split_list_into_n_lists(train_input, number_of_batches), split_list_into_n_lists(train_output, number_of_batches), split_list_into_n_lists(
			heuristics, number_of_batches)


def shuffle_lists_together(train_input, train_output, heuristics):
	list_to_shuffle = list(zip(train_input, train_output, heuristics))
	random.shuffle(list_to_shuffle)
	# [:] means the result will be put into lists not tuples
	train_input[:], train_output[:], heuristics[:] = zip(*list_to_shuffle)
	return train_input, train_output, heuristics


def split_list_into_n_lists(list, n):
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
			winner_from_network = use_network(move[0], training_input, heuristic, keep_prob, tf_output, sess)
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


if __name__ == '__main__':
	get_failed_predictions()
