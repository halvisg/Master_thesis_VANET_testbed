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
sumoBinary = "/usr/bin/sumo-gui" # <sumo-gui>: Path to sumo-gui binary
sumoCmd = [sumoBinary, "-c", "../example_traffic_scenario/line.sumocfg", "--step-length", step_length] # <sumocfg>: Path to sumocfg file
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

