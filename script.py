import os
import subprocess
import sys

criterio_de_parada = sys.argv[1]
variacao = sys.argv[2]

arquivos = [arquivo for arquivo in os.listdir('.') if arquivo.endswith('.txt')]

resultados = []

for arquivo in arquivos:
    caminho_arquivo = arquivo
    comando = ["python", "main.py", caminho_arquivo, criterio_de_parada, variacao]
    
    print(f"Executando: {' '.join(comando)}")
    
    resultado = subprocess.run(comando, capture_output=True, text=True)
    saida = resultado.stdout

    for linha in saida.splitlines():
        if "valor ótimo global:" in linha:
            resultados.append((arquivo, linha.strip()))

print("\nResumo Final:")
for arquivo, resultado in resultados:
    print(f"{arquivo}: {resultado}")
