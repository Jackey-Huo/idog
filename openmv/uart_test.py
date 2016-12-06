
format_buf  = [0x68, 0x00, 0x00, 0x00, 0x00, 0x00, 0x68]
out_buf     = [0x68, 0x00, 0x00, 0x00, 0x00, 0x00, 0x16, 0x0d, 0x0a]
while True:
    in_buf = raw_input()
    if(ord(in_buf[0]) != format_buf[0] or \
       ord(in_buf[6]) != format_buf[6]):
        continue
    print ' '.join("{:02x}".format(ord(x)) for x in in_buf[1: 6])
    print ' '.join("{:02x}".format(x) for x in out_buf)


