uart.setup(0, 9600, 8, 0, 1, 0)
print('init.lua ver 1.2')
wifi.setmode(wifi.STATION)
print('set mode=STATION (mode='..wifi.getmode()..')')
print('MAC: ',wifi.sta.getmac())
print('chip: ',node.chipid())
print('heap: ',node.heap())
-- wifi config start
wifi.sta.config("skyworks_plus","Innovation201604")
-- wifi config end
--
-- uart config start
require("main")
--require("telnet_srv")

--setupTelnetServer()

