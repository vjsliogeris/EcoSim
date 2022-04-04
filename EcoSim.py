#EcoSim.py
import math
import random
import copy
import numpy as np

#STarting parameters
START_FUNDS = 100000
START_PROD_PRICE = 50
START_QUALITY = 1

#R&D effect parameters
RD_p_max = START_PROD_PRICE
RD_p_min = 10
RD_breakpoint = 50000
RD_effective_width = 25000

#R&D quality effect parameters
RD_quality_scalefactor = 50000

#Consumer parameters
demand_per_player = 12500 #Maybe works dunno lmao
demand_at_free = None
demand = None
max_price_X = 200

def gen_demand_linear(max_price, demand_X):
    output = [0.0]
    max_increase_per_p = (demand_X * 4)/((max_price) * (max_price+1))
    for _ in range(max_price):
        u = random.random() #Could add more parameters here
        element = u*max_increase_per_p + output[0]
        output = [element] + output
    return output

def gen_demand_hyperbolic(max_price, demand_X):
    output = [0.0]
    i = max_price_X
    for _ in range(max_price):
        max_increase = 1/(i**2)
        element = max_increase + output[0]
        output = [element] + output
        i -= 1
    s = 0
    for q in output:
        s += q

    a = demand_X / s
    output = [0.0]
    i = max_price_X
    for _ in range(max_price):
        u = random.random() #Could add more parameters here
        max_increase = a/(i**2)
        element = max_increase * (u + 0.5) + output[0]
        output = [element] + output
        i -= 1
    s = 0
    for q in output:
        s += q

    return np.asarray(output)

def sigma(x):
    return 1/(1 + math.exp(-x))



'''Handles the game happening
'''
class Game:
    def __init__(self, playerlist, max_turns):
        self.finished = False
        self.turn_count = 0
        self.max_turns = max_turns
        self.players = {}
        self.p_ready = {}
        for player, ID in playerlist:
            self.players[ID] = Player(player, ID)
        for player in self.players.values():
            self.p_ready[player.ID] = False
        demand_X = len(playerlist) * demand_per_player
        self.demand = gen_demand_hyperbolic(max_price_X, demand_X)

    
    def print_players(self):
        for player in self.players.values():
            print(player)

    def print_readiness(self):
        for playerID in self.p_ready.keys():
            playername = self.players[playerID].name
            readiness = self.p_ready[playerID]

            print("{0} is ready: {1}".format(playername, readiness))
    
    def get_status_text(self, ID):
        return self.players[ID].get_status()

    def take_action(self, ID, rd, rd_quality, prod, sell_price):
        relevant_player = self.players[ID]
        self.p_ready[ID] = relevant_player.take_action(rd, rd_quality, prod, sell_price)

    def step(self):
        #Check if can step
        can_step = True

        for playerID in self.p_ready.keys():
            readiness = self.p_ready[playerID]
            can_step = can_step and readiness

        if not can_step:
            raise Exception('Not all players ready to step')
        

        #Try to sell stock
        temp_demand = copy.deepcopy(self.demand)

        consider_price = len(temp_demand)-2

        quality_sum = 0
        for player in self.players.values():
            quality_sum += player.quality

        quality_map = {}
        total_stock = 0
        for ID, player in self.players.items():
            quality_map[ID] = player.quality
            total_stock += player.stock


        while temp_demand[0] > 0 and total_stock > 1: #May need work
            u = random.random() * quality_sum
            for ID, quality in quality_map.items():
#                print(u)
#                print(quality_map)
                u -= quality
                if u < 0:
                    winner_ID = ID
                    break
            demand_at_P = temp_demand[consider_price]

            winner_stock = self.players[winner_ID].stock
            
            if winner_stock > demand_at_P:
                total_stock -= demand_at_P
                temp_demand[consider_price] = 0
                consider_price -= 1
                self.players[winner_ID].stock -= demand_at_P
                self.players[winner_ID].funds += demand_at_P * consider_price
            elif winner_stock < demand_at_P:
                total_stock -= self.players[winner_ID].stock
                temp_demand[consider_price] -= self.players[winner_ID].stock
                self.players[winner_ID].funds +=self.players[winner_ID].stock * consider_price
                self.players[winner_ID].stock = 0
                quality_sum -= quality_map[winner_ID]
                del quality_map[winner_ID]
            else:
                total_stock -= demand_at_P
                self.players[winner_ID].funds += self.players[winner_ID].stock* consider_price
                temp_demand[consider_price] = 0
                self.players[winner_ID].stock = 0
                consider_price -= 1
                quality_sum -= quality_map[winner_ID]
                del quality_map[winner_ID]
#            print(self.players[winner_ID].stock)
#            print(quality_map)

            #seems shit
#            print(temp_demand[20:30])
#            print(temp_demand[45:55])
#            print(temp_demand[70:80])
#            print(temp_demand[95:105])
        #print(self.get_status_text(0))
        #print(self.get_status_text(1))
        #print(self.get_status_text(2))
        #Forecasts
        u = np.random.rand(3)
        winners = u > 2/3
        losers = u < 1/3

        slices_poor = math.ceil(max_price_X / 3)
        slices_rich = math.ceil(max_price_X*2 / 3)

        poor_win = (u[0]-0.5)/3
        mid_win = (u[1]-0.5)/3
        rich_win = (u[2]-0.5)/3
        self.demand[:slices_poor] *= 1+poor_win
        self.demand[slices_poor:slices_rich] *= 1+mid_win
        self.demand[slices_rich:] *= 1+rich_win
        report = ""

        if winners[0]:
            report += "The lower class has grown.\n"
        elif losers[0]:
            report += "The lower class has shrunk.\n"
        else:
            report += "The lower class is unaffected.\n"

        if winners[1]:
            report += "The middle class has grown.\n"
        elif losers[1]:
            report += "The middle class has shrunk.\n"
        else:
            report += "The middle class is unaffected.\n"

        if winners[2]:
            report += "The upper class has grown.\n"
        elif losers[2]:
            report += "The upper class has shrunk.\n"
        else:
            report += "The upper class is unaffected.\n"
        self.turn_count += 1
        if self.turn_count == self.max_turns:
            self.finished = True
            max_funds = 0
            max_ID = None
            for player in self.players.values():
                report += "{0} finished the game with {1} in their bank. They had {2} quality and {3} production costs\n".format(player.name, player.funds, player.quality, player.prod_price)
                if player.funds > max_funds:
                    max_ID = player.ID
                    max_funds = player.funds
            winner = self.players[max_ID]
            report += "{0} won with {1} in their account.\n".format(winner.name, winner.funds)

        return report, self.finished
        

    def __str__(self):
        return "tostr"

'''Handles each of the players
'''
class Player:
    def __init__(self, playername, ID):
        print("Initialising player {0} ({1})".format(playername, ID))
        self.name = playername
        self.ID = ID
        self.funds = START_FUNDS
        self.stock = 0
        self.prod_price = START_PROD_PRICE
        self.rd_spent = 0
        self.rd_quality_spent = 0
        self.sell_price = None
        self.quality = START_QUALITY

    def _get_new_price(self):
        scaled_rd_spent = (self.rd_spent - RD_breakpoint) / (RD_effective_width / (2*math.log(2+(3**0.5))))
        new_prodprice = RD_p_max - ((RD_p_max - RD_p_min)*sigma(scaled_rd_spent))
        return new_prodprice
    def _get_new_quality(self):
        new_quality = math.log((self.rd_quality_spent)/RD_quality_scalefactor + 1) + 1
        return new_quality

    def get_status(self):
        output = {}
        output['name'] = self.name
        output['ID'] = self.ID
        output['funds'] = self.funds
        output['stock'] = self.stock
        output['prod_price'] = self.prod_price
        output['quality'] = self.quality
        output['rd_spent'] = self.rd_spent
        output['rd_quality_spent'] = self.rd_quality_spent
        return output


    def take_action(self, rd, rd_quality, prod, sell_price):
        #Check if can afford
        expenses = 0
        expenses += prod * self.prod_price
        expenses += rd
        expenses += rd_quality
        if expenses > self.funds:
            raise Exception('Can\'t afford')
        #Spend money
        self.funds -= expenses
        #Make product
        self.stock += prod
        #Invest in R&D
        self.rd_spent += rd
        self.rd_quality_spent += rd_quality
        
        #Update prod price
        self.prod_price = self._get_new_price()

        #Update quality accor
        self.quality = self._get_new_quality()

        #update sell price
        self.sell_price = sell_price

        return True

    def __str__(self):
        return "Player {0} ({3}) with the cash {1} and current stock {2}".format(self.name, self.funds, self.stock, self.ID)
