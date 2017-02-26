# coding: utf-8
#cython: profile=True
# distutils: define_macros=CYTHON_TRACE_NOGIL=1
"""Cython用のクラス"""
import random
from libc.stdlib cimport rand

cdef int WALL = -1

cdef random_next(int max_board):

    cdef int max_num

    if max_board <= 5:  # 盤面の数字が5以上の時は新しい数字は3が上限
        max_num = 3
    else:
        max_num = max_board - 2  # 盤面の数字が6以上の時は新しい数字はn-2が上限

    cdef int s = int((max_num * (max_num + 1)) / 2)
    #cdef int r = random.randint(0, s - 1)
    cdef int r = rand() % s
    cdef int k = 0
    cdef int i
    for i in range(max_num):
        k += max_num - i
        if r < k:
            return i + 1

"""
cdef random_next(int max_board):
    # 盤面の最大の数字がmax_boardのとき、埋める数字から確率的に傾斜をかけてひとつ選び返す

    cdef int max_num

    if max_board <= 5:  # 盤面の数字が5以上の時は新しい数字は3が上限
        max_num = 3
    else:
        max_num = max_board - 2  # 盤面の数字が6以上の時は新しい数字はn-2が上限

    prob = {}
    cdef int s = 0
    cdef int k, p,r
    cdef int i, j
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
"""

cdef make_adjacent(int TABLE_SIZE):
    #adjacent = [[0] * 4 for i in range(TABLE_SIZE ** 2)]
    #adjacent = np.zeros((TABLE_SIZE ** 2, 4), dtype=np.int32)
    cdef int adjacent[100][4]
    # すべてのマスに対して

    cdef int i

    for i in range(TABLE_SIZE ** 2):
        adjacent[i][0] = i - TABLE_SIZE
        adjacent[i][1] = i - 1
        adjacent[i][2] = i + 1
        adjacent[i][3] = i + TABLE_SIZE
    # 一列目から上を削除
    for i in range(TABLE_SIZE):
        adjacent[i][0] = WALL
    # 一番下の行から下を削除
    for i in range(TABLE_SIZE * (TABLE_SIZE - 1), TABLE_SIZE * TABLE_SIZE):
        adjacent[i][3] = WALL
    # 左の列から左を削除
    for i in range(TABLE_SIZE):
        adjacent[i * TABLE_SIZE][1] = WALL
    # 右の列から右を削除
    for i in range(TABLE_SIZE):
        adjacent[(i + 1) * TABLE_SIZE - 1][2] = WALL

    return adjacent


cdef class Board:
    cdef int TABLE_SIZE
    cdef int ADJACENT[100][4]
    cdef int board[100]
    cdef list selectable
    cdef int turn_number
    cdef int connected[100]


    def __init__(self, table_size=4):
        """board"""
        #self.board = np.zeros(Board.TABLE_SIZE ** 2, dtype=np.int32)
        cdef int i
        self.TABLE_SIZE = table_size

        for i in range(self.TABLE_SIZE ** 2):
                self.board[i] = 0
        self.selectable = []
        self.turn_number = 0
        self.ADJACENT = make_adjacent(self.TABLE_SIZE)


    def init_board(self):
        """randomly init board"""
        for i in range(self.TABLE_SIZE ** 2):
            self.board[i] = random.randint(1, 3)
        self.selectable = []
        self.turn_number = 0

    def print_board(self):

        for i in range(self.TABLE_SIZE):
            row = ""
            for j in range(self.TABLE_SIZE):
                row += str(self.board[i * self.TABLE_SIZE + j])

            print(row)

    def selectable_list(self):
        if len(self.selectable) == 0:
            self._selectable_list()
        return self.selectable

    def select_cell(self, cell, return_board_before_drop=False):
        """実際にCellを返す。return_board_before_drop=Trueのときは実際に数字を落とす前の状態のboardを返す(描画用)"""
        # 選んだCellとつながっているCellを0にする。選んだCellは値を1増やす
        self._erace_connected(cell)

        if return_board_before_drop:
            # Selfのコピーを返す
            board_before_drop =  self.clone()
        # 数字を落とす
        self._drop()

        # 落とした後0をランダムで埋める
        self._renew_board()
        # turn numberを増やす
        self.turn_number += 1
        # 新しいboardのself.selectableを更新
        self._selectable_list()
        if return_board_before_drop:
            return board_before_drop
    def set_board(self, given_board):
        """boardに外からあたえられたboardをセットする"""
        cdef int i
        for i in range(self.Board ** 2):
            self.board[i] = given_board[i]

    def get_table_size(self):
        return self.TABLE_SIZE

    def get_turn_num(self):
        return self.turn_number

    def get_board(self):
        new_board = [0] * (self.TABLE_SIZE ** 2)
        for i in range(self.TABLE_SIZE ** 2):
            new_board[i] = self.board[i]
        return new_board

    def max_board(self):
        """盤面の中で最大の値を返す"""

        cdef int T = self.TABLE_SIZE ** 2
        cdef int a = 0
        cdef int i = 0
        for i in range(T):
            if self.board[i] > a:
                a = self.board[i]

        return a

    def clone(self):
        cdef int i
        new_board = Board(table_size=self.TABLE_SIZE)
        for i in range(self.TABLE_SIZE ** 2):
            new_board.board[i] = self.board[i]
        new_board.turn_number = self.turn_number
        return new_board

    def is_game_end(self):
        if len(self.selectable_list()) == 0:
            return True
        else:
            return False

    def play(self):
        """適当にプレイする"""
        self.init_board()
        while True:
            if self.is_game_end() == False:
                self.select_cell(self.selectable_list()[0])
                self.print_board()
                print("")
            else:
                break


    cdef _selectable_list(self):
        """Boardからselectable list を作る"""
        selectable_list = []
        cdef int T = self.TABLE_SIZE **2
        cdef int i, j
        for i in range(T):
            for j in range(4):
                if self.ADJACENT[i][j] != -1:
                    if self.board[i] == self.board[self.ADJACENT[i][j]]:
                        selectable_list.append(i)
                        break
        self.selectable = selectable_list

    cdef _erace_connected(self, cell):
        """ 選んだCellとつながっているCellを0にする。選んだCellは値を1増やす"""
        #self.connected_ = []
        #intiialize self.conncected. 0 represents it it not connected, 1 represents it is connected
        cdef int i
        cdef int selected_cell
        for i in range(self.TABLE_SIZE ** 2):
            self.connected[i] = 0

        self._connected(cell)
        selected_cell = self.board[cell]
        # for connected_cell in self.connected_:
           # self.board[connected_cell] = 0
        for i in range(self.TABLE_SIZE ** 2):
            if self.connected[i] == 1:
                self.board[i] =0
        self.board[cell] += selected_cell + 1

    cdef _drop(self):
        #new_board = np.zeros(self.TABLE_SIZE ** 2)
        cdef int new_board[100]
        cdef int i, j, k
        cdef int T = self.TABLE_SIZE
        for i in range(100):
            new_board[i] = 0
        for j in range(T):
            # kは下から何番目かを表す
            k = 0
            for i in range(T):
                # (T-1-i, j)(下からi番目)
                if self.board[(T - 1 - i) * T + j] != 0:
                    new_board[(T - 1 - k) * T + j] = self.board[(T - 1 - i) * T + j]
                    k += 1
        self.board = new_board


    cdef _renew_board(self):
        """0になっているところをランダムに埋める"""
        cdef int max_board = self.max_board()
        cdef int T = self.TABLE_SIZE ** 2
        cdef int i
        for i in range(T):
            if self.board[i] == 0:
                self.board[i] = random_next(max_board)

    cdef _connected(self, int cell):
        """途中で使うよう"""
        cdef int adj
        cdef int j
        for j in range(4):
            adj =  self.ADJACENT[cell][j]
            if adj != WALL:
                #if adj not in self.connected_ :
                if self.connected[adj] != 1:
                    if self.board[cell] == self.board[adj]:
                        #self.connected_.append(adj)
                        self.connected[adj] = 1
                        self._connected(adj)


def test(n):
    cdef int i
    for i in range(n):

        board = Board()
        board.init_board()
        if len(board.selectable_list()) != 0:
            board.select_cell(board.selectable_list()[0])



