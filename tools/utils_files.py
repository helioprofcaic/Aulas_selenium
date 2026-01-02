import json
import csv
import os
from collections import Counter


class AnalisadorGrade:
    """
    Analisa os dados das aulas a partir de um arquivo JSON,
    converte para CSV e gera um relatório de resumo.
    """

    def __init__(self, caminho_json='aulas_coletadas.json'):
        """
        Inicializa o analisador com o caminho para o arquivo JSON.

        :param caminho_json: O caminho para o arquivo aulas_coletadas.json.
        """
        self.caminho_json = caminho_json
        self.dados_aulas = self._carregar_dados()

    def _carregar_dados(self):
        """
        Carrega os dados das aulas do arquivo JSON.
        Retorna uma lista de dicionários ou uma lista vazia se o arquivo não for encontrado.
        """
        if not os.path.exists(self.caminho_json):
            print(f"Aviso: O arquivo '{self.caminho_json}' não foi encontrado.")
            return []
        try:
            with open(self.caminho_json, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Erro ao ler o arquivo JSON: {e}")
            return []

    def salvar_como_csv(self, caminho_csv='aulas_coletadas.csv'):
        """
        Converte os dados das aulas para o formato CSV e salva em um arquivo.
        """
        if not self.dados_aulas:
            print("Não há dados para salvar.")
            return

        headers = ['data_cadastro', 'Horário (inicial ~ final)', 'Data Aula', 'Turma', 'Componente', 'Situação', 'Ações']
        
        # Mapeamento das chaves do JSON para os cabeçalhos do CSV
        mapa_chaves = {
            'data_cadastro': 'data_cadastro',
            'horario': 'Horário (inicial ~ final)',
            'dataAula': 'Data Aula',
            'turma': 'Turma',
            'componenteCurricular': 'Componente',
            'status': 'Situação'
        }

        try:
            with open(caminho_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for aula in self.dados_aulas:
                    linha_csv = {header: '' for header in headers}  # Inicializa com strings vazias
                    for chave_json, chave_csv in mapa_chaves.items():
                        if chave_json in aula:
                            linha_csv[chave_csv] = aula[chave_json]
                    writer.writerow(linha_csv)
            print(f"Dados salvos com sucesso em '{caminho_csv}'.")
        except IOError as e:
            print(f"Erro ao salvar o arquivo CSV: {e}")


def main():
    """
    Menu principal para interagir com o analisador de grade.
    """
    # O caminho para o JSON agora é relativo à localização do script
    caminho_json = os.path.join(os.path.dirname(__file__), '..', 'data', 'aulas_coletadas.json')
    analisador = AnalisadorGrade(caminho_json)

    while True:
        print("\nMenu:")
        print("1. Exportar para CSV")
        print("2. Sair")

        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            caminho_csv = os.path.join(os.path.dirname(__file__), '..', 'data', 'aulas_coletadas.csv')
            analisador.salvar_como_csv(caminho_csv)
        elif escolha == '2':
            break
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == '__main__':
    main()
