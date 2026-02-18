#!/usr/bin/env python3
"""
Shared utilities for WiFi jammer suite
"""

import numpy as np
import logging
from datetime import datetime

def setup_logging(log_file=None, level=logging.INFO):
    """Setup logging configuration"""
    if log_file is None:
        log_file = f"jammer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def generate_noise(nsamples, power=1.0):
    """Generate complex Gaussian noise"""
    real = np.random.normal(0, 1, nsamples)
    imag = np.random.normal(0, 1, nsamples)
    noise = (real + 1j * imag) / np.sqrt(2)
    return noise * np.sqrt(power)

def validate_frequency(freq, bands=None):
    """Validate frequency is within supported bands"""
    if bands is None:
        bands = {
            '2.4GHz': (2.4e9, 2.5e9),
            '5GHz': (5.0e9, 6.0e9)
        }
    
    for band_name, (min_freq, max_freq) in bands.items():
        if min_freq <= freq <= max_freq:
            return True, band_name
    
    return False, None

def format_frequency(freq):
    """Format frequency for display"""
    if freq >= 1e9:
        return f"{freq/1e9:.3f}GHz"
    elif freq >= 1e6:
        return f"{freq/1e6:.1f}MHz"
    else:
        return f"{freq:.0f}Hz"

def calculate_eirp(tx_power_dbm, antenna_gain_dbi, cable_loss_db=0):
    """Calculate Effective Isotropic Radiated Power"""
    return tx_power_dbm + antenna_gain_dbi - cable_loss_db

# WiFi channel frequencies
WIFI_CHANNELS = {
    # 2.4 GHz channels
    **{f"ch{i}": 2.412e9 + (i-1) * 5e6 for i in range(1, 15)},
    # 5 GHz channels (UNII-1, UNII-2, UNII-3)
    **{f"ch{i}": 5.180e9 + (i-36) * 20e6 for i in range(36, 65)},
    **{f"ch{i}": 5.745e9 + (i-149) * 20e6 for i in range(149, 166)},
}

def get_wifi_channels(band='2.4GHz'):
    """Get WiFi channel frequencies for specified band"""
    if band == '2.4GHz':
        return {k: v for k, v in WIFI_CHANNELS.items() if k.startswith('ch') and int(k[2:]) <= 14}
    elif band == '5GHz':
        return {k: v for k, v in WIFI_CHANNELS.items() if k.startswith('ch') and int(k[2:]) >= 36}
    else:
        return WIFI_CHANNELS
