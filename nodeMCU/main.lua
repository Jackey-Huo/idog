tmr.alarm(0, 1000, 1, function()
   if wifi.sta.getip() == nil then
      print("Connecting to AP...")
   else
      print('IP: ',wifi.sta.getip())
      tmr.stop(0)
   end
end)

right_wheel = 1
left_wheel  = 2

pwm.setup(1, 1000, 0)
pwm.setup(2, 1000, 0)

pwm.start(1)
pwm.start(2)

function go_ahead()
    gpio.write(left_wheel, gpio.HIGH)
    gpio.write(right_wheel, gpio.HIGH)
end 

function stop()
    pwm.setduty(left_wheel, 0)
    pwm.setduty(right_wheel, 0)
end

function turn_left()
    gpio.write(left_wheel, gpio.LOW)
    gpio.write(right_wheel, gpio.HIGH)
end

function turn_right()
    gpio.write(left_wheel, gpio.HIGH)
    gpio.write(right_wheel, gpio.LOW)
end

function walk(ahead_speed, turn_speed) -- +left; -right
    if ahead_speed > 10 then
        go_ahead_speed = 10
    else
        go_ahead_speed = ahead_speed
    end
    if turn_speed > 0 then
        right_speed = go_ahead_speed + turn_speed
        if right_speed > 10 then
            right_speed = 10
        end
        pwm.setduty(left_wheel, 100 * go_ahead_speed)
        pwm.setduty(right_wheel, 100 * right_speed)
    else
        left_speed = ahead_speed - turn_speed
        if left_speed > 10 then
            left_speed = 10
        end
        pwm.setduty(left_wheel, 100 * left_speed)
        pwm.setduty(right_wheel, 100 * ahead_speed)
    end
end


