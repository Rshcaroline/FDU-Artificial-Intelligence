# GomokuAgent

A web version of the gomoku game with AI. 

This is the final project for Artificial Intelligence(DATA130008.01)@ Fudan University.

Built together with[@Anthony-Xu](https://github.com/Anthony-Xu) and [@iriserika](https://github.com/iriserika) .

- Play Gomoku on PC

  First run the game server, enter command: ```python run.py```

  Open the website http://127.0.0.1:5000/ in your browser.

- Play Gomoku on Mobile

  Please make sure your server and mobile are connected to the same WLAN.

  First run the game server, enter command: ```python runp.py``` 

  Scan the QR code appearing on the screen using *Wechat*.

**Happy Gomoku！** :-)

## Current AIs

- AI0: just for a test
- AI1: greedy algorithm & evaluation function ver 1
- AI2: 2-layer naive a-b prunning
- AI3: MCTS
- AI4: 8-layer speed-optimized version of a-b prunning
- AI5: greedy algorithm & evaluation function ver 2(improved)
- AI6: greedy algorithm & evaluation function ver 1, also can find a game with same opening and place a stone(from 5570 game history)
