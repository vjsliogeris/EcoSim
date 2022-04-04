import EcoSim

playerlist = [["Alice", 0],["Bob", 1],["Charlie",2]]

game = EcoSim.Game(playerlist)
game.print_players()
game.print_readiness()

game.take_action(0, 50000, 1000, 75) #Balanced, spend all
game.take_action(1, 75000, 500, 75) #Research heavy, spend all
game.take_action(2, 0, 2000, 55) #Quick buck, save

game.print_readiness()
game.print_players()

print(game.get_status_text(0))
print(game.get_status_text(1))
print(game.get_status_text(2))

game.step()
