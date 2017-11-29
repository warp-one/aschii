def sieve(n):
    np1 = n+1
    s = range(np1)
    s[1] = 0
    sqrtn = int(round(n**.5))
    for i in xrange(2, sqrtn + 1):
        if s[i]:
            s[i*i: np1: i] = [0] * len(xrange(i*i, np1, i))
    return filter(None, s)