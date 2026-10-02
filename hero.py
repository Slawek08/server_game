import json

class Hero:
    def __init__(self, name: str, attack: int):
        self.name = name
        self.attack = attack
        self.health = 1000
        self.dodge = 100 - self.attack
    
    def to_json(self):
        hero_dict = self.__dict__
        text_json = json.dumps(hero_dict)
        return text_json

    @staticmethod
    def from_json(text_json):
        data_dict = json.loads(text_json)
        new_hero = Hero(name=data_dict["name"], attack=data_dict["attack"])

        new_hero.health = data_dict["health"]
        new_hero.dodge = data_dict["dodge"]

        return new_hero


# hero = Hero("Frodo", 20)
# hero_json = hero.to_json()
# print(f"Hero JSON {hero_json}")
# hero_text = Hero.from_json(hero_json)
# print(f"Python object: * name {hero_text.name}, * attack {hero_text.attack}")
