<h1> B.A.T.M.A.N-ADV </h1> 
<p> For the implementation of the WiFi mesh network, 3 Raspberry Pi 4 devices were used. </p>

<h2> First steps </h2> 
<ol>
  <li>Issue command</li>
    <pre><code> sudo apt-get update && sudo apt-get upgrade -y</code></pre>
  
  <li> Reboot the Raspberry Pi with command </li>
    <pre><code> sudo reboot -n </code></pre>
</ol>

<h2> Setup batman-adv </h2>
<ol>
  <li> To manage the mesh network, a utility called <b>batctl</b> needs to be installed.  This can be done using command </li>
    <pre><code> sudo apt-get install -y batctl </code></pre>
  
  <li> Using your preferred editor create a file ~/start-batman-adv.sh </li>
    <pre><code> vi ~/start-batman-adv.sh </code></pre> or
    <pre> <code> nvim ~/start-batman-adv.sh </code> </pre> or
    <pre> <code> nano ~/start-batman-adv.sh </code> </pre> 
  
  <li> The file should contain the following:</li>
  <pre><code>
  #!/bin/bash
  # batman-adv interface to use
  sudo batctl if add wlan0
  sudo ifconfig bat0 mtu 1468 
  # Tell batman-adv this is a gateway client
  sudo batctl gw_mode client  
  # Activates batman-adv interfaces
  sudo ifconfig wlan0 up
  sudo ifconfig bat0 up
  </code></pre>
</ol>
