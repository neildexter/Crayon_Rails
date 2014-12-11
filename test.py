import time, random, operator as op

def conv_to_cube(coord):
    col = coord[1]
    row = coord[0]
    x = col - (row - (row % 2)) / 2
    z = row
    y = -x-z
    return (x,y,z)

def dist3(src,dest):
    row1 = src[0]
    col1 = src[1]
    x1 = col1 - (row1 - row1 % 2)/2
    row2 = dest[0]
    col2 = dest[1]
    x2 = col2 - (row2 - row2 % 2)/2
    return (abs(x1-x2)+abs(x1+row1+x2+row2)+abs(row1-row2))/2

def dist1(src,dest):
    x1 = src[1] - (src[0] - src[0] % 2)/2
    z1 = src[0]
    x2 = dest[1] - (dest[0] - dest[0] % 2)/2
    z2 = dest[0]
    return (abs(x1-x2)+abs(x1+z1+x2+z2)+abs(z1-z2))/2

def dist2(src,dest):
    src_cube = conv_to_cube(src)
    dest_cube = conv_to_cube(dest)
    return sum(map(abs,map(op.sub, src_cube, dest_cube)))/2

test_time1 = time.time()
for i in range(1000):
    for j in range(1000):
        dist1((0,0),(i,j))

print time.time() - test_time1

test_time2 = time.time()
for i in range(1000):
    for j in range(1000):
        dist2((0,0),(i,j))

print time.time() - test_time2

test_time3 = time.time()
for i in range(1000):
    for j in range(1000):
        dist3((0,0),(i,j))

print time.time() - test_time3
