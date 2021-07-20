# with open('config.txt') as f:
#     for line in f.readlines():
#         if '#' in line:
#             continue
#         host_type, ip, port, = line.split(',')
#         break
#     print(host_type, ip, port)
#
# total = 0
# for i in range(1, 100):
#     total += i
# print(total)
# print(sum(range(1, 100)))
#
# i = 1
# total_c = 0
# while i < 100:
#     total_c += i
#     i += 1
# print(total_c)

# import numpy as np
# a = np.array([1, 2, 3])
# b = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
# b[1, 1] = 10
# print(a.shape)
# print(b.shape)
# print(a.dtype)
# print(a)
# print(b)

import numpy as np


people_type = np.dtype({
    'names': ['name', 'chinese', 'english', 'math'],
    'formats': ['S32', 'i', 'i', 'i']})

peoples = np.array(
        [
            ("zhangfei", 66, 65, 30),
            ("guanyu", 95, 85, 98),
            ("zhaoyun", 93, 92, 96),
            ("huangzhong", 90, 88, 77),
            ("dianwei", 80, 90, 90)
        ], dtype=people_type)


ranking = sorted(peoples, key=lambda x: x[1] + x[2] + x[3], reverse=True)
print(ranking)
