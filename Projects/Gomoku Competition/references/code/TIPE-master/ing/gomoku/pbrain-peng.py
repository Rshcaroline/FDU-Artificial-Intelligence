import pisqpipe as pp
from pisqpipe import DEBUG_EVAL, DEBUG

pp.infotext = 'name="pbrain-pypeng", author="Peng-Wei Chen", version="2.0", country="Taiwan", www="https://github.com/pinnertw/TIPE"'

# setup
MAX_BOARD = 100
board = [[0 for i in xrange(MAX_BOARD)] for j in xrange(MAX_BOARD)]
pp.width, pp.height, first = 15, 15, True
neighbor = [15, 0, 15, 0]

# unfinished
def neigh(x, y):
    global neighbor
    neighbor[0] = max(0, min(neighbor[0], x-2))
    neighbor[1] = min(15, max(neighbor[1], x+3))
    neighbor[2] = max(0, min(neighbor[2], y-2))
    neighbor[3] = min(15, max(neighbor[3], y+3))


def print_score(turn):
        flag1 = 0
        print "\t",
        for i in range(15):
                print i, "\t",
        print "\n\n",
        for i in xrange(15):
            print flag1, "\t", 
            for j in xrange(15):
                print determine_tree(i, j, [], [], 2, turn), "\t",
            flag1 += 1
            print "\n\n",

def brain_init():
    if pp.width < 5 or pp.height < 5:
        pp.pipeOut("ERROR size of the board")
        return
    if pp.width > MAX_BOARD or pp.height > MAX_BOARD:
        pp.pipeOut("ERROR Maximal board size is {}".format(MAX_BOARD))
        return
    pp.pipeOut("OK")

def brain_restart():
    for x in xrange(pp.width):
        for y in xrange(pp.height):
            board[x][y] = 0
    global first
    first = True
    pp.pipeOut("OK")

def isFree(x, y):
    return x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] == 0

def brain_my(x, y):
    if isFree(x,y):
        board[x][y] = 1
        neigh(x, y)
    else:
        pp.pipeOut("ERROR my move [{},{}]".format(x, y))

def brain_opponents(x, y):
    global first
    if isFree(x,y):
        first = False
        board[x][y] = 2
        neigh(x, y)
    else:
        pp.pipeOut("ERROR opponents's move [{},{}]".format(x, y))

def brain_block(x, y):
    if isFree(x,y):
        board[x][y] = 3
        neigh(x, y)
    else:
        pp.pipeOut("ERROR winning move [{},{}]".format(x, y))

def brain_takeback(x, y):
    if x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] != 0:
        board[x][y] = 0
        return 0
    return 2

def print_board():
    li1 = []
    li2 = []
    for x in xrange(pp.height):
        for y in xrange(pp.width):
            if board[x][y] == 1:
                li1.append((x, y))
            elif board[x][y] == 2:
                li2.append((x, y))
    print 1, li1
    print 2, li2

def maxi(a, b, c):
# return the two biggest numbers among these three numbers
    if a > b:
        if b > c:
            return a, b
        else:
            return a, c
    else:
        if a > c:
            return a, b
        else:
            return b, c

def note(x, y, z):
    if x in [0.5, 1.5, 2.5, 3.5] or x + y in [0.5, 1.5, 2.5] or x + y + z in [0.5, 1.5] or y > 3:
        return 0
    elif x >= 4.5:
        return 1000
    elif x == 4 or x + y > 3 and z > 0:
        return 100
    elif x == 3.75 or x + y > 3:
        return 61
    elif x == 3 or x + y > 3 and z > 0:
        return 60
    elif x == 2.75 or x + y > 2:
        return 31
    elif x == 2 or x + y > 1 and z > 0:
        return 30
    elif x == 1.75 or x + y > 1:
        return 11
    elif x == 1 or z > 0:
        return 10
    elif x == 0.75:
        return 1

def evalue(x, y, turn, my, op):
# my: the one who plays
    if turn == 1:
        a, b = 1, 2
    elif turn == 0:
        a, b = 2, 1
    flag1, flag2, flag3, flag4, note1, note2 = 0, 0, 0, 0, 0, 0

# left-up to right-down
    for i in range(1, 5):
        if x-i < 0 or y-i < 0 or board[x-i][y-i] == b or (x-i, y-i) in op:
            flag1 -= 0.25
            break
        elif board[x-i][y-i] == a or (x-i, y-i) in my:
            flag1 += 1
        elif board[x-i][y-i] == 0 and flag4 == 0:
            flag4 += 1
            flag2 = flag1
            flag1 = 0
        else:
            break
    if flag4 == 1:
        flag1, flag2 = flag2, flag1
    for i in range(1, 5):
        if x+i > pp.height - 1 or y+i > pp.width - 1 or board[x+i][y+i] == b or (x+i, y+i) in op:
            flag1 -= 0.25
            break
        elif board[x+i][y+i] == a or (x+i, y+i) in my:
            flag1 += 1
        elif board[x+i][y+i] == 0 and flag4 == 0:
            flag4 += 2
            flag2 = flag1
            flag1 = 0
        elif board[x+i][y+i] == 0 and flag4 == 1:
            flag4 += 2
            flag3 = flag1
            flag1 = 0
        else:
            break
    if flag4 == 2:
        flag1, flag2 = flag2, flag1
    elif flag4 == 3:
        flag1, flag3 = flag3, flag1
    flag1 += 1
    flag2, flag3 = max(flag2, flag3), min(flag2, flag3)
    note1 = note(flag1, flag2, flag3)

# left to right
    flag1, flag2, flag3, flag4 = 0, 0, 0, 0
    for i in range(1, 5):
        if y-i < 0 or board[x][y-i] == b or (x, y-i) in op:
            flag1 -= 0.25
            break
        elif board[x][y-i] == a or (x, y-i) in my:
            flag1 += 1
        elif board[x][y-i] == 0 and flag4 == 0:
            flag4 += 1
            flag2 = flag1
            flag1 = 0
        else:
            break
    if flag4 == 1:
        flag1, flag2 = flag2, flag1
    for i in range(1, 5):
        if y+i > pp.width - 1 or board[x][y+i] == b or (x, y+i) in op:
            flag1 -= 0.25
            break
        elif board[x][y+i] == a or (x, y+i) in my:
            flag1 += 1

        elif board[x][y+i] == 0 and flag4 == 0:
            flag4 += 2
            flag2 = flag1
            flag1 = 0
        elif board[x][y+i] == 0 and flag4 == 1:
            flag4 += 2
            flag3 = flag1
            flag1 = 0
        else:
            break
    if flag4 == 2:
        flag1, flag2 = flag2, flag1
    elif flag4 == 3:
        flag1, flag3 = flag3, flag1
    flag1 += 1
    flag2, flag3 = max(flag2, flag3), min(flag2, flag3)
    note2 = note(flag1, flag2, flag3)

# left-down to right-up
    flag1, flag2, flag3, flag4 = 0, 0, 0, 0
    for i in range(1, 5):
        if x+i > pp.height - 1 or y-i < 0 or board[x+i][y-i] == b or (x+i, y-i) in op:
            flag1 -= 0.25
            break
        elif board[x+i][y-i] == a or (x+i, y-i) in my:
            flag1 += 1
        elif board[x+i][y-i] == 0 and flag4 == 0:
            flag4 += 1
            flag2 = flag1
            flag1 = 0
        else:
            break
    if flag4 == 1:
        flag1, flag2 = flag2, flag1
    for i in range(1, 5):
        if x-i < 0 or y+i > pp.width - 1 or board[x-i][y+i] == b or (x-i, y+i) in op:
            flag1 -= 0.25
            break
        elif board[x-i][y+i] == a or (x-i, y+i) in my:
            flag1 += 1
        elif board[x-i][y+i] == 0 and flag4 == 0:
            flag4 += 2
            flag2 = flag1
            flag1 = 0
        elif board[x-i][y+i] == 0 and flag4 == 1:
            flag4 += 2
            flag3 = flag1
            flag1 = 0
        else:
            break
    if flag4 == 2:
        flag1, flag2 = flag2, flag1
    elif flag4 == 3:
        flag1, flag3 = flag3, flag1
    flag1 += 1
    flag2, flag3 = max(flag2, flag3), min(flag2, flag3)
    note1, note2 = maxi(note1, note2, note(flag1, flag2, flag3))

# up to down
    flag1, flag2, flag3, flag4 = 0, 0, 0, 0
    for i in range(1, 5):
        if x-i < 0 or board[x-i][y] == b or (x-i, y) in op:
            flag1 -= 0.25
            break
        elif board[x-i][y] == a or (x-i, y) in my:
            flag1 += 1
        elif board[x-i][y] == 0 and flag4 == 0:
            flag4 += 1
            flag2 = flag1
            flag1 = 0
        else:
            break
    if flag4 == 1:
        flag1, flag2 = flag2, flag1
    for i in range(1, 5):
        if x+i > pp.height - 1 or board[x+i][y] == b or (x+i, y) in op:
            flag1 -= 0.25
            break
        elif board[x+i][y] == a or (x+i, y) in my:
            flag1 += 1
        elif board[x+i][y] == 0 and flag4 == 0:
            flag4 += 2
            flag2 = flag1
            flag1 = 0
        elif board[x+i][y] == 0 and flag4 == 1:
            flag4 += 2
            flag3 = flag1
            flag1 = 0
        else:
            break
    if flag4 == 2:
        flag1, flag2 = flag2, flag1
    elif flag4 == 3:
        flag1, flag3 = flag3, flag1
    flag1 += 1
    flag2, flag3 = max(flag2, flag3), min(flag2, flag3)
    note1, note2 = maxi(note1, note2, note(flag1, flag2, flag3))
    return note1 + note2

def determine_tree(x, y, my, op, level, turn):
# my and op : AI and opponents
    if level == 1:
        return evalue(x, y, 1, my, op) - evalue(x, y, 0, op, my)
# max
    elif turn == 1:
        a = 10000
        for i in xrange(neighbor[0], neighbor[1]):
            for j in xrange(neighbor[2], neighbor[3]):
                if board[i][j] == 0 and (i, j) not in my and (i, j) not in op:
                    my.append((x, y))
                    a = min(a, determine_tree(i, j, my, op, level - 1, 0))
                    my.pop()

# min
    elif turn == 0:
        a = -10000
        for i in xrange(neighbor[0], neighbor[1]):
            for j in xrange(neighbor[2], neighbor[3]):
                if board[i][j] == 0 and (i, j) not in my and (i, j) not in op:
                    op.append((x, y))
                    a = max(a, determine_tree(i, j, my, op, level - 1, 1))
                    op.pop()
    return a

def find(level, turn):
    global first
    if first:
        first = False
        return 7, 7, 0
    if turn == 1:
        x1, y1, score = 0, 0, -10000
        for x in xrange(neighbor[0], neighbor[1]):
            for y in xrange(neighbor[2], neighbor[3]):
                if board[x][y] == 0:
                    z = determine_tree(x, y, [], [], level, 1)
                if score < z:
                    score = z
                    x1 = x
                    y1 = y
        return x1, y1, score
    elif turn == 0:
        x1, y1, score = 0, 0, 10000
        for x in xrange(neighbor[0], neighbor[1]):
            for y in xrange(neighbor[2], neighbor[3]):
                if board[x][y] == 0:
                    z = determine_tree(x, y, [], [], level, 0)
                if score > z:
                    score = z
                    x1 = x
                    y1 = y
        return x1, y1, score

"""brain_my(x, y), brain_opponents(x, y), brain_takeback(x, y),
   print_score(turn), print_board(), brain_turn() find(level, turn)"""

def brain_turn():
    if pp.terminateAI:
        return
    i = 0
    while True:
        x1, y1, score = find(2, 1)
        i += 1
        if pp.terminateAI:
            return
        if isFree(x1, y1):
            break
    if i > 1:
                pp.pipeOut("DEBUG {} coordinates didn't hit an empty field".format(i))
    else:
        pp.do_mymove(x1, y1)

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
        c = str(board[x][y])
        win32gui.ExtTextOut(dc, rc[2]-15, 3, 0, None, c, ())
        win32gui.ReleaseDC(wnd, dc)

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
