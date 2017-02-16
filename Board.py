# coding: utf-8

# In[1]:

import numpy as np
import random


# In[2]:

TABLE_SIZE = 5
ALL_CELLS = []
for x in range(TABLE_SIZE):
    for y in range(TABLE_SIZE):
        ALL_CELLS.append((x, y))
ADJECENT = {}
table_init = np.zeros((TABLE_SIZE, TABLE_SIZE))
for i in range(TABLE_SIZE):
    for j in range(TABLE_SIZE):
        ADJECENT[(i, j)] = []
        current_cell = np.array([i, j])
        for a in np.array([[0, 1], [1, 0], [-1, 0], [0, -1]]):
            adj = current_cell + a
            if 0 <= adj[0] < TABLE_SIZE and 0 <= adj[1] < TABLE_SIZE:
                ADJECENT[(i, j)].append(tuple(adj))


def random_next(max_board):
    """盤面の最大の数字がmax_boardのとき、埋める数字から確率的に傾斜をかけてひとつ選び返す"""
    if max_board <= 5:          # 盤面の数字が5以上の時は新しい数字は3が上限
        max_num = 3
    else:
        max_num = max_board - 2    # 盤面の数字が6以上の時は新しい数字はn-2が上限

    prob = {}
    s = 0
    for i in range(1, max_num + 1):
        prob[i] = max_num + 1 - i
    for k, p in prob.items():
        s += p
    r = random.uniform(0, s)
    s = 0
    for k, p in prob.items():
        s += p
        if r < s:
            return k


# In[24]:

class Board(object):
    """盤面のクラス"""

    def __init__(self):
        """盤面の初期化。完全ランダムで埋める"""
        self.board = np.zeros((TABLE_SIZE, TABLE_SIZE), dtype=np.int32)

        for i in range(TABLE_SIZE):
            for j in range(TABLE_SIZE):
                self.board[i, j] = random.randint(1, 3)
        self.selectable = self.__selectable_list()
        self.turn_number = 0

    def select_cell(self, cell):
        """セルを選択し、消去。その後下に落とし新しいところは埋める"""
        init_cell = self.board[cell]
        self.__connect(cell)
        self.__erace_connected()
        if self.con_list:
            self.board[cell] = init_cell + 1
            self.__drop()
        self.__renew_board()
        self.turn_number += 1
        self.selectable = self.__selectable_list()

    def selectable_list(self):
        return self.selectable

    def play_game(self):
        """ゲームをプレイする。入力はx座標y座標を一個ずつ打ち込む。終わり判定なし。10ターンで終了"""
        n = 0
        while n < 10:
            self.print_board()
            cell = self.__get_valid_input()
            self.select_cell(cell)
            n += 1

    def print_board(self):
        """ボードを表示する。座標番号つき"""
        s = " "
        for i in range(TABLE_SIZE):
            s = s + " " + str(i)
        print(s)

        for i in range(TABLE_SIZE):
            s = str(i)
            for j in range(TABLE_SIZE):
                s = s + " " + str(self.board[i, j])
            print(s)


    def __selectable_list(self):
        """選べる場所の集合.おける座標をタプルのセットで返す"""
        l = []
        for cell in ALL_CELLS:
            if cell not in l:
                for adj in ADJECENT[cell]:
                    if self.board[adj] == self.board[cell]:
                        l.append(cell)
                        l.append(adj)
                        break
        return list(set(l))

    def is_game_end(self):
        """おける場所がなくゲーム終了の場合にTrue,ゲームが続く場合Falseを返す"""
        l = self.selectable_list()
        if len(l) == 0:
            return True
        else:
            return False

    def max_board(self):
        """盤面の中で最大の値を返す"""
        ma = -1
        for cell in ALL_CELLS:
                if self.board[cell] >= ma:
                    ma = self.board[cell]
        return ma

    def __connected(self, cell):

        """選択したCellと同じ数字でつながっているCellの座標を返す。途中で使う用。"""
        # cell is given as tuple
        for x in ADJECENT[cell]:
            if x not in self.con_list:
                if self.board[cell] == self.board[x]:
                    self.con_list.append(x)
                    self.__connected(x)

    def __connect(self, cell):

        """選択したCellと同じ数字でつながっているCellの座標を返す"""
        self.con_list = []
        self.__connected(cell)

    def __erace_connected(self):
        """つながっている部分をすべて0に変える"""
        for x in self.con_list:
            self.board[x] = 0

    def __drop(self):

        """0に変えた後0を消して上にある数字を下に落下させる"""

        for i in range(TABLE_SIZE):
            # move column i
            new_column = []
            for j in range(TABLE_SIZE):
                if self.board[j, i] != 0:  # i列の０を除いたリスト上→下と右→左が対応
                    new_column.append(self.board[j, i])

            for k in range(-1, -TABLE_SIZE - 1, -1):
                try:
                    self.board[k, i] = new_column[k]
                except IndexError:
                    self.board[k,  i] = 0


    def __renew_board(self):
        """0になっているところをランダムに埋める"""
        max_board = self.max_board()
        for cell in ALL_CELLS:
            if self.board[cell] == 0:
                self.board[cell] = random_next(max_board)

    def __get_valid_input(self):
        """入力をうけとりタプルで返す。"""
        while True:
            try:
                a = input("type x-axis")
                x = int(a)
                if 0 <= x < TABLE_SIZE:
                    break
                else:
                    print("type correct x-axis")
            except ValueError:
                print("type an integer")
        while True:
            try:
                a = input("type y-axis")
                y = int(a)
                if 0 <= y < TABLE_SIZE:
                    break
                else:
                    print("type correct y-axis")
            except ValueError:
                print("type an integer")
        return x, y

def test(n):
    for i in range(n):
        board = Board()
        board.select_cell(board.selectable_list()[0])
def main():
    board = Board()
    board.select_cell(board.selectable_list()[0])
    print(board.board, board.selectable_list())

# In[4]:

if __name__ == "__main__":
    main()