# Change IP for each raspbery pi
sudo ifconfig wlan0 192.168.7.3 netmask 255.255.255.0 up

# Execute babel
sudo babeld wlan0
