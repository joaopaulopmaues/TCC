import tensorflow as tf
import numpy as np
import pandas as pd
import os
from sklearn.model_selection import train_test_split

# Função para carregar e preprocessar os arquivos CSV
def carregar_csv(caminho_arquivo):
    df = pd.read_csv(caminho_arquivo, header=None)
    matriz = df.to_numpy(dtype=np.float32)
    matriz = np.expand_dims(matriz, axis=-1)  # Adiciona a dimensão do canal
    return matriz

def prepare_input(caminhos_pastas): # caminhos_pastas is the folder for 

    # Carrega matrizes e rótulos
    matrizes, labels, arquivos = [], [], []
    for caminho_pasta, rotulo in caminhos_pastas.items():
        arquivos_csv = [os.path.join(caminho_pasta, arquivo) for arquivo in os.listdir(caminho_pasta) if (arquivo.endswith(".csv"))]
        for arquivo in arquivos_csv:
            matrizes.append(carregar_csv(arquivo))
            labels.append(rotulo)
            arquivos.append(arquivo)

    # Divide os dados em treino e teste
    matrizes_train, matrizes_test, labels_train, labels_test, arquivos_train, arquivos_test = train_test_split(
        matrizes, labels, arquivos, test_size=0.1, random_state=42, stratify=labels
    )

    # Converte os conjuntos de treino e teste para tensores
    entradas_train = tf.convert_to_tensor(np.array(matrizes_train), dtype=tf.float32)
    labels_train = tf.convert_to_tensor(np.array(labels_train), dtype=tf.int32)
    entradas_test = tf.convert_to_tensor(np.array(matrizes_test), dtype=tf.float32)
    labels_test = tf.convert_to_tensor(np.array(labels_test), dtype=tf.int32)
    return entradas_train, labels_train, entradas_test, labels_test