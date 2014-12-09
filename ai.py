from itertools import permutations, ifilter
from globals import *
import pygame as pg, operator as op, numpy as np, math as m, time, random as r, copy
import board as b
import display as d
# Returns true if any of the conditions are broken

pg.init()

start_time = time.time()

f = open('game_board.txt', 'r')

terr_matrix = [line.replace('\n', '').split(' ') for line in f]

start = (9,2) #(int(r.random()*10), int(r.random()*30))

# hex_names = {start: "START",
#              (3, 2): "Abbot",
#              (9, 6): "Baker",
#              (5, 28): "Camino",
#              (1, 8): "Dawson",
#              (4, 16): "Emmen",
#              (1, 23): "Flint" }
#
# resources = {(3, 2): ["Coffee"],
#             (9, 6): ["Bauxite", "Corn"],
#             (5, 28): ["Bauxite"],
#             (1, 8): ["Copper"],
#             (4, 16): ["Corn"],
#             (1, 23): ["Cotton"] }

inv_resources = {}
for coord, rsc_list in resources.iteritems():
    for rsc in rsc_list:
        inv_resources[rsc] = inv_resources.get(rsc, [])
        inv_resources[rsc].append(coord)
#
# demands = {(3, 2): "Corn", # to Abbot (from Emmen)
#             (5, 28): "Copper", # to Camino (from Dawson)
#             (1, 23): "Bauxite" } #to Flint (from Camino) (OR BAKER?????)
inv_demands = {}
for coord, rsc in demands.iteritems():
    inv_demands[rsc] = inv_demands.get(rsc, [])
    inv_demands[rsc].append(coord)

##### IMPORTANT: Make sure payout keys are the same as demand keys, or it will not calculate final costs correctly

payouts = {(3, 2): 20,
            (5, 28): 37,
            (1, 23): 16 }

# Returns list of indices that have a resource
# [i for i, j in enumerate(resources.values()) if 'a' in j]

# d1...d3 are the locations from the demands dictionary
d1 = demands.keys()[0]
d2 = demands.keys()[1]
d3 = demands.keys()[2]

s1 = inv_resources[demands[d1]]
s2 = inv_resources[demands[d2]]
s3 = inv_resources[demands[d3]]

#print s1, s2, s3

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

print len(all_perms)
#### NOTE: Move, THEN build. Need to factor this into the model
#### If first_turn, plan two builds

for perm in all_perms:
    b2 = copy.deepcopy(b1)
    delivery = 0
    delivery_num = 0
    payouts_remaining = copy.copy(payouts)
    total_build_cost = 0
    total_moves = 0
    cash_on_hand = 33
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
    #print perm, ai_payout[perm], total_moves, total_build_cost, total_cost_all
    del b2

best_perm = max(ai_payout, key = ai_payout.get)

# total_build_cost = 0
# payouts_remaining = copy.copy(payouts)
# cash_on_hand = 40
# total_moves = 0

#best_perm = ((9, 2), (1, 8), (4, 16), (5, 28), (5, 28), (9, 6), (1, 23))

print "optimal\n", best_perm, ai_payout[best_perm]


delivery = 0
delivery_num = 0
payouts_remaining = copy.copy(payouts)
total_build_cost = 0
total_moves = 0

# 3.085  a_star
# 0.493 heuristic
# 0.487 conv_to_cube
# 0.737 hex_distance
# 1.036 valid
# 5.105 cost
#### 4.038 adj (unnecessary checking...no need if cost is always invoked from a_star which uses adjacent vertices anyway
# 1.116 (lambda???) (could possibly be a list comprehension or something?)
# 1.810 adj_list
# 1.429 dict:get // reduce some simple dictionaries to lists
# 5.951 map
# 5.446 deep_copy
# 2.537 deepcopy:dict
# 1.011 deepcopy:tuple
# 0.896 copy:reconstruct



for i in range(len(best_perm)-1):
    build_cost, moves = b1.ai_a_star(best_perm[i],best_perm[i+1],1)

    # total_moves += moves
    # total_build_cost += build_cost
    # build_cost_so_far += build_cost
    # if best_perm[i+1] in payouts_remaining:
    #     # pop forces dictionary to remove payments that have been issues
    #     delivery_num = 3 - len(payouts_remaining)
    #     delivery += (payouts_remaining.pop(best_perm[i+1])-build_cost_so_far)*(dsc_factor)**delivery_num
    #     build_cost_so_far = 0
    #ai_payout[perm] += (money_earned-build_cost)*(dsc_factor)**(total_moved/12.)
    #print build_cost_so_far
# Deletes the notional board b2 so the name can be reused for testing each other possible permutations
#print delivery/total_moves, total_build_cost, total_moves
#print perm, "payout", ai_payout[perm], "total moved", total_moved, "build cost", total_build_cost

#print "ai payout", ai_payout[best_perm], "total build cost", total_build_cost, "total moves", total_moves

d.display(b1)

print "total time", time.time()-start_time

input("Press Enter")