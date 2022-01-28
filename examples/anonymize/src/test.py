for len_1 in range (2, 20):
    for len_2 in range (2, 20):
        h = round((len_1 + len_2) / 2)
        gap_1 = len_1 / h
        gap_2 = len_2 / h
        print (f'len1: {len_1}, len2: {len_2}, h: {h}, gap1: {gap_1}, gap2: {gap_2}')

        index_1 = index_2 = 0
        i = j = 0

        for k in range(h):
            print(k)
            print(f"1: Accessing {i}")
            if i >= len_1:
                print("ERROR")
            print(f"2: Accessing {j}")
            if j >= len_2:
                print("ERROR")

            index_1 += gap_1
            index_2 += gap_2

            i = round(index_1)
            j = round(index_2)
