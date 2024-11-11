import sys
import csv
import subprocess
import threading
import time
import os


def headerCSV(filename):
    headers = [
        "Source Host", "Destination Host", 
        "Packets Sent (No Load)", "Packet Loss (No Load)", "Packet Delivery Ratio (No Load)", 
        "Delay (No Load)", "Test Duration (No Load)", "Bytes Sent (No Load)", "Throughput (No Load)", 
        "CPU Usage (No Load)", "Memory Usage (No Load)", "Temperature (No Load)",
        
        "Packets Sent (Low Load)", "Packet Loss (Low Load)", "Packet Delivery Ratio (Low Load)", 
        "Delay (Low Load)", "Bytes Transferred (Low Load)", "Throughput (Low Load)", 
        "CPU Usage (Low Load)", "Memory Usage (Low Load)", "Temperature (Low Load)",

        "Packets Sent (Normal Load)", "Packet Loss (Normal Load)", "Packet Delivery Ratio (Normal Load)", 
        "Delay (Normal Load)", "Bytes Transferred (Normal Load)", "Throughput (Normal Load)", 
        "CPU Usage (Normal Load)", "Memory Usage (Normal Load)", "Temperature (Normal Load)",

        "Packets Sent (High Load)", "Packet Loss (High Load)", "Packet Delivery Ratio (High Load)", 
        "Delay (High Load)", "Bytes Transferred (High Load)", "Throughput (High Load)", 
        "CPU Usage (High Load)", "Memory Usage (High Load)", "Temperature (High Load)"
    ]
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)


def writerResults(filename, source, dest, linesNoLoad, transferred_bytes, throughput, linesLowLoad, linesNormalLoad, linesHighLoad,
                  linesLowLoad2, linesNormalLoad2, linesHighLoad2,
                  cpu_usage_no_load, mem_usage_no_load, temperature_no_load,
                  cpu_usage_low, mem_usage_low, temperature_low,
                  cpu_usage_normal, mem_usage_normal, temperature_normal,
                  cpu_usage_high, mem_usage_high, temperature_high):
    
    # Extrair estatísticas para a condição de "sem carga"
    no_load_stats = extract_ping_and_throughput_stats(linesNoLoad, transferred_bytes, throughput)

    # Extrair estatísticas para carga baixa
    
    print('\n\n-------')
    print(linesLowLoad2)
    print('******\n\n')
    low_load_stats = extract_ping_stats(linesLowLoad)
    low_load_throughput_stats = extract_throughput_stats(linesLowLoad2)

    # Extrair estatísticas para carga normal
    normal_load_stats = extract_ping_stats(linesNormalLoad)
    normal_load_throughput_stats = extract_throughput_stats(linesNormalLoad2)

    # Extrair estatísticas para carga alta
    high_load_stats = extract_ping_stats(linesHighLoad)
    high_load_throughput_stats = extract_throughput_stats(linesHighLoad2)

    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            source, dest,
            no_load_stats["packets_sent"], no_load_stats["packet_loss"], f"{no_load_stats['packet_delivery_ratio']}%",
            no_load_stats["delay"], no_load_stats["test_duration"], no_load_stats["bytes_sent"],
            no_load_stats["throughput"], cpu_usage_no_load, mem_usage_no_load, temperature_no_load,
            low_load_stats["packets_sent"], low_load_stats["packet_loss"], f"{low_load_stats['packet_delivery_ratio']}%",
            low_load_stats["delay"], low_load_throughput_stats["transferred_bytes"], low_load_throughput_stats["throughput"],
            cpu_usage_low, mem_usage_low, temperature_low,
            normal_load_stats["packets_sent"], normal_load_stats["packet_loss"], f"{normal_load_stats['packet_delivery_ratio']}%",
            normal_load_stats["delay"], normal_load_throughput_stats["transferred_bytes"], normal_load_throughput_stats["throughput"],
            cpu_usage_normal, mem_usage_normal, temperature_normal,
            high_load_stats["packets_sent"], high_load_stats["packet_loss"], f"{high_load_stats['packet_delivery_ratio']}%",
            high_load_stats["delay"], high_load_throughput_stats["transferred_bytes"], high_load_throughput_stats["throughput"],
            cpu_usage_high, mem_usage_high, temperature_high,
        ])

def extract_throughput_stats(lines):
    if len(lines) != 2:
        print("Erro: A entrada deve conter exatamente dois valores (bytes e throughput).")
        return None

    try:
        transferred_bytes = lines[0]  # Bytes transferidos
        throughput = lines[1]          # Throughput
        
        # Exibindo os resultados
        print(f"Throughput de sender: {throughput / 8:.2f} MB/s ({throughput:.2f} Mbps)")
        
        return {
            "transferred_bytes": f"{transferred_bytes:.2f} MBytes",
            "throughput": f"{throughput / 8:.2f} MB/s ({throughput:.2f} Mbps)"
        }
    except (IndexError, ValueError) as e:
        print(f"Erro ao processar os dados de throughput: {e}")
        return None


def extract_ping_and_throughput_stats(linesPing, transferred_bytes, throughput):
    stats_line = linesPing[-2]  
    times = linesPing[-1]
    stats = stats_line.split(",")

    # Ping Data
    packet_sent = stats[0].split()
    packet_received = stats[1].split()
    packet_loss = stats[2].split()
    avg_time = times.split('=')[1].split('/')[1]
    delay = avg_time + " ms"
    packet_delivery_ratio = (float(packet_received[0]) / float(packet_sent[0])) * 100

    # TP data
    test_duration = '10000 ms'  # Duração do teste pode ser ajustada conforme necessário
    bytes_sent = f"{transferred_bytes} MBytes"
    throughput_str = f"{throughput / 8:.2f} MB/s ({throughput:.2f} Mbps)"
    
    return {
        "packets_sent": packet_sent[0],
        "packet_loss": packet_loss[0],
        "packet_delivery_ratio": packet_delivery_ratio,
        "delay": delay,
        "test_duration": test_duration,
        "bytes_sent": bytes_sent,
        "throughput": throughput_str,
    }


def extract_ping_stats(lines):
    stats_line = lines[-2]
    times = lines[-1]
    stats = stats_line.split(",")

    packet_sent = stats[0].split()
    packet_received = stats[1].split()
    packet_loss = stats[2].split()
    avg_time = times.split('=')[1].split('/')[1]
    delay = avg_time + " ms"
    packet_delivery_ratio = (float(packet_received[0]) / float(packet_sent[0])) * 100

    return {
        "packets_sent": packet_sent[0],
        "packet_loss": packet_loss[0],
        "packet_delivery_ratio": packet_delivery_ratio,
        "delay": delay,
    }

def overloadNetwork(destIp, numPackets, numBytes, time):
    overload_command = f"sudo ping -f -s {numBytes} -i {time} {destIp} -c {numPackets}"
    result = subprocess.Popen(overload_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    output_lines = []
    try:
        while True:
            line = result.stdout.readline()
            if not line:
                break
            print(line.strip())
            output_lines.append(line.strip())
    except KeyboardInterrupt:
        result.kill()

    result.wait()

    if result.returncode != 0:
        print("Error executing ping command.")
        stderr_output = result.stderr.read()
        print(stderr_output)
        return []

    return output_lines

def overloadNetworkIperf3(destIp, load_type):
    """
    Realiza a sobrecarga de rede com base no tipo de carga (baixa, normal, alta) usando iperf3.
    """
    if load_type == "low":
        command = f"iperf3 -c {destIp} -b 1M -t 10"
    elif load_type == "normal":
        command = f"iperf3 -c {destIp} -b 10M -t 10"
    elif load_type == "high":
        command = f"iperf3 -c {destIp} -b 100M -t 10"
    
    # Executa o iperf3 com o comando selecionado
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    lines = []
    try:
        while True:
            line = process.stdout.readline()
            if not line:
                break
            print(line.strip()) 
            lines.append(line.strip())
    except KeyboardInterrupt:
        process.kill()

    if process.poll() is not None:
        process.terminate()

    throughput = None
    transferredBytes = None

    # Busca o throughput e bytes transferidos no resultado
    for line in lines:
        if "sec" in line and "sender" in line:
            parts = line.split()
            try:
                transferredBytes = float(parts[4])
                throughput = float(parts[6])
                print(f"Throughput de sender: {throughput / 8:.2f} MB/s ({throughput} Mbps)")
                break
            except (IndexError, ValueError) as e:
                print(f"Erro extraindo dados de throughput: {e}")
                return None, None

    return transferredBytes, throughput


def myping(destIp, n):
    parameter = "-c"
    result = subprocess.Popen(["ping", parameter, n, destIp], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

    lines = []
    try:
        while True:
            line = result.stdout.readline()
            if not line:
                break
            print(line.strip())
            lines.append(line.strip())
    except KeyboardInterrupt:
        result.kill()

    if result.poll() is not None:
        result.terminate()

    return lines


def myThroughput(destIp):
    # Define the iperf3 command with the specified server IP
    command = f"iperf3 -c {destIp} -f m"

    # Executes the iperf3 command
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

    # List to store the output lines for later analysis
    lines = []

    try:
        # Reads the command output in real time, line by line
        while True:
            line = process.stdout.readline()
            if not line:
                break
            print(line.strip()) 
            lines.append(line.strip())
    except KeyboardInterrupt:
        process.kill()

    if process.poll() is not None:
        process.terminate()

    throughput = None
    transferredBytes = None

    # Loop through the lines to find the receiver's throughput and transferred bytes
    for line in lines:
        if "sec" in line and "receiver" in line:
            parts = line.split()
            try:
                # Extract the transferred bytes and the throughput
                transferredBytes = float(parts[4])
                throughput = float(parts[6])
                print(f"Throughput for receiver: {throughput/8:.2f} MB/s ({throughput} Mbps)")
                break
            except (IndexError, ValueError) as e:
                print(f"Error extracting throughput data: {e}")
                return None, None

    return transferredBytes, throughput

def getCPUUsage():
    command = "top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\\([0-9.]*\\)%* id.*/\\1/' | awk '{print 100 - $1}'"
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True)
    return result.stdout.strip()

def getMemoryUsage():
    command = "free | grep Mem | awk '{print $3/$2 * 100.0}'"
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True)
    return result.stdout.strip()

def getTemperature():
    command = "vcgencmd measure_temp | egrep -o '[0-9]*\.[0-9]*'"
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True)
    return result.stdout.strip()

def monitorResources(interval, cpu_usage_list, mem_usage_list, temperature_list):
    while True:
        cpu_usage = getCPUUsage()
        mem_usage = getMemoryUsage()
        temperature = getTemperature()

        cpu_usage_list.append(cpu_usage)
        mem_usage_list.append(mem_usage)
        temperature_list.append(temperature)

        print(f"CPU Usage: {cpu_usage}% | Memory Usage: {mem_usage}% | Temperature: {temperature}")
        time.sleep(interval)

def main():
    nPacketsTransmitted = sys.argv[1]
    hostNameSource = sys.argv[2]
    hostNameDest = sys.argv[3]
    filename = sys.argv[4]

    # Define the destination IP
    if hostNameDest == 'rasp1':
        ipNameDest = '192.168.7.1'
    elif hostNameDest == 'rasp2':
        ipNameDest = '192.168.7.2'
    elif hostNameDest == 'rasp3':
        ipNameDest = '192.168.7.3'

    # Lists to store resource usage
    cpu_usage_list = []
    mem_usage_list = []
    temperature_list = []

    # Start monitoring in a separate thread
    
    monitor_thread = threading.Thread(target=monitorResources, args=(1, cpu_usage_list, mem_usage_list, temperature_list))
    monitor_thread.daemon = True  # Torna o thread um daemon
    monitor_thread.start()

    # Run tests without load
    print("Running tests with no load...")
    linesNoLoad = myping(ipNameDest, nPacketsTransmitted)
    cpu_usage_no_load = getCPUUsage()
    mem_usage_no_load = getMemoryUsage()
    temperature_no_load = getTemperature()

    # Here, we call the throughput test just once after the initial ping test (without load)
    print("Running throughput test...")
    transferred_bytes, throughput = myThroughput(ipNameDest)
    # Here we can store the throughput or log it, depending on your use case
    print(f"Transferred bytes: {transferred_bytes} MB | Throughput: {throughput} MB/s")

    # Run tests with low load
    print("Running tests with low load...")
    linesLowLoad = overloadNetwork(ipNameDest, nPacketsTransmitted, "128", "0.1")
    linesLowLoad2 = overloadNetworkIperf3(ipNameDest, "low")
    cpu_usage_low = getCPUUsage()
    mem_usage_low = getMemoryUsage()
    temperature_low = getTemperature()

    # Run tests with normal load
    print("Running tests with normal load...")
    linesNormalLoad = overloadNetwork(ipNameDest, nPacketsTransmitted, "45000", "0.01")
    linesNormalLoad2 = overloadNetworkIperf3(ipNameDest, "normal")
    cpu_usage_normal = getCPUUsage()
    mem_usage_normal = getMemoryUsage()
    temperature_normal = getTemperature()

    # Run tests with high load
    print("Running tests with high load...")
    linesHighLoad = overloadNetwork(ipNameDest, nPacketsTransmitted, "65507", "0.001")
    linesHighLoad2 = overloadNetworkIperf3(ipNameDest, "high")
    cpu_usage_high = getCPUUsage()
    mem_usage_high = getMemoryUsage()
    temperature_high = getTemperature()

    # Stop the resource monitoring thread
    #stop_event.set()
    monitor_thread.join(timeout=1)
    
    # Write results to CSV
    try:
        with open(filename, 'r') as f:       
            print("Arquivo Encontrado")
            writerResults(filename, hostNameSource, hostNameDest, linesNoLoad, transferred_bytes, throughput, linesLowLoad, linesNormalLoad, linesHighLoad,                                 linesLowLoad2, linesNormalLoad2, linesHighLoad2,
                  cpu_usage_no_load, mem_usage_no_load, temperature_no_load,
                  cpu_usage_low, mem_usage_low, temperature_low,
                  cpu_usage_normal, mem_usage_normal, temperature_normal,
                  cpu_usage_high, mem_usage_high, temperature_high)
    except IOError:
        print ('Arquivo não encontrado!\n Criando o arquivo: ', filename)
        headerCSV(filename)
        writerResults(filename, hostNameSource, hostNameDest, linesNoLoad, transferred_bytes, throughput, linesLowLoad, linesNormalLoad, linesHighLoad,
                  linesLowLoad2, linesNormalLoad2, linesHighLoad2,
                  cpu_usage_no_load, mem_usage_no_load, temperature_no_load,
                  cpu_usage_low, mem_usage_low, temperature_low,
                  cpu_usage_normal, mem_usage_normal, temperature_normal,
                  cpu_usage_high, mem_usage_high, temperature_high)

    print("Test completed and results written to CSV.")

if __name__ == "__main__":
    main()



