from tospaceidbmp280 import *
from machine import Pin, I2C
from tospaceidmpu6050 import MPU6050
from tospaceidmq2 import MQ2
from utime import sleep
led = Pin(25, Pin.OUT)
led.value(1)
print("================ ToSpace Edtech =================")
# smoke sensor part
pin=26
sensor = MQ2(pinData = pin, baseVoltage = 3.3)
print("Calibrating")
sensor.calibrate()
print("Calibration completed")
print("Base resistance:{0}".format(sensor._ro))

# mpu6050 part

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
imu = MPU6050(i2c)

# bmp part

# it helps in calibrating altitude .It is optional, else put ERROR = 0 
ERROR = 0 # hPa 

# declare pins for I2C communication
sclPin = Pin(1) # serial clock pin
sdaPin = Pin(0) # serial data pin

# Initiate I2C 
i2c_object = I2C(0,              # positional argument - I2C id
                 scl = sclPin,   # named argument - serial clock pin
                 sda = sdaPin,   # named argument - serial data pin
                 freq = 1000000) # named argument - i2c frequency

result = I2C.scan(i2c_object)
print("I2C scan result : ", result) # 118 in decimal is same as 0x76 in hexadecimal
if result != []:
    print("I2C connection successfull")
else:
    print("No devices found !")
# create a BMP 280 object
bmp280_object = BMP280(i2c_object,
                       addr = 0x76, # change it 
                       use_case = BMP280_CASE_WEATHER)

# configure the sensor
# These configuration settings give most accurate values in my case
# tweak them according to your own requirements

bmp280_object.power_mode = BMP280_POWER_NORMAL

bmp280_object.oversample = BMP280_OS_HIGH

bmp280_object.temp_os = BMP280_TEMP_OS_8

bmp280_object.press_os = BMP280_TEMP_OS_4


bmp280_object.standby = BMP280_STANDBY_250

bmp280_object.iir = BMP280_IIR_FILTER_2


print("BMP Object created successfully !")
sleep(2) # change it as per requirement
print("\n")


# Function for calculation altitude from pressure and temperature values
# because altitude() method is not present in the Library

def altitude_HYP(hPa , temperature):
    # Hypsometric Equation (Max Altitude < 11 Km above sea level)
    temperature = temperature
    local_pressure = hPa
    sea_level_pressure = 1013.25 # hPa      
    pressure_ratio = sea_level_pressure/local_pressure # sea level pressure = 1013.25 hPa
    h = (((pressure_ratio**(1/5.257)) - 1) * temperature ) / 0.0065
    return h


# altitude from international barometric formula, given in BMP 180 datasheet
def altitude_IBF(pressure):
    local_pressure = pressure    # Unit : hPa
    sea_level_pressure = 1013.25 # Unit : hPa
    
    pressure_ratio = local_pressure / sea_level_pressure
    
    altitude = 44330*(1-(pressure_ratio**(1/5.255)))
    return altitude



def mpu6050():
    ax=round(imu.accel.x,2)
    ay=round(imu.accel.y,2)
    az=round(imu.accel.z,2)
    gx=round(imu.gyro.x)
    gy=round(imu.gyro.y)
    gz=round(imu.gyro.z)
    tem=round(imu.temperature,2) 
    print("ax",ax,"\t","ay",ay,"\t","az",az,"\t","gx",gx,"\t","gy",gy,"\t","gz",gz,"\t","Temperature",tem,"        ",end="\r")
def smoke():
    print("Smoke: {:.1f}".format(sensor.readSmoke())+" - ", end="")
    print("LPG: {:.1f}".format(sensor.readLPG())+" - ", end="")
    print("Methane: {:.1f}".format(sensor.readMethane())+" - ", end="")
    print("Hydrogen: {:.1f}".format(sensor.readHydrogen()))

while True:
    mpu6050()
    print("\n")
    smoke()
    print("\n")
    # accquire temperature value in celcius
    temperature_c = bmp280_object.temperature # degree celcius
    
    # convert celcius to kelvin
    temperature_k = temperature_c + 273.15
    
    # accquire pressure value
    pressure = bmp280_object.pressure  # pascal
    
    # convert pascal to hectopascal (hPa)
    # 1 hPa = 100 Pa
    # Therefore 1 Pa = 0.01 hPa
    pressure_hPa = ( pressure * 0.01 ) + ERROR # hPa
    
    # accquire altitude values from HYPSOMETRIC formula
    h = altitude_HYP(pressure_hPa, temperature_k)
    
    # accquire altitude values from International Barometric Formula
    altitude = altitude_IBF(pressure_hPa)
    
    print("Temperature : ",temperature_c," Degree Celcius")
    print("Pressure : ",pressure," Pascal (Pa)")
    print("Pressure : ",pressure_hPa," hectopascal (hPa) or millibar (mb)")
    print("Altitude (Hypsometric Formula) : ", h ," meter")
    print("Altitude (International Barometric Formula) : ", altitude ," meter")
    
    # bmp280_object.print_calibration()
    # bmp280_object.load_test_calibration()
    print("\n")
    sleep(1)
    
