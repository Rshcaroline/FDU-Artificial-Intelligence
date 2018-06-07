import pisqpipe as pp
from pisqpipe import DEBUG_EVAL, DEBUG

pp.infotext = 'name="pbrain-pypeng", author="Peng-Wei Chen", version="1.0", country="Taiwan", www="https://github.com/pinnertw/lescodes/TIPE/simulation-tools"'

MAX_BOARD = 100
board = [[0 for i in xrange(MAX_BOARD)] for j in xrange(MAX_BOARD)]


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
        pp.pipeOut("OK")

def isFree(x, y):
        return x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] == 0

def brain_my(x, y):
        if isFree(x,y):
                board[x][y] = 1
        else:
                pp.pipeOut("ERROR my move [{},{}]".format(x, y))

def brain_opponents(x, y):
        if isFree(x,y):
                board[x][y] = 2
        else:
                pp.pipeOut("ERROR opponents's move [{},{}]".format(x, y))

def brain_block(x, y):
        if isFree(x,y):
                board[x][y] = 3
        else:
                pp.pipeOut("ERROR winning move [{},{}]".format(x, y))

def brain_takeback(x, y):
        if x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] != 0:
                board[x][y] = 0
                return 0
        return 2

def maxi(a, b, c):
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
                return 1
        elif x >= 4.5:
                return 64
        elif x == 4 or x + y > 3 and z > 0:
                return 32
        elif x == 3.75 or x + y > 3:
                return 16
        elif x == 3 or x + y > 3 and z > 0:
                return 15
        elif x == 2.75 or x + y > 2:
                return 8
        elif x == 2 or x + y > 1 and z > 0:
                return 7
        elif x == 1.75 or x + y > 1:
                return 4
        elif x == 1 or z > 0:
                return 3
        elif x == 0.75:
                return 2

def evalue(x, y, z):
        if z == 1:
                a, b = 1, 2
        elif z == 2:
                a, b = 2, 1
        flag1, flag2, flag3, flag4, note1, note2 = 0, 0, 0, 0, 0, 0

# left-up to right-down
        for i in range(1, 5):
                if x-i < 0 or y-i < 0 or board[x-i][y-i] == b:
                        flag1 -= 0.25
                        break
                elif board[x-i][y-i] == a:
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
                if x+i > pp.height - 1 or y+i > pp.width - 1 or board[x+i][y+i] == b:
                        flag1 -= 0.25
                        break
                elif board[x+i][y+i] == a:
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
                if y-i < 0 or board[x][y-i] == b:
                        flag1 -= 0.25
                        break
                elif board[x][y-i] == a:
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
                if y+i > pp.width - 1 or board[x][y+i] == b:
                        flag1 -= 0.25
                        break
                elif board[x][y+i] == a:
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
                if x+i > pp.height - 1 or y-i < 0 or board[x+i][y-i] == b:
                        flag1 -= 0.25
                        break
                elif board[x+i][y-i] == a:
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
                if x-i < 0 or y+i > pp.width - 1 or board[x-i][y+i] == b:
                        flag1 -= 0.25
                        break
                elif board[x-i][y+i] == a:
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
                if x-i < 0 or board[x-i][y] == b:
                        flag1 -= 0.25
                        break
                elif board[x-i][y] == a:
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
                if x+i > pp.height - 1 or board[x+i][y] == b:
                        flag1 -= 0.25
                        break
                elif board[x+i][y] == a:
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

def find():
        x1, y1, score = 0, 0, 0
        for x in xrange(pp.height):
                for y in xrange(pp.width):
                        if board[x][y] == 0:
                                z = evalue(x, y, 1) + evalue(x, y, 2)
                                if score < z:
                                        score = z
                                        x1 = x
                                        y1 = y
        return x1, y1, score

def brain_turn():
        if pp.terminateAI:
            return
        i = 0
        while True:
                x1, y1, score = find()
                i += 1
                if pp.terminateAI:
                        return
                if isFree(x1, y1):
                        break
        if i > 1:
            pp.pipeOut("DEBUG {} coordinates didn't hit an empty field".format(i))
        if score == 12 and isFree(7, 7):
            pp.do_mymove(7, 7)
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
