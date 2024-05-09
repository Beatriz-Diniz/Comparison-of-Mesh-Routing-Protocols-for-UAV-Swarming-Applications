# B.A.T.M.A.N-ADV 
For the implementation of the WiFi mesh network, 3 Raspberry Pi 4 devices were used.

## Initial Configuration  
1. Update and upgrade the system with the following command:
```bash
sudo apt-get update && sudo apt-get upgrade -y
```

2. Restart the Raspberry Pi using:
```bash
sudo reboot -n 
```
---

## Setting Up batman-adv
1. Install the **batctl** utility to manage the mesh network by executing:
```bash
sudo apt-get install -y batctl
```

2. Create a startup script using your preferred text editor. For example, you can use:
```bash
nvim ~/start-batman-adv.sh
```

3. Populate the script with the necessary configurations:  
```bash
    #!/bin/bash
    # batman-adv interface to use
    sudo batctl if add wlan0
    sudo ifconfig bat0 mtu 1468

    # Tell batman-adv this is a gateway client
    sudo batctl gw_mode client

    # Activates batman-adv interfaces
    sudo ifconfig wlan0 up
    sudo ifconfig bat0 up
```
4. Grant execution permissions to the script with:
```bash
sudo chmod +x ~/start-batman-adv.sh
```

5. Define the network interface for wlan0 by creating a new configuration file:
```bash
sudo nvim /etc/network/interfaces.d/wlan0
```
then add these settings:
```bash
auto wlan0
iface wlan0 inet manual
        wireless-channel 1
        wireless-essid my-ad-hoc-network
        wireless-mode ad-hoc
        wireless-ap 02:12:34:56:78:9A
```

6. Load the batman-adv kernel module automatically at startup:
```bash
echo 'batman-adv' | sudo tee --append /etc/modules
```

7. Prevent DHCP from managing the wlan0 interface:
```bash
echo 'denyinterfaces wlan0' | sudo tee --append /etc/dhcpcd.conf
```

8. Ensure the startup script runs at boot by modifying /etc/rc.local:
```bash
sudo vi /etc/rc.local
```
Insert the following line before the final **exit 0**:
```bash
/home/pi/start-batman-adv.sh &

```
---

## Creating the gateway
In just one Raspberry Pi or more if the network has many nodes

1. Install the DHCP software using the command:
```bash
sudo apt-get install -y dnsmasq
```

2. 
Set up the DHCP server by modifying the **dnsmasq.conf** file as the root user:
```bash
sudo nvim /etc/dnsmasq.conf
```
Then, append the following lines to the end of the file:
```bash
interface=bat0
dhcp-range=192.168.199.2,192.168.199.99,255.255.255.0,12h
```

3. Update the startup script to incorporate routing rules that forward mesh traffic to the home or office network and perform Network Address Translation on the responses. Additionally, designate the node as a mesh gateway and set up the gateway interface IP address. To implement these changes, modify the **start-batman-adv.sh** file with the following content:
```bash
#!/bin/bash
# batman-adv interface to use
sudo batctl if add wlan0
sudo ifconfig bat0 mtu 1468

# Tell batman-adv this is an internet gateway
sudo batctl gw_mode server

# Enable port forwarding
sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables -A FORWARD -i eth0 -o bat0 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i bat0 -o eth0 -j ACCEPT

# Activates batman-adv interfaces
sudo ifconfig wlan0 up
sudo ifconfig bat0 up
sudo ifconfig bat0 192.168.199.1/24
```

4. (Optional) edit:
```bash
sudo nvim /etc/wpa_supplicant/wpa_supplicant.conf
```
to add the settings for a Wi-Fi network.

5. (Optional) To add names for MAC addresses, edit the file:
```bash
sudo nvim /etc/bat-hosts
```
e.g.:
```bash
b8:27:eb:8e:ec:6c   rasp1
b8:27:eb:bd:4d:e5   rasp2
b8:27:eb:01:d4:bb   rasp3
```

6. Reboot all your Raspberry Pis.

---
   
## Checking the Gateway Status

1.Run the command: 
```bash
sudo batctl if
``` 
to display the interfaces participating in the mesh. You should see **wlan0: active** indicating that the WiFi interface wlan0 is actively part of the mesh. 

2. Run the command:
```bash
sudo batctl n
```
to display the neighboring mesh nodes that your gateway node can detect. You should see output similar to this:
```bash
[B.A.T.M.A.N. adv 2018.3, MainIF/MAC: wlan0/b8:27:eb:8e:ec:6c (bat0/ba:bf:0a:fd:33:e5 BATMAN_IV)]
IF             Neighbor             last-seen
    wlan0       rasp1   0.980s
    wlan0       rasp2   0.730s
```

---

## To run the script and save metrics in a CSV file, such as delay and throughput

1. Create the script:
```bash
nvim batman-adv_testes.py
```
add to the script:
```python
import sys
import csv
import subprocess

def headerCSV(filename):
    headers = ["Source Host", "Destination Host", "Packets Sent", "Packet Loss", "Packet Delivery Ratio", "Delay", 
               "Test duration", "Bytes Sent", "Throughput"]
    
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)

def writerResults(filename, source, host, linesPing, linesTP):
    
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
    testDuration = linesTP[0].split(" ")
    testDuration = testDuration[2].split("ms")
    testDuration = str(testDuration[0]) + " ms"
    bytesSent = linesTP[1].split(" ")
    bytesSent = str(bytesSent[1]) + " Bytes"
    throughput = linesTP[2].split(": ")
    throughput = throughput[1]

    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([source, host, packetSent[0], packetLoss[0], str(packetDeliveryRatio) + "%" ,delay, testDuration, bytesSent, throughput])

def myping(source, host, n):
    # Choose parameter based on OS
    parameter = "-c"

    # Constructing the ping command
    result = subprocess.Popen(["batctl", "ping", parameter, n, host], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Interpreting the response
    output, errors = result.communicate()
 
    # Parsing ping output
    lines = output.splitlines()
    if len(lines) < 2:
        print("Invalid ping response")
        return

    # Extracting relevant information
    stats_line = lines[-2]  
    stats = stats_line.split(",")

    if len(stats) < 3:
        print("Invalid ping statistics")
        exit

    print(output)
    return lines

def myThroughput(host):
    # Constructing the ping command
    result = subprocess.Popen(["batctl", "tp", host], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Interpreting the response
    output, errors = result.communicate() 
    lines = output.splitlines()
    
    print(output)
    return lines

# Testing the function
nPacketsTransmitted = sys.argv[1]
hostNameSource = sys.argv[2]
hostNameDest = sys.argv[3]
filename = sys.argv[4]

statsPing = myping(hostNameSource, hostNameDest, nPacketsTransmitted)
statsTP = myThroughput(hostNameDest)

try:
    with open(filename, 'r') as f:       
        print("Arquivo Encontrado")
        writerResults(filename, hostNameSource, hostNameDest, statsPing, statsTP)            
except IOError:
    print ('Arquivo não encontrado!\n Criando o arquivo: ', filename)
    headerCSV(filename)
    writerResults(filename, hostNameSource, hostNameDest, statsPing, statsTP)
```

2. To run:
```bash
sudo python3 batman-adv_testes.py nPacketsToSend hostSource hostDest fileName.csv
```
