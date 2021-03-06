# coding: utf-8


import numpy as np
import Game
import matplotlib.pyplot as plt
import time
import matplotlib.ticker as mticker


class Player(object):
    """雛形"""

    def __init__(self):
        pass

    def next_cell(self, board):
        pass


class Random(object):
    """Randomに選ぶAIのクラス"""

    def __init__(self):
        self.name = "Random"

    def next_cell(self, board):
        """boardを受け取り、次に選択するcellの座標をタプルで返す"""

        return board.rand_choice()
        # return random.choice(board.selectable_list)


class Human(object):
    """手動対戦のクラス"""

    def __init__(self):
        pass

    def next_cell(self, board):
        """boardを受け取り、次に選択するcellの座標をタプルで返す。
        入力は3, 4のようにタプルで。おけるようになるまでやりなおさせる。
        ゲームをやめる場合"C"を入力しFalseを返す"""
        while True:
            a = input(u"座標を入力してください。"
                      u"(例)3, 4。Cを入力すると中断します。")
            if a == "C":  # Cが入力されたら中断
                return False

            l = a.split(',')
            try:
                x = int(l[0])
                y = int(l[1])
                if (x, y) in board.selectable_list():
                    return x, y

                else:
                    print(u"選べる座標を選んでください。選べる座標は",
                          board.selectable_list(), u"です")
            except ValueError:
                print(u"正しい座標を入力してください")


class MonteCarloSecond(object):

    def __init__(self, second=0.5, turn_weight=0.01):
        """1ターンにSecondが終わるまで繰り返した値を評価値として使う。
            self.eval_list : list
                プレイ時のそれぞれの局面での評価値(a, ma)
                {a: 最大の数字,ma：ゲーム終了までのターン数}
            self.game_num : int
                合計で何ゲームプレイしたか
            self.num_try: list
                それぞれの局面で平均何回プレーして期待値をもとめたかのリスト
            self.turn_weight : float
                turn数にかける重み
        """
        self.parameter = second
        # それぞれのターンでの評価値のTupleのList。eval_list[0] = (turn number, max number, max
        # adjacent)
        self.eval_list = []
        self.game_num = 0
        self.num_try = []  # 何手目で平均何回プレーしたかの記録
        self.turn_weight = turn_weight
        self.name = "MonteCarloSecond"

    def next_cell(self, board):
        """
        モンテカルロ法の評価値が一番高かった手を返す

        """
        # 評価用に新しいBoardをつくる

        board_eval = board.clone()
        self.num_selectable_ = len(board.selectable_list())

        # おける場所が５ヶ所以上の場合は、与えられた時間をおける場所で割る。
        # おける場所が５こに満たない場合は与えられた時間を５で割る(数千回とかの無駄な繰り返しをなくす。)

        if self.num_selectable_ >= 10:
            self.second_each_ = self.parameter / float(self.num_selectable_)
        else:
            self.second_each_ = self.parameter / 10

        # board_evalを使って実験をする
        max_score = 0
        best_cell = (10, 10)
        for a in board.selectable_list():  # それぞれの選択肢において
            self.repeat = 0
            eva = self.monte_eval(a, board_eval)
            # その選択肢の評価値 eva(turn_number, max_num, max_adjacent, sum_adjacent)

            # score = self.turn_weight * eva[0] + eva
            score = eva[1] + 0.001 * (0.0 * eva[2] + 0.0 * eva[3] + 0.2 * eva[0])
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
        result_max_adjacent = []  # 最大セルに隣接するセルの最大値のリスト
        result_sum_adjacent = []  # 最大セルに隣接するセルの和
        start_time = time.clock()
        while time.clock() - start_time < self.second_each_:
            new_board = current_board.clone()
            new_board.select_cell(cell)
            result = (Game.Game(Random()).play(board=new_board,
                                               result=False))  # 実際にプレイをする
            result_max.append(result[2])
            result_turn.append(result[1])
            result_max_adjacent.append(result[3])
            result_sum_adjacent.append(result[4])
            self.game_num += 1  # 合計で何ゲームプレイしたのかを記録しておく
            self.repeat += 1

        return (float(sum(result_turn)) / len(result_turn),
                float(sum(result_max)) / len(result_max),
                float(sum(result_max_adjacent) / len(result_max_adjacent)),
                float(sum(result_sum_adjacent) / len(result_sum_adjacent)))


class MonteCarlo(object):

    def __init__(self, repeat=10, turn_weight=0.01):
        """1ターンにSecondが終わるまで繰り返した値を評価値として使う。
            repeat: int
                それぞれのターンで試行を繰り返す回数

            eval_list : list
                プレイ時のそれぞれの局面での評価値(a, ma)
                {a: 最大の数字,ma：ゲーム終了までのターン数}

            game_num : int
                合計で何ゲームプレイしたか

            num_try: list
                それぞれの局面で平均何回プレーして期待値をもとめたかのリスト

            turn_weight : float
                turn数にかける重み
        """
        self.parameter = repeat
        # それぞれのターンでの評価値のTupleのList。eval_list[0] = (turn number, max number, max
        # adjacent)
        self.eval_list = []
        self.game_num = 0
        self.num_try = []  # 何手目で平均何回プレーしたかの記録
        self.turn_weight = turn_weight
        self.name = "MonteCarlo"

    def next_cell(self, board):
        """
        モンテカルロ法の評価値が一番高かった手を返す

        """
        # 評価用に新しいBoardをつくる

        board_eval = board.clone()

        # board_evalを使って実験をする
        max_score = 0
        best_cell = 0
        for a in board.selectable_list():  # それぞれの選択肢において
            self.repeat = 0
            eva = self.monte_eval(a, board_eval)
            # その選択肢の評価値 eva(turn_number, max_num, max_adjacent, sum_adjacent)

            # score = self.turn_weight * eva[0] + eva
            # Parameters have to be adjusted
            score = eva[1] + 0.001 * (eva[2] + 0.01 * eva[3] + 0.1 * eva[0])
            if score > max_score:
                max_score = score
                best_cell = a
                expectation = eva

        self.eval_list.append(expectation)
        self.num_try.append(self.parameter)
        return best_cell

    def monte_eval(self, cell, current_board):
        """cellのマスの評価値を算出する。(ターン数の合計,最大値の合計)を返す"""
        result_max = []  # 最大値のリスト
        result_turn = []  # ターン数のリスト
        result_max_adjacent = []  # 最大セルに隣接するセルの最大値のリスト
        result_sum_adjacent = []  # 最大セルに隣接するセルの和
        # start_time = time.clock()
        # while time.clock() - start_time < self.second_each_:
        for i in range(self.parameter):
            new_board = current_board.clone()
            new_board.select_cell(cell)
            result = (Game.Game(Random()).play(board=new_board,
                                               result=False))  # 実際にプレイをする
            result_max.append(result[2])
            result_turn.append(result[1])
            result_max_adjacent.append(result[3])
            result_sum_adjacent.append(result[4])
            self.game_num += 1  # 合計で何ゲームプレイしたのかを記録しておく
            self.repeat += 1

        return (float(sum(result_turn)) / len(result_turn),
                float(sum(result_max)) / len(result_max),
                float(sum(result_max_adjacent) / len(result_max_adjacent)),
                float(sum(result_sum_adjacent) / len(result_sum_adjacent)))


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
            new_game = Game.Game(MonteCarloSecond(second=0.5,
                                                  turn_weight=parameters[i]))
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
    plt.fill_between(parameters, max_means + max_std,
                     max_means - max_std, alpha=0.1)
    plt.xlabel("parameter")
    plt.ylabel("max_num")
    plt.grid()
    plt.subplot(212)
    plt.plot(parameters, turn_num_means)
    plt.fill_between(parameters, turn_num_means + turn_num_std,
                     turn_num_means - turn_num_std, alpha=0.1)
    plt.xlabel("parameter")
    plt.ylabel("turn_num")
    plt.grid()
    plt.show()


def test():
    player1 = MonteCarlo(repeat=20)
    new_game = Game.Game(player1)
    new_game.play(show=True)


def test_second(n):
    player1 = MonteCarloSecond(second=0.5)
    new_game = Game.Game(player1, table_size=n)
    new_game.play(show=True)
    plt.plot(player1.num_try)
    plt.ylabel("number of try")
    plt.grid()
    plt.show()


def show_expectation(n=5, max_num=3):
    # Create Data
    player1 = MonteCarloSecond(second=0.5, turn_weight=0.01)
    new_game = Game.Game(player1, table_size=n)

    new_game.play(show=True, max_num=max_num)

    expectation = np.array(player1.eval_list)
    # expectation[:,0] : turn_num, expectation[:,1]:max_num

    # Plot Dataauto
    # with plt.xkcd():

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

    ax1.plot(expectation[:, 0], label="turn number", c="blue")
    ax1.yaxis.set_major_locator(mticker.LinearLocator(10))
    ax1.set_ylim(bottom=0)
    ax1.grid(True)

    ax1.spines["top"].set_color("None")
    plt.ylabel("Turn Number")

    ax2.plot(expectation[:, 1], label="Max Number")
    ax2.plot(expectation[:, 2], label="Max Adjacent")
    ax2.plot([], [], label="sum of adjacent", c="green")
    ax2.set_xticks(np.arange(0, len(expectation), 10))

    ax2.spines["top"].set_color("None")

    plt.ylabel("Max Number")
    plt.legend(loc="best")
    ax2.grid(True)

    ax3 = ax1.twinx()
    ax3.plot(player1.num_try, label="Number of try", color="orange")
    ax3.plot([], [], label="Turn Number", c="blue")
    plt.ylabel("Number of try")
    ax3.spines["top"].set_color("None")
    ax3.set_ylim(bottom=0)
    ax3.grid(False)
    ax3.yaxis.set_major_locator(mticker.LinearLocator(10))
    plt.legend()

    ax4 = ax2.twinx()
    ax4.plot(expectation[:, 3], label="sum of adjacent", color="green")
    ax4.set_ylabel("Sum of Adjacent")
    ax4.spines["top"].set_color("None")

    ax4.grid(False)

    print(expectation)

    plt.show()


if __name__ == "__main__":
    show_expectation(6, max_num=3)
