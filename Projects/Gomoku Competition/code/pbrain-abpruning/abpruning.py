# -*- coding: utf-8 -*-
"""
alpha-beta pruning method
created by YAO
"""

from util import *
import copy


class Node:
    def __init__(self, player=1, successor=[], isLeaf=False, value=None, action=None):
        if player == 1:
            self.rule = 'max'
        elif player == 2:
            self.rule = 'min'
        self.successor = successor
        self.isLeaf = isLeaf
        self.value = value
        self.action = action  # which action to get this state, its board value is 3-player


def value(node, alpha, beta):

    if node.rule == 'max':
        return maxValue(node, alpha, beta)
    else:
        return minValue(node, alpha, beta)


def maxValue(node, alpha, beta):

    if node.isLeaf:
        return node.value, None  # means no actions next
    else:
        action = None
        temp_alpha = alpha
        up_bound = float('-inf')
        # print 'len', len(node.successor)
        for child in node.successor:
            # print child.value, temp_alpha, beta
            if minValue(child, temp_alpha, beta)[0] > up_bound:
                # print 'hhh', minValue(child, temp_alpha, beta)[0], up_bound
                # print 'first if called'
                up_bound = minValue(child, temp_alpha, beta)[0]
                action = child.action  # renew action
            if up_bound >= beta:
                # print 'second if called'
                return up_bound, None  # pruning, don't care how to arrive it
            temp_alpha = max(temp_alpha, up_bound)
        return up_bound, action


def minValue(node, alpha, beta):

    if node.isLeaf:
        return node.value, None
    else:
        action = None
        temp_beta = beta
        low_bound = float('inf')
        for child in node.successor:
            if maxValue(child, alpha, temp_beta)[0] < low_bound:
                action = child.action  # renew action
                low_bound = maxValue(child, alpha, temp_beta)[0]
            if low_bound <= alpha:
                return low_bound, None  # pruning, don't care how to arrive it
            temp_beta = min(low_bound, temp_beta)
        return low_bound, action


def constructTree(n, board, player, action, prob_position=None):
    """
    construct a tree using given information, and return the root node
    :param
        n: the depth of the tree
        board: the whole board
        player: whose turn
        prob_pos: prob_pos for the temporary board
        action: how to get the root node of this tree
    :return: root node
    """
    expend_num = 6
    node = Node(player=player, action=action)
    successors = []
    if prob_position == None:

        prob_position = probable_position(board)
        if prob_position == None:
            return None
    # print prob_pos
    # print board
    top_list = []

    if n == 1:
        if len(prob_position) < expend_num:
            for pos in prob_position:
                board_copy = [[board[x][y] for y in range(pp.height)] for x in range(pp.width)]
                board_copy[pos[0]][pos[1]] = player
                temp_value = board_evaluation(board_copy)
                # print temp_value
                # successors.append(Node(player=3-player, isLeaf=True, value=board_evaluation(board_copy), action=pos))
                successors.append(Node(player=3 - player, isLeaf=True, value=temp_value, action=pos))  # TODO: need to delete
        else:
            for pos in prob_position:
                board_copy = [[board[x][y] for y in range(pp.height)] for x in range(pp.width)]
                board_copy[pos[0]][pos[1]] = player
                temp_value = board_evaluation(board_copy)
                top_list.append(temp_value)
            temp_list = top_list[:]
            temp_list.sort(reverse=True)
            for v in temp_list[0:expend_num]:
                pos = prob_position[top_list.index(v)]
                successors.append(Node(player=3 - player, isLeaf=True, value=v, action=pos))

    else:
        if len(prob_position) < expend_num:
            # i = 0
            for pos in prob_position:
                # i += 1
                # print pos, 'else called', i
                board_copy = [[board[x][y] for y in range(pp.height)] for x in range(pp.width)]
                board_copy[pos[0]][pos[1]] = player
                # print board_copy
                successors.append(constructTree(n-1, board_copy, 3-player, pos, renew_probable_position(pos, prob_position)))
        else:
            for pos in prob_position:
                board_copy = [[board[x][y] for y in range(pp.height)] for x in range(pp.width)]
                board_copy[pos[0]][pos[1]] = player
                top_list.append(board_evaluation(board_copy))
            temp_list = top_list[:]
            temp_list.sort(reverse=True)
            for v in temp_list[0:expend_num]:
                pos = prob_position[top_list.index(v)]
                board_copy = [[board[x][y] for y in range(pp.height)] for x in range(pp.width)]
                board_copy[pos[0]][pos[1]] = player
                successors.append(constructTree(n - 1, board_copy, 3 - player, pos, renew_probable_position(pos, prob_position)))
    node.successor = successors
    return node


def pruning_brain():
    max_depth = 1

    root_node = constructTree(max_depth, board, 1, None)
    if root_node is None:
        pp.do_mymove(10, 10)
    else:
        max_value, action = value(root_node, float("-inf"), float("inf"))
    # assert action is not None
        pp.do_mymove(action[0], action[1])
    # print(action)