summa = 0
n = 0

while n < 7:
    if n % 3 == 0 or n % 5 == 0:
        summa = summa + n
        
    n = n + 1

print(summa)
