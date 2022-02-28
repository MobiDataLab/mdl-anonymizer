# for len_1 in range (2, 20):
#     for len_2 in range (2, 20):
#         h = round((len_1 + len_2) / 2)
#         gap_1 = len_1 / h
#         gap_2 = len_2 / h
#         print (f'len1: {len_1}, len2: {len_2}, h: {h}, gap1: {gap_1}, gap2: {gap_2}')
#
#         index_1 = index_2 = 0
#         i = j = 0
#
#         for k in range(h):
#             print(k)
#             print(f"1: Accessing {i}")
#             if i >= len_1:
#                 print("ERROR")
#             print(f"2: Accessing {j}")
#             if j >= len_2:
#                 print("ERROR")
#
#             index_1 += gap_1
#             index_2 += gap_2
#
#             i = round(index_1)
#             j = round(index_2)
import time

import numpy

# array = numpy.array([10,11,12,13])
#
#
# a = numpy.array([1,2,3,4])
# b = numpy.array([4])
#
# d = a-b
# print(d)
#
# indexes = numpy.where(abs(d) >= 2)
#
# print (numpy.where(abs(d) >= 2))
#
# print(array[indexes])
import numpy as np


l_timestamp = np.array([0.5])
candidates_timestamps = np.random.rand(3000000)

start = time.time()
temporal_distances = candidates_timestamps - l_timestamp
end = time.time()
print(end-start)


start = time.time()
for c in candidates_timestamps:
    d = abs(l_timestamp - c)
end = time.time()
print(end-start)