#Rafael Frade - 19/08/2020
#Lê os arquivos 7z da RAIZ e gera dois arquivos com os campos campos_selecionados
#no arquivo campos_selecionados.config

import py7zr
import os
import pandas as pd
import shutil

#carrega os campos que irão para o arquivo final
def get_campos_selecionados():
    campos_selecionados={}
    with open(path_campos_selecionados, 'r') as f:
        for line in f:
            line = line.rstrip() #removes trailing whitespace and '\n' chars

            if "=" not in line: continue #skips blanks and comments w/o =
            if line.startswith("#"): continue #skips comments which contain =

            k, v = line.split("=", 1)
            campos_selecionados[k] = v
    #inverte chaves e valores para renomear as colunas do dataframe
    campos_selecionados = {v: k for k, v in campos_selecionados.items()}
    return campos_selecionados

def filter_rais(rais, campos_selecionados):
        rais = rais.rename(columns=campos_selecionados)
        rais = rais[rais["salario"]!="000000,00"]
        rais = rais[rais["salario"]!="000000,00"]
        rais = rais[rais["cnpj"].isin(["0000000", "0"])==False]
        rais["mes_admissao"] = rais["data_admissao"].apply(return_chars, args = (4, 6))
        rais["ano_admissao"] = rais["data_admissao"].apply(return_chars, args = (0, 2))
        rais = rais.drop("data_admissao", 1)

        rais["salario"] = rais["salario"].apply(lambda x: float(x.replace(",",".")))
        return rais

def return_chars(x, begin, end):
    x = str(x)
    length = len(x)
#    return x[length-6:length-4]+x[length-2:length] # retorna mes e ano
    return x[length-end:length-begin] # retorna somente o mes

def get_zip_estado(path_zip):
    zip_estados = []
    for root, dirs, files in os.walk(path_zip + "2017"):
        for name in files:
            if name != "ESTB2017ID.7z" and name.endswith(".7z"):
                zip_estados.append(name)
    return zip_estados

#exclui os arquivos caso existam
def delete_files():
    if os.path.exists(path_base_limpa):
        os.remove(path_base_limpa)

    shutil.rmtree(path_rais + "temp", ignore_errors=True)

def limpar_rais_ano_corrente(path_base_limpa, ano):
    limpar_rais(path_base_limpa, ano)

def limpar_rais(path_base_limpa, ano = 0):
    delete_files()
    zip_estados = get_zip_estado(path_rais)
    campos_selecionados=get_campos_selecionados()

    linhas = 10 ** 5 # numero de linhas processadas por ves
    i = 1
    zip = zip_estados
    zip = "MA2017ID.7z"
    for zip in zip_estados:
        archive = py7zr.SevenZipFile(path_rais + "/2017/" + zip, mode='r')
        archive.extract(path=path_rais + "/tmp")
        archive.close()
        txt = path_rais + "tmp/" + zip.replace(".7z", ".txt")
        print(zip)
        for vinculos in pd.read_csv(txt, chunksize=linhas, encoding="latin1", sep=';',
            usecols = campos_selecionados.keys()):
            # HEADER == FALSE
            vinculos = filter_rais(vinculos, campos_selecionados)
            # se é o ano corrente (16, 17...) não salva o ano
            if ano != 0:
                vinculos = vinculos[vinculos["ano_admissao"]=="17"]
                vinculos = vinculos.drop("ano_admissao", 1)

            vinculos.to_csv(path_base_limpa, mode = 'a',
                encoding="latin1", sep=';', header=(i==1), index=False)
            print(i)
            i = i + 1
        os.remove(txt)

###### Início da execução ######

path_rais = "/home/rafael/arquivos/mestrado/pesquisa/labor_renata/rais_id/"
path_campos_selecionados=path_rais + "campos_selecionados.config"
path_base_limpa = path_rais + "base_limpa_2017.csv"

#limpar_rais(path_base_limpa) # gera a base com vinculos iniciados em qualquer ano
limpar_rais_ano_corrente(path_base_limpa, ano=17) # gera a base com vinculos iniciados em 2017

------TESTES
if os.path.exists(path_rais + "acre_base_limpa.csv"):
    os.remove(path_rais + "acre_base_limpa.csv")
campos_selecionados=get_campos_selecionados()
acre = "/home/rafael/arquivos/mestrado/pesquisa/labor_renata/rais_id/2017/AC2017ID.txt"
dados = pd.read_csv(acre, encoding="latin1", sep=';', usecols=campos_selecionados.keys())
dados = filter_rais(dados, campos_selecionados)
dados = dados[dados["ano_admissao"]=="17"]
dados.to_csv(path_rais + "acre_base_limpa.csv", mode = 'a',
    encoding="latin1", sep=';', index=False)
