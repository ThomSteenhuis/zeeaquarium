import Adafruit_ADS1x15 as ADS
import time

class ADS1115:
    def __init__(self):
        self.adc1 = ADS.ADS1115(address=0x48)
        self.adc2 = ADS.ADS1115(address=0x49)
        self.adc3 = ADS.ADS1115(address=0x4a)
        self.adc4 = ADS.ADS1115(address=0x4b)
    
    def read(self, channel = 0, gain = 1, data_rate = 128):
        if channel < 4:
            return self.adc1.read_adc(channel, gain, data_rate)
        elif channel < 8:
            return self.adc2.read_adc(channel - 4, gain, data_rate)
        elif channel < 12:
            return self.adc3.read_adc(channel - 8, gain, data_rate)
        else:
            return self.adc4.read_adc(channel - 12, gain, data_rate)
        