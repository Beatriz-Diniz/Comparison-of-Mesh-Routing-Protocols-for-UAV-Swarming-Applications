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




