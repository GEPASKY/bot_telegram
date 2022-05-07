from requests import get


class Pokemon:
    def __init__(self, name):
        self.pokemons = get(f'https://pokeapi.co/api/v2/pokemon/{name}').json()

    def name(self):
        return self.pokemons['name']

    def order(self):
        return self.pokemons['order']

    def abilities(self):
        ab = list()
        for i in range(len(self.pokemons['abilities'])):
            ab.append(self.pokemons['abilities'][i]['ability']['name'])
        return ', '.join(ab)

    def height(self):
        return self.pokemons['height']

    def weight(self):
        return self.pokemons['weight']
