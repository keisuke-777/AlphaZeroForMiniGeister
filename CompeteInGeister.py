# ゲームを管理
# ミニガイスター用

import random
import math
import csv
from GuessEnemyPiece import PRINT_DEBUG

# ゲームの状態
class State:
    # 初期化
    def __init__(self, pieces=None, enemy_pieces=None, depth=0):

        # 駒の配置
        if pieces != None:
            self.pieces = pieces
        else:
            self.pieces = [0] * 20

        if enemy_pieces != None:
            self.enemy_pieces = enemy_pieces
        else:
            self.enemy_pieces = [0] * 20

        # ターンの深さ(ターン数)
        self.depth = depth

        # ゴール周りの判定用
        self.is_goal = False
        self.goal_player = -1

        # 駒の初期配置
        if pieces == None or enemy_pieces == None:
            # 青2赤2
            # piece_list = [1, 1, 2, 2]
            piece_list = [2, 1, 1, 2]

            random.shuffle(piece_list)  # 配置をランダムに
            self.pieces[13] = piece_list[0]
            self.pieces[14] = piece_list[1]
            self.pieces[17] = piece_list[2]
            self.pieces[18] = piece_list[3]

            self.keep_pieces_color = [0] * 8
            self.keep_pieces_color[0] = piece_list[3]
            self.keep_pieces_color[1] = piece_list[2]
            self.keep_pieces_color[2] = piece_list[1]
            self.keep_pieces_color[3] = piece_list[0]

            random.shuffle(piece_list)  # 配置をランダムにして使い回し
            self.enemy_pieces[13] = piece_list[0]
            self.enemy_pieces[14] = piece_list[1]
            self.enemy_pieces[17] = piece_list[2]
            self.enemy_pieces[18] = piece_list[3]

            self.keep_pieces_color[4] = piece_list[0]
            self.keep_pieces_color[5] = piece_list[1]
            self.keep_pieces_color[6] = piece_list[2]
            self.keep_pieces_color[7] = piece_list[3]

        self.winner_is_me = False

    def get_blue_from_keep_pieces_color(self):
        # print("keep_pieces_color", self.keep_pieces_color)
        blue_id_list = []
        for index, blue_or_red_num in enumerate(self.keep_pieces_color):
            if blue_or_red_num == 1:
                blue_id_list.append(index)
        return blue_id_list

    # 負けかどうか
    def is_lose(self):
        if not any(elem == 1 for elem in self.pieces):  # 自分の青駒が存在しないなら負け
            # print("青喰われ：負け")
            return True
        if not any(elem == 2 for elem in self.enemy_pieces):  # 敵の赤駒が存在しない(全部取っちゃった)なら負け
            # print("赤喰い：負け")
            return True
        # 前の手でゴールされてたらis_goalがTrueになってる(ような仕様にする)
        if self.is_goal:
            # print("ゴール")
            return True
        return False

    # 勝ちかどうか
    def is_win(self):
        if not any(elem == 1 for elem in self.enemy_pieces):  # 相手の青駒が存在しないなら勝ち
            # print("青喰い：勝ち")
            return True
        if not any(elem == 2 for elem in self.pieces):  # 自分の赤駒が存在しない(全部取らせた)なら勝ち
            # print("赤喰わせ：勝ち")
            return True
        return False

    # 判定だけis_doneにさせて、勝敗はこっちで見とく必要があるかもしれない

    # 引き分けかどうか
    def is_draw(self):
        return self.depth >= 200  # 300手

    # ゲーム終了かどうか
    def is_done(self):
        return self.is_lose() or self.is_win() or self.is_draw()

    # デュアルネットワークの入力の2次元配列の取得
    def pieces_array(self):
        # プレイヤー毎のデュアルネットワークの入力の2次元配列の取得
        def pieces_array_of(pieces):
            table_list = []
            # 青駒(1)→赤駒(2)の順に取得
            for j in range(1, 3):
                table = [0] * 20
                table_list.append(table)
                # appendは参照渡しなのでtable書き換えればtable_listも書き換わる
                for i in range(20):
                    if pieces[i] == j:
                        table[i] = 1

            return table_list

        # デュアルネットワークの入力の2次元配列の取得(自分と敵両方)
        return [pieces_array_of(self.pieces), pieces_array_of(self.enemy_pieces)]

    # position->0~20
    # direction->下:0,左:1,上:2,右:3

    # 駒の移動元と移動方向を行動に変換
    def position_to_action(self, position, direction):
        return position * 4 + direction

    # 行動を駒の移動元と移動方向に変換
    def action_to_position(self, action):
        return (int(action / 4), action % 4)  # position,direction

    # 合法手のリストの取得
    def legal_actions(self):
        actions = []
        for p in range(20):
            # 駒の存在確認
            if self.pieces[p] != 0:
                # 存在するなら駒の位置を渡して、その駒の取れる行動をactionsに追加
                actions.extend(self.legal_actions_pos(p))
        # 青駒のゴール行動は例外的に合法手リストに追加
        if self.pieces[0] == 1:
            actions.extend([2])  # 0*4 + 2
        if self.pieces[3] == 1:
            actions.extend([14])  # 3*4 + 2
        return actions

    # 駒ごと(駒1つに着目した)の合法手のリストの取得
    def legal_actions_pos(self, position):
        actions = []
        x = position % 4
        y = int(position / 4)
        # 下左上右の順に行動できるか検証し、できるならactionに追加
        # ちなみにand演算子は左の値を評価して右の値を返すか決める(左の値がTrue系でなければ右の値は無視する)ので、はみ出し参照してIndexErrorにはならない(&だとなる)
        if y != 4 and self.pieces[position + 4] == 0:  # 下端でない and 下に自分の駒がいない
            actions.append(self.position_to_action(position, 0))
        if x != 0 and self.pieces[position - 1] == 0:  # 左端でない and 左に自分の駒がいない
            actions.append(self.position_to_action(position, 1))
        if y != 0 and self.pieces[position - 4] == 0:  # 上端でない and 上に自分の駒がいない
            actions.append(self.position_to_action(position, 2))
        if x != 3 and self.pieces[position + 1] == 0:  # 右端でない and 右に自分の駒がいない
            actions.append(self.position_to_action(position, 3))
        # 青駒のゴール行動の可否は1ターンに1度だけ判定すれば良いので、例外的にlegal_actionsで処理する(ここでは処理しない)
        return actions

    # 次の状態の取得
    def next(self, action):
        # 次の状態の作成
        state = State(self.pieces.copy(), self.enemy_pieces.copy(), self.depth + 1)

        # position_bef->移動前の駒の位置、position_aft->移動後の駒の位置
        # 行動を(移動元, 移動方向)に変換
        position_bef, direction = self.action_to_position(action)

        # 合法手がくると仮定
        # 駒の移動(後ろに動くことは少ないかな？ + if文そんなに踏ませたくないな と思ったので判定を左右下上の順番にしてるけど意味あるのかは不明)
        if direction == 0:  # 下
            position_aft = position_bef + 4
        elif direction == 1:  # 左
            position_aft = position_bef - 1
        elif direction == 2:  # 上
            if position_bef == 0 or position_bef == 3:  # 0と5の上行動はゴール処理なので先に弾く
                state.is_goal = True
                position_aft = (
                    position_bef  # position_befを入れて駒の場所を動かさない(勝敗は決しているので下手に動かさない方が良いはず)
                )
            else:
                position_aft = position_bef - 4
        elif direction == 3:  # 右
            position_aft = position_bef + 1
        else:
            print("error関数名:next")

        # 実際に駒移動
        state.pieces[position_aft] = state.pieces[position_bef]
        state.pieces[position_bef] = 0

        # 移動先に敵駒が存在した場合は取る(比較と値入れどっちが早いかあとで調べて最適化したい)
        # piecesとenemy_piecesを対応させるには値をひっくり返す必要がある(要素のインデックスは0~35だから、 n->35-n でひっくり返せる)
        if state.enemy_pieces[19 - position_aft] != 0:
            state.enemy_pieces[19 - position_aft] = 0

        # 駒の交代(ターンプレイヤが切り替わるため)(pieces <-> enemy_pieces)
        tmp = state.pieces
        state.pieces = state.enemy_pieces
        state.enemy_pieces = tmp
        return state

    # 先手かどうか
    def is_first_player(self):
        return self.depth % 2 == 0

    # どちらのプレイヤーが勝利したか判定
    # 勝敗決定時にやるだけだからそんな高速化しないで大丈夫
    def winner_checker(self, win_player):
        if self.is_goal:
            win_player[self.goal_player] += 1
            return

        board = [0] * 20
        if self.depth % 2 == 0:
            my_p = self.pieces.copy()
            rev_ep = list(reversed(self.enemy_pieces))
            for i in range(20):
                board[i] = my_p[i] - rev_ep[i]
        else:
            my_p = list(reversed(self.pieces))
            rev_ep = self.enemy_pieces.copy()
            for i in range(20):
                board[i] = rev_ep[i] - my_p[i]

        if not any(elem == 1 for elem in board):  # 先手の青駒が存在しない
            win_player[1] += 1  # 後手の勝ち
        elif not any(elem == 2 for elem in board):  # 先手の赤駒が存在しない
            win_player[0] += 1  # 先手の勝ち
        elif not any(elem == -1 for elem in board):  # 後手の青駒が存在しない
            win_player[0] += 1  # 先手の勝ち
        elif not any(elem == -2 for elem in board):  # 後手の赤駒が存在しない
            win_player[1] += 1  # 後手の勝ち
        else:
            print(self)
            print("これはゴール行動なのでは？？？？")

    # 文字列表示
    def __str__(self):
        row = "|{}|{}|{}|{}|"
        hr = "\n---------------------\n"

        # 1つのボードに味方の駒と敵の駒を集める
        board = [0] * 20
        if self.depth % 2 == 0:
            my_p = self.pieces.copy()
            rev_ep = list(reversed(self.enemy_pieces))
            for i in range(20):
                board[i] = my_p[i] - rev_ep[i]
        else:
            my_p = list(reversed(self.pieces))
            rev_ep = self.enemy_pieces.copy()
            for i in range(20):
                board[i] = rev_ep[i] - my_p[i]

        board_essence = []
        for i in board:
            if i == 1:
                board_essence.append("先青")
            elif i == 2:
                board_essence.append("先赤")
            elif i == -1:
                board_essence.append("後青")
            elif i == -2:
                board_essence.append("後赤")
            else:
                board_essence.append("　　")

        str = (hr + row + hr + row + hr + row + hr + row + hr + row + hr).format(
            *board_essence
        )
        return str


# ランダムで行動選択
def random_action(state):
    legal_actions = state.legal_actions()
    return legal_actions[random.randint(0, len(legal_actions) - 1)]


# 人間に行動を選択させる
def human_player_action(state):
    # 盤面を表示
    print(state)

    # 入力を待つ(受ける)
    before_move_place = int(input("Please enter to move piece (左上~右下にかけて0~19) : "))
    direction = int(input("direction (下0 左1 上2 右3) : "))
    move = state.position_to_action(before_move_place, direction)

    # 合法手か確認
    legal_actions = state.legal_actions()
    if any(elem == move for elem in legal_actions):
        return move

    # エラー処理(デバッグでしか使わんから適当)
    print("非合法手が選択された為、ランダムに行動しました")
    return legal_actions[random.randint(0, len(legal_actions) - 1)]


# モンテカルロ木探索の行動選択
def mcts_action(state):
    # モンテカルロ木探索のノード
    class node:
        # 初期化
        def __init__(self, state):
            self.state = state  # 状態
            self.w = 0  # 累計価値
            self.n = 0  # 試行回数
            self.child_nodes = None  # 子ノード群

        # 評価
        def evaluate(self):
            # ゲーム終了時
            if self.state.is_done():
                # 勝敗結果で価値を取得
                value = -1 if self.state.is_lose() else 0  # 負けは-1、引き分けは0

                # 累計価値と試行回数の更新
                self.w += value
                self.n += 1
                return value

            # 子ノードが存在しない時
            if not self.child_nodes:
                # プレイアウトで価値を取得
                value = playout(self.state)

                # 累計価値と試行回数の更新
                self.w += value
                self.n += 1

                # 子ノードの展開
                if self.n == 10:
                    self.expand()
                return value

            # 子ノードが存在する時
            else:
                # UCB1が最大の子ノードの評価で価値を取得
                value = -self.next_child_node().evaluate()

                # 累計価値と試行回数の更新
                self.w += value
                self.n += 1
                return value

        # 子ノードの展開
        def expand(self):
            legal_actions = self.state.legal_actions()
            self.child_nodes = []
            for action in legal_actions:
                self.child_nodes.append(node(self.state.next(action)))

        # UCB1が最大の子ノードを取得
        def next_child_node(self):
            # 試行回数nが0の子ノードを返す
            for child_node in self.child_nodes:
                if child_node.n == 0:
                    return child_node

            # UCB1の計算
            t = 0
            for c in self.child_nodes:
                t += c.n
            ucb1_values = []
            for child_node in self.child_nodes:
                ucb1_values.append(
                    -child_node.w / child_node.n
                    + 2 * (2 * math.log(t) / child_node.n) ** 0.5
                )

            # UCB1が最大の子ノードを返す
            return self.child_nodes[argmax(ucb1_values)]

    # ルートノードの生成
    root_node = node(state)
    root_node.expand()

    # ルートノードを評価 (rangeを変化させると評価回数を変化させられる)
    for _ in range(100):
        root_node.evaluate()

    # 試行回数の最大値を持つ行動を返す
    legal_actions = state.legal_actions()
    n_list = []
    for c in root_node.child_nodes:
        n_list.append(c.n)
    return legal_actions[argmax(n_list)]


# 最大値のインデックスを返す
def argmax(collection, key=None):
    return collection.index(max(collection))


# ゲームの終端までシミュレート
def playout(state):
    if state.is_lose():
        return -1

    if state.is_draw():
        return 0

    return -playout(state.next(random_action(state)))


import GuessEnemyPiece
import numpy as np
import itertools
import time
from pv_mcts import predict
from dual_network import DN_INPUT_SHAPE
from pathlib import Path
from tensorflow.keras.models import load_model


# 動作確認
if __name__ == "__main__":

    # GuessEnemyPieceに必要な処理
    path = sorted(Path("./model").glob("*.h5"))[-1]
    model = load_model(str(path))

    # 勝利数を保管[先手、後手]
    win_player = [0, 0]

    with open("estimate_accuracy.csv", "w") as csvFile:
        csvWriter = csv.writer(csvFile)
        # csvWriter.writerow([])  # 改行

        for _ in range(100):

            # 直前の行動を保管
            just_before_action_num = 0

            # 状態の生成
            state = State()
            blue_id_list = state.get_blue_from_keep_pieces_color()
            # ii_state = GuessEnemyPiece.II_State({4, 7})
            ii_state = GuessEnemyPiece.II_State(
                {blue_id_list[2], blue_id_list[3]}, {blue_id_list[0], blue_id_list[1]}
            )

            # ゲーム終了までのループ
            while True:
                # ゲーム終了時
                if state.is_done():
                    # print("ゲーム終了:ターン数", state.depth)

                    # if state.is_lose():
                    #     if state.depth % 2 == 0:
                    #         print("敗北")
                    #     else:
                    #         print("勝利or引き分け")
                    # else:
                    #     if state.depth % 2 == 1:
                    #         print("勝利or引き分け")
                    #     else:
                    #         print("敗北")
                    break

                # 次の状態の取得
                if state.depth % 2 == 0:
                    just_before_action_num = random_action(state)  # ランダム
                    # just_before_action_num = mcts_action(state)  # モンテカルロ
                    # just_before_action_num = human_player_action(state)  # 人間
                    # print("ランダムAIの行動番号", just_before_action_num)
                    if just_before_action_num == 2 or just_before_action_num == 14:
                        print("ランダムAIのゴール")
                        state.is_goal = True
                        state.goal_player = 0
                        break
                    state = state.next(just_before_action_num)
                else:
                    just_before_enemy_action_num = just_before_action_num
                    guess_player_action = GuessEnemyPiece.guess_enemy_piece_player_for_debug(
                        model, ii_state, just_before_enemy_action_num
                    )

                    GuessEnemyPiece.measure_estimate_accuracy(
                        ii_state, state, csvWriter
                    )
                    just_before_action_num = guess_player_action
                    if PRINT_DEBUG:
                        print(ii_state.return_estimate_value())  # 現状の推測値をプリントするやつ
                        print("自作AIの行動番号", just_before_action_num)

                    # just_before_action_num = random_action(state)  # ランダムエージェント

                    if just_before_action_num == 2 or just_before_action_num == 14:
                        print("自作AIのゴール")
                        state.is_goal = True
                        state.goal_player = 1
                        break
                    state = state.next(just_before_action_num)

                # 文字列表示
                # print("depth", state.depth)
                if PRINT_DEBUG:
                    print(state)
            state.winner_checker(win_player)
            print(win_player)

    csvFile.close()
