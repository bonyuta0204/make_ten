# coding: utf-8


import random
import numpy as np
import Board
import Game
import matplotlib.pyplot as plt
import time


class Player(object):
    """雛形"""

    def __init__(self):
        pass

    def next_cell(self, board):
        pass


# In[7]:

class Random(object):
    """Randomに選ぶAIのクラス"""

    def __init__(self):
        pass

    def next_cell(self, board):
        """boardを受け取り、次に選択するcellの座標をタプルで返す"""
        return random.choice(board.selectable_list())


class Human(object):
    """手動対戦のクラス"""

    def __init__(self):
        pass

    def next_cell(self, board):
        """boardを受け取り、次に選択するcellの座標をタプルで返す。入力は3, 4のようにタプルで。おけるようになるまでやりなおさせる。ゲームをやめる場合"C"を入力しFalseを返す"""
        while True:
            a = input(u"座標を入力してください。(例)3, 4。Cを入力すると中断します。")
            if a == "C":  # Cが入力されたら中断
                return False

            l = a.split(',')
            try:
                x = int(l[0])
                y = int(l[1])
                if (x, y) in board.selectable_list():
                    return x, y

                else:
                    print(u"選べる座標を選んでください。選べる座標は", board.selectable_list(), u"です")
            except ValueError:
                print(u"正しい座標を入力してください")


# In[9]:

class MonteCarlo(object):
    def __init__(self, repeat=5):
        """repeatの数だけランダム試行を行う
            self.eval_list : list
                プレイ時のそれぞれの局面での評価値(a, ma){a: 最大の数字,ma：ゲーム終了までのターン数}
            self.game_num : int
                プレイしたゲーム数の合計
        """
        self.repeat = repeat
        self.eval_list = []
        self.game_num = 0

    def next_cell(self, board):
        """モンテカルロ法の評価値が一番高かった手を返す。"""
        # 評価用に新しいBoardをつくる
        board_eval = Board.Board()
        board_eval.board = np.copy(board.board)
        # board_evalを使って実験をする
        ma = (-1, -1)
        best_cell = (10, 10)
        for a in board.selectable_list():  # それぞれの選択肢において
            eva = self.monte_eval(a, board_eval)  # その選択肢の評価値

            if eva[1] > ma[1]:  # 最大の数字が過去最高の時
                ma = eva
                best_cell = a

            elif eva[1] == ma[1]:  # 最大の数字が同列一位の時はターン数が多い方を優先
                if eva[0] > ma[0]:
                    ma = eva
                    best_cell = a

            else:
                pass

        self.eval_list.append(ma)

        return best_cell

    def monte_eval(self, cell, current_board):
        """cellのマスの評価値を算出する。(ターン数の合計,最大値の合計)を返す"""
        result_max = []  # 最大値のリスト
        result_turn = []  # ターン数のリスト
        for i in range(self.repeat):  # 毎回インスタンスを生成しないといけない？タプルにすれば大丈夫？
            new_board = Board.Board()
            new_board.board = np.copy(current_board.board)
            new_board.select_cell(cell)
            result = (Game.Game(Random()).play(board=new_board, result=False))  # 実際にプレイをする
            result_max.append(result[2])
            result_turn.append(result[1])
            self.game_num += 1  # 合計で何ゲームプレイしたのかを記録しておく
        return float(sum(result_turn)) / len(result_turn), float(sum(result_max)) / len(result_max)


class MonteCarloSecond(object):
    def __init__(self, second=1.0):
        """1ターンにSecondが終わるまで繰り返した値を評価値として使う。
            self.eval_list : list
                プレイ時のそれぞれの局面での評価値(a, ma){a: 最大の数字,ma：ゲーム終了までのターン数}
            self.game_num : int
                合計で何ゲームプレイしたか
            self.num_try: list
                それぞれの局面で平均何回プレーして期待値をもとめたかのリスト
        """
        self.second = second
        self.eval_list = []
        self.game_num = 0
        self.num_try = []  # 何手目で平均何回プレーしたかの記録

    def next_cell(self, board):
        """モンテカルロ法の評価値が一番高かった手を返す

        。"""
        # 評価用に新しいBoardをつくる
        board_eval = Board.Board()
        board_eval.board = np.copy(board.board)
        self.num_selectable_ = len(board.selectable_list())
        self.second_each_ = self.second / float(self.num_selectable_)

        # board_evalを使って実験をする
        ma = (-1, -1)
        best_cell = (10, 10)
        for a in board.selectable_list():  # それぞれの選択肢において
            self.repeat = 0
            eva = self.monte_eval(a, board_eval)  # その選択肢の評価値

            if eva[1] > ma[1]:  # 最大の数字が過去最高の時
                ma = eva
                best_cell = a

            elif eva[1] == ma[1]:  # 最大の数字が同列一位の時はターン数が多い方を優先
                if eva[0] > ma[0]:
                    ma = eva
                    best_cell = a

            else:
                pass

        self.eval_list.append(ma)
        self.num_try.append(float(self.repeat / self.num_selectable_))
        return best_cell

    def monte_eval(self, cell, current_board):
        """cellのマスの評価値を算出する。(ターン数の合計,最大値の合計)を返す"""
        result_max = []  # 最大値のリスト
        result_turn = []  # ターン数のリスト
        start_time = time.clock()
        while time.clock() - start_time < self.second_each_:
            new_board = Board.Board()
            new_board.board = np.copy(current_board.board)
            new_board.select_cell(cell)
            result = (Game.Game(Random()).play(board=new_board, result=False))  # 実際にプレイをする
            result_max.append(result[2])
            result_turn.append(result[1])
            self.game_num += 1  # 合計で何ゲームプレイしたのかを記録しておく
            self.repeat += 1

        return float(sum(result_turn)) / len(result_turn), float(sum(result_max)) / len(result_max)


def main():

    player1 = MonteCarloSecond(second=1)
    new_game = Game.Game(player1)
    new_game.play(show=True)
    result = np.array(player1.eval_list)
    print("MonteCarloSecond(%f)" % player1.second, player1.game_num)
    plt.subplot(211)
    plt.plot(result[:, 0], label="MonteCarloSecond(%f)" % player1.second)

    plt.subplot(212)
    plt.plot(result[:, 1], label="MonteCarloSecond(%f)" % player1.second)

    player = MonteCarlo(repeat=10)
    new_game = Game.Game(player)
    new_game.play(show=True)
    result = np.array(player.eval_list)
    print("MonteCarlo(%d)" % player.repeat , player.game_num)
    plt.subplot(211)
    plt.plot(result[:, 0], label="MonteCarlo(%d)" % player.repeat)
    plt.ylabel("number of remaining turn")
    plt.grid(True)
    plt.legend(loc="best")
    plt.subplot(212)
    plt.plot(result[:, 1], label="MonteCarlo(%d)" % player.repeat)
    plt.ylabel("max number")
    plt.grid(True)
    plt.legend(loc="best")

    plt.show()


if __name__ == "__main__":
    main()
