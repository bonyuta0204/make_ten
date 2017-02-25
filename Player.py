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
        self.name = "Random"

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
        self.parameter = repeat
        self.eval_list = []
        self.game_num = 0
        self.name = "MonteCarlo"

    def next_cell(self, board):
        """モンテカルロ法の評価値が一番高かった手を返す。"""
        # 評価用に新しいBoardをつくる

        board_eval = board.clone()
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
        for i in range(self.parameter):  # 毎回インスタンスを生成しないといけない？タプルにすれば大丈夫？

            new_board = current_board.clone()
            new_board.select_cell(cell)
            result = (Game.Game(Random()).play(board=new_board, result=False))  # 実際にプレイをする
            result_max.append(result[2])
            result_turn.append(result[1])
            self.game_num += 1  # 合計で何ゲームプレイしたのかを記録しておく
        return float(sum(result_turn)) / len(result_turn), float(sum(result_max)) / len(result_max)


class MonteCarloSecond(object):
    def __init__(self, second=0.5, turn_weight=0.01):
        """1ターンにSecondが終わるまで繰り返した値を評価値として使う。
            self.eval_list : list
                プレイ時のそれぞれの局面での評価値(a, ma){a: 最大の数字,ma：ゲーム終了までのターン数}
            self.game_num : int
                合計で何ゲームプレイしたか
            self.num_try: list
                それぞれの局面で平均何回プレーして期待値をもとめたかのリスト
            self.turn_weight : float
                turn数にかける重み
        """
        self.parameter = second
        self.eval_list = []
        self.game_num = 0
        self.num_try = []  # 何手目で平均何回プレーしたかの記録
        self.turn_weight = turn_weight
        self.name = "MonteCarloSecond"

    def next_cell(self, board):
        """モンテカルロ法の評価値が一番高かった手を返す

        。"""
        # 評価用に新しいBoardをつくる

        board_eval = board.clone()
        self.num_selectable_ = len(board.selectable_list())
        self.second_each_ = self.parameter / float(self.num_selectable_)

        # board_evalを使って実験をする
        max_score = 0
        best_cell = (10, 10)
        for a in board.selectable_list():  # それぞれの選択肢において
            self.repeat = 0
            eva = self.monte_eval(a, board_eval)  # その選択肢の評価値 eva(turn_number, max_num)
            """
            if eva[1] > ma[1]:  # 最大の数字が過去最高の時
                ma = eva
                best_cell = a

            elif eva[1] == ma[1]:  # 最大の数字が同列一位の時はターン数が多い方を優先
                if eva[0] > ma[0]:
                    ma = eva
                    best_cell = a
                """
            score = self.turn_weight * eva[0] + eva[1]
            if score > max_score:
                max_score = score
                best_cell = a
                expectation = eva

        self.eval_list.append(expectation)
        self.num_try.append(float(self.repeat / self.num_selectable_))
        return best_cell

    def monte_eval(self, cell, current_board):
        """cellのマスの評価値を算出する。(ターン数の合計,最大値の合計)を返す"""
        result_max = []  # 最大値のリスト
        result_turn = []  # ターン数のリスト
        start_time = time.clock()
        while time.clock() - start_time < self.second_each_:
            new_board = current_board.clone()
            new_board.select_cell(cell)
            result = (Game.Game(Random()).play(board=new_board, result=False))  # 実際にプレイをする
            result_max.append(result[2])
            result_turn.append(result[1])
            self.game_num += 1  # 合計で何ゲームプレイしたのかを記録しておく
            self.repeat += 1

        return float(sum(result_turn)) / len(result_turn), float(sum(result_max)) / len(result_max)


def main(n):
    max_history = []
    turn_num_history = []
    parameters = np.linspace(0.01, 0.8, n)
    print(parameters)
    for i in range(n):
        max_history_row = []
        turn_num_row = []
        for j in range(5):
            print("parameter i: %d\n try number: %d" % (i, j))
            # i番目のParameterでPlayした結果を格納. result= [board, turn_num, max_board]
            new_game = Game.Game(MonteCarloSecond(second=0.5, turn_weight=parameters[i]))
            result = new_game.play()
            max_history_row.append(result[2])
            turn_num_row.append(result[1])
        max_history.append(max_history_row)
        turn_num_history.append(turn_num_row)

    print(parameters)
    print(max_history)
    print(turn_num_history)

    max_means = np.mean(max_history, axis=1)
    turn_num_means = np.mean(turn_num_history, axis=1)
    max_std = np.std(max_history, axis=1)
    turn_num_std = np.std(turn_num_history, axis=1)

    plt.subplot(211)
    plt.plot(parameters, max_means)
    plt.fill_between(parameters, max_means + max_std, max_means - max_std, alpha=0.1)
    plt.xlabel("parameter")
    plt.ylabel("max_num")
    plt.grid()
    plt.subplot(212)
    plt.plot(parameters, turn_num_means)
    plt.fill_between(parameters, turn_num_means + turn_num_std, turn_num_means - turn_num_std, alpha=0.1)
    plt.xlabel("parameter")
    plt.ylabel("turn_num")
    plt.grid()
    plt.show()


def test():
    player1 = MonteCarlo(repeat=20)
    new_game = Game.Game(player1)
    new_game.play(show=True)


def test_second():
    player1 = MonteCarloSecond(second=0.5)
    new_game = Game.Game(player1)
    new_game.play(show=True)
    plt.plot(player1.num_try)
    plt.ylabel("number of try")
    plt.grid()
    plt.show()

def show_expectation():
    player1 = MonteCarloSecond(second=1.0, turn_weight=0.01)
    new_game = Game.Game(player1)
    new_game.play(show=True)
    expectation =   np.array(player1.eval_list) # expectation[:,0] : turn_num, expectation[:,1]:max_num
    plt.subplot(211)
    plt.plot(expectation[:, 0], label="Turn Number")
    plt.ylabel("Turn Number")
    plt.grid()
    plt.legend()
    plt.subplot(212)
    plt.plot(expectation[:, 1], label="Max Number")
    plt.ylabel("Max Number")
    plt.grid()
    plt.legend()
    plt.show()



if __name__ == "__main__":
    show_expectation()
