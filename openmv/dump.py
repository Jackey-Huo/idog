

import pyb, sensor, image, math
import time, os
from pyb import UART
from pyb import LED

sensor.reset()
sensor.set_framesize(sensor.QVGA)
sensor.set_pixformat(sensor.GRAYSCALE)
clock = time.clock()
roi = (110, 200, 100, 40) #(x, y, w, h)

format_buf  = [0x68, 0x00, 0x00, 0x00, 0x00, 0x00, 0x68]
out_buf     = [0x68, 0x00, 0x00, 0x00, 0x00, 0x00, 0x16, 0x0d, 0x0a]

uart = UART(3, 9600)
uart.init(9600, 8, None, 1, timeout=10)

high_threshold = (210, 255)

led = LED(2)
led.off()



def find_orient(img, _roi=roi):

    sum_pos = 0
    count   = 0
    for x in range(_roi[0], _roi[0] + _roi[2]):
        for y in range(_roi[1], _roi[1] + _roi[3]):
            #print(img.get_pixel(x, y))
            if(img.get_pixel(x, y) == 0):
                sum_pos = sum_pos + x
                count   = count + 1
    img.draw_rectangle(_roi, color=0)
    print(count)
    if(count == 0):
        return 0
    return sum_pos / count


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


while(True):
    clock.tick()
    img = sensor.snapshot()
    #print(clock.fps())
    img.binary([high_threshold])
    orient = find_orient(img)
    print(orient)
    if( 150 <= orient and orient <= 170):
        img.draw_string(160, 120, "go ahead!", color=0)

