import csv
import numpy as np

# 何試合かやったデータをすべて格納してあるcsvを食べて、全試合のデータの平均を算出する(ターン数が多くなるとサンプルが少なくなるけど割り切る)
if __name__ == "__main__":
    max_turn = 300  # ターンの最大値(この値は大きすぎても問題ない)
    sum_estimate_acc = np.array([0] * max_turn, dtype="f4")  # 推測値の正確さを一旦全部足しとく場所
    count_reach_this_turn = [0] * max_turn  # そのターン数をプレイした回数

    # csv内部のデータをソート
    with open("estimate_accuracy.csv") as csv_data:
        reader = csv.reader(csv_data)
        all_data = [row for row in reader]

        for row in all_data:
            if len(row) > 4:  # 空行でrow[n]が範囲外れてエラー吐く対策
                # row[0]=ターン数, row[2]=推測値の正確さ
                index = int(row[0])  # ターン数
                sum_estimate_acc[index] += float(row[2])  # 推測値の正確さを加算
                count_reach_this_turn[index] += 1  # そのターン数をプレイした回数に+1する

    # 現状ここで定義する必要はないけど将来的に使うかも
    average_est = np.array([0] * max_turn, dtype="f4")
    # 出力処理
    with open("average_estimate_accuracy.csv", "w") as csvFile:
        csvWriter = csv.writer(csvFile)

        for index, sum_est in enumerate(sum_estimate_acc):
            if count_reach_this_turn[index] > 0:  # 一度もそのターン数までプレイしていなければデータとして用いない
                # 推測値の正確さの平均をとる
                average_est[index] = sum_est / float(count_reach_this_turn[index])

                csvWriter.writerow([index, average_est[index]])

    csvFile.close()
