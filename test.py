from random import choice as choice

mdict = 50
fdict = 50

m,f = 0,0
for i in range(1, 99+1):
    x = choice(["m","f"])
    if x == "f":
        if f < mdict:
            f += 1
        else:
            m += 1
    else:
        if m < fdict:
            m += 1
        else:
            f += 1
    print x, m, f
