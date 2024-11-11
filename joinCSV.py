import os
import pandas as pd

# Diretório principal onde estão as pastas BABEL, OLSR e BATMAN-ADV
main_directory = './'  # Substitua pelo caminho correto

# Nomes das pastas que contêm os arquivos CSV
folders = ['BABEL', 'OLSR', 'BATMAN-ADV']

# Realiza a concatenação de CSVs em cada pasta
for folder in folders:
    folder_path = os.path.join(main_directory, folder)
    
    # Lista para armazenar os DataFrames de cada arquivo CSV na pasta
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    
    # Verifica se há 3 arquivos na pasta (ou mais, caso necessário)
    if len(csv_files) >= 3:
        # Lista para armazenar DataFrames
        all_dfs = []
        
        # Lê cada CSV e adiciona à lista
        for file in csv_files:
            df = pd.read_csv(os.path.join(folder_path, file))
            all_dfs.append(df)
        
        # Concatena todos os DataFrames (empilhando verticalmente)
        concatenated_data = pd.concat(all_dfs, ignore_index=True)
        
        # Salva o DataFrame combinado em um novo arquivo CSV
        output_file = os.path.join(folder_path, f'{folder}_data.csv')
        concatenated_data.to_csv(output_file, index=False)

        print(f"Concatenação realizada com sucesso para a pasta {folder}. Arquivo salvo como: {output_file}")
    else:
        print(f"A pasta {folder} não contém 3 ou mais arquivos CSV.")

