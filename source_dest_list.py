from itertools import permutations, ifilterfalse
# Returns true if any of the conditions are broken
def determine(x):
    return x.index('s1') > x.index('d1') or x.index('s2') > x.index('d2') or x.index('s3') > x.index('d3')

a = ['s1', 's2', 's3', 'd1', 'd2', 'd3']
b = permutations(a)
b[:] = list(ifilterfalse(determine, b))