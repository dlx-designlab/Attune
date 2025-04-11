import serial
import time

s = serial.Serial('/dev/ttyAMA0', 115200)

s.write(('\r\n\r\n').encode())
time.sleep(2)
s.flushInput()


cmd = 'G0 X0 Y0 Z0'
cmd = '$H'
print(f"Sending: {cmd}")
s.write((cmd + '\n').encode())
grbl_out = s.readline()
print(f"got response: {grbl_out.strip()}")

s.close()