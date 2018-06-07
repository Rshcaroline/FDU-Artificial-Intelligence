board = [[0 for i in xrange(15)] for j in xrange(15)]
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

def my(x, y):
        board[x][y] = 1

def op(x, y):
        board[x][y] = 2
        find()
        print_board()

def takeback(x, y):
        board[x][y] = 0
        print_board()

def restart():
        for x in xrange(15):
                for y in xrange(15):
                        board[x][y]=0
        print "OK"

def print_board():
        flag1 = 0
        print "\t",
        for i in range(15):
                print i, "\t",
        print "\n",
        for i in board:
                print flag1, "\t",
                for j in i:
                        if j == 0:
                                print " \t",
                        else:
                                print j, "\t",
                flag1 += 1
                print "\n\n",

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
                if x+i > 14 or y+i > 14 or board[x+i][y+i] == b:
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
                if y+i > 14 or board[x][y+i] == b:
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
                if x+i > 14 or y-i < 0 or board[x+i][y-i] == b:
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
                if x-i < 0 or y+i > 14 or board[x-i][y+i] == b:
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
                if x+i > 14 or board[x+i][y] == b:
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
    for x in xrange(15):
        for y in xrange(15):
            if board[x][y] == 0:
                z = max(evalue(x, y, 1)+ 1, evalue(x, y, 2))
                if score < z:
                    score = z
                    x1 = x
                    y1 = y
    if score == 6 :
        my(7, 7)
        print 7, 7, score
    else:
        my(x1, y1)
        print x1, y1, score
