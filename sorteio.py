import random
from pprint import pprint

nomes = ['Amauri', 'Ana', 'Léo', 'Fernanda', 'Sueli', 'Dudu', 'Jefferson', 'Ilza', 'Marcia', 'Vitalina']
sorteio = nomes[:]
# sorteio = ['Amauri', 'Ana', 'Léo', 'Fernanda', 'Sueli', 'Dudu', 'Jefferson', 'Ilza', 'Marcia', 'Vitalina']
combinados = {}

for nome in nomes:
    if nome in sorteio:
        sorteio.remove(nome)
    sorteado = random.choice(sorteio)
    combinados[nome] = sorteado
    sorteio.remove(sorteado)
    if not nome in combinados.values():
        sorteio.append(nome)
    if sorteio == []:
        break

if len(set(combinados.keys())) == len(set(combinados.values())) == len(set(combinados.items())):
    pprint(combinados)
    print("Sorteio realizado com sucesso!")