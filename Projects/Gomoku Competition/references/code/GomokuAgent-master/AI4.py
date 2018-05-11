#!/usr/bin/env python

from __future__ import print_function, division
import numba
import numpy as np

board_size = 15
estimate_level = 9
def strategy(state):
    """ Information provided to you:
    state = (board, last_move, playing, board_size)
    board = (x_stones, o_stones)
    stones is a set contains positions of one player's stones. e.g.
        x_stones = {(8,8), (8,9), (8,10), (8,11)}
    playing = 0|1, the current player's index
    Your strategy will return a position code for the next stone, e.g. (8,7)
    """

    global board_size
    board, last_move, playing, board_size = state
    initialize()

    other_player = int(not playing)
    my_stones = board[playing]
    opponent_stones = board[other_player]

    # put the first stone in the center if it's the start of the game
    center = int((board_size-1)/2)

    if last_move is None: # if it's the first move of the game
        best_move = (center, center)
        strategy.zobrist_code = strategy.zobrist_me[best_move]
        return (best_move[0]+1, best_move[1]+1)
    else:
        last_move = (last_move[0]-1, last_move[1]-1)
        # update zobrist_code with opponent last move
        strategy.zobrist_code ^= strategy.zobrist_opponent[last_move]

        # build new state representation
        state = np.zeros(board_size**2, dtype=np.int64).reshape(board_size, board_size)
        for i,j in my_stones:
            state[i-1,j-1] = 1
        for i,j in opponent_stones:
            state[i-1,j-1] = -1

        # if strategy.zobrist_code in U_stone.cache:
        #     print("Calculated Move: %.3f" %U_stone.cache[strategy.zobrist_code])
        # else:
        #     print("Didn't know this move!")

        if len(my_stones) == 0:
            level = 8
        else:
            level = 0

        # clear the U cache
        U_stone.cache = dict()

        alpha = -1.0
        beta = 2.0
        empty_spots_left = np.sum(state==0)
        best_move, best_q = best_action_q(state, strategy.zobrist_code, empty_spots_left, last_move, alpha, beta, 1, level)
    # update zobrist_code with my move
    strategy.zobrist_code ^= strategy.zobrist_me[best_move]
    # return the best move
    return (best_move[0]+1, best_move[1]+1)


level_max_n = [20, 20, 12, 12, 8, 8, 6, 6, 4, 4, 4, 4, 4, 4, 4]
def best_action_q(state, zobrist_code, empty_spots_left, last_move, alpha, beta, player, level):
    "Return the optimal action for a state"

    if empty_spots_left == 0: # Board filled up, it's a tie
        return None, 0.5
    move_interest_values = best_action_q.move_interest_values
    move_interest_values.fill(0) # reuse the same array
    # boost the interests of closer moves by a little bit
    # note that it might boost a taken spot, but an available spot will at least get 10 interest in find_interesting_moves()
    boost_dist = 3
    r, c = last_move
    xmin = max(0, r-boost_dist)
    xmax = min(board_size, r+boost_dist+1)
    ymin = max(0, c-boost_dist)
    ymax = min(board_size, c+boost_dist+1)
    move_interest_values[xmin:xmax, ymin:ymax] = 1.5

    verbose = False
    if level == 0:
        verbose = True

    n_moves = level_max_n[level]
    interested_moves = find_interesting_moves(state, empty_spots_left, move_interest_values, player, n_moves, verbose)

    if len(interested_moves) == 1:
        current_move = interested_moves[0]
        current_move = (current_move[0], current_move[1])
        if level == 0 and player == 1:
            return current_move, 0.5
        q = Q_stone(state, zobrist_code, empty_spots_left, current_move, alpha, beta, player, level)
        return current_move, q

    best_move = (interested_moves[0,0], interested_moves[0,1]) # continue to play even I'm losing

    if player == 1:
        max_q = 0.0
        for current_move in interested_moves:
            current_move = (current_move[0], current_move[1])
            q = Q_stone(state, zobrist_code, empty_spots_left, current_move, alpha, beta, player, level+1)
            if q > alpha: alpha = q
            if q > max_q:
                max_q = q
                best_move = current_move
                # if verbose:
                #     print(current_move, q)
            if q == 1.0 or beta <= alpha:
                break
        best_q = max_q
    elif player == -1:
        min_q = 1.0
        for current_move in interested_moves:
            current_move = (current_move[0], current_move[1])
            q = Q_stone(state, zobrist_code, empty_spots_left, current_move, alpha, beta, player, level+1)
            if q < beta: beta = q
            if q < min_q:
                min_q = q
                best_move = current_move
            if q == 0.0 or beta <= alpha:
                break
        best_q = min_q
    return best_move, best_q


@numba.jit(nopython=True, nogil=True)
def find_interesting_moves(state, empty_spots_left, move_interest_values, player, n_moves, verbose=False):
    """ Look at state and find the interesing n_move moves.
    input:
    -------
    state: numpy.array board_size x board_size
    empty_spots_left: number of empty spots on the board
    player: 1 or -1, the current player
    n_moves: int, desired number of interesing moves
    output:
    -------
    interested_moves: numpy.array final_n_moves x 2
        *note : final_n_moves = 1 if limited
        *       else final_n_moves = n_moves + number of length-4 moves
        *note2: final_n_moves will not exceed empty_spots_left
    # suggested_n_moves: suggested number of moves to
    """
    force_to_block = False
    exist_will_win_move = False
    directions = ((1,1), (1,0), (0,1), (1,-1))
    final_single_move = np.zeros(2, dtype=np.int64).reshape(1,2) # for returning the single move
    for r in range(board_size):
        for c in range(board_size):
            if state[r,c] != 0: continue
            interest_value = 10 # as long as it's a valid point, this is for avoiding the taken spaces
            my_hard_4 = 0
            for dr, dc in directions:
                my_line_length = 1 # last_move
                opponent_line_length = 1
                # try to extend in the positive direction (max 4 times)
                ext_r = r
                ext_c = c
                skipped_1 = 0
                my_blocked = False
                opponent_blocked = False
                for i in range(4):
                    ext_r += dr
                    ext_c += dc
                    if ext_r < 0 or ext_r >= board_size or ext_c < 0 or ext_c >= board_size:
                        break
                    elif state[ext_r, ext_c] == player:
                        if my_blocked is True:
                            break
                        else:
                            my_line_length += 1
                            opponent_blocked = True
                    elif state[ext_r, ext_c] == -player:
                        if opponent_blocked is True:
                            break
                        else:
                            opponent_line_length += 1
                            my_blocked = True
                    elif skipped_1 is 0:
                        skipped_1 = i + 1 # allow one skip and record the position of the skip
                    else:
                        break
                # the backward counting starts at the furthest "unskipped" stone
                forward_my_open = False
                forward_opponent_open = False
                if skipped_1 == 0:
                    my_line_length_back = my_line_length
                    opponent_line_length_back = opponent_line_length
                elif skipped_1 == 1:
                    my_line_length_back = 1
                    opponent_line_length_back = 1
                    forward_my_open = True
                    forward_opponent_open = True
                else:
                    if my_blocked is False:
                        my_line_length_back = skipped_1
                        opponent_line_length_back = 1
                        forward_my_open = True
                    else:
                        my_line_length_back = 1
                        opponent_line_length_back = skipped_1
                        forward_opponent_open = True
                my_line_length_no_skip = my_line_length_back
                opponent_line_length_no_skip = opponent_line_length_back

                # backward is a little complicated, will try to extend my stones first
                ext_r = r
                ext_c = c
                skipped_2 = 0
                opponent_blocked = False
                for i in range(5-my_line_length_no_skip):
                    ext_r -= dr
                    ext_c -= dc
                    if ext_r < 0 or ext_r >= board_size or ext_c < 0 or ext_c >= board_size:
                        break
                    elif state[ext_r, ext_c] == player:
                        my_line_length_back += 1
                        opponent_blocked = True
                    elif skipped_2 is 0 and state[ext_r, ext_c] == 0:
                        skipped_2 = i + 1
                    else:
                        break
                # see if i'm winning
                if my_line_length_back == 5:
                    final_single_move[0,0] = r
                    final_single_move[0,1] = c
                    return final_single_move
                    #interested_n_moves[0] = move
                    #return interested_n_moves, True

                # extend my forward line length to check if there is hard 4
                if skipped_2 is 0:
                    my_line_length += my_line_length_back - my_line_length_no_skip
                else:
                    my_line_length += skipped_2 - 1
                # notice that here the forward length can exceed 5 after extension, but it should be at max 4
                if my_line_length > 4:
                    my_line_length = 4

                backward_my_open = True if skipped_2 > 0 else False
                backward_opponent_open = False
                # then try to extend the opponent
                if opponent_blocked is True:
                    if skipped_2 == 1:
                        backward_opponent_open = True
                else:
                    ext_r = r
                    ext_c = c
                    skipped_2 = 0
                    for i in range(5-opponent_line_length_no_skip):
                        ext_r -= dr
                        ext_c -= dc
                        if ext_r < 0 or ext_r >= board_size or ext_c < 0 or ext_c >= board_size:
                            break
                        elif state[ext_r, ext_c] == -player:
                            opponent_line_length_back += 1
                        elif skipped_2 is 0 and state[ext_r, ext_c] == 0:
                            skipped_2 = i + 1
                        else:
                            break

                    # extend my forward line length to check if there is hard 4
                    if skipped_2 is 0:
                        opponent_line_length += opponent_line_length_back - opponent_line_length_no_skip
                    else:
                        opponent_line_length += skipped_2 - 1
                        backward_opponent_open = True
                        # here if opponent_line_length_back == 5, skipped_2 will be 0 and this flag won't be True
                        # but it do not affect our final result, because we have to block this no matter if it's open
                    # notice that here the forward length can exceed 5 after extension, but it should be at max 4
                    if opponent_line_length > 4:
                        opponent_line_length = 4

                # check if we have to block this
                if opponent_line_length_back == 5:
                    final_single_move[0,0] = r
                    final_single_move[0,1] = c
                    force_to_block = True
                elif force_to_block is False:
                    # if I will win after this move, I won't consider other moves
                    if forward_my_open is True and my_line_length == 4:
                        my_hard_4 += 1
                    if backward_my_open is True and my_line_length_back == 4:
                        my_hard_4 += 1
                    if my_hard_4 >= 2:
                        final_single_move[0,0] = r
                        final_single_move[0,1] = c
                        exist_will_win_move = True
                if force_to_block is False and exist_will_win_move is False:
                    # compute the interest_value for other moves
                    if forward_my_open is True:
                        interest_value += my_line_length ** 4
                    if backward_my_open is True:
                        interest_value += my_line_length_back ** 4
                    if forward_opponent_open is True:
                        interest_value += opponent_line_length ** 4
                    if backward_opponent_open is True:
                        interest_value += opponent_line_length_back ** 4
            # after looking at all directions, record the total interest_value of this move
            move_interest_values[r, c] += interest_value
            if interest_value > 256: # one (length_4) ** 4, highly interesting move
                n_moves += 1

    # all moves have been investigated now see if we have to block first
    if force_to_block is True or exist_will_win_move is True:
        if verbose is True:
            # print(final_single_move[0,0], final_single_move[0,1], "Only One")
            pass
        return final_single_move
    else:
        flattened_interest = move_interest_values.ravel()
        # The interest value > 250 means at least one length_4 or three length_3 which make it highly interesting
        #n_high_interest_moves = np.sum(flattened_interest > 266) # did it in the loop
        if n_moves > empty_spots_left:
            n_moves = empty_spots_left
        high_interest_idx = np.argsort(flattened_interest)[-n_moves:][::-1]
        interested_moves = np.empty(n_moves*2, dtype=np.int64).reshape(n_moves, 2)
        interested_moves[:,0] = high_interest_idx // board_size
        interested_moves[:,1] = high_interest_idx % board_size

        # if verbose is True:
            # print("There are", n_moves, "interested_moves")
            # for i in range(n_moves):
                # print(interested_moves[i,0],interested_moves[i,1],'  :  ', flattened_interest[high_interest_idx[i]])
        return interested_moves


def Q_stone(state, zobrist_code, empty_spots_left, current_move, alpha, beta, player, level):
    # update the state
    state[current_move] = player
    # update the zobrist code for the new state
    if player == 1:
        move_code = strategy.zobrist_me[current_move]
    else:
        move_code = strategy.zobrist_opponent[current_move]
    new_zobrist_code = zobrist_code ^ move_code

    result = U_stone(state, new_zobrist_code, empty_spots_left-1, current_move, alpha, beta, player, level)
    # revert the changes for the state
    state[current_move] = 0
    return result


def U_stone(state, zobrist_code, empty_spots_left, last_move, alpha, beta, player, level):
    try:
        return U_stone.cache[zobrist_code]
    except:
        pass

    if i_will_win(state, last_move, player):
        return 1.0 if player == 1 else 0.0
    elif level >= estimate_level:
        result = estimate_U(state, player)
    else:
        best_move, best_q = best_action_q(state, zobrist_code, empty_spots_left, last_move, alpha, beta, -player, level)
        result = best_q

    U_stone.cache[zobrist_code] = result
    return result


@numba.jit(nopython=True, nogil=True)
def estimate_U(state, player):
    u = 0.0
    my_max_n = 0
    opponent_max_n = 0
    for i in range(board_size):
        for j in range(board_size):
            # horizontal wins --
            if j <= board_size - 5:
                my_blocked, opponent_blocked = False, False
                my_n, opponent_n = 0, 0
                for k in range(5):
                    if state[i, j+k] == -1:
                        my_blocked = True
                        opponent_n += 1
                    elif state[i, j+k] == 1:
                        opponent_blocked = True
                        my_n += 1
                    if my_blocked is True and opponent_blocked is True:
                        break
                if my_blocked is False:
                    u += 3 ** my_n
                    if my_n > my_max_n:
                        my_max_n = my_n
                if opponent_blocked is False:
                    u -= 3 ** opponent_n
                    if opponent_n > opponent_max_n:
                        opponent_max_n = opponent_n
            # vertical wins |
            if i <= board_size - 5:
                my_blocked, opponent_blocked = False, False
                my_n, opponent_n = 0, 0
                for k in range(5):
                    if state[i+k, j] == -1:
                        my_blocked = True
                        opponent_n += 1
                    elif state[i+k, j] == 1:
                        opponent_blocked = True
                        my_n += 1
                    if my_blocked is True and opponent_blocked is True:
                        break
                if my_blocked is False:
                    u += 3 ** my_n
                    if my_n > my_max_n:
                        my_max_n = my_n
                if opponent_blocked is False:
                    u -= 3 ** opponent_n
                    if opponent_n > opponent_max_n:
                        opponent_max_n = opponent_n
            # left oblique wins /
            if i <= board_size - 5 and j >= 4:
                my_blocked, opponent_blocked = False, False
                my_n, opponent_n = 0, 0
                for k in range(5):
                    if state[i+k, j-k] == -1:
                        my_blocked = True
                        opponent_n += 1
                    elif state[i+k, j-k] == 1:
                        opponent_blocked = True
                        my_n += 1
                    if my_blocked is True and opponent_blocked is True:
                        break
                if my_blocked is False:
                    u += 3 ** my_n
                    if my_n > my_max_n:
                        my_max_n = my_n
                if opponent_blocked is False:
                    u -= 3 ** opponent_n
                    if opponent_n > opponent_max_n:
                        opponent_max_n = opponent_n
            # right oblique wins \
            if i <= board_size - 5 and j <= board_size - 5:
                my_blocked, opponent_blocked = False, False
                my_n, opponent_n = 0, 0
                for k in range(5):
                    if state[i+k, j+k] == -1:
                        my_blocked = True
                        opponent_n += 1
                    elif state[i+k, j+k] == 1:
                        opponent_blocked = True
                        my_n += 1
                    if my_blocked is True and opponent_blocked is True:
                        break
                if my_blocked is False:
                    u += 3 ** my_n
                    if my_n > my_max_n:
                        my_max_n = my_n
                if opponent_blocked is False:
                    u -= 3 ** opponent_n
                    if opponent_n > opponent_max_n:
                        opponent_max_n = opponent_n
    if player == 1: # next move is opponent
        longer = 2 * (3 **opponent_max_n)  # one of the longest can get 1 longer
        block = 3 ** my_max_n
        u -= max(longer, block)
    else: # next move is me
        longer = 2 * (3 ** my_max_n)
        block = 3 ** opponent_max_n
        u += max(longer, block)

    if u > 0:
        result = 1.0 - 0.5 * np.exp(-u**2 * 0.0001)
    else:
        result = 0.5 * np.exp(-u**2 * 0.0001)
    return result


@numba.jit(nopython=True,nogil=True)
def i_will_win(state, last_move, player):
    """ Return true if I will win next step if the opponent don't have 4-in-a-row.
    Winning Conditions:
        1. 5 in a row.
        2. 4 in a row with both end open. (free 4)
        3. 4 in a row with one missing stone x 2 (hard 4 x 2)
     """
    r, c = last_move
    # try all 4 directions, the other 4 is equivalent
    directions = [(1,1), (1,0), (0,1), (1,-1)]
    n_hard_4 = 0 # number of hard 4s found
    for dr, dc in directions:
        line_length = 1 # last_move
        # try to extend in the positive direction (max 4 times)
        ext_r = r
        ext_c = c
        skipped_1 = 0
        for i in range(4):
            ext_r += dr
            ext_c += dc
            if ext_r < 0 or ext_r >= board_size or ext_c < 0 or ext_c >= board_size:
                break
            elif state[ext_r, ext_c] == player:
                line_length += 1
            elif skipped_1 is 0 and state[ext_r, ext_c] == 0:
                skipped_1 = i+1 # allow one skip and record the position of the skip
            else:
                break
        if line_length is 5:
            return True # 5 in a row
        # try to extend in the opposite direction
        ext_r = r
        ext_c = c
        skipped_2 = 0
        # the backward counting starts at the furthest "unskipped" stone
        if skipped_1 is not 0:
            line_length_back = skipped_1
        else:
            line_length_back = line_length
        line_length_no_skip = line_length_back
        for i in range(5-line_length_back):
            ext_r -= dr
            ext_c -= dc
            if ext_r < 0 or ext_r >= board_size or ext_c < 0 or ext_c >= board_size:
                break
            elif state[ext_r, ext_c] == player:
                line_length_back += 1
            elif skipped_2 is 0 and state[ext_r, ext_c] == 0:
                skipped_2 = i + 1
            else:
                break
        if line_length_back is 5:
            return True # 5 in a row
        if line_length_back == 4 and skipped_2 is not 0:
            n_hard_4 += 1 # backward hard 4
            if n_hard_4 == 2:
                return True # two hard 4

        # extend the forward line to the furthest "unskipped" stone
        if skipped_2 is 0:
            line_length += line_length_back - line_length_no_skip
        else:
            line_length += skipped_2 - 1
        if line_length >= 4 and skipped_1 is not 0:
            n_hard_4 += 1 # forward hard 4
            if n_hard_4 == 2:
                return True # two hard 4 or free 4
    return False


def initialize():
    # initialize zobrist for u caching
    if not hasattr(strategy, 'zobrist_me'):
        strategy.zobrist_me = np.random.randint(np.iinfo(np.int64).max, size=board_size**2).reshape(board_size,board_size)
    #if not hasattr(strategy, 'zobrist_opponent'):
        strategy.zobrist_opponent = np.random.randint(np.iinfo(np.int64).max, size=board_size**2).reshape(board_size,board_size)
    #if not hasattr(strategy, 'zobrist_code'):
        strategy.zobrist_code = 0
    if not hasattr(U_stone, 'cache'):
        U_stone.cache = dict()
    if not hasattr(best_action_q, 'move_interest_values'):
        best_action_q.move_interest_values = np.zeros(board_size**2, dtype=np.float32).reshape(board_size,board_size)


def finish():
    del strategy.zobrist_me
    del strategy.zobrist_opponent
    del strategy.zobrist_code
    del U_stone.cache
    del best_action_q.move_interest_values
    return
