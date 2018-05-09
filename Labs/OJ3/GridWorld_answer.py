# -*- coding: utf-8 -*-
# __author__ = 'siyuan'
import random
WORLD_SIZE = 5
discount = 0.9
# left, up, right, down
actions = ['L', 'U', 'R', 'D']


def construct_MDP(A_POS, A_TO_POS, A_REWARD, B_POS, B_TO_POS, B_REWARD):
    nextState = []
    actionReward = []
    for i in range(0, WORLD_SIZE):
        nextState.append([])
        actionReward.append([])
        for j in range(0, WORLD_SIZE):
            next = dict()
            reward = dict()
            if i == 0:
                next['U'] = [i, j]
                reward['U'] = -1.0
            else:
                next['U'] = [i - 1, j]
                reward['U'] = 0.0

            if i == WORLD_SIZE - 1:
                next['D'] = [i, j]
                reward['D'] = -1.0
            else:
                next['D'] = [i + 1, j]
                reward['D'] = 0.0

            if j == 0:
                next['L'] = [i, j]
                reward['L'] = -1.0
            else:
                next['L'] = [i, j - 1]
                reward['L'] = 0.0

            if j == WORLD_SIZE - 1:
                next['R'] = [i, j]
                reward['R'] = -1.0
            else:
                next['R'] = [i, j + 1]
                reward['R'] = 0.0

            if [i, j] == A_POS:
                next['L'] = next['R'] = next['D'] = next['U'] = A_TO_POS
                reward['L'] = reward['R'] = reward['D'] = reward['U'] = A_REWARD

            if [i, j] == B_POS:
                next['L'] = next['R'] = next['D'] = next['U'] = B_TO_POS
                reward['L'] = reward['R'] = reward['D'] = reward['U'] = B_REWARD

            nextState[i].append(next)
            actionReward[i].append(reward)

    return nextState, actionReward


# value iteration
def value_iteration(nextState, actionReward):
    world = [[0 for _ in range(WORLD_SIZE)] for _ in range(WORLD_SIZE)]
    while True:
        # keep iteration until convergence
        difference = 0
        for i in range(0, WORLD_SIZE):
            for j in range(0, WORLD_SIZE):
                values = []
                for action in actions:
                    newPosition = nextState[i][j][action]
                    values.append(actionReward[i][j][action] + discount * world[newPosition[0]][newPosition[1]])
                new_v = max(values)
                difference += abs(world[i][j]-new_v)
                world[i][j] = new_v
        if difference < 1e-4:
            print('Value Iteration')
            for j in range(WORLD_SIZE):
                print([round(each_v, 1)for each_v in world[j]])
            break


def policy_evaluation(world, policy, nextState, actionReward):
    while True:
        difference = 0
        for i in range(0, WORLD_SIZE):
            for j in range(0, WORLD_SIZE):
                action = actions[policy[i][j]]
                newPosition = nextState[i][j][action]
                new_v = actionReward[i][j][action] + discount * world[newPosition[0]][newPosition[1]]
                difference += abs(world[i][j]-new_v)
                world[i][j] = new_v
        if difference < 1e-4:
            break
    return world


# policy iteration
def policy_iteration(nextState, actionReward):
    # random initialize state value and policy
    world = [[0 for _ in range(WORLD_SIZE)] for _ in range(WORLD_SIZE)]
    policy = [[random.randint(0, len(actions)-1) for _ in range(WORLD_SIZE)] for _ in range(WORLD_SIZE)]
    while True:
        world = policy_evaluation(world, policy, nextState, actionReward)
        unchanged = True
        for i in range(0, WORLD_SIZE):
            for j in range(0, WORLD_SIZE):
                policy_action = actions[policy[i][j]]
                policy_newPosition = nextState[i][j][policy_action]
                policy_value = actionReward[i][j][policy_action] + discount * world[policy_newPosition[0]][policy_newPosition[1]]
                values = []
                for action in actions:
                    newPosition = nextState[i][j][action]
                    values.append(actionReward[i][j][action] + discount * world[newPosition[0]][newPosition[1]])
                if max(values) > policy_value:
                    max_index = 0
                    for k in range(1, len(values)):
                        if values[k] > values[max_index]:
                            max_index = k
                    policy[i][j] = max_index
                    unchanged = False
        if unchanged:
            break
    print('Policy Iteration')
    for j in range(WORLD_SIZE):
        print([round(each_v, 1) for each_v in world[j]])


def process_read(x):
    from_state = [int(x[0][1]), int(x[0][-2])]
    to_state = [int(x[1][1]), int(x[1][-2])]
    reward = float(x[-1])
    return from_state, to_state, reward


while True:
    try:
        A_list = input().strip().split()
        B_list = input().strip().split()
        A_POS, A_TO_POS, A_REWARD = process_read(A_list)
        B_POS, B_TO_POS, B_REWARD = process_read(B_list)
        nextState, actionReward = construct_MDP(A_POS, A_TO_POS, A_REWARD, B_POS, B_TO_POS, B_REWARD)
        value_iteration(nextState, actionReward)
        policy_iteration(nextState, actionReward)
    except EOFError:
        break


# Try to solve Grid World problem based on MDP.
# The grid world is of 5*5 size. The cells of the grid correspond to
# the states of the environment. At each cell, four actions are possible: north,
# south, east, and west, which deterministically cause the agent to move one
# cell in the respective direction on the grid. Actions that would take the agent
# off the grid leave its location unchanged, but also result in a reward of -1.
# Other actions result in a reward of 0, except those that move the agent out
# of the special states A and B. From state A, all four actions yield a reward of
# A_reward and take the agent to A_to. From state B, all actions yield a reward of B_reward
# and take the agent to B_to.The discount factor gamma=0.9.
# Try to use value iteration and policy iteration.

#input:
# [0,1] [4,1] 10.0
# [0,3] [2,3] 5.0

