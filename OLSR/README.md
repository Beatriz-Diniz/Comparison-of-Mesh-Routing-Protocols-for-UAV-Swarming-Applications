# OLSR

## Initial Configuration  
1. Update and upgrade the system with the following command:
```bash
sudo apt-get update && sudo apt-get upgrade -y
```
2. nstall the dependencies

```bash
sudo apt-get install -y libc6 git bison flex libgps-dev libbz2-dev \
automake g++ gpsd gpsd-clients libgtk2.0-dev libpango1.0-dev \
libcairo2-dev
```
3. edit the file:
```bash
sudo nvim /etc/apt/sources.list
```
add the line:
```bash
deb http://ftp.de.debian.org/debian buster main
```

4. Restart the Raspberry Pi using:
```bash
sudo reboot -n 
```
---

## Setting Up OLSR
1. Install olsrd:
```bash
sudo apt-get update
sudo apt-get install olsrd -y
```
2. Create the files:
* config_ad_hoc.sh:
  ```bash
  nvim config_ad_hoc.sh
  ```
  ```bash
  # could be a different command if you are using a different OS on your RPi
  #sudo systemctl stop dhcpcd 

  # Use your own interface name if its not wlan0
  sudo iwconfig wlan0 mode Ad-Hoc

  # Use your own interface name if its not wlan0
  # you can change the name of your network here
  sudo iwconfig wlan0 essid "NetworkAdHoc"

  ###############################################
  # EDIT MADE HERE
  # you will need a unique IP address for each device in your mesh network
  # you should keep all of them in the same subnet. 
  # I had my IP address in the 192.168.7.xxx subnet
  ###############################################
  # Use your own interface name if its not wlan0
  # Change IP for each raspbery pi
  sudo ifconfig wlan0 192.168.7.3 netmask 255.255.255.0 up

  #sudo olsrd -i wlan0
  ```
* start_olsrd.sh
  ```bash
  nvim start_olsrd.sh
  ```
  ```bash
  # Use your wireless interface name here if its not wlan0
  sudo olsrd -i wlan0
  ```

3. Edit the file:
```bash
sudo nvim /etc/rc.local
```
and append to the end of the file, just before **exit 0**:
```bash
/home/rasp/config_ad_hoc.sh &

#only rasp add 
/home/rasp/start_olsrd.sh &
```

4. Change the permissions so that the files can be executed:
```bash
sudo chmod +x start_olsrd.sh
sudo chmod +x config_ad_hoc.sh
```

5. Create or modify the file:
```bash
sudo nvim /etc/network/interfaces.d/wlan0
```
```bash
auto wlan0
iface wlan0 inet manual
        wireless-channel 1
        wireless-mode ad-hoc
```

6. Reboot all your Raspberry Pis.

---

## To run the script and save metrics in a CSV file, such as delay and throughput

1. Install iperf3:
```bash
sudo apt-get install -y iperf3
```

2. Create the file:
```bash
nvim olsrd_tests.py
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
sudo python3 olsrd_tests.py nPacketsToSend hostSource hostDest fileName.csv
```

