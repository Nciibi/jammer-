#!/usr/bin/env python3
"""
Unified launcher for WiFi jammer suite
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

def check_dependencies():
    """Check required dependencies"""
    deps = {
        'uhd': 'USRP support',
        'numpy': 'Numerical operations',
    }
    
    missing = []
    for dep, desc in deps.items():
        try:
            __import__(dep)
        except ImportError:
            missing.append(f"{dep} ({desc})")
    
    if missing:
        print("❌ Missing dependencies:")
        for m in missing:
            print(f"   - {m}")
        print("\nInstall with: pip install -r requirements.txt")
        return False
    
    return True

def launch_usrp_jammer(args):
    """Launch USRP-based jammer"""
    print("🚀 Launching USRP jammer...")
    
    if args.channel_hop:
        from jammer.channel_hopper import ChannelHopper
        hopper = ChannelHopper(
            rate=args.rate,
            gain=args.gain,
            hop_interval=args.hop_interval
        )
        hopper.jam()
    else:
        from jammer.jammer import Jammer
        jammer = Jammer(
            freq=args.frequency,
            rate=args.rate,
            gain=args.gain,
            duration=args.duration
        )
        jammer.transmit()

def launch_hackrf_jammer(args):
    """Launch HackRF-based jammer"""
    script_path = Path(__file__).parent / "hackrf_jammer_modes.sh"
    
    if not script_path.exists():
        print(f"❌ HackRF script not found: {script_path}")
        return
    
    mode = "full" if args.full_band else "hop"
    print(f"🚀 Launching HackRF jammer ({mode} mode)...")
    
    try:
        subprocess.run([str(script_path), mode], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ HackRF jammer failed: {e}")
    except KeyboardInterrupt:
        print("\n👋 HackRF jammer stopped")

def launch_gnuradio(args):
    """Launch GNU Radio flowgraph"""
    grc_path = Path(__file__).parent.parent / "gnuradio" / "wifi_jammer.grc"
    
    if not grc_path.exists():
        print(f"❌ GNU Radio flowgraph not found: {grc_path}")
        return
    
    print("🚀 Launching GNU Radio flowgraph...")
    
    try:
        subprocess.run(["gnuradio-companion", str(grc_path)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ GNU Radio failed: {e}")
    except FileNotFoundError:
        print("❌ GNU Radio not installed. Install with: sudo apt install gnuradio")

def main():
    parser = argparse.ArgumentParser(
        description="WiFi Jammer Suite - Unified Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launch.py --usrp --freq 2.437e9 --gain 20
  python launch.py --usrp --hop --hop-interval 0.5
  python launch.py --hackrf --hop
  python launch.py --hackrf --full-band
  python launch.py --gnuradio
        """
    )
    
    # Platform selection
    platform = parser.add_mutually_exclusive_group(required=True)
    platform.add_argument('--usrp', action='store_true', help='Use USRP platform')
    platform.add_argument('--hackrf', action='store_true', help='Use HackRF platform')
    platform.add_argument('--gnuradio', action='store_true', help='Use GNU Radio flowgraph')
    
    # USRP parameters
    parser.add_argument('--freq', '--frequency', type=float, default=2.437e9,
                       help='Target frequency (Hz)')
    parser.add_argument('--rate', type=float, default=10e6,
                       help='Sample rate (Hz)')
    parser.add_argument('--gain', type=int, default=20,
                       help='TX gain (dB)')
    parser.add_argument('--duration', type=int, default=60,
                       help='Transmission duration (seconds)')
    parser.add_argument('--hop', '--channel-hop', action='store_true',
                       help='Enable channel hopping (USRP only)')
    parser.add_argument('--hop-interval', type=float, default=0.5,
                       help='Channel hop interval (seconds)')
    
    # HackRF parameters
    parser.add_argument('--full-band', action='store_true',
                       help='Use full-band mode (HackRF only)')
    
    args = parser.parse_args()
    
    # Safety warning
    print("🚨 WARNING: This device will transmit RF signals!")
    print("📻 Ensure you have proper authorization and licensing")
    print("🔧 Press Ctrl+C to stop at any time")
    print()
    
    # Check dependencies
    if args.usrp and not check_dependencies():
        sys.exit(1)
    
    try:
        if args.usrp:
            launch_usrp_jammer(args)
        elif args.hackrf:
            launch_hackrf_jammer(args)
        elif args.gnuradio:
            launch_gnuradio(args)
    except KeyboardInterrupt:
        print("\n👋 Jammer stopped by user")
    except Exception as e:
        print(f"\n💥 Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
