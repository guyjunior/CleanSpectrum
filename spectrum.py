from pymsfilereader import MSFileReader
import pandas as pd
import matplotlib.pyplot as plt
import os

# Novos parâmetros de substâncias com nomes e cores associadas
substancias = [
    (4, "FTMS + c ESI Full ms [70.0000-1050.0000]", "PBA POS", 'r'),  # Cor vermelha
    (4, "FTMS + c ESI Full ms [70.0000-1050.0000]", "PBM POS", 'g'),  # Cor verde
    (4, "FTMS + c ESI Full ms [70.0000-1050.0000]", "PMA POS", 'b'),  # Cor azul
    (4, "FTMS + c ESI Full ms [70.0000-1050.0000]", "PMM POS", 'm')   # Cor magenta
]

def obter_dados_e_processar(leitor, scan_Number, scan_filter):
    dados = leitor.GetMassListFromScanNum(
        scanNumber=scan_Number,
        scanFilter=scan_filter
    )
    return pd.DataFrame({'Massa': dados[0][0], 'Intensidade': dados[0][1]})

def processar_arquivo_amostra(nome_arquivo, substancias, dados_br):
    amostra = MSFileReader(nome_arquivo)
    amostra.SetCurrentController('MS', 1)
    amostra.SetMassTolerance(userDefined=True, massTolerance=6.0, units=1)

    for (scan_Number, scan_filter, nome_substancia, cor) in substancias:
        dados = obter_dados_e_processar(amostra, scan_Number, scan_filter)
        
        # Subtrair a intensidade da amostra de limpeza (BR.raw)
        dados['Intensidade'] = dados['Intensidade'] - dados_br['Intensidade'].reindex(dados.index, fill_value=0)

        # Filtrar os dados com Intensidade acima de 20
        dados_filtrados = dados[dados['Intensidade'] > 20]

        # Plotar o cromatograma com stem (pico a pico) usando cor específica
        markerline, stemlines, baseline = plt.stem(
            dados_filtrados['Massa'], 
            dados_filtrados['Intensidade'], 
            label=f"{nome_substancia} ({os.path.basename(nome_arquivo)})",
            basefmt=" ",  # Remove a linha horizontal
            linefmt=cor,
            markerfmt=f'{cor}o'
        )
        
        # Customizar as cores dos elementos
        plt.setp(markerline, color=cor)
        plt.setp(stemlines, color=cor)

        # Adicionar o tempo de retenção (Massa) em todos os picos com intensidade acima de 20
        for idx, row in dados_filtrados.iterrows():
            plt.text(row['Massa'], row['Intensidade'], f"{row['Massa']:.2f}", 
                     fontsize=8, ha='center', va='bottom', color=cor)

# Carregar a amostra de limpeza (BR.raw)
def carregar_amostra_limpeza(caminho_amostra_br, scan_Number, scan_filter):
    amostra_br = MSFileReader(caminho_amostra_br)
    amostra_br.SetCurrentController('MS', 1)
    amostra_br.SetMassTolerance(userDefined=True, massTolerance=6.0, units=1)
    return obter_dados_e_processar(amostra_br, scan_Number, scan_filter)

# Caminho das amostras
caminho_amostras = r"C:\Users\guyjunior\Desktop\Sample\Monica"
caminho_amostra_br = r"C:\Users\guyjunior\Desktop\Sample\Monica\br\BR.raw"

# Carregar dados da amostra de limpeza (BR.raw)
scan_Number_br = 4
scan_filter_br = "FTMS + c ESI Full ms [70.0000-1050.0000]"
dados_br = carregar_amostra_limpeza(caminho_amostra_br, scan_Number_br, scan_filter_br)

# Criar a figura para plotagem antes do loop de arquivos
plt.figure(figsize=(12, 8))

# Processar cada arquivo de amostra e subtrair a amostra de limpeza
for arquivo in os.listdir(caminho_amostras):
    if arquivo.endswith(".raw") and arquivo != "BR.raw":  # Exclui BR.raw da plotagem
        caminho_arquivo = os.path.join(caminho_amostras, arquivo)
        processar_arquivo_amostra(caminho_arquivo, substancias, dados_br)

# Configurações do gráfico após o loop
plt.xlabel('Tempo de Retenção')
plt.ylabel('Intensidade')
plt.title('Detecção de picos - Todas as amostras (com subtração da amostra de limpeza)')
plt.legend(loc='best', fontsize='small')  # Posiciona melhor a legenda e ajusta o tamanho
plt.tight_layout()
plt.show()