import csv
import numpy as np


# 動作確認
if __name__ == "__main__":
    max_turn = 300
    sum_estimate_acc = np.array([0] * max_turn, dtype="f4")
    count_reach_this_turn = [0] * max_turn

    # csv内部のデータをソート
    with open("estimate_accuracy.csv") as csv_data:
        reader = csv.reader(csv_data)
        all_data = [row for row in reader]

        for row in all_data:
            if len(row) > 4:  # 空行などの対策
                index = int(row[0])
                sum_estimate_acc[index] += float(row[2])
                count_reach_this_turn[index] += 1

    average_est = np.array([0] * max_turn, dtype="f4")
    # 出力
    with open("average_estimate_accuracy.csv", "w") as csvFile:
        csvWriter = csv.writer(csvFile)

        for index, sum_est in enumerate(sum_estimate_acc):
            if count_reach_this_turn[index] > 0:
                average_est[index] = sum_est / float(count_reach_this_turn[index])

                csvWriter.writerow([index, average_est[index]])

    csvFile.close()
