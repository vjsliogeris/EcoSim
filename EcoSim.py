#EcoSim.py
import math

START_FUNDS = 100000
START_PROD_PRICE = 50

RD_p_max = START_PROD_PRICE
RD_p_min = 10
RD_breakpoint = 500000
RD_effective_width = 100000


def sigma(x):
    return 1/(1 + math.exp(-x))



'''Handles the game happening
'''
class Game:
    def __init__(self, playerlist):
        self.players = {}
        self.p_ready = {}
        for player, ID in playerlist:
            self.players[ID] = Player(player, ID)
        for player in self.players.values():
            self.p_ready[player.ID] = False

    
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

    def take_action(self, ID, rd, prod, sell_price):
        relevant_player = self.players[ID]
        self.p_ready[ID] = relevant_player.take_action(rd, prod, sell_price)

    def step(self):
        can_step = True

        for playerID in self.p_ready.keys():
            readiness = self.p_ready[playerID]
            can_step = can_step and readiness

        if not can_step:
            raise Exception('Not all players ready to step')

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

    def _get_new_price(self):
        scaled_rd_spent = (self.rd_spent - RD_breakpoint) / RD_effective_width
        new_prodprice = RD_p_max - ((RD_p_max - RD_p_min)*sigma(scaled_rd_spent))
        return new_prodprice

    def get_status_text(self):
        print("A")
        raise Exception('')


    def take_action(self, rd, prod, sell_price):
        #Check if can afford
        expenses = 0
        expenses += prod * self.prod_price
        expenses += rd
        if expenses > self.funds:
            raise Exception('Can\'t afford')
        #Spend money
        self.funds -= expenses
        #Make product
        self.stock += prod
        #Invest in R&D
        self.rd_spent += rd
        #Update prod price
        self.prod_price = self._get_new_price()

        return True

    def __str__(self):
        return "Player {0} ({3}) with the cash {1} and current stock {2}".format(self.name, self.funds, self.stock, self.ID)
