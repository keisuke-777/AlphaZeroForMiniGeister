import time
import numpy as np

# n_loops = 1000

# start_time = time.time()
# data = np.empty(n_loops, dtype=np.float32)
# for i in range(n_loops):
#     bbb = 1
#     data[i] = bbb
# end_time = time.time()

# print(data)
# print(str(end_time - start_time) + " [sec]")  # print calculation time


# start_time = time.time()
# data = [0] * n_loops
# for i in range(n_loops):
#     bbb = 1
#     data[i] = bbb
# end_time = time.time()

# print(data)
# print(str(end_time - start_time) + " [sec]")  # print calculation time

pieces = np.array([0] * 20, dtype=np.float32)
enemy_pieces = np.array([0] * 20, dtype=np.float32)

pieces[13] = 2
pieces[14] = 1
pieces[17] = 1
pieces[18] = 2
enemy_pieces[13] = 2
enemy_pieces[14] = 1
enemy_pieces[17] = 1
enemy_pieces[18] = 2

start_time = time.time()
table_list = []
# 青駒(1)→赤駒(2)の順に取得
for j in range(1, 3):
    table = [0] * 20
    table_list.append(table)
    # appendは参照渡しっぽいのでtable書き換えればtable_listも書き換わってハッピー
    for i in range(20):
        if pieces[i] == j:
            table[i] = 1
end_time = time.time()

print(table_list)
print(str(end_time - start_time) + " [sec]")  # print calculation time


start_time = time.time()
table_list = [
    np.array([0] * 20, dtype=np.float32),
    np.array([0] * 20, dtype=np.float32),
]
# print(table_list)
# appendは参照渡しっぽいのでtable書き換えればtable_listも書き換わってハッピー
for i in range(20):
    if pieces[i] == 1:
        table_list[0][i] = 1
    elif pieces[i] == 2:
        table_list[1][i] = 1
end_time = time.time()

print(table_list)
print(str(end_time - start_time) + " [sec]")  # print calculation time
