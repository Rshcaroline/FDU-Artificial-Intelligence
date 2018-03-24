import heapq


class PriorityQueue(object):
    def __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item, priority):
        entry = (priority, self.count, item)
        heapq.heappush(self.heap, entry)
        self.count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.heap)
        return item

    def isEmpty(self):
        return len(self.heap) == 0

    def update(self, item, priority):
        for index, (p, c, i) in enumerate(self.heap):
            if i == item:
                if p <= priority:
                    break
                del self.heap[index]
                self.heap.append((priority, c, item))
                heapq.heapify(self.heap)
                break
        else:
            self.push(item, priority)


class node:
    """define node"""

    def __init__(self, state, parent, path_cost, action):
        self.state = state
        self.parent = parent
        self.path_cost = path_cost
        self.action = action


class problem:
    """searching problem"""

    def __init__(self, initial_state, actions):
        self.initial_state = initial_state
        self.actions = actions
        # 可以在这里随意添加代码或者不加

    def search_actions(self, state):
        relt = []
        for action in self.actions:
            if action[0] == state:
                relt += [action]
        return relt

    def solution(self, node):
        loc = node
        path = []
        while loc.state != self.initial_state:
            path.append(loc.state)
            loc = loc.parent
        return [self.initial_state] + path[::-1]
        # raise Exception('获取从初始节点到node的路径')

    def transition(self, state, action):
        if action[0] == state:
            return action[1]
        else:
            raise Exception('transition error')
        # raise Exception('节点的状态（名字）经过action转移之后的状态（名字）')

    def goal_test(self, state):
        return state == "Goal"
        # raise Exception('判断state是不是终止节点')

    def step_cost(self, state1, action, state2):
        if (action[0] == state1) and (action[1] == state2):
            return int(action[2])
        # raise Exception('获得从state1到通过action到达state2的cost')

    def child_node(self, node_begin, action):
        child = node(state=self.transition(node_begin.state, action),
                     parent=node_begin,
                     path_cost=node_begin.path_cost + self.step_cost(node_begin.state, action, self.transition(node_begin.state, action)),
                     action=action)
        return child
        # raise Exception('获取从起始节点node_begin经过action到达的node')


def UCS(problem):
    node_test = node(problem.initial_state, '', 0, '')
    frontier = PriorityQueue()
    frontier.push(node_test, node_test.path_cost)
    explored = []
    while not frontier.isEmpty():
        node_test = frontier.pop()
        if problem.goal_test(node_test.state):
            return problem.solution(node_test)
        explored += [node_test.state]
        for action in problem.search_actions(node_test.state):
            child = problem.child_node(node_test, action)
            if child.state not in explored:
                frontier.update(child, child.path_cost)
    return "Unreachable"


def main():
    actions = []
    while True:
        a = input().strip()
        if a != 'END':
            a = a.split()
            actions += [a]
        else:
            break
    graph_problem = problem('Start', actions)
    answer = UCS(graph_problem)
    s = "->"
    if answer == "Unreachable":
        print(answer)
    else:
        path = s.join(answer)
        print(path)


if __name__ == '__main__':
    main()