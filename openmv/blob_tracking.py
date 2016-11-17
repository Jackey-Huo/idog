# Blob Detection Example
#
# This example shows off how to use the find_blobs function to find color
# blobs in the image. This example in particular looks for dark green objects.

import sensor, image, time, pyb

uart = pyb.UART(3)
uart.init(9600)
# For color tracking to work really well you should ideally be in a very, very,
# very, controlled enviroment where the lighting is constant...
red_threshold   = (   30,   65,  50,   95,   45,   75)
# You may need to tweak the above settings for tracking green things...
# Select an area in the Framebuffer to copy the color settings.

sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # use RGB565.
sensor.set_framesize(sensor.QQVGA) # use QQVGA for speed.
sensor.skip_frames(10) # Let new settings take affect.
sensor.set_whitebal(False) # turn this off.
clock = time.clock() # Tracks FPS.

for i in range(20):
    img = sensor.snapshot()

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

delimiter = ' '
while(True):
    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot() # Take a picture and return the image.pri

    blobs = img.find_blobs([red_threshold])
    if blobs:
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

        ahead_speed = square_orig - square
        if (ahead_speed < 0):
            ahead_speed = 0
        else:
            ahead_speed = int(ahead_speed / 100)

        turn_speed = int((x_centor_orig - x_centor) / 7)

        buf_list = ["walk(", str(ahead_speed), ",", str(turn_speed), ")"]
        buf = delimiter.join(buf_list)
        print(buf) # Note: Your OpenMV Cam runs about half as fast while
        uart.write(buf+'\n')
        print(square)
        print(square_orig)
    else:
        continue

