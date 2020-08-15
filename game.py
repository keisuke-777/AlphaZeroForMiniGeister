# ====================
# ミニガイスター
# 青駒→1
# 赤駒→2
# ====================

# パッケージのインポート
import random
import math

# import numpy as np

# ゲームの状態
class State:
    # 初期化
    def __init__(self, pieces=None, enemy_pieces=None, depth=0):

        self.is_goal = False

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

        # 駒の初期配置
        if pieces == None or enemy_pieces == None:
            # とりあえず固定で学習を進める(あとで様子みてからランダムにしたい)
            self.pieces[13] = 2
            self.pieces[14] = 1
            self.pieces[17] = 1
            self.pieces[18] = 2

            self.enemy_pieces[13] = 2
            self.enemy_pieces[14] = 1
            self.enemy_pieces[17] = 1
            self.enemy_pieces[18] = 2

    # 負けかどうか
    def is_lose(self):
        if not any(elem == 1 for elem in self.pieces):  # 自分の青駒が存在しないなら負け
            # print("青喰い")
            return True
        if not any(elem == 2 for elem in self.enemy_pieces):  # 敵の赤駒が存在しない(全部取っちゃった)なら負け
            # print("赤喰い")
            return True
        # 前の手でゴールされてたらis_goalがTrueになってる(はず)
        if self.is_goal:
            # print("ゴール")
            return True
        return False

    # 引き分けかどうか
    def is_draw(self):
        return self.depth >= 300  # 300手

    # ゲーム終了かどうか
    def is_done(self):
        return self.is_lose() or self.is_draw()

    # デュアルネットワークの入力の2次元配列の取得
    def pieces_array(self):
        # プレイヤー毎のデュアルネットワークの入力の2次元配列の取得
        def pieces_array_of(pieces):
            table_list = []
            # 青駒(1)→赤駒(2)の順に取得
            for j in range(1, 3):
                table = [0] * 20
                table_list.append(table)
                # appendは参照渡しっぽいのでtable書き換えればtable_listも書き換わってハッピー
                for i in range(20):
                    if pieces[i] == j:
                        table[i] = 1

            return table_list

        # デュアルネットワークの入力の2次元配列の取得(自分と敵両方)
        return [pieces_array_of(self.pieces), pieces_array_of(self.enemy_pieces)]

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
            # 駒の移動時
            if self.pieces[p] != 0:
                # 移動前の駒の位置を渡す
                actions.extend(self.legal_actions_pos(p))
        # 青駒のゴール行動は例外的に合法手リストに追加
        if self.pieces[0] == 1:
            actions.extend([2])  # 0*4 + 2
        if self.pieces[3] == 1:
            actions.extend([14])  # 3*4 + 2
        return actions

    # 駒の移動時の合法手のリストの取得
    def legal_actions_pos(self, position):
        actions = []
        x = position % 4
        y = int(position / 4)
        # 合法手の取得
        # ちなみにand演算子は左の値を評価して右の値を返すか決める(左の値がTrue系でなければ右の値は無視する)ので、はみ出してIndexErrorみたいにはならん(&だとなる)
        if y != 4 and self.pieces[position + 4] == 0:  # 下端でない and 下に自分の駒がいない
            actions.append(self.position_to_action(position, 0))
        if x != 0 and self.pieces[position - 1] == 0:  # 左端でない and 左に自分の駒がいない
            actions.append(self.position_to_action(position, 1))
        if y != 0 and self.pieces[position - 4] == 0:  # 上端でない and 上に自分の駒がいない
            actions.append(self.position_to_action(position, 2))
        if x != 3 and self.pieces[position + 1] == 0:  # 右端でない and 右に自分の駒がいない
            actions.append(self.position_to_action(position, 3))
        # 青駒のゴール行動は例外的にlegal_actionsで処理する(ここでは処理しない)
        return actions

    # 次の状態の取得
    def next(self, action):
        # 次の状態の作成
        state = State(self.pieces.copy(), self.enemy_pieces.copy(), self.depth + 1)

        # 行動を(移動元, 移動方向)に変換
        position_bef, direction = self.action_to_position(action)

        # 合法手がくると仮定
        # 駒の移動(後ろに動くの少ないかな？ + if文そんなに踏ませたくないな。と思ったので判定を左右下上の順番にしてるけど意味あるんかは知らん)
        if direction == 1:
            position_aft = position_bef - 1
        elif direction == 3:
            position_aft = position_bef + 1
        elif direction == 0:
            position_aft = position_bef + 4
        elif direction == 2:
            if position_bef == 0 or position_bef == 3:
                state.is_goal = True
                position_aft = position_bef  # こことりあえずposition_bef入れてるけど大丈夫かなぁ(position_befならとりあえず相手の駒食ったりはしない)
            else:
                position_aft = position_bef - 4
        else:
            print("何もしてないのに壊れました")

        # 実際に駒移動
        state.pieces[position_aft] = state.pieces[position_bef]
        state.pieces[position_bef] = 0

        # 敵駒存在した場合は取る(比較と値入れどっちが早いかあとで調べて最適化したい)
        if state.enemy_pieces[19 - position_aft] != 0:
            state.enemy_pieces[19 - position_aft] = 0

        # 駒の交代
        tmp = state.pieces
        state.pieces = state.enemy_pieces
        state.enemy_pieces = tmp
        return state

    # 先手かどうか
    def is_first_player(self):
        return self.depth % 2 == 0

    # 文字列表示
    def __str__(self):
        row = "|{}|{}|{}|{}|"
        hr = "\n---------------------\n"
        # ここの処理とかあるのにnumpy使わんの頭おかしいけど使わん。
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
                board_essence.append("自青")
            elif i == 2:
                board_essence.append("自赤")
            elif i == -1:
                board_essence.append("敵青")
            elif i == -2:
                board_essence.append("敵赤")
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


# 動作確認
if __name__ == "__main__":
    # 状態の生成
    state = State()

    # ゲーム終了までのループ
    while True:
        # ゲーム終了時
        if state.is_done():
            # print(state.depth)
            break

        # 次の状態の取得
        state = state.next(random_action(state))

        # 文字列表示
        # print(state)
