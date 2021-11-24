from roulette import Weapon_Type
from roulette import RandomCore


shotguns = Weapon_Type("shotguns")
rifles = Weapon_Type("rifles")
pistols = Weapon_Type("pistols")
misc = Weapon_Type("misc")
major = RandomCore()

class Interface():
    
    primary_gun = "unknown"
    secondary_gun = "unknown"

    def __init__(self):
        self.greet_and_help()
        
    def greet_and_help(self, *dump):
        #dump is just to collect anything this function may get and ignore it
        print("Hunt Loadout Manager 0.1 приветствует тебя, охотник!")
        print("Программа работает в цикле. Команды вводятся кодом, например HQP или HQ или H")
        print("Известные коды (регистр и порядок не важны):")
        print("H - предложить экипировку")
        print("Q - экипировка для квартермейстера(большой и средний слот)")
        print("P - вывести суммарную цену покупки 2 стоволов")
        print("Отдельные команды:")
        print("С1 - поменять основной слот")
        print("С2 - поменять второй слот")
        print("Help - вывести эту информацию")
        print("Удачной охоты!")

    


    def cycle(self):
        """Loop interface function

                
        """
        command = ""
    
        while command != "exit":
            reroll_commands = {"c1": "primary", "c2": "secondary"}
            command = (input(">>").lower()) #print a command prompt and lowercase an input
            # command, quart, show_price, unknown_command = self.decypher(command_raw)
            if command == "exit":
                break
            elif command == "help":
                self.greet_and_help()
            elif command in reroll_commands.keys():                
                data = major.reroll(reroll_commands[command])
                # print("Rerolled: ", reroll_commands[command], ", new ")
                print("Rerolled, new %s is %s" % (reroll_commands[command], data[reroll_commands[command]+"_gun"]))
            elif "h" in command:
                quart = "q" in command
                show_price = "p" in command
                data =  major.create_loadout(quart)  #hardcoded class? looks shitty
                self.primary_gun, self.secondary_gun, total_price = data["primary_gun"], data["secondary_gun"], data["price"]
                if show_price:
                    # print("Primary: ", self.primary_gun, ". Secondary: ", self.secondary_gun, ". Price: ", total_price)
                    print("Primary: ", self.primary_gun, ". Secondary: ", self.secondary_gun, ". Price: TBD")
                else:
                    print("Primary: ", self.primary_gun, ". Secondary: ", self.secondary_gun, ". ")
            else:
                print("Неизвестная команда. Попробуй другую.")
        

if __name__ == "__main__":
    app = Interface()
    app.cycle()

    


