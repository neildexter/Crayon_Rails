from itertools import permutations, ifilter
from globals import *
import pygame as pg, operator as op, numpy as np, math as m, time, random as rand, copy, pickle
import board as b
import bisect
import collections
import display as d
from beta_bandit import *

def good(x, s1, s2, s3, d1, d2, d3):
    for source1 in s1:
        if source1 in x:
            # index returns the earliest instance in the list, so repeats (source AND dest) are okay
            # If multiple instances of sources and destinations exist, there is never an efficient permutation with S1 D1 S1 D1
            # Therefore, the below code is sufficient to encode the condition
            if not any(x.index(source1) < idx for idx in [i for i, coord in enumerate(x) if coord == d1]):
                return False
    for source2 in s2:
        if source2 in x:
            if not any(x.index(source2) < idx for idx in [i for i, coord in enumerate(x) if coord == d2]):
                return False
    for source3 in s3:
        if source3 in x:
            if not any(x.index(source3) < idx for idx in [i for i, coord in enumerate(x) if coord == d3]):
                return False
    return True

def inc_func(x):
    if x<1:
        y = m.exp(x)
    else:
        y = x
    return y

def find_perms(demand_combo):
    demands = [(inv_names[dem[0]], dem[1]) for dem in demand_combo]

    # for name, rsc, payout in demand_combo:
    #     coord = inv_names[name]
    #     payouts[coord] = payouts.get(coord, [])
    #     payouts[coord].append(payout)

    d1 = demands[0][0]
    d2 = demands[1][0]
    d3 = demands[2][0]

    s1 = inv_resources[demands[0][1]]
    s2 = inv_resources[demands[1][1]]
    s3 = inv_resources[demands[2][1]]

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
    return sources_list, all_perms, demands

def perm_cost(board, source_combo, payouts, start, perm, cash, loan):
    perm = (start,)+perm

    test_board = b.Board(copy.copy(board.terrain), copy.copy(board.tracks), copy.copy(board.cost_dict), board.adj_list)
    payouts_remaining = copy.copy(payouts)
    delivery = 0
    delivery_num = 0
    total_build_cost = 0
    total_moves = 0
    total_cost_all = 0.
    total_cost_delivery = 0

    dsc_factor = float(.95)

    for i in range(len(perm)-1):
        build_cost, moves = test_board.ai_a_star(perm[i], perm[i+1], 1)

        total_moves += moves
        total_build_cost += build_cost
        total_cost_delivery += build_cost

        if cash < build_cost:
            total_cost_delivery += m.fabs(cash-build_cost)
            loan += 2*m.fabs(cash-build_cost)
            cash = 0
        else:
            cash -= build_cost

        for src in source_combo:
            if src in perm[0:i+1] and (perm[i+1], src) in payouts_remaining: #and \
                delivery_num = 3 - len(payouts_remaining)
                # Pop forces dictionary to remove payments that have been issues
                payout = payouts_remaining.pop((perm[i+1], src))
                # Accumulates payouts made minus the cost to make the delivery, discounted by deliveries made so far
                delivery += (payout-total_cost_delivery)*dsc_factor**delivery_num
                if loan > 0:
                    if loan > payout:
                        loan -= payout
                        # cash still 0
                    else:
                        cash = payout - loan
                        loan = 0
                else:
                    cash += payout
                # Reset build cost for discount calculation
                total_cost_all += total_cost_delivery
                total_cost_delivery = 0
    # Need to use an increasing function that is approximately f(x) = x for large numbers, exp(x) for negative
    return delivery, total_cost_all, total_moves

def plan(current_board, current_loc, all_demands, cash, loan, first_turn = True):
    all_starts = [inv_names["Calcutta"], inv_names['Bombay'], inv_names['Madras'], inv_names['Delhi'], inv_names['Karachi']]

    if first_turn == True:
        possible_starts = all_starts
    else:
        possible_starts = [current_loc]

    ai_payout = {}
    costs_dict = {}
    moves_dict = {}
    deliveries_dict = {}
    perms_dict = {}
    payouts = {}

    for demand_combo in all_demands:
        sources_list, all_perms, demands = find_perms(demand_combo)
        for source_combo in sources_list:
            payouts[(demand_combo, source_combo)] = {(inv_names[dem[0]], src) : dem[2] for dem in demand_combo for src in source_combo if dem[1] in resources[src]}
            for start in possible_starts:
                perms_dict[(demand_combo, source_combo, start)] = all_perms[source_combo]

    N = 2700
    bb = BetaBandit(perms_dict.keys())

    for i in range(N):
        # Get a recommendation via Bayesian Bandits
        choice = bb.get_recommendation()

        #Convert the choice into a demand, sources, and start
        demand_combo = choice[0]
        source_combo = choice[1]
        chosen_start = choice[2]

        # Figures out which list of permutations to work with
        perms_list = perms_dict[choice]
        new_ai_payout = 0
        delivery = -100

        if len(perms_list) > 0:
            # Remove the permutation being tested (so it is not calculated twice)
            perm = perms_list.pop()

            delivery, total_cost_all, total_moves = perm_cost(current_board, source_combo, payouts[(demand_combo, source_combo)], chosen_start, perm, cash, loan)
            new_ai_payout = inc_func(delivery)/(total_moves/12.)

            ai_payout[choice+(perm,)] = new_ai_payout
            deliveries_dict[choice+(perm,)] = delivery
            costs_dict[choice+(perm,)] = total_cost_all
            moves_dict[choice+(perm,)] = total_moves

            bb.set_results(choice, delivery)
        print i, new_ai_payout, delivery, choice
    best_perm = max(ai_payout.iteritems(), key = op.itemgetter(1))[0]
    print ai_payout[best_perm], best_perm
    return best_perm

def first_turn(current_board, all_demands, cash, loan):
    #current_plan = plan(current_board, [], all_demands, cash, loan, True)

    current_plan = ((('Mangalore', 'Goats', 36), ('Rawalpindi', 'Mica', 18), ('Mangalore', 'Oil', 45)), ((6, 20), (18, 18), (1, 17)), (13, 25), ((18, 18), (6, 20), (1, 17), (1, 17), (47, 21), (47, 21)))

    starting_loc = current_plan[2]
    build_plan = list((starting_loc,) + current_plan[3])
    source_plan = current_plan[1]
    move_plan = copy.copy(build_plan)
    demand_plan = current_plan[0]

    #Build first 40 million (okay, other players might get in the way, but for now let's ignore that)

    #next_dest = build_plan[0] #Set the first place to go to as the first item to build to
    build_cost, build_plan = make_build(current_board, 1, build_plan, 20)
    cash, loan = update_cash(cash, loan, build_cost, 0)

    #==========
    # Other people's first turns would go here...
    #==========

    build_cost, build_plan = make_build(current_board, 1, build_plan, 20)
    cash, loan = update_cash(cash, loan, build_cost, 0)

    return move_plan, build_plan, demand_plan, source_plan, cash, loan

def update_cash(cash, loan, cost, payout):
    if cost != 0:
        if cash > cost:
            cash -= cost
        else:
            cash = 0
            loan += 2*m.fabs(cost)
    if payout != 0:
        if loan > payout:
            loan -= payout

        elif cash == 0:
            cash = payout - loan
            loan = 0
        else:
            cash += payout
    if loan > 40:
        print "#####ERROR! Cannot borrow more than 20M rupees"
        print cash, loan
    if loan > 0:
        print "WARNING! Loan to repay of", loan
    return cash, loan

def make_build(current_board, player_num, build_plan, spending_limit = 20):
    print "Current build plan", build_plan
    build_cost = 0
    if len(build_plan) > 1:
        done = False
        built_to = build_plan.pop(0)
        while (not len(build_plan) == 0) and (not done):
            came_from, cost_so_far, move_cost = current_board.a_star(built_to, build_plan[0], player_num)
            path = current_board.reconstruct_path(came_from, built_to, build_plan[0])
            for i in range(len(path) - 1):
                next_move_cost = current_board.cost_dict[path[i], path[i+1]]
                if build_cost + next_move_cost < spending_limit and not done:
                    built_to = path[i+1]
                    if current_board.tracks.get((path[i], path[i+1]), 0) != player_num:
                        print "Rail built:", path[i], path[i+1], next_move_cost, hex_names.get(path[i+1], "")
                    #else:
                        #print "(No build)", path[i], path[i+1], hex_names.get(path[i+1], "")
                    current_board.create_rail(path[i], path[i+1],player_num)
                    build_cost += next_move_cost
                else:
                    done = True
            if not done:
                build_plan.pop(0)
        build_plan = [built_to,] + build_plan
    else:
        print "#####ERROR! No locations to build to in build_plan"
    print "Money unspent:", spending_limit - build_cost
    return build_cost, build_plan

def make_move(current_board, cash, loan, player_num, move_plan, inventory, demand_plan, source_plan, move_limit = 12):
    print "Current move plan", move_plan
    moves_taken = 0
    demand_fulfilled = ()
    if len(move_plan) > 1:
        done = False
        demand_at_loc = {}
        for dem in demand_plan:
            coord = inv_names[dem[0]]
            demand_at_loc[coord] = demand_at_loc.get(coord,[])
            demand_at_loc[coord].append(dem[1])
        items_demanded = [dem[1] for dem in demand_plan]
        payouts = [(inv_names[dem[0]], dem[1], dem[2]) for dem in demand_plan]
        current_loc = move_plan.pop(0)
        while (not len(move_plan) == 0) and (not done):
            came_from, cost_so_far, move_cost = current_board.a_star(current_loc, move_plan[0], player_num)
            path = current_board.reconstruct_path(came_from, current_loc, move_plan[0])
            if cost_so_far[move_plan[0]] > 0:
                print "WARNING! Current path contains unbuilt rail. Cost to go:", cost_so_far[move_plan[0]], "Cash:", cash
            for i in range(len(path) - 1):
                if moves_taken + 1 <= move_limit and not done:
                    if current_board.cost_dict[(path[i],path[i+1])] == 0:
                        current_loc = path[i+1]
                        print current_loc, hex_names.get(current_loc, "")
                        moves_taken += 1
                        if current_loc == move_plan[0] and current_loc in source_plan: #Add all items necessary to fulfill objective (algorithm lists the location twice, so this should only happen once per location?
                            for rsc in resources[current_loc]:
                                num_needed = items_demanded.count(rsc)
                                if num_needed > 0:
                                    for i in range(num_needed):
                                        print rsc, "has been added to inventory"
                                        inventory.append(rsc) #add item to inventory
                                    if len(inventory) > 3:
                                        print "#####ERROR! Inventory too large"
                                        print inventory
                        for rsc in items_demanded:
                            if (rsc in inventory) and (rsc in demand_at_loc.get(current_loc,[])): #and an item demanded is in inventory (check all demands in case more than one is demanded here
                                payout = [pyt[2] for pyt in payouts if pyt[0] == current_loc and pyt[1] == rsc]
                                cash, loan = update_cash(cash, loan, 0, payout[0])
                                inventory.pop(inventory.index(rsc))
                                print rsc, "has been delivered to", hex_names[current_loc], "for", payout[0]
                                print "Cash:", cash, "Loan:", loan

                                demand_fulfilled = (hex_names[current_loc], rsc, payout[0])

                                done = True
                    else:
                        done = True
                        print "#####ERROR! Cannot move along unbuilt rail"
                else:
                    done = True
            if not done:
                move_plan.pop(0)
        move_plan = [current_loc,]+move_plan
    else:
        print "#####ERROR! No moves in current move plan"
    remaining_moves = move_limit - moves_taken
    return remaining_moves, inventory, demand_fulfilled, move_plan, cash, loan


# MAIN FUNCTIONS

pg.init()

demand_cards = [[("Pune", "Millet", 21),
                ("Mangalore", "Goats", 36),
                ("Anuradhapura", "Imports", 10)],

               [("Rawalpindi", "Mica", 18),
                ("Quetta", "Copper", 40),
                ("Colombo", "Textiles", 28)],

               [("Ahmadabad", "Coal", 17),
                ("Darjeeling", "Cotton", 33),
                ("Mangalore", "Oil", 45)] ]

new_demands = [[

all_demands = {}
for d1 in demand_cards[0]:
    for d2 in demand_cards[1]:
        for d3 in demand_cards[2]:
            all_demands[(d1, d2, d3)] = (d1, d2, d3)

f = open('india_rails_gameboard.txt', 'r')
terr_matrix = [line.replace('\n', '').split(' ') for line in f]
f.close()

current_board = b.Board({},{},{},{},terr_matrix)
cash_on_hand = 50
loan_to_repay = 0

ai_num = 1

start_time = time.time()

move_plan, build_plan, demand_plan, source_plan, cash_on_hand, loan_to_repay = first_turn(current_board, all_demands, cash_on_hand, loan_to_repay)

print "Cash after first two builds: ", cash_on_hand

inventory = []

for i in range(10):
    remaining_moves = 12
    done = False
    iter = 0
    while remaining_moves > 0 and not done:
        remaining_moves, inventory, demand_fulfilled, move_plan, cash_on_hand, loan = make_move(current_board, cash_on_hand, loan_to_repay, ai_num, move_plan, inventory, demand_plan, source_plan, remaining_moves)

        if demand_fulfilled != ():
            print "Demand fulfilled:", demand_fulfilled
            for dem_card in demand_cards:
                if demand_fulfilled in dem_card:
                    demand_cards.pop(demand_cards.index(dem_card))
                    demand_cards.append(new_demands.pop(0))
        iter += 1
        if iter > 1:
            done = True

    build_cost, build_plan = make_build(current_board, ai_num, build_plan, cash_on_hand)
    cash_on_hand, loan_to_repay = update_cash(cash_on_hand, loan_to_repay, build_cost, 0)

    print "Build/Move", i
    print "Cash:", cash_on_hand, "Loan:", loan_to_repay

#d.display(current_board)

print "total time", time.time()-start_time

input("Press Enter")