# ====================
# ベストプレイヤーの評価
# ====================

# パッケージのインポート
from game import State, random_action, human_player_action, mcts_action
from pv_mcts import pv_mcts_action, high_value_action
from tensorflow.keras.models import load_model
from tensorflow.keras import backend as K
from pathlib import Path
import numpy as np

# パラメータの準備
EP_GAME_COUNT = 100  # 1評価あたりのゲーム数

drow_count = 0

# 先手プレイヤーのポイント
def first_player_point(ended_state):
    # 1:先手勝利, 0:先手敗北, 0.5:引き分け
    if ended_state.is_lose():
        return 0 if ended_state.is_first_player() else 1
    # print("引き分けました")
    global drow_count
    drow_count = drow_count + 1
    return 0.5


# 1ゲームの実行
def play(next_actions):
    # 状態の生成
    state = State()

    # ゲーム終了までループ
    while True:
        # ゲーム終了時
        if state.is_done():
            break

        # 行動の取得
        next_action = next_actions[0] if state.is_first_player() else next_actions[1]
        action = next_action(state)

        # 次の状態の取得
        state = state.next(action)

    # 先手プレイヤーのポイントを返す
    return first_player_point(state)


# 任意のアルゴリズムの評価
def evaluate_algorithm_of(label, next_actions):
    # 複数回の対戦を繰り返す
    total_point = 0
    for i in range(EP_GAME_COUNT):
        # 1ゲームの実行
        if i % 2 == 0:
            total_point += play(next_actions)
        else:
            total_point += 1 - play(list(reversed(next_actions)))

        # 出力
        print("\rEvaluate {}/{}".format(i + 1, EP_GAME_COUNT), end="")
    print("")

    # 平均ポイントの計算
    average_point = total_point / EP_GAME_COUNT
    print("total_point", total_point, "EP_GAME_COUNT", EP_GAME_COUNT)
    print(label, average_point)


# ベストプレイヤーの評価
def evaluate_best_player():
    # ベストプレイヤーのモデルの読み込み
    model = load_model("./model/best.h5")

    # 行動価値が高い行動を選択し続けるエージェントvsランダム
    # pv_high_value_action = high_value_action(model)
    # next_actions = (pv_high_value_action, random_action)
    # evaluate_algorithm_of("Value_VS_Random", next_actions)

    # PV MCTSで行動選択を行う関数の生成
    next_pv_mcts_action = pv_mcts_action(model, 0.0)

    # VSランダム
    next_actions = (next_pv_mcts_action, random_action)
    evaluate_algorithm_of("VS_Random", next_actions)

    # VS_過去の自分
    # first_model = load_model("./model/first_best.h5")  # 過去のモデルの読み込み
    # first_next_pv_mcts_action = pv_mcts_action(first_model, 0.0)  # PV MCTSで行動選択を行う関数の生成
    # next_actions = (next_pv_mcts_action, first_next_pv_mcts_action)
    # evaluate_algorithm_of("VS_過去の自分", next_actions)

    # VSランダム
    # next_actions = (first_next_pv_mcts_action, random_action)
    # evaluate_algorithm_of("first_VS_Random", next_actions)

    # 人類との戦い human_player_action
    # next_actions = (human_player_action, next_pv_mcts_action)
    # evaluate_algorithm_of("自己対戦", next_actions)

    # VSモンテカルロ木探索
    # next_actions = (next_pv_mcts_action, mcts_action)
    # evaluate_algorithm_of("VS_MCTS", next_actions)

    # モデルの破棄
    K.clear_session()
    del model
    # del first_model


def evaluate_miniGeisterLog():
    global drow_count
    for i in range(1, 34):
        drow_count = 0
        model_pass_str = "./miniGeisterLog/log" + str(i) + ".h5"
        model = load_model(model_pass_str)

        # valueVSランダム
        # pv_high_value_action = high_value_action(model)
        # next_actions = (pv_high_value_action, random_action)
        # evaluate_algorithm_of("Value_VS_Random", next_actions)
        # print("drow:", drow_count)

        # valueVSモンテカルロ木探索
        pv_high_value_action = high_value_action(model)
        next_actions = (pv_high_value_action, mcts_action)
        evaluate_algorithm_of("Value_VS_Mcts", next_actions)
        print("drow:", drow_count)

        K.clear_session()
        del model


# 動作確認
if __name__ == "__main__":
    # evaluate_best_player()
    evaluate_miniGeisterLog()
