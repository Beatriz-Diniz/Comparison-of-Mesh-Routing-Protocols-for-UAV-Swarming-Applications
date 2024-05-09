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

## Setting Up batman-adv
1. Install the <b>batctl</b> utility to manage the mesh network by executing:
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
Insert the following line before the final <b>exit 0</b>:
```bash
/home/pi/start-batman-adv.sh &

```
##
