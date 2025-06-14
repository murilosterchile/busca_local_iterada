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
def solucao_inicial(orcamento,equipamentos):
    custo = 0
    lista_equipamentos = []
    id_equipamentos = []
    n = len(equipamentos)
    tentativas = 10000
    controle = 0

    # escolhe um equipamento aleatoriamente enquanto o orcamento não for atingido e adiciona a solução inicial e garante que o loop não seja infinito
    while orcamento > custo and controle <= tentativas:
        i = random.choice(range(n))

        #só adiciona o equipamento se ele ainda não foi adicionado e o custo do equipamento é menor ou igual ao orcamento restante
        if i not in id_equipamentos and equipamentos[i][0] <= orcamento - custo:
            id_equipamentos.append(i)
            custo += equipamentos[i][0]
            lista_equipamentos.append(equipamentos[i])

        controle += 1

    return lista_equipamentos, id_equipamentos, custo


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


# atualiza a soma dos poderes e sinergias sem recalcular tudo, apenas as alteracoes dos indices que mudaram
def atualiza_poder_sinergias(poder_atual, equipamentos, sinergias, indices_antes, removido, adicionado):
    poder_atualizado = poder_atual
    poder_atualizado -= equipamentos[removido][1]
    poder_atualizado += equipamentos[adicionado][1]

    for outro in indices_antes:
        if outro != removido:
            poder_atualizado -= sinergias[max(removido, outro)][min(removido, outro)]
        if outro != adicionado:
            poder_atualizado += sinergias[max(adicionado, outro)][min(adicionado, outro)]

    return poder_atualizado


# busca local que escolhe o vizinho usando first improvement
def busca_local(equipamentos, sinergias, orcamento, indices_solucao, custo_atual):
    poder_atual = soma_poder_sinergias([equipamentos[i] for i in indices_solucao], sinergias, indices_solucao)
    melhorou = True
    vizinhos = list(set(range(len(equipamentos))) - set(indices_solucao))

    while melhorou:
        melhorou = False
        random.shuffle(vizinhos)

        if not vizinhos:
            break

        # escolha aleatória de um item da solução atual
        i = random.choice(indices_solucao)

        for j in vizinhos:
            novo_custo = custo_atual - equipamentos[i][0] + equipamentos[j][0]

            if novo_custo <= orcamento and j not in indices_solucao:
                indice_i = indices_solucao.index(i)
                antigo = indices_solucao[indice_i]
                indices_solucao[indice_i] = j

                novo_poder = atualiza_poder_sinergias(poder_atual, equipamentos, sinergias,
                                                      indices_solucao, antigo, j)

                if novo_poder > poder_atual:
                    poder_atual = novo_poder
                    custo_atual = novo_custo
                    vizinhos = list(set(range(len(equipamentos))) - set(indices_solucao))
                    melhorou = True
                    break
                else:
                    # desfaz a alteração
                    indices_solucao[indice_i] = antigo

    return poder_atual, indices_solucao, vizinhos, custo_atual


# perturbacao nos indices atuais da busca local
# fator deve ser um valor entre 0 e 1, onde 0 é nenhuma perturbacao e 1 é a maior perturbacao possivel
def perturbacao(indices_atuais, vizinhos, fator, equipamentos, custo_atual, orcamento):
    numero_trocas = fator * (len(indices_atuais))
    numero_trocas = math.ceil(numero_trocas)

    vizinhos_disponiveis = vizinhos.copy()
    random.shuffle(vizinhos_disponiveis)

    novos_indices = indices_atuais.copy()
    novo_custo = custo_atual

    # escolhe as posicoes da solucao atual para trocar
    posicoes_para_trocar = random.sample(range(len(indices_atuais)), numero_trocas)

    # troca as posicoes escolhidas com os vizinhos disponiveis escolhidos aleatoriamente
    for pos in posicoes_para_trocar:
        if vizinhos_disponiveis:
            # calcula o novo custo incrementalmente
            equip_removido = novos_indices[pos]
            equip_adicionado = vizinhos_disponiveis.pop()

            custo_temporario = novo_custo - equipamentos[equip_removido][0] + equipamentos[equip_adicionado][0]

            if custo_temporario <= orcamento:
                novos_indices[pos] = equip_adicionado
                novo_custo = custo_temporario
            else:
                # se excede o orçamento, nao faz a troca e tenta o proximo vizinho
                continue

    return novos_indices, novo_custo


def busca_local_iterada(equipamentos, sinergias, orcamento, solucao_inicial, indices_iniciais, custo_inicial, parada):
    valor_otimo_global = 0
    fator = 0.2
    indices_atual = indices_iniciais.copy()
    custo_atual = custo_inicial
    iteracao = 0

    ia = time.time()
    while True:

        # busca local
        poder_atual, indices_atual, vizinhos, custo_atual = busca_local(equipamentos, sinergias, orcamento, indices_atual, custo_atual)

        # controle para saber se esta caindo no mesmo otimo local
        indices_comparacao = indices_atual.copy()

        # controla o otimo global
        if poder_atual > valor_otimo_global:
            valor_otimo_global = poder_atual
            indices_otimo = indices_atual.copy()
            it = iteracao
            fa = time.time()
            print(f"Tempo ate a busca local {iteracao + 1}: {fa - ia:.2f} segundos")
            print(f"Melhor solução já encontrada: {valor_otimo_global}")
            print(f"indices dos equipamentos da melhor solução já encontrada: {sorted(indices_otimo)}\n")

        # nível de perturbacao adaptativo, se continua no mesmo otimo local, aumenta o fator até sair dele, apos isso volta para o valor inicial
        if 'indices_otimo' in locals() and indices_comparacao == indices_otimo:
            if fator >= 0 and fator < 0.6:
                fator += 0.05
        else:
            fator = 0.2

        # perturbacao na solucao atual
        indices_atual, custo_atual = perturbacao(indices_atual, vizinhos, fator, equipamentos, custo_atual, orcamento)

        iteracao += 1

        # criterio de parada
        if iteracao >= parada:
            break

    fb = time.time()

    print("\n"'valor ótimo global:', valor_otimo_global, ', na iteração:', it + 1, ', tempo total de excucao:',
          f'{fb - ia:.2f} segundos')
    print(f"fator perturbacao: {0.2}\n")
    print("\n")


if __name__ == '__main__':
    # receber por linha de comando:
    # sys.argv[1]: caminho do arquivo de entrada
    # sys.argv[2]: valor de critério de parada
    # sys.argv[3]: parametro de variação
    # ex: python main.py 05.txt 200 10

    # seed para reproducibilidade
    random.seed(sys.argv[3])

    orcamento, equipamentos, sinergias = ler_arquivo_equipamentos()

    # solucao inicial
    sol_inicial, indices_inicial, custo_inicial = solucao_inicial(orcamento, equipamentos)

    print(
        f'\nindices dos equipamentos da solução incial: {sorted(indices_inicial)} \npoder solucao incial: {soma_poder_sinergias(sol_inicial, sinergias, indices_inicial)}\n')

    # busca local iterada
    busca_local_iterada(equipamentos, sinergias, orcamento, sol_inicial, indices_inicial, custo_inicial, int(sys.argv[2]))
