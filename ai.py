from itertools import permutations, ifilter
from globals import *
import pygame as pg, operator as op, numpy as np, math as m, time, random as r, copy
import board as b
import display as d
# Returns true if any of the conditions are broken

pg.init()

start_time = time.time()

f = open('india_rails_gameboard.txt', 'r')

terr_matrix = [line.replace('\n', '').split(' ') for line in f]

inv_names = {name: coord for coord, name in hex_names.items()}
resources = {}

for name, rsc_list in resources_by_name.iteritems():
    coord = inv_names[name]
    resources[coord] = rsc_list

start = inv_names["Calcutta"]

inv_resources = {}
for coord, rsc_list in resources.iteritems():
    for rsc in rsc_list:
        inv_resources[rsc] = inv_resources.get(rsc, [])
        inv_resources[rsc].append(coord)

##### IMPORTANT: Make sure payout keys are the same as demand keys, or it will not calculate final costs correctly

demand_cards = [
            ("Delhi",       "Machinery",     20),
            ("Calcutta",    "Textiles",      13),
            ("Jamshedpur",  "Millet",        20)]

# ((26, 45), (20, 40), (13, 25), (16, 27), (20, 36), (26, 45), (25, 40)) 0.00318532850239 69 57 57.0

#demands = {loc: needed}
demands = {inv_names[dem[0]] : dem[1] for dem in demand_cards}
payouts = {inv_names[dem[0]] : dem[2] for dem in demand_cards}

inv_demands = {}
for coord, rsc in demands.iteritems():
    inv_demands[rsc] = inv_demands.get(rsc, [])
    inv_demands[rsc].append(coord)

# Returns list of indices that have a resource
# [i for i, j in enumerate(resources.values()) if 'a' in j]

# d1...d3 are the locations from the demands dictionary
d1 = demands.keys()[0]
d2 = demands.keys()[1]
d3 = demands.keys()[2]

s1 = inv_resources[demands[d1]]
s2 = inv_resources[demands[d2]]
s3 = inv_resources[demands[d3]]

print d1, d2, d3
print s1, s2, s3

b1 = b.Board(terr_matrix,hex_names)
b2 = copy.deepcopy(b1)

def good(x):
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

    # PROBLEM: If there is a good required from s1, and a demand for another good at s1, how to treat this:
    # include both:
    #   --in good() function, set parameters so that there is no constraint regarding order
    #   --in algorithm, check if source has been visited (list of sources indexed with items)
# def good(x):
#     return x.index(s1[0]) < x.index(d1) and \
#            x.index(s2[0]) < x.index(d2) and \
#            x.index(s3[0]) < x.index(d3)

ai_payout = {}

# Rate at which future turns are discounted (this will need tweaking
dsc_factor = float(1)

def inc_func(x):
    if x<1:
        y = m.exp(x)
    else:
        y = x
    return y

all_perms = []
for source1 in s1:
    for source2 in s2:
        for source3 in s3:
            perms = permutations([source1, source2, source3, d1, d2, d3])
            perm_list = []
            perm_list[:] = list(ifilter(good, perms))
            all_perms.extend(perm_list)

# cities = [s1[0], s2[0], s3[0], d1, d2, d3]
# perms = permutations(cities)
# all_perms = []
# all_perms[:] = list(ifilter(good, perms))

#### NOTE: Move, THEN build. Need to factor this into the model
#### If first_turn, plan two builds

iter = 0.
total_perms = float(len(all_perms))
print total_perms
for perm in all_perms:
    b2 = copy.deepcopy(b1)
    delivery = 0
    delivery_num = 0
    payouts_remaining = copy.copy(payouts)
    total_build_cost = 0
    total_moves = 0
    cash_on_hand = 50
    loan_to_repay = 0
    total_cost_all = 0.
    total_cost_delivery = 0
    # Adds the start node to the tuple before running calculations
    #lperm = list(perm)
    #lperm.insert(0,start)
    perm = (start,)+perm
    ai_payout[perm] = 0
    for i in range(len(perm)-1):
        build_cost, moves = b2.ai_a_star(perm[i],perm[i+1],1)

        total_moves += moves
        total_build_cost += build_cost
        total_cost_delivery += build_cost

        if cash_on_hand < build_cost:
            #print "\t", perm[i+1], i+1, cash_on_hand, build_cost, total_cost_all
            total_cost_delivery += m.fabs(cash_on_hand-build_cost)
            loan_to_repay += 2*m.fabs(cash_on_hand-build_cost)
            cash_on_hand = 0
        else:
            cash_on_hand -= build_cost

        if perm[i+1] in payouts_remaining and \
            any(visited in inv_resources[demands[perm[i+1]]] for visited in perm[0:i+1]): # means a source has been visited
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
    ai_payout[perm] = inc_func(delivery)/(total_moves/12.)
    # Deletes the notional board b2 so the name can be reused for testing each other possible permutations
    print perm, ai_payout[perm], total_moves, total_build_cost, total_cost_all
    iter += 1
    print iter/total_perms
    del b2



best_perm = max(ai_payout, key = ai_payout.get)

# total_build_cost = 0
# payouts_remaining = copy.copy(payouts)
# cash_on_hand = 40
# total_moves = 0

#best_perm = ((9, 2), (1, 8), (4, 16), (5, 28), (5, 28), (9, 6), (1, 23))

print "optimal\n", best_perm, ai_payout[best_perm]

print b1.cost(inv_names["Patna"], (21, 39), 1)

for i in range(len(best_perm)-1):
    build_cost, moves = b1.ai_a_star(best_perm[i],best_perm[i+1],1)
d.display(b1)

print "total time", time.time()-start_time

input("Press Enter")