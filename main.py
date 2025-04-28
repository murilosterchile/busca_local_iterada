import random
import time
import math

# função para ler o arquivo de dados
def ler_arquivo_equipamentos(nome_arquivo):

    with open(nome_arquivo, 'r') as arquivo:
        linha1 = arquivo.readline().strip().split()
        orcamento = float(linha1[0])
        n = int(linha1[1])

        equipamentos = []
        for _ in range(n):
            custo, poder = map(float, arquivo.readline().strip().split())
            equipamentos.append((custo, poder))

        matriz_sinergia = []
        for i in range(n):
            valores = list(map(float, arquivo.readline().strip().split()))
            linha_matriz = [0.0] * n
            for j in range(i):
                if j < len(valores):
                    linha_matriz[j] = valores[j]
            matriz_sinergia.append(linha_matriz)

    return orcamento, equipamentos, matriz_sinergia

# solução inicial valida aleatoria
def solucao_inicial(orcamento,equipamentos,sinergias):
    custo = 0
    aux = []
    aux2 = []

    while orcamento > custo:
        sin = random.choice(sinergias)
        i = sinergias.index(sin)

        if i not in aux2:
            aux2.append(i)
            custo += equipamentos[i][0]
            aux.append(equipamentos[i])

    return aux,aux2

# soma o poder e sinergia de um conjunto de equipamentos
def soma_poder_sinergias(equipamentos, sinergias, indices):
    poder_total = 0

    for equipamento in equipamentos:
        poder_total += equipamento[1]

    indexes = sorted(indices)

    for i in range(len(indices)):
        for j in range(i):
            x = indexes[i]
            y = indexes[j]
            poder_total += sinergias[x][y]

    return poder_total

# atualiza a soma dos poderes e sinergias sem recalcular tudo
def atualiza_poder_sinergias(poder_atual, equipamentos, sinergias, indices, removido, adicionado):
    poder_atualizado = poder_atual
    poder_atualizado -= equipamentos[removido][1]
    poder_atualizado += equipamentos[adicionado][1]

    for outro in indices:
        if outro != removido:
            poder_atualizado -= sinergias[max(removido, outro)][min(removido, outro)]
            poder_atualizado += sinergias[max(adicionado, outro)][min(adicionado, outro)]

    return poder_atualizado



# busca local que escolhe o vizinho usando fist improvement
def busca_local(equipamentos, sinergias, orcamento, solucao_inicial, indices_iniciais):
    otimo_local = solucao_inicial.copy()
    indices_otimo_local = indices_iniciais.copy()
    poder_otimo_local = soma_poder_sinergias(otimo_local, sinergias, indices_otimo_local)
    melhorou = True
    indices_para_testar = indices_otimo_local.copy()
    vizinhos = list(set(range(len(equipamentos))) - set(indices_otimo_local))

    while melhorou:
        melhorou = False
        random.shuffle(vizinhos)

        if not vizinhos:
            break

        i = random.choice(indices_para_testar)

        for j in vizinhos:

            novo_custo = 0

            for x in indices_otimo_local:
                if x != i:
                    novo_custo += equipamentos[x][0]

            novo_custo += equipamentos[j][0]

            if novo_custo <= orcamento:
                novos_indices = indices_otimo_local.copy()
                novos_indices[novos_indices.index(i)] = j
                novo_poder = atualiza_poder_sinergias(poder_otimo_local, equipamentos, sinergias, indices_otimo_local, i, j)

                if novo_poder >= poder_otimo_local:
                    otimo_local = [equipamentos[x] for x in novos_indices]
                    indices_otimo_local = novos_indices
                    poder_otimo_local = novo_poder
                    indices_para_testar = indices_otimo_local.copy()
                    melhorou = True
                    vizinhos = list(set(range(len(equipamentos))) - set(indices_otimo_local))
                    break



    return otimo_local, indices_otimo_local,vizinhos


# perturbacao nos indices atuais da busca local
# fator deve ser um valor entre 0 e 1, onde 0 é nenhuma perturbacao e 1 é a maior perturbacao possivel
def perturbacao(indices_atuais, vizinhos, fator):
    numero_trocas = fator*(len(indices_atuais))
    numero_trocas = math.ceil(numero_trocas)

    vizinhos_disponiveis = vizinhos.copy()
    random.shuffle(vizinhos_disponiveis)

    novos_indices = indices_atuais.copy()
    posicoes_para_trocar = random.sample(range(len(indices_atuais)), numero_trocas)

    for pos in posicoes_para_trocar:
        if vizinhos_disponiveis:

            novo_indice = vizinhos_disponiveis.pop()
            novos_indices[pos] = novo_indice

        else:
            break

    return novos_indices



if __name__ == '__main__':
    orcamento, equipamentos, sinergias = ler_arquivo_equipamentos('dados.txt')

    ia = time.time()
    sol_inicial, indices_inicial = solucao_inicial(orcamento, equipamentos, sinergias)
    fa = time.time()
    print("Solução inicial:", indices_inicial)
    print("Poder inicial:", soma_poder_sinergias(sol_inicial, sinergias, indices_inicial))
    print(f"Tempo de execução: {fa - ia:.4f} segundos")

    ib = time.time()
    sol_final, indices_final,vizinhos = busca_local(equipamentos, sinergias, orcamento, sol_inicial, indices_inicial)
    fb = time.time()
    print("Melhor solução:",  indices_final)
    print("Melhor poder:", soma_poder_sinergias(sol_final, sinergias, indices_final))
    print(f"Tempo de execução: {fb - ib:.4f} segundos")

