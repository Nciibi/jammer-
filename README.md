# SDR Jammer Suite

A comprehensive collection of Software-Defined Radio (SDR) jamming tools for educational and research purposes. This suite includes implementations for both USRP and HackRF platforms with advanced features like channel hopping, graceful shutdowns, and robust error handling.

## ⚠️ Legal Disclaimer

**FOR EDUCATIONAL AND RESEARCH PURPOSES ONLY**

- Ensure you have proper authorization and licensing before transmitting
- Check local regulations regarding RF transmission
- Use only in controlled environments (labs, test ranges)
- Authors are not responsible for misuse or illegal activities
- Always comply with FCC/ITU regulations in your jurisdiction

## 📋 Features

- **Unified Launcher**: Single CLI interface for all platforms
- **Multiple Platform Support**: USRP B200, HackRF One, GNU Radio
- **Dual Operation Modes**: Channel hopping and full-band jamming
- **Automatic Waveform Generation**: On-demand IQ file creation
- **Python Package**: Importable modules for custom development
- **Channel Hopping**: Automatic frequency switching
- **Noise Generation**: Complex Gaussian noise transmission
- **Graceful Shutdown**: Signal handling and resource cleanup
- **Comprehensive Logging**: Detailed operation logs
- **Error Handling**: Robust error recovery mechanisms
- **Configurable Parameters**: Adjustable frequency, gain, timing

## 🛠️ Hardware Requirements

### USRP Implementation
- USRP B200 or compatible device
- USB 3.0 connection
- TX/RX antenna (2.4GHz/5GHz)
- UHD drivers installed

### HackRF Implementation  
- HackRF One or compatible device
- USB 2.0/3.0 connection
- Antenna with appropriate frequency range
- HackRF software suite

## 📦 Software Dependencies

### Python Dependencies
```bash
pip install uhd numpy
```

### System Dependencies
- **USRP**: UHD drivers (`uhd-config-info`)
- **HackRF**: HackRF tools (`hackrf_transfer`, `siggen`)
- **Linux**: Bash shell, GNU coreutils

## 🚀 Quick Start

### Unified Launcher (Recommended)
```bash
# Navigate to project directory
cd wifi-jammer

# Make launcher executable
chmod +x jammer/launch.py

# USRP single frequency jamming
python jammer/launch.py --usrp --freq 2.437e9 --gain 20

# USRP channel hopping
python jammer/launch.py --usrp --hop --hop-interval 0.5

# HackRF channel hopping
python jammer/launch.py --hackrf --hop

# HackRF full-band jamming
python jammer/launch.py --hackrf --full-band

# GNU Radio flowgraph
python jammer/launch.py --gnuradio
```

### Individual Components
```bash
# USRP channel hopper
python jammer/channel_hopper.py

# HackRF jammer (modes)
chmod +x jammer/hackrf_jammer_modes.sh
./jammer/hackrf_jammer_modes.sh hop
./jammer/hackrf_jammer_modes.sh full

# GNU Radio
gnuradio-companion gnuradio/wifi_jammer.grc
```

## 📖 Usage Examples

### Unified Launcher Interface
```bash
# View all options
python jammer/launch.py --help

# USRP examples
python jammer/launch.py --usrp --freq 2.437e9 --duration 30
python jammer/launch.py --usrp --hop --gain 25 --hop-interval 0.3

# HackRF examples  
python jammer/launch.py --hackrf --hop
python jammer/launch.py --hackrf --full-band

# GNU Radio
python jammer/launch.py --gnuradio
```

### Python API
```python
from jammer import Jammer, ChannelHopper

# USRP single frequency
jammer = Jammer(freq=2.437e9, gain=20, duration=60)
jammer.transmit()

# USRP channel hopping
hopper = ChannelHopper(rate=10e6, gain=22, hop_interval=0.5)
hopper.jam()
```

## � Project Structure

```
wifi-jammer/
├── README.md                 # This documentation
├── LICENSE                   # MIT license with educational disclaimer
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore patterns
├── jammer/                  # Main jammer package
│   ├── __init__.py          # Package initialization
│   ├── launch.py            # Unified launcher (CLI interface)
│   ├── jammer.py            # USRP single-frequency jammer
│   ├── channel_hopper.py    # USRP channel hopping jammer
│   ├── hackrf_jammer.sh     # HackRF jammer script
│   ├── hackrf_jammer_modes.sh # HackRF with mode selection
│   └── utils.py             # Shared utilities
├── gnuradio/                # GNU Radio integration
│   ├── wifi_jammer.grc      # GNU Radio flowgraph
│   └── screenshots/         # UI screenshots (optional)
├── iq_samples/              # Pre-generated IQ files
│   └── README.md            # IQ file documentation
└── docs/                    # Additional documentation
    └── reference.txt        # Technical reference
```

## 🔧 Configuration

### Frequency Bands
- **2.4GHz WiFi**: 2.412-2.462 GHz (Channels 1-11)
- **5GHz WiFi**: 5.180-5.745 GHz (Channels 36-149)
- **Custom**: Any frequency within hardware limits

### Default Parameters
| Parameter | USRP | HackRF (Hop) | HackRF (Full) |
|-----------|------|-------------|---------------|
| Sample Rate | 10 MS/s | 20 MS/s | 60 MS/s |
| TX Gain | 22 dB | 47 dB | 47 dB |
| Hop Interval | 500ms | 300ms | N/A |
| Bandwidth | 20MHz | 20MHz | 60MHz |
| Waveform | Generated | wifi_noise_20mhz.iq | wifi_noise_60mhz.iq |

## 📊 Monitoring & Logging

### Log Files
- **USRP**: `channel_hopper.log`
- **HackRF**: Console output

### Real-time Monitoring
```bash
# Monitor USRP logs
tail -f channel_hopper.log

# Monitor HackRF output (both modes)
./jammer/hackrf_jammer_modes.sh hop | tee hackrf_hop.log
./jammer/hackrf_jammer_modes.sh full | tee hackrf_full.log

# Monitor unified launcher output
python jammer/launch.py --usrp --hop | tee usrp.log
python jammer/launch.py --hackrf --hop | tee hackrf.log
```

### Performance Metrics
- Transmission rate (tx/sec)
- Frequency tuning accuracy
- Channel hop timing
- Error rates and recovery

## 🛡️ Safety Features

### Signal Handling
- **SIGINT/SIGTERM**: Graceful shutdown
- **Keyboard Interrupt**: Clean exit
- **Resource Cleanup**: Gain reset, thread termination

### Error Recovery
- Hardware re-initialization
- Frequency tuning verification
- Transmission retry logic
- Thread-safe operations

## 🧪 Testing

### Hardware Verification
```bash
# Check USRP
uhd_find_devices

# Check HackRF
hackrf_info
```

### Software Tests
```bash
# Test USRP connection
python3 -c "import uhd; print('UHD OK')"

# Test HackRF tools
hackrf_transfer --version
```

### Safe Transmission Test
```python
# Low power, short duration test
hopper = ChannelHopper(gain=5, hop_interval=1.0)
hopper.jam()
```

## 🔍 Troubleshooting

### Common Issues

**USRP Not Found**
```bash
# Check USB connection
lsusb | grep -i usrp

# Reinstall UHD drivers
sudo apt install uhd
```

**Permission Denied**
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Or use sudo (not recommended)
sudo python3 channel_hopper.py
```

**Frequency Tuning Errors**
- Check hardware frequency limits
- Verify antenna compatibility
- Reduce sample rate for stability

**Transmission Errors**
- Check USB bandwidth
- Reduce gain/power settings
- Verify IQ file integrity (HackRF)
- Check waveform generation (`siggen` availability)

**Waveform Issues**
```bash
# Manually generate missing waveforms
siggen -f 2437000000 -r 20M -n 60 -m qam64 -o wifi_noise_20mhz.iq
siggen -f 2437000000 -r 60M -n 60 -m qam64 -o wifi_noise_60mhz.iq

# Check waveform files
ls -la wifi_noise_*.iq
```

### Debug Mode
```bash
# Enable verbose logging
export UHD_LOG_LEVEL=debug
python3 channel_hopper.py
```

## 📚 Technical Details

### Signal Generation
- **USRP**: Real-time complex Gaussian noise generation
- **HackRF (Hop)**: 20MHz QAM64 waveform (`wifi_noise_20mhz.iq`)
- **HackRF (Full)**: 60MHz QAM64 waveform (`wifi_noise_60mhz.iq`)
- **Power Normalization**: Unit variance
- **Automatic Generation**: Missing waveforms created on-demand

### Channel Hopping Algorithm
1. **USRP**: Real-time frequency tuning with noise generation
2. **HackRF (Hop)**: Switch between pre-generated 20MHz waveforms
3. **HackRF (Full)**: Single 60MHz transmission covering all channels
4. **Timing**: 300ms hop interval (HackRF), 500ms (USRP)

### Thread Architecture
- **Main Thread**: Transmission loop
- **Hopper Thread**: Frequency switching
- **Signal Handler**: Graceful shutdown
- **Lock**: Thread synchronization

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure proper error handling
5. Submit pull request

### Development Guidelines
- Follow PEP 8 (Python)
- Add comprehensive logging
- Include signal handlers
- Test with actual hardware
- Document parameter ranges

## 📄 License

This project is provided for educational purposes. Users are responsible for compliance with local regulations.

## 🙏 Acknowledgments

- Ettus Research (USRP hardware)
- Great Scott Gadgets (HackRF)
- GNU Radio community
- SDR enthusiasts worldwide

## 📞 Support

For technical questions and issues:
1. Check troubleshooting section
2. Review log files for errors
3. Verify hardware compatibility
4. Test with minimal configuration

---

**Remember**: With great power comes great responsibility. Use these tools ethically and legally.
