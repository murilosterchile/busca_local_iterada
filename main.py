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
        num_equipamentos = int(linha1[1])

        equipamentos = []
        for _ in range(num_equipamentos):
            custo, poder = map(float, arquivo.readline().strip().split())
            equipamentos.append((custo, poder))

        #matriz de sinergia com valores na diagonal superior direita iguais a 0.0
        matriz_sinergia = []
        for i in range(num_equipamentos):
            valores = list(map(float, arquivo.readline().strip().split()))
            linha_matriz = [0.0] * num_equipamentos
            for j in range(i):
                if j < len(valores):
                    linha_matriz[j] = valores[j]
            matriz_sinergia.append(linha_matriz)

    return orcamento, equipamentos, matriz_sinergia

# solução inicial valida aleatoria
def solucao_inicial(orcamento,equipamentos,sinergias):
    custo = 0
    lista_equipamentos = []
    id_equipamentos = []
    n = len(equipamentos)

    # escolhe um equipamento aleatoriamente enquanto o orcamento não for atingido e adiciona a solução inicial
    while orcamento > custo:
        i = random.choice(range(n))

        if i not in id_equipamentos:
            id_equipamentos.append(i)
            custo += equipamentos[i][0]
            lista_equipamentos.append(equipamentos[i])

    return lista_equipamentos, id_equipamentos


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

    # faz a busca enquanto não atingir o otimo local
    while melhorou:
        melhorou = False
        random.shuffle(vizinhos)

        if not vizinhos:
            break

        # escolhe aleatoriamente um indice da solução atual para testar
        i = random.choice(indices_para_testar)

        # testa todos os vizinhos do i e verifica se algum melhora a solução, retorna uma nova solução atualizada caso seja verdade
        for j in vizinhos:

            novo_custo = 0

            for x in indices_otimo_local:
                if x != i:
                    novo_custo += equipamentos[x][0]

            novo_custo += equipamentos[j][0]

            # verifica se o custo esta dentro do orcamento
            if novo_custo <= orcamento:
                novos_indices = indices_otimo_local.copy()
                novos_indices[novos_indices.index(i)] = j
                novo_poder = atualiza_poder_sinergias(poder_otimo_local, equipamentos, sinergias, indices_otimo_local,
                                                      novos_indices, i, j)

                # verifica se a nova solucao é melhor que a atual, caso seja, atualiza a solucao atual
                if novo_poder > poder_otimo_local:
                    otimo_local = [equipamentos[x] for x in novos_indices]
                    indices_otimo_local = novos_indices
                    poder_otimo_local = novo_poder
                    indices_para_testar = indices_otimo_local.copy()
                    melhorou = True
                    vizinhos = list(set(range(len(equipamentos))) - set(indices_otimo_local))
                    break

    return poder_otimo_local, otimo_local, indices_otimo_local, vizinhos


# perturbacao nos indices atuais da busca local
# fator deve ser um valor entre 0 e 1, onde 0 é nenhuma perturbacao e 1 é a maior perturbacao possivel
def perturbacao(indices_atuais, vizinhos, fator):
    numero_trocas = fator*(len(indices_atuais))
    numero_trocas = math.ceil(numero_trocas)

    vizinhos_disponiveis = vizinhos.copy()
    random.shuffle(vizinhos_disponiveis)

    novos_indices = indices_atuais.copy()

    # escolhe as posicoes da solucao atual para trocar
    posicoes_para_trocar = random.sample(range(len(indices_atuais)), numero_trocas)

    # troca as posicoes escolhidas com os vizinhos disponiveis escolhidos aleatoriamente
    for pos in posicoes_para_trocar:
        if vizinhos_disponiveis:

            novo_indice = vizinhos_disponiveis.pop()
            novos_indices[pos] = novo_indice

        else:
            break

    return novos_indices


def busca_local_iterada(equipamentos, sinergias, orcamento, solucao_inicial, indices_iniciais, parada):
    valor_otimo_global = 0
    fator = 0.2
    novos_indices = indices_iniciais.copy()
    nova_solucao = solucao_inicial.copy()
    iteracao = 0

    ia = time.time()
    while True:

        # busca local
        poder_atual, solucao_atual, indices_atuais, vizinhos = busca_local(equipamentos, sinergias, orcamento, nova_solucao, novos_indices)

        # controle para saber se esta caindo no mesmo otimo local
        indices_comparacao = indices_atuais.copy()

        # atualiza os vizinhos para a perturbacao
        vizinhos_atual = vizinhos.copy()

        # controla o otimo global
        if poder_atual > valor_otimo_global:
            valor_otimo_global = poder_atual
            indices_otimo = indices_atuais.copy()
            it = iteracao
            fa = time.time()
            print(f"Tempo ate a busca local {iteracao + 1}: {fa - ia:.2f} segundos")
            print(f"Melhor solução já encontrada: {valor_otimo_global}")
            print(f"indices dos equipamentos da melhor solução já encontrada: {sorted(indices_otimo)}\n")


        # nível de perturbacao adaptativo, se continua no mesmo otimo local, aumenta o fator até sair dele, apos isso volta para o valor inicial
        if indices_comparacao == indices_otimo:
            if fator >=0 and fator < 0.6:
                fator += 0.05
        else:
            fator = 0.2

        # perturbacao na solucao atual
        alteracao = perturbacao(indices_atuais, vizinhos_atual, fator)
        novos_indices = alteracao.copy()
        nova_solucao = [equipamentos[x] for x in novos_indices]

        iteracao += 1

        # criterio de parada
        if iteracao >= parada:
            break


    fb = time.time()

    print("\n"'valor ótimo global:', valor_otimo_global, ', na iteração:', it+1, ', tempo total de excucao:', f'{fb - ia:.2f} segundos')
    print(f"fator perturbacao: {0.2}\n")
    print("\n")


if __name__ == '__main__':
    # receber por linha de comando:
    # sys.argv[1]: caminho do arquivo de entrada
    # sys.argv[2]: valor de critério de parada
    # sys.argv[3]: seed para o random
    # ex: python main.py 05.txt 200 10

    # seed para reproducibilidade
    random.seed(sys.argv[3])

    orcamento, equipamentos, sinergias = ler_arquivo_equipamentos()

    # solucao inicial
    sol_inicial, indices_inicial = solucao_inicial(orcamento, equipamentos, sinergias)

    print(f'\nindices dos equipamentos da solução incial: {sorted(indices_inicial)} \npoder solucao incial: {soma_poder_sinergias(sol_inicial, sinergias, indices_inicial)}\n')

    # busca local iterada
    busca_local_iterada(equipamentos, sinergias, orcamento, sol_inicial, indices_inicial, int(sys.argv[2]))
