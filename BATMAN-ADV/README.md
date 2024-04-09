# B.A.T.M.A.N-ADV 
For the implementation of the WiFi mesh network, 3 Raspberry Pi 4 devices were used.

## First steps  
1. Issue command
<pre><code> sudo apt-get update && sudo apt-get upgrade -y</code></pre>

2. Reboot the Raspberry Pi with command
<pre><code> sudo reboot -n </code></pre>

## Setup batman-adv
1. To manage the mesh network, a utility called <b>batctl</b> needs to be installed.  This can be done using command </li>
<pre><code> sudo apt-get install -y batctl </code></pre>

2. Using your preferred editor create a file ~/start-batman-adv.sh </li>
<pre><code> vi ~/start-batman-adv.sh </code></pre> or
<pre> <code> nvim ~/start-batman-adv.sh </code> </pre> or
<pre> <code> nano ~/start-batman-adv.sh </code> </pre>

3. The file should contain the following:  
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
