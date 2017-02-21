"""Cython用のクラス"""
import random
import numpy as np

WALL = -1


def random_next(max_board):
    """盤面の最大の数字がmax_boardのとき、埋める数字から確率的に傾斜をかけてひとつ選び返す"""
    if max_board <= 5:  # 盤面の数字が5以上の時は新しい数字は3が上限
        max_num = 3
    else:
        max_num = max_board - 2  # 盤面の数字が6以上の時は新しい数字はn-2が上限

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


def make_adjacent(TABLE_SIZE):
    adjacent = [[0] * 4 for i in range(TABLE_SIZE ** 2)]
    # すべてのマスに対して

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


class Board(object):
    TABLE_SIZE = 5
    ADJACENT = make_adjacent(TABLE_SIZE)

    def __init__(self):
        """board"""
        self.board = np.zeros(Board.TABLE_SIZE ** 2, dtype=np.int32)
        self.selectable = None
        self.turn_number = 0

    def init_board(self):
        """randomly init board"""
        for i in range(Board.TABLE_SIZE ** 2):
            self.board[i] = random.randint(1, 3)

    def print_board(self):

        for i in range(Board.TABLE_SIZE):
            row = ""
            for j in range(Board.TABLE_SIZE):
                row += str(self.board[i * Board.TABLE_SIZE + j])

            print(row)

    def selectable_list(self):
        if self.selectable is None:
            self._selectable_list()
        return self.selectable

    def select_cell(self, cell, return_board_before_drop=False):
        """実際にCellを返す。return_board_before_drop=Trueのときは実際に数字を落とす前の状態のboardを返す(描画用)"""
        # 選んだCellとつながっているCellを0にする。選んだCellは値を1増やす
        self._erace_connected(cell)
        if return_board_before_drop:
            # Selfのコピーを返す
            return self.clone_board()
        # 数字を落とす
        self._drop()

        # 落とした後0をランダムで埋める
        self._renew_board()
        # turn numberを増やす
        self.turn_number += 1
        # 新しいboardのself.selectableを更新
        self._selectable_list()

    def max_board(self):
        """盤面の中で最大の値を返す"""

        return np.amax(self.board)

    def clone_board(self):
        pass
    @profile
    def _selectable_list(self):
        """Boardからselectable list を作る"""
        selectable_list = []
        for i in range(Board.TABLE_SIZE ** 2):
            for j in range(4):
                if self.ADJACENT[i][j] != -1:
                    if self.board[i] == self.board[self.ADJACENT[i][j]]:
                        selectable_list.append(i)
                        break
        self.selectable = selectable_list

    def _erace_connected(self, cell):
        """ 選んだCellとつながっているCellを0にする。選んだCellは値を1増やす"""
        self.connected_ = []
        self._connected(cell)
        selected_cell = self.board[cell]
        for connected_cell in self.connected_:
            self.board[connected_cell] = 0
        self.board[cell] += selected_cell + 1

    def _drop(self):
        new_board = [0] * (Board.TABLE_SIZE ** 2)
        for j in range(Board.TABLE_SIZE):
            # kは下から何番目かを表す
            k = 0
            for i in range(Board.TABLE_SIZE):
                # (T-1-i, j)(下からi番目)
                if self.board[(Board.TABLE_SIZE - 1 - i) * Board.TABLE_SIZE + j] != 0:
                    new_board[(Board.TABLE_SIZE - 1 - k) * Board.TABLE_SIZE + j] = self.board[(Board.TABLE_SIZE - 1 - i) * Board.TABLE_SIZE + j]
                    k += 1
        self.board = new_board


    def _renew_board(self):
        """0になっているところをランダムに埋める"""
        max_board = self.max_board()
        # ind は　Board＝＝0のIndex
        for i in range(Board.TABLE_SIZE):
            if self.board[i] == 0:
                self.board[i] = random_next(max_board)

    def _connected(self, cell):
        """途中で使うよう"""
        for adj in Board.ADJACENT[cell]:
            if adj != WALL:
                if adj not in self.connected_ :
                    if self.board[cell] == self.board[adj]:
                        self.connected_.append(adj)
                        self._connected(adj)


def test(n):

    for i in range(n):

        board = Board()
        if len(board.selectable_list()) != 0:
            board.select_cell(board.selectable_list()[0])

if __name__ == "__main__":
    test(1000)
