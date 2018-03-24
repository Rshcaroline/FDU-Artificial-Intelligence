import sys

def easy_sum(s):
    if s == '':
        raise Exception('完成str转int，并进行加操作')
    else:
        return int(s[0])+int(s[2])


def main():
    for input in sys.stdin:
        s = input.strip()
        print(easy_sum(s))


if __name__ == '__main__':
    main()