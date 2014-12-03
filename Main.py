# Designed to be a framework for an AI for India Rails

# Basic move metric: ( payoff - cost ) / (moves)
# Payoff: the amount listed on the card
# Cost: cost of the least expensive legal rail line connecting the two cities
#	Calculating cost:
#		
# (Question: how much is it worth it to connect extra cities?)
#
# Moves: the number of moves to from the current location to complete "all considered deliveries"
# (Question: how would this be calculated for two separate deliveries?
#		Answer: Plan a list of construction to connect the cities in each delivery
#				Plan the shortest moves to accomplish the "most economical path" with that construction
# 
