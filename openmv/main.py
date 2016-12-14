# Blob Detection Example
#
# This example shows off how to use the find_blobs function to find color
# blobs in the image. This example in particular looks for dark green objects.

import sensor, image, time, pyb

uart = pyb.UART(3)
uart.init(128000, 8, None, 1, timeout=10)

led_uart   = pyb.LED(2)
led_uart.off()

# blue led to show find target
led_track  = pyb.LED(1)
led_track.off()

# red led to show warning
led_failed = pyb.LED(3)
led_failed.off()
# For color tracking to work really well you should ideally be in a very, very,
# very, controlled enviroment where the lighting is constant...
red_threshold   = (   30,   65,  50,   95,   45,   75)
# You may need to tweak the above settings for tracking green things...
# Select an area in the Framebuffer to copy the color settings.

sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # use RGB565.
sensor.set_framesize(sensor.QVGA) # use QQVGA for speed.
sensor.skip_frames(20) # Let new settings take affect.
sensor.set_whitebal(False) # turn this off.
clock = time.clock() # Tracks FPS.

x_centor_orig_sum = 0
y_centor_orig_sum = 0
square_orig_sum   = 0


format_buf  = [0x68, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x16]
out_buf     = [0x68, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x16, 0x0d, 0x0a]

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




def get_orig_blob():
    x_centor_orig_sum = 0
    y_centor_orig_sum = 0
    square_orig_sum   = 0
    for i in range(10):  #cache 10 page and get the average
        while(True):     #cache the first capture with blob
            img = sensor.snapshot() # Take a picture and return the image.
            blobs = img.find_blobs([red_threshold])
            if blobs:
                square_orig = 0
                for b in blobs:
                    # Draw a rect around the blob.
                    img.draw_rectangle(b[0:4]) # rect
                    img.draw_cross(b[5], b[6]) # cx, cy
                    tmp_x_centor_orig = b[5]
                    tmp_y_centor_orig = b[6]
                    tmp_width_orig    = b[2]
                    tmp_height_orig   = b[3]
                    tmp_square_orig   = tmp_width_orig * tmp_height_orig
                    if(tmp_square_orig > square_orig):
                        x_centor_orig = tmp_x_centor_orig
                        y_centor_orig = tmp_y_centor_orig
                        square_orig = tmp_square_orig
                break
            else:
                print("failed!")
        x_centor_orig_sum = x_centor_orig_sum + x_centor_orig
        y_centor_orig_sum = y_centor_orig_sum + y_centor_orig
        square_orig_sum   = square_orig_sum + square_orig

    x_centor_orig = x_centor_orig_sum / 10
    y_centor_orig = y_centor_orig_sum / 10
    square_orig   = square_orig_sum   / 10
    return (x_centor_orig, y_centor_orig, square_orig)

def find_speed(img, x_centor_orig, y_centor_orig, square_orig):
    blobs = img.find_blobs([red_threshold])
    if blobs:
        led_failed.off()
        square = 0
        for b in blobs:
            # Draw a rect around the blob.
            img.draw_rectangle(b[0:4]) # rect
            img.draw_cross(b[5], b[6]) # cx, cy
            tmp_x_centor = b[5]
            tmp_y_centor = b[6]
            tmp_square = b[2] * b[3]
            if(tmp_square > square):
                square = tmp_square
                x_centor = tmp_x_centor
                y_centor = tmp_y_centor

        ahead_speed = (square_orig - square) \
                            + (y_centor_orig - y_centor)
        if (ahead_speed <= 0):
            ahead_speed = 0
        else:
            if 30 < ahead_speed and ahead_speed < 100:
                ahead_speed = 1
            else:
                ahead_speed = int(ahead_speed / 100)

        turn_speed = int((x_centor_orig - x_centor) / 20)
        left_speed = ahead_speed - turn_speed
        right_speed = ahead_speed + turn_speed
        return (ahead_speed, max(min(int(left_speed), 10), 0),
            max(min(int(right_speed), 10), 0))
    else: #turn on the red led to show warning
        led_track.off()
        led_failed.on()
        print("fuck!")
        return ()


orig_blob = (160, 82, 500)

#while True:
#    uart.write(org_out_buf(0x01, 0x00, 0x03, 0x03))


while(True):
    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot() # Take a picture and return the image.
    #print(clock.fps()) # Note: Your OpenMV Cam runs about half as fast while
    # connected to your computer. The FPS should increase once disconnected.
    orient = find_speed(img, orig_blob[0], orig_blob[1], orig_blob[2])
    if(orient):
        print(orient) #just for debug
        led_failed.off()
        uart.write(org_out_buf(0x01, 0x00, orient[2], orient[1]))
        led_track.toggle()
    else:
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
