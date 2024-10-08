# BABEL

## Setting Up BABEL
1. Install olsrd:
```bash
sudo apt-get update
sudo apt-get install babeld -y
```

2. Configure wlan0
```bash
sudo nvim /etc/network/interfaces.d/wlan0
```
```bash
auto wlan0
iface wlan0 inet manual
        wireless-channel 11
        wireless-essid my-mesh-network
        wireless-mode ad-hoc
        wireless-ap 02:12:34:56:78:9A
```

3. Create the file:
```bash
nvim runBabel.sh
```
and paste:
```bash
# Change IP for each raspbery pi
sudo ifconfig wlan0 192.168.7.1 netmask 255.255.255.0 up

# Execute babel
sudo babeld wlan0
```

4. Change the permissions so that the files can be executed:
```bash
sudo chmod +x runBabel.sh
```

5. Edit the file:
```bash
sudo nvim /etc/rc.local
```
and append to the end of the file, just before exit 0:
```bash
/home/rasp/runBabel.sh &
```

6. Reboot all your Raspberry Pis.

## To run the script and save metrics in a CSV file, such as delay and throughput
It's th same steps and script as OLSR
1. Install iperf3:
```bash
sudo apt-get install -y iperf3
```

2. Create the file:
```bash
nvim babeld_tests.py
```
```python
import sys
import csv
import subprocess
import re

def headerCSV(filename):
    headers = ["Source Host", "Destination Host", "Packets Sent", "Packet Loss", "Packet Delivery Ratio", "Delay", 
               "Test duration", "Bytes Sent", "Throughput"]
    
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)

def writerResults(filename, source, destIp, linesPing, linesTP):
    
    # Extracting relevant information
    stats_line = linesPing[-2]  
    times  = linesPing[-1]
    stats = stats_line.split(",")

    # Ping Data
    packetSent = stats[0].split()
    packetReceived = stats[1].split()
    packetLoss = stats[2].split()
    avgTime = times.split('=')[1].split('/')[1]
    delay = avgTime + " ms"
    packetDeliveryRatio = ((float(packetReceived[0])/float(packetSent[0])) * 100)

    # TP data
    testDuration = '10000 ms'
    bytesSent = str(linesTP[0]) + " MBytes"
    throughput = str(linesTP[1]/8) + " MB/s (" + str(linesTP[1]) + " Mbps)"
    
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([source, destIp, packetSent[0], packetLoss[0], str(packetDeliveryRatio) + "%" ,delay, 
                         testDuration, bytesSent, throughput])

def myping(destIp, n):
    parameter = "-c"
    result = subprocess.Popen(["ping", parameter, n, destIp], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    
    # print pin while exec
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

def main():
    # Testing the function
    nPacketsTransmitted = sys.argv[1]
    hostNameSource = sys.argv[2]
    hostNameDest = sys.argv[3]
    filename = sys.argv[4]

    # Assigns the correct IP to the host
    if(hostNameDest == 'rasp1'):
        ipNameDest = '192.168.7.1'
    
    if(hostNameDest == 'rasp2'):
        ipNameDest = '192.168.7.2'
    
    if(hostNameDest == 'rasp3'):
        ipNameDest = '192.168.7.3'

    statsPing = myping(ipNameDest, nPacketsTransmitted)
    statsTP = myThroughput(ipNameDest)
    try:
        with open(filename, 'r') as f:       
            print("Arquivo Encontrado")
            writerResults(filename, hostNameSource, hostNameDest, statsPing, statsTP)            
    except IOError:
        print ('Arquivo não encontrado!\n Criando o arquivo: ', filename)
        headerCSV(filename)
        writerResults(filename, hostNameSource, hostNameDest, statsPing, statsTP)

if __name__=="__main__":
    main()
```

3. To run:
```bash
sudo python3 babeld_tests.py nPacketsToSend hostSource hostDest fileName.csv
```
