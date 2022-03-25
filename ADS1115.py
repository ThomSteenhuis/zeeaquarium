import Adafruit_ADS1x15 as ADS

class ADS1115:
    def __init__(self):
        self.adc1 = ADS.ADS1115(address=0x48)
        self.adc2 = ADS.ADS1115(address=0x49)
    
    def read(self, channel = 0, gain = 1):
        if channel < 4:
            return self.adc1.read_adc(channel, gain)
        else:
            return self.adc2.read_adc(channel - 4, gain)