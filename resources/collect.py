from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
import datetime
import time
import os

# collect.py is as of now only able to collect data for only one drone at a time
# this script also assumes that the drone creates a file /tmp/start_collect_vehicle_0 
# when arriving at its starting point, and deletes it when entering RTL mode

#Example <connection-string> for connecting to a drone through MAVProxy: udp:127.0.0.1:9002
veh = connect("<connection-string>", wait_ready=False) 

print("Connected")

while not os.path.isfile('/tmp/start_collect_vehicle_0'):
    time.sleep(0.2)
past_date = datetime.datetime.now()

while os.path.isfile('/tmp/start_collect_vehicle_0'):

    loc = veh.location.global_frame
    speed = veh.groundspeed 

    future_date = datetime.datetime.now()
    difference = (future_date - past_date)
    total_seconds = difference.total_seconds()


    print(str(loc) + "," + str(speed) + "," + str(total_seconds))

    time.sleep(0.1)







