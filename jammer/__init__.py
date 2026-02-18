"""
WiFi Jammer Suite

A comprehensive collection of SDR jamming tools for educational and research purposes.
Supports both USRP and HackRF platforms with advanced features like channel hopping.
"""

__version__ = "1.0.0"
__author__ = "WiFi Jammer Project"
__license__ = "MIT"

from .jammer import Jammer
from .channel_hopper import ChannelHopper

__all__ = ["Jammer", "ChannelHopper"]
