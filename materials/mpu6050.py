#!/usr/bin/python
import smbus
import math
import time

# 전원 관리 레지스터
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c
step_flag = 0   # 걸음을 인식하는 동작을 할 경우를 저장하는 플래그 변수
sum_step = 0    # 걸음 수(현재 걸음 수로 저장하나 엔드디바이스 개발 시 신호만 보내서 어플에서 카운트 할 예정)

def read_byte(adr):
    
    return bus.read_byte_data(address, adr)


def read_word(adr):
    
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high << 8) + low
    
    return val

 
def read_word_2c(adr):

    val = read_word(adr)

    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def dist(a,b):

    return math.sqrt((a*a)+(b*b))

def get_x_rotation(x,y,z):

    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)

def get_y_rotation(x,y,z):

    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)

 
bus = smbus.SMBus(1) # 라즈베리파이 버전 2 미만은 (0), 그 이상은 (1)로 지정
address = 0x68       # i2cdetect 명령을 통해 읽은 주소 값

# sleep 모드인 mpu6050 동작 시키기
bus.write_byte_data(address, power_mgmt_1, 0)

try:
	while True:
                
                time.sleep(0.5)

#                print ("--------------------------------------------------------")
#                print ("=>X, Y, Z 자이로 센서 데이터")
#                print ("---------")

                gyro_xout = read_word_2c(0x43)
                gyro_yout = read_word_2c(0x45)
                gyro_zout = read_word_2c(0x47)

#                print ("gyro_xout: ", gyro_xout, " scaled: ", (gyro_xout / 131))
#                print ("gyro_yout: ", gyro_yout, " scaled: ", (gyro_yout / 131))
#                print ("gyro_zout: ", gyro_zout, " scaled: ", (gyro_zout / 131))

#                print ("=>가속 데이터")
#                print ("------------------")
            
                accel_xout = read_word_2c(0x3b)          
                accel_yout = read_word_2c(0x3d)
                accel_zout = read_word_2c(0x3f)

                accel_xout_scaled = accel_xout / 16384.0
                accel_yout_scaled = accel_yout / 16384.0
                accel_zout_scaled = accel_zout / 16384.0

                print ("accel_xout: ", accel_xout, " scaled: ", accel_xout_scaled)
                print ("accel_yout: ", accel_yout, " scaled: ", accel_yout_scaled)
                print ("accel_zout: ", accel_zout, " scaled: ", accel_zout_scaled)
                print ("x rotation: " , get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled))
                print ("y rotation: " , get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled))
                print ("--------------------------------------------------------")


except KeyboardInterrupt:
     GPIO.cleanup()