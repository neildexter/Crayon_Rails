import board, cell, time, copy

f = open('game_board.txt', 'r')
terr_matrix = [line.replace('\n', '').split(' ') for line in f]

start = (9,2)

hex_names = {start: "START",
             (3, 2): "Abbot",
             (9, 6): "Baker",
             (5, 28): "Camino",
             (1, 8): "Dawson",
             (4, 16): "Emmen",
             (1, 23): "Flint" }

b1 = board.Board(terr_matrix,hex_names)

class test(object):
    def __init__(self, test1_dict, test2_dict):
        self.test1_dict = test1_dict
        self.test2_dict = test2_dict
    # def __getattr__(self, key):
    #     return self[key]

    # def __deepcopy__(self,memo):
    #     cls = self.__class__
    #     memo[id(self)] = result
    #     for k, v in self.__dict__.items():
    #         setattr(result, k, deepcopy(v,mem))
    #     return result

a = test({},{})
a.test1_dict = {}
for i in range(len(terr_matrix)):
    for j in range(len(terr_matrix[0])):
        a.test1_dict[(i,j,'ne')] = 0
        a.test1_dict[(i,j,'e')] = 0
        a.test1_dict[(i,j,'se')] = 0
        a.test1_dict[(i,j,'sw')] = 0
        a.test1_dict[(i,j,'w')] = 0
        a.test1_dict[(i,j,'nw')] = 0

a.test2_dict = {}
for i in range(len(terr_matrix)):
    for j in range(len(terr_matrix[0])):
        a.test2_dict[(i,j)] = terr_matrix[i][j]

test_time1 = time.time()
for i in range(1000):
    b = copy.deepcopy(a)
print time.time() - test_time1

test_time2 = time.time()
for i in range(1000):
    b2 = copy.deepcopy(b1)
print time.time() - test_time2