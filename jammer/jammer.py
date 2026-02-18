#!/usr/bin/env python3
import uhd
import numpy as np
import time
import signal
import sys
import argparse
import logging
from datetime import datetime

class Jammer:
    def __init__(self, freq=2.437e9, rate=10e6, gain=20, duration=60):
        self.freq = freq      # WiFi Ch6 (2.437 GHz)
        self.rate = rate      # Sample rate
        self.gain = gain      # TX gain (0-30dB)
        self.duration = duration  # Seconds
        self.running = False
        
        # Setup logging
        self.setup_logging()
        
        # Validate and init USRP
        self.init_usrp()
        
        # Generate noise buffer (continuous Gaussian noise)
        self.noise = self.generate_noise(1024 * 1024)  # 1M samples buffer
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def setup_logging(self):
        """Configure logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'jammer_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def init_usrp(self):
        """Initialize USRP with error handling"""
        try:
            self.logger.info("Initializing USRP B200...")
            self.usrp = uhd.usrp.MultiUSRP("type=b200")
            
            # Get device info
            mboard_name = self.usrp.get_mboard_name()
            serial = self.usrp.get_mboard_serial()
            self.logger.info(f"USRP detected: {mboard_name} (S/N: {serial})")
            
            self.setup_usrp()
            
        except uhd.usrp.UsrpError as e:
            self.logger.error(f"USRP initialization failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during USRP init: {e}")
            raise
    
    def setup_usrp(self):
        """Configure TX chain with validation"""
        try:
            self.usrp.set_tx_rate(self.rate)
            actual_rate = self.usrp.get_tx_rate()
            self.logger.info(f"TX rate set: {actual_rate/1e6:.3f} MS/s")
            
            tune_req = uhd.libpyuhd.types.tune_request(self.freq)
            self.usrp.set_tx_freq(tune_req, 0)
            actual_freq = self.usrp.get_tx_freq(0)
            freq_error = abs(actual_freq - self.freq)
            
            if freq_error > 1e6:  # More than 1MHz error
                self.logger.warning(f"Frequency tuning error: {freq_error/1e3:.1f}kHz")
            
            self.usrp.set_tx_gain(self.gain, 0)
            actual_gain = self.usrp.get_tx_gain(0)
            self.logger.info(f"TX gain set: {actual_gain} dB")
            
            self.usrp.set_tx_antenna("TX/RX", 0)
            
            self.logger.info(f"USRP configured: {actual_freq/1e9:.3f}GHz, {actual_rate/1e6:.1f}MS/s, {actual_gain}dB")
            
        except uhd.usrp.UsrpError as e:
            self.logger.error(f"USRP configuration failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during setup: {e}")
            raise
    
    def generate_noise(self, nsamples):
        """Complex Gaussian noise (full spectrum jam)"""
        try:
            real = np.random.normal(0, 1, nsamples)
            imag = np.random.normal(0, 1, nsamples)
            noise = (real + 1j * imag) / np.sqrt(2)  # Normalize power
            self.logger.info(f"Generated {nsamples:,} noise samples")
            return noise
        except Exception as e:
            self.logger.error(f"Noise generation failed: {e}")
            raise

    def transmit(self):
        """Stream noise continuously with improved timing"""
        try:
            streamer = self.usrp.get_tx_streamer(uhd.usrp.StreamArgs("fc32", "sc16"))
            
            # Pre-fill TX buffer
            num_samps = len(self.noise)
            tx_buffer = np.zeros(num_samps, dtype=np.complex64)
            tx_buffer[:] = self.noise[:]
            
            self.logger.info(f"Starting jammer for {self.duration}s at {self.freq/1e9:.3f}GHz")
            self.running = True
            
            metadata = uhd.types.TXMetadata()
            start_time = time.time()
            transmission_count = 0
            last_progress = start_time
            
            # Calculate number of transmissions needed
            buffer_duration = num_samps / self.rate  # Duration of one buffer
            transmissions_needed = int(self.duration / buffer_duration)
            
            for i in range(transmissions_needed):
                if not self.running:
                    break
                    
                try:
                    streamer.send(tx_buffer, metadata)
                    transmission_count += 1
                    
                    # Update timestamp for next transmission
                    if metadata.has_time_spec:
                        metadata.time_spec = metadata.time_spec + uhd.types.TimeSpec(buffer_duration)
                    
                    # Progress logging every 5 seconds
                    current_time = time.time()
                    if current_time - last_progress >= 5.0:
                        elapsed = current_time - start_time
                        remaining = max(0, self.duration - elapsed)
                        rate = transmission_count / elapsed
                        self.logger.info(f"Progress: {elapsed:.1f}s elapsed, {remaining:.1f}s remaining, {rate:.1f} tx/sec")
                        last_progress = current_time
                        
                except uhd.usrp.UsrpError as e:
                    self.logger.error(f"Transmission error: {e}")
                    time.sleep(0.1)  # Brief pause before retry
                    continue
                    
            self.logger.info(f"Jamming completed: {transmission_count} transmissions in {time.time() - start_time:.1f}s")
            
        except uhd.usrp.UsrpError as e:
            self.logger.error(f"USRP transmission failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during transmission: {e}")
            raise
        finally:
            self.cleanup()
    
    def signal_handler(self, sig, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {sig} - stopping jammer")
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if hasattr(self, 'usrp') and self.usrp:
                # Reset gain to minimum
                self.usrp.set_tx_gain(0, 0)
                self.logger.info("TX gain reset to minimum")
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="USRP WiFi Jammer - Educational/Research Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python jammer.py --channel ch6 --gain 20 --duration 30
  python jammer.py --freq 2.437e9 --gain 25 --duration 60
  python jammer.py --channel ch11 --gain 15 --duration 120
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--channel', '-c', choices=['ch1', 'ch6', 'ch11', 'ch36', 'ch149'],
                     help='WiFi channel to jam')
    group.add_argument('--freq', '-f', type=float,
                     help='Frequency in Hz (e.g., 2.437e9 for 2.437 GHz)')
    
    parser.add_argument('--gain', '-g', type=int, default=20, choices=range(0, 31),
                     help='TX gain in dB (0-30, default: 20)')
    parser.add_argument('--duration', '-d', type=int, default=60,
                     help='Jamming duration in seconds (default: 60)')
    parser.add_argument('--rate', '-r', type=float, default=10e6,
                     help='Sample rate in Hz (default: 10e6)')
    
    return parser.parse_args()

if __name__ == "__main__":
    # WiFi channels mapping
    channels = {
        'ch1': 2.412e9, 'ch6': 2.437e9, 'ch11': 2.462e9,
        'ch36': 5.180e9, 'ch149': 5.745e9
    }
    
    try:
        args = parse_arguments()
        
        # Determine frequency
        if args.channel:
            if args.channel not in channels:
                print(f"Error: Unknown channel {args.channel}")
                sys.exit(1)
            freq = channels[args.channel]
            print(f"Using channel {args.channel} ({freq/1e9:.3f} GHz)")
        else:
            freq = args.freq
            print(f"Using custom frequency {freq/1e9:.3f} GHz")
        
        # Validate frequency range
        if freq < 1e6 or freq > 6e9:
            print("Error: Frequency must be between 1MHz and 6GHz")
            sys.exit(1)
        
        print("🚨 WARNING: This device will transmit RF signals!")
        print("📻 Ensure you have proper authorization and licensing")
        print("🔧 Press Ctrl+C to stop at any time")
        print()
        
        # Create and run jammer
        jammer = Jammer(
            freq=freq,
            rate=args.rate,
            gain=args.gain,
            duration=args.duration
        )
        
        jammer.transmit()
        
    except KeyboardInterrupt:
        print("\n👋 Jammer stopped by user")
    except uhd.usrp.UsrpError as e:
        print(f"\n💥 USRP Error: {e}")
        print("Check USRP connection and drivers")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)
    finally:
        print("🏁 Jammer shutdown complete")
