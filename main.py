import random
import time
import math
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
def atualiza_poder_sinergias(poder_atual, equipamentos, sinergias, indices_antes, indices_depois, removido, adicionado):
    poder_atualizado = poder_atual
    poder_atualizado -= equipamentos[removido][1]
    poder_atualizado += equipamentos[adicionado][1]

    for outro in indices_antes:
        if outro != removido:
            poder_atualizado -= sinergias[max(removido, outro)][min(removido, outro)]

    for outro in indices_depois:
        if outro != adicionado:
            poder_atualizado += sinergias[max(adicionado, outro)][min(adicionado, outro)]

    return poder_atualizado



# busca local que escolhe o vizinho usando first improvement
def busca_local(equipamentos, sinergias, orcamento, solucao_inicial, indices_iniciais):
    otimo_local = solucao_inicial.copy()
    indices_otimo_local = indices_iniciais.copy()
    poder_otimo_local = soma_poder_sinergias(otimo_local, sinergias, indices_otimo_local)
    melhorou = True
    indices_para_testar = indices_otimo_local.copy()
    vizinhos = list(set(range(len(equipamentos))) - set(indices_otimo_local))

    tempo_inicio = time.time()
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
                novo_poder = atualiza_poder_sinergias(poder_otimo_local, equipamentos, sinergias, indices_otimo_local,novos_indices, i, j)

                if novo_poder > poder_otimo_local:
                    otimo_local = [equipamentos[x] for x in novos_indices]
                    indices_otimo_local = novos_indices
                    poder_otimo_local = novo_poder
                    indices_para_testar = indices_otimo_local.copy()
                    melhorou = True
                    vizinhos = list(set(range(len(equipamentos))) - set(indices_otimo_local))
                    break

    tempo_final = time.time()
    return poder_otimo_local,otimo_local, indices_otimo_local,vizinhos, tempo_inicio, tempo_final


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
    #verificar se precisa atualizar as soluções
    return novos_indices


def busca_local_iterada(equipamentos, sinergias, orcamento, solucao_inicial, indices_iniciais):
    valor_otimo_global = 0
    fator = 0.2
    novos_indices = indices_iniciais.copy()
    nova_solucao = solucao_inicial.copy()
    iteracao = 0

    ia = time.time()
    while True:

        poder_atual, solução_atual, indices_atuais, vizinhos, tempo_inicio, tempo_final = busca_local(equipamentos, sinergias, orcamento, nova_solucao, novos_indices)

        # controle para saber se esta caindo no mesmo otimo local
        indices_comparacao = indices_atuais.copy()

        vizinhos_atual = vizinhos.copy()

        # controla o otimo global
        if poder_atual > valor_otimo_global:
            valor_otimo_global = poder_atual
            indices_otimo = indices_atuais.copy()
            it = iteracao
            fa = time.time()
            print(f"Tempo da busca local {iteracao}: {fa - ia:.2f} segundos")
            print(f"Melhor solução já encontrada: {valor_otimo_global}")

        # nível de perturbacao adaptativo, se continua no mesmo melhor local, aumenta o fator até sair dele, apos isso volta para o valor inicial
        if indices_comparacao == indices_otimo:
            if fator >=0 and fator < 0.8:
                fator += 0.1
        else:
            fator = 0.2


        alteracao = perturbacao(indices_atuais, vizinhos_atual, fator)
        novos_indices = alteracao.copy()
        nova_solucao = [equipamentos[x] for x in novos_indices]

        iteracao += 1
        if iteracao >= 50:
            break

    fb = time.time()

    print('valor ótimo global:', valor_otimo_global, 'com interação:', it, 'tempo total:', f'{fb - ia:.2f}')
    print(indices_otimo)



if __name__ == '__main__':
    # receber por linha de comando:
    # sys.argv[1]: caminho do arquivo de entrada
    # sys.argv[2]: valor de critério de parada
    # sys.argv[3]: parametro de variação
    orcamento, equipamentos, sinergias = ler_arquivo_equipamentos()

    sol_inicial, indices_inicial = solucao_inicial(orcamento, equipamentos, sinergias)

    busca_local_iterada(equipamentos, sinergias, orcamento, sol_inicial, indices_inicial)
