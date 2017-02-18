# coding: utf-8

# In[1]:

import sys
import Board

from PyQt5.QtWidgets import (QWidget, QApplication, QFrame, QMainWindow,
                             QPushButton, QHBoxLayout, QVBoxLayout, QLabel,
                             QComboBox, QGroupBox, QLineEdit, QGridLayout)
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
import Player


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.GUIBoard = GUIBoard()

        self.init_ui()

    def init_ui(self):
        self.setGeometry(300, 300, 1000, 600)
        self.setWindowTitle("Board Test")

        # label for turn
        self.turn_label = QLabel("Turn")
        # signal
        self.GUIBoard.turn_change.connect(self.renew_turn)
        self.GUIBoard.is_game_end.connect(self.game_over)
        # label for game over

        self.is_game_over_label = QLabel("")

        # combobox to select Ai

        select_AI = QComboBox()
        select_AI.addItem("Random")
        select_AI.addItem("MonteCarlo")
        select_AI.addItem("MonteCarloSecond")
        select_AI.currentTextChanged.connect(self.combobox_change)
        # label for parameter

        self.parameter = QLabel("second")

        # line edotor for paramater of ai
        self.line_edit = QLineEdit()
        self.line_edit.textChanged.connect(self.line_edit_change)
        # combobox to change table size

        self.select_size = QComboBox()
        self.select_size.addItem("4")
        self.select_size.addItem("5")
        self.select_size.addItem("6")
        self.select_size.currentTextChanged.connect(self.table_size_change)

        # label for select_size
        self.select_size_label = QLabel("select table size")
        # GroupBox for AI

        AI_box = QGroupBox()
        AI_layout = QGridLayout()

        AI_layout.addWidget(select_AI, 0, 0, 1, 2)
        AI_layout.addWidget(self.parameter, 1, 0)
        AI_layout.addWidget(self.line_edit, 1, 1)
        AI_layout.addWidget(self.select_size_label, 2, 0)
        AI_layout.addWidget(self.select_size, 2, 1)
        AI_box.setLayout(AI_layout)

        # buttons

        start_btn = QPushButton("start")
        start_btn.clicked.connect(self.GUIBoard.start)

        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.GUIBoard.init_board)

        pause_btn = QPushButton("Pause")
        pause_btn.clicked.connect(self.GUIBoard.pause)

        # GroupBox for Buttons

        buttons_box = QGroupBox()
        buttons_layout = QHBoxLayout()

        buttons_layout.addWidget(start_btn)
        buttons_layout.addWidget(reset_btn)
        buttons_layout.addWidget(pause_btn)

        buttons_box.setLayout(buttons_layout)

        # V box

        tool_box = QGroupBox()

        vbox = QVBoxLayout()
        vbox.addWidget(self.turn_label)
        vbox.addWidget(self.is_game_over_label)
        vbox.addStretch(1)
        vbox.addWidget(AI_box)
        vbox.addStretch(1)
        vbox.addWidget(buttons_box)

        tool_box.setLayout(vbox)

        # board
        hbox = QHBoxLayout()
        hbox.addWidget(self.GUIBoard, stretch=2)
        hbox.addWidget(tool_box, stretch=1)

        self.setLayout(hbox)

        self.GUIBoard.player = Player.Random()
        self.show()

    def combobox_change(self, text):
        """      select_AI.addItem("Random")
        select_AI.addItem("MonteCarlo")
        select_AI.addItem("MonteCarloSecond")"""
        if text == "Random":
            self.GUIBoard.player = Player.Random()
            self.parameter.setText("No Parameter")
        if text == "MonteCarlo":
            self.GUIBoard.player = Player.MonteCarlo()
            self.parameter.setText("Repeat Number")
        if text == "MonteCarloSecond":
            self.GUIBoard.player = Player.MonteCarloSecond()
            self.parameter.setText("Second per a turn")

    def line_edit_change(self, text):
        try:
            parameter = int(text)
            self.GUIBoard.player.parameter = parameter
        except ValueError:
            self.line_edit.clear()

    def renew_turn(self, turn):
        self.turn_label.setText("Turn : %d" % turn)
        print("%d" % turn)

    def game_over(self, gameover):
        if gameover:
            self.is_game_over_label.setText("Game Over")
        else:
            self.is_game_over_label.clear()

    def table_size_change(self, text):
        self.GUIBoard.Board.change_table_size(int(text))
        self.GUIBoard.init_board()
        self.GUIBoard.update()


class GUIBoard(QFrame):
    """盤面のクラス"""

    # Class Constant
    BOARD_SIZE = 500

    # signal

    turn_change = pyqtSignal(int)
    is_game_end = pyqtSignal(bool)

    def __init__(self):
        """盤面の初期化。完全ランダムで埋める.Playerの選択も"""
        super().__init__()

        self.init_ui()
        self.init_board()

    def init_board(self):
        self.Board = Board.Board()
        # self.player = Player.MonteCarloSecond(second=1)
        self.ispaused = True
        self.resize(500, 500)
        self.Board_drawn = self.Board
        self.drop_timer = QTimer(self)
        self.drop_timer.setInterval(200)
        self.is_game_end.emit(False)
        self.drop_timer.timeout.connect(self.draw_dropped)

    def step(self):
        """step one turn"""
        if not self.ispaused:  # ポーズ中でなければすすめる
            if not self.Board.is_game_end():
                # self.timer.stop()
                next_c = self.player.next_cell(self.Board)

                # draw before_drop
                self.Board_drawn = self.Board.select_cell(next_c, return_board_before_drop=True)
                self.drop_timer.start()

                # draw after_drop
                # self.timer.start()
                self.update()

            else:
                print(self.Board.turn_number)
                # self.timer.stop()
                self.ispaused = True
                self.is_game_end.emit(True)

    def draw_dropped(self):
        """Boardをおとした後の盤面を表示する"""
        self.drop_timer.stop()
        self.Board_drawn = self.Board
        self.update()
        self.turn_change.emit(self.Board.turn_number)
        QTimer.singleShot(100, self.step)

    def start(self):
        """AIをスタートする"""
        self.ispaused = False
        # self.timer = QTimer(self)
        # self.timer.setInterval(300)
        QTimer.singleShot(100, self.step)
        # self.timer.timeout.connect(self.step)

        # self.timer.start()

    def pause(self):
        """AIをストップする"""
        self.ispaused = True

    def mousePressEvent(self, event):
        """when mouse clicked"""
        self.mouse_step(event.x(), event.y())

    def mouse_step(self, x, y):
        """select cell which is clicked by mouse"""
        cell = 0
        cell_size = self._get_cell_size()
        for i in range(Board.Board.TABLE_SIZE):
            for j in range(Board.Board.TABLE_SIZE):
                if j * cell_size <= x < (j + 1) * cell_size:
                    if i * cell_size <= y < (i + 1) * cell_size:
                        cell = (i, j)
        if cell in self.Board.selectable_list():
            if not self.Board.is_game_end():
                next_c = cell

                self.Board_drawn = self.Board.select_cell(next_c, return_board_before_drop=True)
                self.drop_timer.start()
                self.update()

    def init_ui(self):
        """GUIBoardのUIの初期化"""
        self.resize(GUIBoard.BOARD_SIZE, GUIBoard.BOARD_SIZE)

    @staticmethod
    def _get_cell_size():
        """それぞれのマスの大きさをピクセル数で返す"""
        return 500 // Board.Board.TABLE_SIZE

    def paintEvent(self, event):
        print("QpainterCalled")

        self._draw_board(self.Board_drawn)

    def _draw_a_cell(self, painter, i, j, value):
        """Draw cell(i, j), value is the number of the cell"""
        colorTable = ["white", 0xCC6666, 0x66CC66, 0x6666CC,
                      0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00, "black", "green", "yellow", "orange"]

        color = QColor(colorTable[value])
        painter.fillRect(j * self._get_cell_size(), i * self._get_cell_size(), self._get_cell_size() - 1,
                         self._get_cell_size() - 1, color)

        font = QFont("Times", 40)
        painter.setFont(font)
        pen_color = QColor("white")
        painter.setPen(pen_color)
        painter.drawText(j * self._get_cell_size(), i * self._get_cell_size(), self._get_cell_size() - 1,
                         self._get_cell_size() - 1,
                         Qt.AlignCenter, str(value))

    def _draw_board(self, board):
        painter = QPainter(self)
        for i in range(Board.Board.TABLE_SIZE):
            for j in range(Board.Board.TABLE_SIZE):
                self._draw_a_cell(painter, i, j, board.board[i][j])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
