# Hello World Example
#
# Welcome to the OpenMV IDE! Click on the gear button above to run the script!

import sensor, image, time
import os
from pyb import UART
from pyb import LED

sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # or sensor.GRAYSCALE
sensor.set_framesize(sensor.QVGA) # or sensor.QQVGA (or others)
sensor.skip_frames(10) # Let new settings take affect.
clock = time.clock() # Tracks FPS.

format_buf  = [0x68, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x16]
out_buf     = [0x68, 0x01, 0x00, 0x00, 0x00, 0x00, 0x01, 0x16, 0x0d, 0x0a]

uart = UART(3, 9600)
uart.init(9600, 8, None, 1, timeout=1)

led = LED(2)
led.off()

def check_in_buf(in_buf):
    if(len(in_buf) < 8):
        return False
    #print(' '.join(hex(x) for x in in_buf[0: 8]))
    if(in_buf[0] != format_buf[0] or \
        in_buf[7] != format_buf[7]):
        return False
    check_bit = 0
    for i in range(1, 6):   #check bit varify
        check_bit = check_bit + in_buf[i]
    if check_bit != in_buf[6]:
        return False


def org_out_buf(cmd, data1=0x00, data2=0x00, data3=0x00, data4=0x00):
    out_buf[1] = cmd
    out_buf[2] = data1
    out_buf[3] = data2
    out_buf[4] = data3
    out_buf[5] = data4
    check_bit = 0
    for i in range(1, 6):   #calculate check bit
        check_bit = check_bit + out_buf[i]
    out_buf[6] = check_bit
    return ''.join(chr(x) for x in out_buf)


uart.write(org_out_buf(0x01, 0x01, 0x21, 0x34))

while(True):
    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot() # Take a picture and return the image.
    #print(clock.fps()) # Note: Your OpenMV Cam runs about half as fast while
    # connected to your computer. The FPS should increase once disconnected.
    if(uart.any()):
        led.on()
        in_buf = uart.readall()
        if check_in_buf(in_buf) == False:
            continue
        print(' '.join(hex(x) for x in in_buf[1: 6]))
        in_buf2 = in_buf[8: ]
        if check_in_buf(in_buf2) == False:
            continue
        print(' '.join(hex(x) for x in in_buf2[1: 6]))
        led.off()
