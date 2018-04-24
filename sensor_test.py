import spidev 
import time 
import os

spi = spidev.SpiDev()
spi.open(0,0)

def ReadChannel(chan):
	if((chan<0) or (chan>7)):
		return -1
	adc = spi.xfer2([1, (8 + chan) << 4, 0])
	data = ((adc[1]&3) << 8) + adc[2]
	return data 

def ConvertVolts(data, places):
	volts = (data * 3.3)/1023
	volts = round(volts, places)
	return volts 

def ConvertTemp(data, places):
	temp = ((data * 330)/1023) - 50
	temp = round(temp, places)
	return temp 

temp_chan0 = 1
delay = 1
print "temp_level temp_volts temp"

while True: 
	temp_level = ReadChannel(temp_chan0)
	temp_volts = ConvertVolts(temp_level, 2)
	temp = ConvertTemp(temp_level, 2)

	print "---------------------------------"
	print temp_level, " ", temp_volts, " ", temp 

	time.sleep(delay)