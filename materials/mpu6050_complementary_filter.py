# Implementation of Complimentary Filter for MPU-6050 6-DOF IMU
# 
# Author: Philip Salmony [pms67@cam.ac.uk]
# Date: 4 August 2018

#from imu import *
from time import sleep, time
from math import sin, cos, tan, pi
import smbus
import math

class IMU:
        
    def __init__(self):
        
        self.power_mgmt_1 = 0x6b
        self.power_mgmt_2 = 0x6c
        self.addr = 0x68
        
        self.bus = smbus.SMBus(1)
        self.bus.write_byte_data(self.addr, self.power_mgmt_1, 0)
        
        print("[IMU] Initialised.")
    
    # rad/s
    def get_gyro_bias(self, N=100):
        bx = 0.0
        by = 0.0
        bz = 0.0
        
        for i in range(N):
            [gx, gy, gz] = self.get_gyro()
            bx += gx
            by += gy
            bz += gz
            sleep(0.01)
            
        return [bx / float(N), by / float(N), bz / float(N)]            
        
    # rad/s
    def get_gyro(self):
        gx = self.read_word_2c(0x43) * math.pi / (180.0 * 131.0)
        gy = self.read_word_2c(0x45) * math.pi / (180.0 * 131.0)
        gz = self.read_word_2c(0x47) * math.pi / (180.0 * 131.0)
        return [gx, gy, gz]        
        
    # m/s^2
    def get_acc(self):
        ax = self.read_word_2c(0x3b) / 16384.0
        ay = self.read_word_2c(0x3d) / 16384.0
        az = self.read_word_2c(0x3f) / 16384.0
        return [ax, ay, az]
    
    # rad
    def get_acc_angles(self):
        [ax, ay, az] = self.get_acc()
        phi = math.atan2(ay, math.sqrt(ax ** 2.0 + az ** 2.0))
        theta = math.atan2(-ax, math.sqrt(ay ** 2.0 + az ** 2.0))
        return [phi, theta]
      
    def read_byte(self, reg_adr):
        return self.bus.read_byte_data(self.addr, reg_adr)
    
    def read_word(self, reg_adr):
        high = self.bus.read_byte_data(self.addr, reg_adr)
        low = self.bus.read_byte_data(self.addr, reg_adr + 1)
        val = (high << 8) + low
        return val
    
    def read_word_2c(self, reg_adr):
        val = self.read_word(reg_adr)
        if (val >= 0x8000):
            return -((65535 - val) + 1)
        else:
            return val
        

imu = IMU()

# Iterations and sleep time
N = 1000
sleep_time = 0.01

# Filter coefficient
alpha = 0.1

print("Calculating average gyro bias...")
[bx, by, bz] = imu.get_gyro_bias(200)

# Complimentary filter estimates
phi_hat = 0.0
theta_hat = 0.0

print("Running...")

# Measured sampling time
dt = 0.0
start_time = time()

for i in range(N):
    dt = time() - start_time
    start_time = time()
    
    # Get estimated angles from raw accelerometer data
    [phi_hat_acc, theta_hat_acc] = imu.get_acc_angles()
    
    # Get raw gyro data and subtract biases
    [p, q, r] = imu.get_gyro()
    p -= bx
    q -= by
    r -= bz
    
    # Calculate Euler angle derivatives 
    phi_dot = p + sin(phi_hat) * tan(theta_hat) * q + cos(phi_hat) * tan(theta_hat) * r
    theta_dot = cos(phi_hat) * q - sin(phi_hat) * r
    
    # Update complimentary filter
    phi_hat = (1 - alpha) * (phi_hat + dt * phi_dot) + alpha * phi_hat_acc
    theta_hat = (1 - alpha) * (theta_hat + dt * theta_dot) + alpha * theta_hat_acc   
    
    # Display results
    print("Phi: " + str(round(phi_hat * 180.0 / pi, 1)) + " | Theta: " + str(round(theta_hat * 180.0 / pi, 1)))

    sleep(sleep_time)