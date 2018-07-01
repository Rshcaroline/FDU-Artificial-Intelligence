import random
import re
import time
import copy
import shape

OUTPUT = False
MAX_BOARD = 20
board = [[0 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]

class Threats(object):

    def __init__(self):
        self.color = None
        self.turn = -1
        self.seq = []
        self.first_seq = []
        self.detected = False
        self.class_dict = shape.threat_dict
        self.victory_dict = shape.victory_dict
        self.shape_dict = shape.class_dict

    def who_am_i(self):
        black, white = 0, 0
        for row in board:
            for i in row:
                if i == 1:
                    black += 1
                elif i == 2:
                    white += 1
        self.color = 1 if black == white else 2
        return self.color

    def get_move(self, array):
        """
        :param: board array, type: list, shape: (pp.height, pp.width)
        :return: the tuple of position, which can outcome threats and double threats, search depth is 2
        """
        self.turn += 1
        self.color = self.who_am_i()
        height, width = len(array), len(array[0])

        if self.turn == 0:
            pos = [(i, j) for i in range(height) for j in range(width)]
            counter = 0
            pp = None
            for p in pos:
                if array[p[0]][p[1]] == self._opp_color(self.color):
                    counter += 1
                    pp = p
            if counter <= 1: 
                if pp is not None:
                    return (min(height-1, max(0, pp[0] + random.randint(-1,1))), min(width-1,max(0, pp[1] + random.randint(-1,1))))
                else:
                    return (height//2, width//2)

        if OUTPUT: print("my victory")
        victory = self.detect_now(array, self.color, shape.threats_dict[0])
        if len(victory):
            return victory[0]

        if OUTPUT: print("your victory")
        threat = self.detect_now(array, self._opp_color(self.color), shape.threats_dict[0])
        if len(threat):
            if len(threat) > 1:
                t0 = self.point_evaluation(self._add_point(array, threat[0][0], threat[0][1], self.color), threat[0], self.color, class_dict=shape.class_dict) 
                t1 = self.point_evaluation(self._add_point(array, threat[1][0], threat[1][1], self.color), threat[1], self.color, class_dict=shape.class_dict)
                return threat[0] if  t0 > t1 else threat[1] 
            else:
                return threat[0]
        

        if OUTPUT: print("my coming victory")
        victory = self.detect_now(array, self.color, shape.threats_dict[1])
        if (len(victory)):
            return victory[0]

        if OUTPUT: print("your coming victory")
        threat = self.detect_now(array, self._opp_color(self.color), shape.threats_dict[1])
        if len(threat):
            if len(threat) > 1:
                t0 = self.point_evaluation(self._add_point(array, threat[0][0], threat[0][1], self.color), threat[0], self.color, class_dict=shape.class_dict) 
                t1 = self.point_evaluation(self._add_point(array, threat[1][0], threat[1][1], self.color), threat[1], self.color, class_dict=shape.class_dict)
                return threat[0] if  t0 > t1 else threat[1] 
            else:
                return threat[0]

        if OUTPUT: print("my double threats")
        threats = self.detect_expend(array, self.color, shape.threats_dict[2])
        if len(threats):
            return threats

        if OUTPUT: print("your double threats")
        threats = self.detect_expend(array, self._opp_color(self.color), shape.threats_dict[2])
        if len(threats):
            return threats

        if OUTPUT: print("your greedy choice")
        choice = self.greedy_search(array, self.color, shape.class_dict)
        return choice 

    def greedy_search(self, array, color, class_dict):
        height, width = len(array), len(array[0])
        pos = [(i, j) for i in range(height) for j in range(width)]
        choices = {}
        for p in pos:
            if array[p[0]][p[1]] == 0:
                t1 = self.point_evaluation(self._add_point(array, p[0], p[1], self.color), p, self.color, class_dict=shape.class_dict) 
                t2 = self.point_evaluation(array, p, self.color, class_dict=shape.class_dict) 
                t = t1 - t2
                if t in choices:
                    choices[t].append(p)
                else:
                    choices[t] = [p]
        idx = max(list(choices))
        return choices[idx][random.randint(0, len(choices[idx])-1)]



    def detect_now(self, array, color, class_dict):
        # if color == 2:
        #     array = self._convert_color(array)
        self.threat_set_my_now = self._detect_threat(array, color, class_dict=class_dict)
        if len(self.threat_set_my_now):
            return self.threat_set_my_now[0][-1]
        return ()
    
    def detect_expend(self, array, color, class_dict):

        # detect the double threat
        threat_set_opp = []

        for gain_square, new_array in self._traverse_array(array, color):
            temp = self._detect_new_threat(new_array, color,  gain_square=gain_square, class_dict=class_dict)
            if len(temp) > 1:
                threat_set_opp.extend(temp)
                return temp[0][2]

        return ()


    def detect_threat(self, array):
        """
        :return: [[type, cost_square], [type, cost_square], ...]
        """
        self.detected = True
        REDIUS = 20
        DEPTH = 1

        # opp and my
        opp_threats = []
        self.threat_set_opp_now = self._detect_threat(
            array, self._opp_color(self.color), class_dict=self.class_dict)

        # detect the double threat
        threat_set_opp = []

        for gain_square, new_array in self._traverse_array(array, self._opp_color(self.color)):
            sub_array, ini_point = self._slice(new_array, gain_square, REDIUS)
            temp = self._detect_new_threat(sub_array, self._opp_color(
                self.color), point_ini=ini_point, gain_square=gain_square, class_dict=self.class_dict)
            if len(temp) > 1:
                threat_set_opp.extend(temp)

        threat_set_opp = self._distinct_threats(
            self.threat_set_opp_now, threat_set_opp)

        self.seq = self._shape_seq(threat_set_opp, self.threat_set_opp_now)


    def _debug_output(self, threat_set):
        print("============")
        for i, t in enumerate(threat_set[0]):
            print("%-2d" % i, end=" ")
        print("|")

        for i, threat in enumerate(threat_set):
            
            for t in threat:
                if t == 0:
                    print("-", end="  ")
                else:
                    print("%d" % t, end="  ")
            print("|%-2d" %i)
        print("============")

    def _color_recursive(self, array, node, color):
        if node is None:
            return array
        else:
            x, y = node[2]
            array[x][y] = color
            self._color_recursive(array, node[0], color)
            return array

    def _distinct_threats(self, threat_set_old, threat_set_new):
        threat_set_new_tmp = [(x[1], x[3]) for x in threat_set_new]
        threat_set_old_tmp = set([(x[1], x[3]) for x in threat_set_old])
        distinct_threat = [threat_set_new[idx] for idx, threat in enumerate(
            threat_set_new_tmp) if threat not in threat_set_old_tmp]
        return distinct_threat

    def _shape_seq(self, threat_set_my, threat_set_opp):
        """
        Shape the sequences for strategies
        """
        pri_map = {"five": (150, 0),
                   "straightfour": (90, 0),
                   "four": (60, 100),
                   "three": (60, 70),
                   "brokenthree": (30, 70),
                   }

        def _shape_move_my(threat):
            moves = []
            while threat is not None:
                moves.append(threat[2])
                threat = threat[0]
            return moves

        def _shape_move_opp(threat):
            moves = [threat[3][0]]
            node = threat[0]
            while node is not None:
                moves.append(node[3][0])
                node = node[0]
            length = 0 if threat[2] is None else 1
            return (pri_map[threat[1]][1]//(len(moves)+length), [moves[-1]])

        seq = [(pri_map[t[1]][0], _shape_move_my(t)) for t in threat_set_my]
        seq += [_shape_move_opp(t) for t in threat_set_opp]

        # print("++++++++++++++++++++++")
        if OUTPUT: self._debug_output(threat_set_my)
        if OUTPUT: self._debug_output(threat_set_opp)
        # print("++++++++++++++++++++++")

        from collections import Counter
        first_counter = Counter([s[1][-1] for s in seq])
        seq = [(first_counter[s[1][-1]] + s[0], s[1]) for s in seq]
        seq.sort(key=lambda x: x[0])
        # print(seq)
        return seq

    def _add_point(self, array, i, j, color):
        array_new = copy.deepcopy(array)
        if array_new[i][j] == 0:
            array_new[i][j] = color
        return array_new

    def _traverse_array(self, array, color):
        height, width = len(array), len(array[0])
        return [((i, j), self._add_point(array, i, j, color)) for i in range(height) for j in range(width) if array[i][j] == 0]

    def _opp_color(self, color):
        return (3 - color) % 3

    def _convert_color(self, array):
        array = copy.deepcopy(array)
        height, width = len(array), len(array[0])
        for i in range(height):
            for j in range(width):
                array[i][j] = self._opp_color(array[i][j])
        return array

    def _slice(self, array, center, radius):
        height, width = len(array), len(array[0])
        subarray = [row[max(0, center[1]-radius):min(center[1]+radius+1, width)]
                    for row in array[max(center[0]-radius, 0): min(center[0]+radius+1, height)]]
        row_ini, col_ini = max(center[0]-radius, 0), max(center[1]-radius, 0)
        return subarray, (row_ini, col_ini)

    def _detect_new_threat(self, array, color, parent=None, gain_square=None, point_ini=(0, 0), class_dict=None):
        if color == 2:
            array = self._convert_color(array)

        r_0, c_0 = point_ini
        threats, N = [], 0
        height, width = len(array), len(array[0])

        # scan the row
        row_idx = gain_square[0]
        list_str = "".join(map(str, array[row_idx]))
        for key in class_dict:
            positions = [
                i.start()+N for i in re.finditer(class_dict[key], list_str)]
            for p in positions:
                threats.append((parent, key[0], gain_square, tuple(
                    [(r_0+row_idx, c_0+p+offset) for offset in key[1]])))

        # scan the col
        col_idx = gain_square[1]
        col = [a[col_idx] for a in array]
        list_str = "".join(map(str, col))
        for key in class_dict:
            positions = [
                i.start()+N for i in re.finditer(class_dict[key], list_str)]
            for p in positions:
                threats.append((parent, key[0], gain_square, tuple(
                    [(r_0+p+offset, c_0+col_idx) for offset in key[1]])))

        # scan diag_1
        dist = gain_square[0] - gain_square[1]
        row_ini, col_ini = (0, -dist) if dist < 0 else (dist, 0)
        diag = [array[i][j] for i in range(
            row_ini, height) for j in range(col_ini, width) if i-j == dist]
        list_str = "".join(map(str, diag))
        for key in class_dict:
            positions = [
                i.start()+N for i in re.finditer(class_dict[key], list_str)]
            for p in positions:
                threats.append((parent, key[0], gain_square, tuple(
                    [(r_0+row_ini+p+offset, c_0+col_ini+p+offset) for offset in key[1]])))

        dist = gain_square[0] + gain_square[1]
        row_ini, col_ini = (dist, 0) if dist < height else (
            height-1, dist-height+1)
        diag = [array[i][j] for i in range(
            row_ini, -1, -1) for j in range(col_ini, width) if i+j == dist]
        list_str = "".join(map(str, diag))
        for key in class_dict:
            positions = [
                i.start()+N for i in re.finditer(class_dict[key], list_str)]
            for p in positions:
                threats.append((parent, key[0], gain_square, tuple(
                    [(r_0+row_ini-p-offset, c_0+col_ini+p+offset) for offset in key[1]])))

        return threats

    def _detect_threat(self, array, color, parent=None, gain_square=None, point_ini=(0, 0), class_dict=None):
        if color == 2:
            array = self._convert_color(array)

        r_0, c_0 = point_ini
        threats, N = [], 0
        height, width = len(array), len(array[0])

        # scan by row
        for row_idx, row in enumerate(array):
            list_str = "".join(map(str, row))
            for key in class_dict:
                positions = [
                    i.start()+N for i in re.finditer(class_dict[key], list_str)]
                for p in positions:
                    threats.append((parent, key[0], gain_square, tuple([
                                    (r_0+row_idx, c_0+p+offset) for offset in key[1]])))

        for col_idx in range(width):
            col = [a[col_idx] for a in array]
            list_str = "".join(map(str, col))
            for key in class_dict:
                positions = [
                    i.start()+N for i in re.finditer(class_dict[key], list_str)]
                for p in positions:
                    threats.append((parent, key[0], gain_square, tuple([
                                    (r_0+p+offset, c_0+col_idx) for offset in key[1]])))

        # scan by diag_1, from TL to BR
        for dist in range(-width+1, height):
            row_ini, col_ini = (0, -dist) if dist < 0 else (dist, 0)
            diag = [array[i][j] for i in range(
                row_ini, height) for j in range(col_ini, width) if i-j == dist]
            list_str = "".join(map(str, diag))
            for key in class_dict:
                positions = [
                    i.start()+N for i in re.finditer(class_dict[key], list_str)]
                for p in positions:
                    threats.append((parent, key[0], gain_square, tuple([
                                    (r_0+row_ini+p+offset, c_0+col_ini+p+offset) for offset in key[1]])))

        # scan by diag_2, from BL to TR
        for dist in range(0, width+height-1):
            row_ini, col_ini = (dist, 0) if dist < height else (
                height-1, dist-height+1)
            diag = [array[i][j] for i in range(
                row_ini, -1, -1) for j in range(col_ini, width) if i+j == dist]
            list_str = "".join(map(str, diag))
            for key in class_dict:
                positions = [
                    i.start()+N for i in re.finditer(class_dict[key], list_str)]
                for p in positions:
                    threats.append((parent, key[0], gain_square, tuple([
                                    (r_0+row_ini-p-offset, c_0+col_ini+p+offset) for offset in key[1]])))
        return threats

    def point_evaluation(self, array, pos, color, class_dict):
        """
        to assess a point
        ":param
            array:
            pos: (x, y)
            color: 1:black, 2:white
        :return:  the diction of number of this color pbrain
        """
        # add judgement here. Details in 'http://zjh776.iteye.com/blog/1979748'

        if color == 2:
            array = self._convert_color(array)

        height, width = len(array), len(array[0])
        class_score = 0

        # scan by row
        row_idx = pos[0]
        list_str = "".join(map(str, array[row_idx]))
        for key in class_dict:
            class_score += len(re.findall(class_dict[key], list_str)) * shape.score_map[key[0]]

        # scan by col
        col_idx = pos[1]
        col = [a[col_idx] for a in array]
        list_str = "".join(map(str, col))
        for key in class_dict:
            class_score += len(re.findall(class_dict[key], list_str)) * shape.score_map[key[0]]

        # scan by diag_1, from TL to BR
        dist = pos[0] - pos[1]
        row_ini, col_ini = (0, -dist) if dist < 0 else (dist, 0)
        diag = [array[i][j] for i in range(
            row_ini, height) for j in range(col_ini, width) if i - j == dist]
        list_str = "".join(map(str, diag))
        for key in class_dict:
            class_score += len(re.findall(class_dict[key], list_str)) * shape.score_map[key[0]]

        # scan by diag_2, from BL to TR
        dist = pos[0] + pos[1]
        row_ini, col_ini = (dist, 0) if dist < height else (
            height - 1, dist - height + 1)
        diag = [array[i][j] for i in range(
            row_ini, -1, -1) for j in range(col_ini, width) if i + j == dist]
        list_str = "".join(map(str, diag))
        for key in class_dict:
            class_score += len(re.findall(class_dict[key], list_str)) * shape.score_map[key[0]]

        return class_score



if __name__ == "__main__":

    array = \
   [[0, 0, 0, 0, 0, 0, 1, 2, 2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
    
    t = Threats()
    t.color = 2
    while True:
        if OUTPUT: t._debug_output(array)
        t1 = time.time()
        print(t.turn)
        if OUTPUT: print(t.get_move(array))
        if OUTPUT: print("you are: %s" % t.color)
        if OUTPUT: print("input your move (format: x,y):", end=" ")
        pos = input()
        pos = eval("[%s]" % pos)
        if array[pos[0]][pos[1]]: 
            continue
        array[pos[0]][pos[1]] = t.color
        if OUTPUT: print(time.time()-t1)
