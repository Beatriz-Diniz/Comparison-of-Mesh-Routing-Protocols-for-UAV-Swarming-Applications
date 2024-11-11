import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Função para converter Throughput para MB/s
def convert_throughput(value):
    if 'KB/s' in value:
        return float(value.split()[0]) / 1024  # Converte de KB/s para MB/s
    elif 'Kbps' in value:
        return (float(value.split()[0]) / 8) / 1024  # Converte de Kbps para MB/s
    elif 'MB/s' in value:
        return float(value.split()[0])  # Já está em MB/s
    elif 'Mbps' in value:
        return float(value.split()[0]) / 8  # Converte de Mbps para MB/s
    return float(value)  # Caso esteja em formato numérico sem unidade

# Carregar os arquivos CSV
protocol1_df = pd.read_csv('./BATMAN-ADV/BATMAN-ADV_data.csv')
protocol2_df = pd.read_csv('./OLSR/OLSR_data.csv')
protocol3_df = pd.read_csv('./BABEL/BABEL_data.csv')

# Adicionar uma coluna 'Protocol' para identificar os dados de cada protocolo
protocol1_df['Protocol'] = 'BATMAN-ADV'
protocol2_df['Protocol'] = 'OLSR'
protocol3_df['Protocol'] = 'BABEL'

# Combinar os três DataFrames em um único
combined_df = pd.concat([protocol1_df, protocol2_df, protocol3_df])

# Selecionar as colunas relevantes para a comparação
relevant_columns = ['Protocol', 'Test duration', 'Bytes Sent', 'Throughput', 'Packets Sent', 'Delay']
comparison_df = combined_df[relevant_columns]

# Converter as colunas relevantes para o formato numérico (remover unidades, como %, MB, etc.)
comparison_df['Test duration'] = comparison_df['Test duration'].str.rstrip(' ms').astype('float')
comparison_df['Throughput'] = comparison_df['Throughput'].apply(convert_throughput)
comparison_df['Bytes Sent'] = comparison_df['Bytes Sent'].str.extract(r'(\d+.\d+)').astype('float')
comparison_df['Delay'] = comparison_df['Delay'].str.rstrip(' ms').astype('float')

# Usar .loc[] para evitar o SettingWithCopyWarning
comparison_df.loc[:, 'Packets Sent'] = comparison_df['Packets Sent'].astype('int')
comparison_df.loc[:, 'Test Version'] = comparison_df.groupby('Protocol').cumcount() + 1  # Criar uma coluna de versão de teste

# Configurar o estilo dos gráficos
sns.set(style="whitegrid")

# Plotar gráfico de Delay por Pacotes Enviados
plt.figure(figsize=(10, 6))
sns.lineplot(x='Packets Sent', y='Delay', hue='Protocol', marker='o', data=comparison_df)
plt.title('Delay x Packets Sent')
plt.ylabel('Delay (ms)')
plt.xlabel('Packets Sent')
plt.legend(title='')
plt.show()

# Calcular a média de Throughput por protocolo
mean_throughput = comparison_df.groupby('Protocol')['Throughput'].mean().reset_index()
mean_throughput_dict = mean_throughput.set_index('Protocol')['Throughput'].to_dict()

# Plotar gráfico de Throughput por versão de teste
plt.figure(figsize=(10, 6))
line_plot = sns.lineplot(x='Test Version', y='Throughput', hue='Protocol', marker='o', data=comparison_df)
plt.title('Throughput')
plt.ylabel('Throughput (MB/s)')
plt.xlabel('Test')

# Adicionar médias na legenda
handles, labels = line_plot.get_legend_handles_labels()
new_labels = []
for label in labels:
    avg_value = mean_throughput_dict[label]
    new_labels.append(f"{label} (Média: {avg_value:.2f} MB/s)")

# Definir a posição da legenda
plt.legend(new_labels, title='', loc='lower right', bbox_to_anchor=(1.15, 1), frameon=False)
plt.tight_layout()  # Ajusta o layout para evitar sobreposição
plt.show()
