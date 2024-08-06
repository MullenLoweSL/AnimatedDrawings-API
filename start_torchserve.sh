#!/bin/bash
# start_torchserve.sh

# Start TorchServe
/opt/conda/bin/torchserve --start --ts-config /home/torchserve/config.properties 

# Check if TorchServe started correctly
if [ $status -ne 0 ]; then
  echo "TorchServe failed to start with status $status." >> /var/log/torchserve-startup.log
  exit 1
fi

# Check if TorchServe is healthy
sleep 10
if ! curl -s http://localhost:8080/ping | grep -q 'Healthy'; then
  echo "TorchServe is not healthy." >> /var/log/torchserve-startup.log
  exit 1
fi

echo "TorchServe started and is healthy." >> /var/log/torchserve-startup.log

# Keep the script running to prevent supervisor from restarting
tail -f /dev/null
