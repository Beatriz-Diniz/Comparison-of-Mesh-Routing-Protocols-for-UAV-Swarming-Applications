import pandas as pd
import matplotlib.pyplot as plt
import os
import re

def convert_to_float(value):
    """Converte strings numéricas e percentuais em float."""
    if isinstance(value, str):
        value = re.sub(r'[^\d.-]', '', value)  # Remove tudo que não seja número, ponto ou sinal de menos
        try:
            return float(value)
        except ValueError:
            return None
    return float(value) if isinstance(value, (int, float)) else None

def extract_throughput(value):
    """Extrai o throughput em MB/s de strings."""
    if isinstance(value, str):
        match = re.search(r'([\d.]+) MB/s', value)
        return float(match.group(1)) if match else None
    return None

def convert_columns(df):
    """Converte colunas específicas do DataFrame para float."""
    columns_to_convert = [
        'Packet Loss (No Load)', 'Packet Delivery Ratio (No Load)',
        'Delay (No Load)', 'Bytes Sent (No Load)', 'Throughput (No Load)',
        'Packet Loss (Low Load)', 'Packet Delivery Ratio (Low Load)', 
        'Delay (Low Load)', 'Bytes Transferred (Low Load)', 'Throughput (Low Load)',
        'Packet Loss (Normal Load)', 'Packet Delivery Ratio (Normal Load)',
        'Delay (Normal Load)', 'Bytes Transferred (Normal Load)', 'Throughput (Normal Load)',
        'Packet Loss (High Load)', 'Packet Delivery Ratio (High Load)',
        'Delay (High Load)', 'Bytes Transferred (High Load)', 'Throughput (High Load)'
    ]
    throughput_columns = [col for col in columns_to_convert if 'Throughput' in col]

    for column in columns_to_convert:
        if column in df.columns:
            df[column] = df[column].apply(extract_throughput if column in throughput_columns else convert_to_float)
    return df

def aggregate_results(df_filtered, columns_dict, metric_name):
    results = {}
    for load_type, column in columns_dict.items():
        df_load = df_filtered.filter(like=load_type).copy()
        df_load['Protocol'] = df_filtered['Protocol']
        
        results[load_type] = df_load.groupby(['Protocol', f'Packets Sent ({load_type})'])[column].agg(['mean', 'std']).reset_index()
        results[load_type].columns = ['Protocol', 'Packets Sent', f'Mean {metric_name} ({load_type})', f'Standard Deviation {metric_name} ({load_type})']
    
    return results

def plot_results(results, metric_name, y_label, unit="", save_dir="plots"):
    os.makedirs(save_dir, exist_ok=True)
    colors = {'Batman': 'blue', 'OLSR': 'green', 'Babel': 'orange'}
    packets_sent_ticks = [5, 10, 50, 100, 500, 1000, 5000]
    summary_data = {}

    for load_type, data in results.items():
        plt.figure(figsize=(10, 6))
        for protocol in data['Protocol'].unique():
            protocol_data = data[data['Protocol'] == protocol]
            color = colors.get(protocol, 'gray')
            packets_sent = protocol_data['Packets Sent']
            mean = protocol_data[f'Mean {metric_name} ({load_type})']
            std = protocol_data[f'Standard Deviation {metric_name} ({load_type})']
            overall_mean, overall_std = mean.mean(), std.mean()

            plt.plot(packets_sent, mean, marker='o', label=f"{protocol} (Mean: {overall_mean:.2f}{unit})", color=color)
            plt.fill_between(packets_sent, mean - std, mean + std, color=color, alpha=0.2)
            summary_data.setdefault(protocol, {})[load_type] = f"{overall_mean:.2f} ± {overall_std:.2f}"

        plt.title(f"{metric_name} by Packets Sent - {load_type}")
        plt.xlabel("Packets Sent")
        plt.ylabel(f"{y_label} ({unit})" if unit else y_label)
        plt.legend()
        plt.grid(True, which="both", linestyle="--", linewidth=0.5)
        plt.xscale('log')
        plt.xticks(packets_sent_ticks, packets_sent_ticks)
        plt.tight_layout()
        plt.savefig(f"{save_dir}/{metric_name}_{load_type}.png", dpi=300)
        plt.close()

    summary_df = pd.DataFrame.from_dict(summary_data, orient='index').reset_index().rename(columns={'index': 'Protocol'})
    fig, ax = plt.subplots(figsize=(8, len(summary_df) * 0.7 + 1))
    ax.axis('off')
    table_obj = ax.table(cellText=summary_df.values, colLabels=summary_df.columns, cellLoc='center', loc='center')
    table_obj.auto_set_font_size(False)
    table_obj.set_fontsize(12)
    table_obj.auto_set_column_width(col=list(range(len(summary_df.columns))))
    table_obj.scale(1.5, 1.5)
    plt.savefig(f"{save_dir}/{metric_name}_summary_table.png", dpi=300)
    plt.close()

def main():
    batman = pd.read_csv("./BATMAN-ADV/BatmanOverload.csv")
    olsr = pd.read_csv("./OLSR/OlsrOverload.csv")
    babel = pd.read_csv("./BABEL/BabelOverload.csv")
    
    batman['Protocol'], olsr['Protocol'], babel['Protocol'] = 'Batman', 'OLSR', 'Babel'
    df = pd.concat([batman, olsr, babel]).drop(columns=['Source Host', 'Destination Host', 'Test Duration (No Load)'], errors='ignore')
    df = convert_columns(df)
    df_filtered = df[df['Packets Sent (No Load)'] != 10000]
    
    metric_columns = {
        'Packet Loss': {'No Load': 'Packet Loss (No Load)', 'Low Load': 'Packet Loss (Low Load)', 'Normal Load': 'Packet Loss (Normal Load)', 'High Load': 'Packet Loss (High Load)'},
        'Delay': {'No Load': 'Delay (No Load)', 'Low Load': 'Delay (Low Load)', 'Normal Load': 'Delay (Normal Load)', 'High Load': 'Delay (High Load)'},
        'CPU Usage': {'No Load': 'CPU Usage (No Load)', 'Low Load': 'CPU Usage (Low Load)', 'Normal Load': 'CPU Usage (Normal Load)', 'High Load': 'CPU Usage (High Load)'},
        'Memory Usage': {'No Load': 'Memory Usage (No Load)', 'Low Load': 'Memory Usage (Low Load)', 'Normal Load': 'Memory Usage (Normal Load)', 'High Load': 'Memory Usage (High Load)'},
        'Temperature': {'No Load': 'Temperature (No Load)', 'Low Load': 'Temperature (Low Load)', 'Normal Load': 'Temperature (Normal Load)', 'High Load': 'Temperature (High Load)'},
        'Throughput': {'No Load': 'Throughput (No Load)', 'Low Load': 'Throughput (Low Load)', 'Normal Load': 'Throughput (Normal Load)', 'High Load': 'Throughput (High Load)'}
    }
    
    for metric_name, columns_dict in metric_columns.items():
        results = aggregate_results(df_filtered, columns_dict, metric_name)
        plot_results(results, metric_name, metric_name, "%" if "Usage" in metric_name else "ms", save_dir="plots")

if __name__ == "__main__":
    main()
