import random
import time
import sys

# função para ler o arquivo de dados
def ler_arquivo_equipamentos():

    # sys.argv[1]: caminho do arquivo de entrada
    with open(sys.argv[1], 'r') as arquivo:
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

#solução inicial valida aleatoria
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

#busca local que escolhe o vizinho usando fist improvement
def busca_local(equipamentos, sinergias, orcamento, solucao_inicial, indices_iniciais):
    otimo_local = solucao_inicial.copy()
    indices_otimo_local = indices_iniciais.copy()
    poder_otimo_local = soma_poder_sinergias(otimo_local, sinergias, indices_otimo_local)
    melhorou = True
    indices_para_testar = indices_otimo_local.copy()
    random.shuffle(indices_para_testar)

    tempo_inicio = time.time()
    while melhorou:
        melhorou = False

        for j in indices_para_testar:
            vizinhos = list(set(range(len(equipamentos))) - set(indices_otimo_local))

            if not vizinhos:
                break

            i = random.choice(vizinhos)
            novo_custo = 0

            for x in indices_otimo_local:
                if x != j:
                    novo_custo += equipamentos[x][0]

            novo_custo += equipamentos[i][0]

            if novo_custo <= orcamento:
                novos_indices = indices_otimo_local.copy()
                novos_indices[novos_indices.index(j)] = i
                novo_poder = soma_poder_sinergias([equipamentos[x] for x in novos_indices], sinergias, novos_indices)

                if novo_poder >= poder_otimo_local:
                    otimo_local = [equipamentos[x] for x in novos_indices]
                    indices_otimo_local = novos_indices
                    poder_otimo_local = novo_poder
                    # tempo decorrido
                    print(f"Tempo de troca: {time.time() - tempo_inicio:.4f} segundos")
                    # novo melhor local
                    print (poder_otimo_local)
                    # visualização_solução()
                    #precisa de uma função, fazer depois que resolver o resto
                    indices_para_testar = indices_otimo_local.copy()
                    random.shuffle(indices_para_testar)
                    melhorou = True
                    break

    tempo_final = time.time()
    return otimo_local, indices_otimo_local, tempo_inicio, tempo_final


if __name__ == '__main__':

    # receber por linha de comando:
    # sys.argv[1]: caminho do arquivo de entrada
    # sys.argv[2]: valor de critério de parada
    # sys.argv[3]: parametro de variação
    orcamento, equipamentos, sinergias = ler_arquivo_equipamentos()

    ia = time.time()
    sol_inicial, indices_inicial = solucao_inicial(orcamento, equipamentos, sinergias)
    fa = time.time()
    print("Solução inicial:", sol_inicial, indices_inicial)
    print("Poder inicial:", soma_poder_sinergias(sol_inicial, sinergias, indices_inicial))
    print(f"Tempo de execução: {fa - ia:.4f} segundos")

    
    sol_final, indices_final, ib, fb = busca_local(equipamentos, sinergias, orcamento, sol_inicial, indices_inicial)
    print("Melhor solução:",  indices_final)
    print("Melhor poder:", soma_poder_sinergias(sol_final, sinergias, indices_final))
    print(f"Tempo de execução: {fb - ib:.4f} segundos")

