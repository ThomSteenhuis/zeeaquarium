import Adafruit_ADS1x15

class ADS1115:
    def __init__(self):
        self.adc = Adafruit_ADS1x15.ADS1115()
    
    def read(self, channel = 0, gain = 1):
        data = self.adc.read_adc(channel, gain)
        return data