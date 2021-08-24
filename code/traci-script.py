#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import print_function
import time
import traci
import handler

#ARMED DRONES
#udp:127.0.0.1:8777 12
#udp:127.0.0.1:8999 7

step_length = "0.1"
sumoBinary = "<sumo-gui>" # <sumo-gui>: Path to sumo-gui binary
sumoCmd = [sumoBinary, "-c", "<sumocfg>>", "--step-length", step_length] # <sumocfg>: Path to sumocfg file
traci.start(sumoCmd)
step = 0
simulation_end = False
handler = handler.Handler(step_length,traci)

while traci.simulation.getMinExpectedNumber() > 0 and step < 1000:
    handler.step(traci)
    traci.simulationStep()
    step += 1
    time.sleep(0.1)

handler.simulation_end = True
traci.close(False)









# TODO:
# Implement Voltage check on batteries, if below a certain level, RTL
# 1. If new vehicles but no new drones, dont try to create thread.
# 2. Ensure RTL mode with while loop if drone is told to go outside geofence or over max altidtude
# 3. Look more into overshooting and undershooting
# 4. Some parameters must be tweked, i.e how long the drone waits to goto next waypoint, or how long it takes for the drone to check if there is a new location
# Maybe let the drone check the angle between current location and next point. It can skip all points that is in a direct line.
# - a = angle_to_next point
# while angle_delta < some_degrees
# Location = LocationQueue.get()
# simple_goto(Location)

# 5. Time synchronisation is a hard task and meant calls for further research. Now every drone has to wait for a new
# drone to enter the network at it's starting location, and vehicles may also not be able to keep up correct speed
# and acceleration. This will affect the reflection of the simulation.
# 6. Buffer overflow
#KNOWN BUGS
#-The syncing does not work if the simulation is finished before all drones hav reached their starting points.
#-The vehicles does not enter RTL moode iff they finish in a straigh line and the last point is sent to the drone before the simulation is finished.
#This is due to the blocking behavior of self.locationqueue.get() on line 134 in Vehicle.pyø

