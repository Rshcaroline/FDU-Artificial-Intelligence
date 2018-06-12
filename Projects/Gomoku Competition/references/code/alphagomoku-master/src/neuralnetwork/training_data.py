import glob
import pickle
from os.path import isfile
from sys import argv
from typing import List, Tuple

from gomokuapp.board import Board, BoardStruct, MovesStruct

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


if __name__ == '__main__':
	if len(argv) > 1:
		process_training_data(argv[1:], should_print=True)
	else:
		process_training_data(_TRAINING_DATA_FILES, should_print=True)
