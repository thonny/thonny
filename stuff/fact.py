def fact(n):
    if n == 0:
        return 1
    else:
        return fact(n-1) * n

print(fact(3))