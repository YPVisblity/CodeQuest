請定義一個 generate_arithmetic_sequence(a, d, n) 函數，其中 a 為首項、d 為公差、n 為項數（a、d、n 都是整數，d 可以是負數）。

請先建立一個空串列 sequence，接著使用 for 迴圈搭配公式 term = a + i * d（i 從 0 到 n-1）依序計算等差數列的每一項，並將每一項加入 sequence，最後回傳 sequence（一維 list）。

例如：
- generate_arithmetic_sequence(2, 3, 5) 應回傳 [2, 5, 8, 11, 14]
- generate_arithmetic_sequence(10, -4, 4) 應回傳 [10, 6, 2, -2]

注意：評測時會用不同的首項、公差與項數測試，不要把答案寫死。
