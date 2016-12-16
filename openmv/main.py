# Blob Detection Example
#
# This example shows off how to use the find_blobs function to find color
# blobs in the image. This example in particular looks for dark green objects.

import sensor, time, pyb
from Vision_contr import find_speed, org_out_buf,\
                    check_in_buf, initPID

# config uart
uart = pyb.UART(3)
uart.init(128000, 8, None, 1, timeout=10)

# config led
led_uart   = pyb.LED(2) # green led to show uart
led_uart.off()
led_track  = pyb.LED(1) # blue led to show find target
led_track.off()
led_failed = pyb.LED(3) # red led to show warning
led_failed.off()

# cam sensor config
sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # use RGB565.
sensor.set_framesize(sensor.QVGA) # use QQVGA for speed.
sensor.skip_frames(20) # Let new settings take affect.
sensor.set_whitebal(False) # turn this off.
clock = time.clock() # Tracks FPS.

# set orig blob, can also call get_init_blob in Vision_contr
orig_blob = (160, 82, 500)

# pid init
pid = initPID()

while(True):
    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot() # Take a picture and return the image.
    #print(clock.fps()) # Note: Your OpenMV Cam runs about half as fast while
    # connected to your computer. The FPS should increase once disconnected.
    orient = find_speed(img, orig_blob, pid)
    if(orient):
        print(orient) #just for debug
        led_failed.off()
        led_track.on()
        uart.write(org_out_buf(0x01, 0x00, orient[2], orient[1]))
        led_track.toggle()
    else:
        led_track.off()
        led_failed.on()
        uart.write(org_out_buf(0x01, 0x00, 0x00, 0x00))
    if(uart.any()):
        led_track.off()
        led_failed.off()
        in_buf = uart.readall()
        if check_in_buf(in_buf) == False:
            continue
        print(' '.join(hex(x) for x in in_buf[1: 6]))
        in_buf2 = in_buf[8: ]
        if check_in_buf(in_buf2) == False:
            continue
        else:
            led_uart.on()
        print(' '.join(hex(x) for x in in_buf2[1: 6]))
        led_uart.off()
