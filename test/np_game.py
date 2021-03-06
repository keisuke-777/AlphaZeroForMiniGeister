# ====================
# ミニガイスター
# 青駒→1
# 赤駒→2
# ====================

import random
import math
import numpy as np

# ゲームの状態
class State:
    # 初期化
    def __init__(
        self,
        pieces=np.array([0] * 20, dtype=np.float32),
        enemy_pieces=np.array([0] * 20, dtype=np.float32),
        depth=0,
    ):

        self.is_goal = False

        # 駒の配置
        self.pieces = pieces
        self.enemy_pieces = enemy_pieces

        # ターンの深さ(ターン数)
        self.depth = depth

        # 駒の初期配置
        if depth == 0:
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
        if not np.any(self.pieces == 1):  # 自分の青駒が存在しないなら負け
            # print("青喰い")
            return True
        if not np.any(self.enemy_pieces == 2):  # 敵の赤駒が存在しない(全部取っちゃった)なら負け
            # print("赤喰い")
            return True
        if self.is_goal:  # 前の手でゴールされてる
            # print("ゴール")
            return True
        return False

    def is_lose_neo(self):
        # 意味わからんけど遅くなった？(同速説はある)
        if (
            (not np.any(self.pieces == 1))
            | (not np.any(self.enemy_pieces == 2))
            | self.is_goal
        ):
            return True
        return False

    # def is_lose_neo2(self):
    #     # notが遅いんじゃないかと思ったけどそれより遅い。多分2倍ぐらい遅い
    #     if (
    #         np.any(self.pieces == 1)
    #         and np.any(self.enemy_pieces == 2)
    #         and self.is_goal != True
    #     ):
    #         return False
    #     return True

    # 引き分けかどうか
    def is_draw(self):
        return self.depth >= 300  # 300手

    # ゲーム終了かどうか
    def is_done(self):
        return self.is_lose() or self.is_draw()

    # デュアルネットワークの入力の2次元配列の取得
    # ここなぜか知らんけど処理すごい早いので改良できんかった
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


import time

# 動作確認
if __name__ == "__main__":
    # 状態の生成
    state = State()
    # ゲーム終了までのループ #whileループはforで代用するより早い
    # while True:
    #     # ゲーム終了時
    #     if state.is_done():
    #         print(state.depth)
    #         break

    #     # 次の状態の取得
    #     state = state.next(random_action(state))

    #     # 文字列表示
    #     print(state)

    start_time = time.time()
    for i in range(1000):
        state.is_lose()
    end_time = time.time()
    print(str(end_time - start_time) + " [sec]")  # print calculation time

    start_time = time.time()
    for i in range(1000):
        state.is_lose_neo()
    end_time = time.time()
    print(str(end_time - start_time) + " [sec]")  # print calculation time

    start = time.time()
    i = 0
    sumation = 0
    while True:
        sumation += 1
        if sumation > 999998:
            break
    elapsed_time = time.time() - start
    print("while_time:{0}".format(elapsed_time) + "[sec]")

    start = time.time()
    i = 0
    sumation = 0
    for i in range(1000000):
        sumation += i
    elapsed_time = time.time() - start
    print("for_time:{0}".format(elapsed_time) + "[sec]")

    # state.pieces[13] = 0
    # state.pieces[12] = 2
    # start_time = time.time()
    # for i in range(1000):
    #     a = state.legal_actions()
    # end_time = time.time()

    # print(a)

    # print(str(end_time - start_time) + " [sec]")  # print calculation time
