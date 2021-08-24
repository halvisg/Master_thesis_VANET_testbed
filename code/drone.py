import math
import os
import queue
import threading
from dronekit import VehicleMode
import time

"""
Class Vehicle
This class represents a pairing between a simulated vehicles and a MAVLink drone.

"""


class Vehicle:

    def __init__(self, name, pairing):
        self.name = name
        self.pairing = pairing
        self.locationQueue = queue.Queue(maxsize=0)
        self.next_step = True
        self.prev_location = []
        self.set_prev_bearing = 0
        self.current_bearing = None
        self.drone_turning = False
        self.drone_default_alt = 0
        self.drone_straight_cycle = 0
        self.prev_bearing = 0

    def start(self, handler):
        """
        Starts a thread of the runLocationQueue method that checks if the drone has any more locations to visit before
        concluding flight.
        :param handler: Object of class Handler
        :return:
        """
        thread = threading.Thread(target=self._runLocationQueue,
                                  args=(self.pairing, self.name, self.drone_default_alt, handler))
        handler.drone_threads.append(thread)
        thread.start()

    def _runLocationQueue(self, vehicle_obj, vehicle_id, alt, handler):

        """
        Controls the movement of drones.
        Each individual drone is given its own thread from updateLocationQueue, and
        is attached to the assigned simulation vehicle. The drone periodically checks whether
        the queue with coordinates is updated, and follows them in a FIFO manner.
        When all coordinates have been reached and the simulation has ended, the drone will
        enter Return to launch (RTL) mode.
        :param handler: Instance of Handler, used to monitor if the simulation is finished.
        :param alt: maximum altitude
        :param vehicle_obj: drone instance as obtained by running DroneKits connect() method
        :param vehicle_id: The corresponding ID in the SUMO simulation, typically "vehicle_<n>".
        """

        num_packets_sent = 0
        start_point_reached = False
        self._armAndTakeoff(vehicle_obj, int(alt))
        starting_point = self.locationQueue.get()[0]
        print("Going to start")

        self._gotoStartingPoint(vehicle_obj, starting_point)

        #Only start to duplicate path when all vehicles has reached their starting point
        handler.update_start_point_reached()
        while not handler.get_start_points_reached_indicator():
            time.sleep(0.1)

        
        #Uncomment next line if using in combination with collect.py
        #open('/tmp/start_collect_'+str(self.name), 'a').close()

        start_point_reached = True

        #Set max drone speed, change to fit scenario
        vehicle_obj.airspeed = 10

        while not handler.simulation_end:
            if self.locationQueue.empty():
                print(vehicle_id + "passing")
                pass

            else:
                if not start_point_reached:
                    starting_point = self.locationQueue.get()[0]
                    self._gotoStartingPoint(vehicle_obj, starting_point)
                    num_packets_sent += 1
                    start_point_reached = True

                prev = self.locationQueue.get()
                prev_a = prev[1]
                prev_loc = prev[0]
                if prev_a == 1:
                    vehicle_obj.simple_goto(prev_loc)
                    num_packets_sent += 1
                    a = 1
                    while a == 1 and handler.simulation_end is False:
                        cur = self.locationQueue.get()
                        a = cur[1]
                        loc = cur[0]
                        if a == 1:
                            vehicle_obj.simple_goto(loc)
                            num_packets_sent += 1
                        else:
                            self._leash(vehicle_obj, prev_loc)
                            num_packets_sent += 1
                        prev_loc = loc
                        time.sleep(0.1)
                else:
                    self._leash(vehicle_obj, loc)
                    num_packets_sent += 1

            time.sleep(0.1)

        # Simulation is finished, but drone still have to finish the waypoint-queue
        while not self.locationQueue.empty():
            prev = self.locationQueue.get()
            prev_a = prev[1]
            prev_loc = prev[0]
            if prev_a == 1:
                vehicle_obj.simple_goto(prev_loc)
                num_packets_sent += 1
                a = 1
                while a == 1 and not self.locationQueue.empty():
                    cur = self.locationQueue.get()
                    a = cur[1]
                    loc = cur[0]
                    if a == 1:
                        vehicle_obj.simple_goto(loc)
                        num_packets_sent += 1
                    else:
                        self._leash(vehicle_obj, prev_loc)
                        num_packets_sent += 1
                    prev_loc = loc
                    time.sleep(0.1)
            else:
                self._leash(vehicle_obj, prev_loc)
                num_packets_sent += 1
                time.sleep(0.1)

        self._leash(vehicle_obj, prev_loc)
        num_packets_sent += 1

        # Prints number of commands sent to a drone
        print("Number of packets sent:" + str(num_packets_sent))

        #Uncomment next line if using in combination with collect.py
        #os.remove('/tmp/start_collect_'+str(self.name))

        # Make sure the drone sets the mode to RTL
        while not vehicle_obj.mode == VehicleMode("RTL"):
            vehicle_obj.mode = VehicleMode("RTL")

    def _armAndTakeoff(self, vehicle_obj, aTargetAltitude):
        """
        Performs basic check on a drone before taking off to a specified altitude
        :param vehicle_obj: drone to arm
        :param aTargetAltitude: target altitude
        """

        print("Basic pre-arm checks")
        # Don't try to arm until autopilot is ready
        while not vehicle_obj.is_armable:
            print(" Waiting for vehicle to initialise...")
            time.sleep(2)

        print("Arming motors")
        # Confirm vehicle armed before attempting to take off
        while not vehicle_obj.armed:
            print(" Waiting for arming...")
            vehicle_obj.mode = VehicleMode("GUIDED")
            vehicle_obj.armed = True
            time.sleep(3)

        print("Taking off!")

        # Take off to target altitude
        vehicle_obj.simple_takeoff(aTargetAltitude)

        # Wait until the vehicle reaches a safe height before continuing,
        # otherwise the command may be overridden.
        while True:
            print(" Altitude: ", vehicle_obj.location.global_relative_frame.alt)
            # Break and return from function just below target altitude.
            if vehicle_obj.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
                print("Reached target altitude")
                break
            time.sleep(1)

    def _gotoStartingPoint(self, vehicle_obj, target):
        """
        Makes sure that a specified drone arrives at the starting point before executing the rest of the path
        :param vehicle_obj: specified drone #type: dronekit.Vehicle
        :param target: target position #type: LocationGlobalRelative
        :return:
        """
        current_location = vehicle_obj.location.global_relative_frame
        target_distance = self._get_distance_metres(current_location, target)
        vehicle_obj.simple_goto(target)

        while vehicle_obj.mode.name == "GUIDED":  # Stop action if we are no longer in guided mode.
            remaining_distance = self._get_distance_metres(vehicle_obj.location.global_frame, target)
            if remaining_distance <= 1:  # Just below target, in case of undershoot.
                print(vehicle_obj.airspeed)
                break
            time.sleep(0.1)

    def _leash(self, vehicle_obj, target):
        """
        Make sure that the drone comes close to the specified waypoint before accepting new commands.
        This method is used as a part of mitigating an issue where drones stop at each waypoint, hindering continuous
        motion of the drone. This issue is not a bug, but rather the drone behavior defined by ArduPilot.
        :param vehicle_obj: drone object #type dronekit.Vehicle
        :param target: target location #type: LocationGlobalRelative
        :return:
        """
        current_location = vehicle_obj.location.global_relative_frame
        target_distance = self._get_distance_metres(current_location, target)
        vehicle_obj.simple_goto(target)

        # Stop action if we are no longer in guided mode.
        while vehicle_obj.mode.name == "GUIDED":
            remaining_distance = self._get_distance_metres(vehicle_obj.location.global_frame, target)
            # Just below target, in case of undershoot.
            if remaining_distance <= 5:
                break
            time.sleep(0.1)

    def _get_distance_metres(self, aLocation1, aLocation2):
        """
        Returns the ground distance in metres between two LocationGlobal objects.

        This method is an approximation, and will not be accurate over large distances and close to the
        earth's poles. It is taken from the ArduPilot test code:
        https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
        """

        dlat = aLocation2.lat - aLocation1.lat
        dlong = aLocation2.lon - aLocation1.lon
        return math.sqrt((dlat * dlat) + (dlong * dlong)) * 1.113195e5

    def _straigth_run(self, vehicle_obj, handler):

        prev = self.locationQueue.get()
        prev_a = prev[1]
        prev_loc = prev[0]

        if prev_a == 1:
            vehicle_obj.simple_goto(prev_loc)
            a = 1
            while a == 1 and handler.simulation_end is False:
                cur = self.locationQueue.get()
                a = cur[1]
                loc = cur[0]
                if a == 1:
                    vehicle_obj.simple_goto(loc)
                else:
                    self._leash(vehicle_obj, prev_loc)
                prev_loc = loc
                time.sleep(0.1)

            self._leash(vehicle_obj, loc)

