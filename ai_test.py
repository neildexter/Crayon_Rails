from itertools import permutations, ifilter
from globals import *
import math as m, time, copy, pickle
import board as b
#import display as d
# Returns true if any of the conditions are broken

#pg.init()

start_time = time.time()

f = open('india_rails_gameboard.txt', 'r')

terr_matrix = [line.replace('\n', '').split(' ') for line in f]

f.close()

pkl_file = open('cost_dict.pk1', 'rb')
cost_dict = pickle.load(pkl_file)

inv_names = {name: coord for coord, name in hex_names.items()}
resources = {}

for name, rsc_list in resources_by_name.iteritems():
    coord = inv_names[name]
    resources[coord] = rsc_list


inv_resources = {}
for coord, rsc_list in resources.iteritems():
    for rsc in rsc_list:
        inv_resources[rsc] = inv_resources.get(rsc, [])
        inv_resources[rsc].append(coord)

##### IMPORTANT: Make sure payout keys are the same as demand keys, or it will not calculate final costs correctly

#all_starts = [inv_names["Calcutta"], inv_names['Bombay'], inv_names['Madras'], inv_names['Delhi'], inv_names['Karachi']]
all_starts = [inv_names["Calcutta"]]

demand_card1 = [("Pune", "Millet", 21),
                ("Mangalore", "Goats", 36), # Best combo
                ("Anuradhapura", "Imports", 10)]

demand_card2 = [("Rawalpindi", "Mica", 18), # Best combo
                ("Quetta", "Copper", 40),
                ("Colombo", "Textiles", 28)]

demand_card3 = [("Ahmadabad", "Coal", 17),
                ("Darjeeling", "Cotton", 33),
                ("Mangalore", "Oil", 45)] # Best combo

all_demands = {}
for d1 in demand_card1:
    for d2 in demand_card2:
        for d3 in demand_card3:
            all_demands[(d1, d2, d3)] = (d1, d2, d3)


def good(x, s1, s2, s3, d1, d2, d3):
    for source1 in s1:
        if source1 in x and not source1 in [d1, d2, d3]:
            # index returns the earliest instance in the list, so repeats (source AND dest) are okay
            if x.index(source1) > x.index(d1):
                return False
    for source2 in s2:
        if source2 in x and not source2 in [d1, d2, d3]:
            if x.index(source2) > x.index(d2):
                return False
    for source3 in s3:
        if source3 in x and not source3 in [d1, d2, d3]:
            if x.index(source3) > x.index(d3):
                return False
    return True

# Rate at which future turns are discounted (this will need tweaking
dsc_factor = float(1)

def inc_func(x):
    if x<1:
        y = m.exp(x)
    else:
        y = x
    return y

def find_perms(demand_combo):
    demands = [(inv_names[dem[0]], dem[1]) for dem in demand_combo]
    payouts = { inv_names[dem[0]] : dem[2] for dem in demand_combo}

    d1 = demands[0][0]
    d2 = demands[1][0]
    d3 = demands[2][0]

    print d1, d2, d3

    s1 = inv_resources[demands[0][1]]
    s2 = inv_resources[demands[1][1]]
    s3 = inv_resources[demands[2][1]]

    print s1, s2, s3

    sources_list = []
    all_perms = {}
    for source1 in s1:
        for source2 in s2:
            for source3 in s3:
                sources_list.append((source1, source2, source3))
                perms = permutations([source1, source2, source3, d1, d2, d3])
                perm_list = []
                perm_list[:] = list(ifilter(lambda x: good(x, s1, s2, s3, d1, d2, d3), perms))
                all_perms[(source1, source2, source3)] = perm_list
    return sources_list, all_perms, demands, payouts

def perm_cost(board, demands, payouts, start, perm, cash_on_hand, loan_to_repay):
    perm = (start,)+perm

    test_board = b.Board(copy.copy(board.terrain), copy.copy(board.tracks), copy.copy(board.cost_dict), board.adj_list)
    payouts_remaining = copy.copy(payouts)
    delivery = 0
    delivery_num = 0
    total_build_cost = 0
    total_moves = 0
    total_cost_all = 0.
    total_cost_delivery = 0
    for i in range(len(perm)-1):
        build_cost, moves = test_board.ai_a_star(perm[i], perm[i+1], 1)

        total_moves += moves
        total_build_cost += build_cost
        total_cost_delivery += build_cost

        if cash_on_hand < build_cost:
            total_cost_delivery += m.fabs(cash_on_hand-build_cost)
            loan_to_repay += 2*m.fabs(cash_on_hand-build_cost)
            cash_on_hand = 0
        else:
            cash_on_hand -= build_cost

        if perm[i+1] in payouts_remaining and \
            any(visited in inv_resources[[dem for dem in demands if dem[0] == perm[i+1]][0][1]] for visited in perm[0:i+1]): # means a source has been visited
            delivery_num = 3 - len(payouts_remaining)
            # Pop forces dictionary to remove payments that have been issues
            payout = payouts_remaining.pop(perm[i+1])
            # Accumulates payouts made minus the cost to make the delivery, discounted by deliveries made so far
            delivery += (payout-total_cost_delivery)*dsc_factor**delivery_num
            if loan_to_repay > 0:
                if loan_to_repay > payout:
                    loan_to_repay -= payout
                    # cash_on_hand still 0
                else:
                    cash_on_hand = payout - loan_to_repay
                    loan_to_repay = 0
            else:
                cash_on_hand += payout
            # Reset build cost for discount calculation
            total_cost_all += total_cost_delivery
            total_cost_delivery = 0
    # Need to use an increasing function that is approximately f(x) = x for large numbers, exp(x) for negative
    return delivery, total_cost_all, total_moves
    #print perm, ai_payout_sources
    # Deletes the notional board b2 so the name can be reused for testing each other possible permutations
    #print perm, ai_payout[perm], total_moves, total_build_cost, total_cost_all

#### NOTE: Move, THEN build. Need to factor this into the model
#### If first turn, plan two builds

b1 = b.Board({},{},{},{},terr_matrix)
iter = 0.
#total_perms = float(len(all_perms))
ai_payout = {}
cash_on_hand = 50
loan_to_repay = 0
#all_demands = [(('Mangalore', 'Goats', 36), ('Colombo', 'Textiles', 28), ('Ahmadabad', 'Coal', 17))]
all_demands = [(("Delhi", "Machinery", 20),("Calcutta", "Textiles", 13), ("Jamshedpur", "Millet", 20))]
for demand_combo in all_demands:
    print demand_combo
    sources_list, all_perms, demands, payouts = find_perms(demand_combo)
    for source in sources_list:
        print source
        for possible_start in all_starts:
            print possible_start
            for perm in all_perms[source]:
                delivery, total_cost_all, total_moves = perm_cost(b1, demands, payouts, possible_start, perm, cash_on_hand, loan_to_repay)
                ai_payout[(demand_combo, source, possible_start, perm)] = inc_func(delivery)/(total_moves/12.)

# with open('ai_payout_test.pickle', 'wb') as handle:
#    pickle.dump(ai_payout, handle)

print "total time", time.time()-start_time

# best_perm = {}
# for possible_start in start:
#     for sources in sources_list:
#         best_perm[sources] = max(ai_payout[possible_start][sources], key = ai_payout[possible_start][sources].get)

# total_build_cost = 0
# payouts_remaining = copy.copy(payouts)
# cash_on_hand = 40
# total_moves = 0

#best_perm = ((9, 2), (1, 8), (4, 16), (5, 28), (5, 28), (9, 6), (1, 23))
# for possible_start in start:
#     for sources in sources_list:
#         print "\n", best_perm[sources], ai_payout[possible_start][sources][best_perm[sources]]

# for i in range(len(best_perm)-1):
#     build_cost, moves = b1.ai_a_star(best_perm[i],best_perm[i+1],1)


input("Press Enter")