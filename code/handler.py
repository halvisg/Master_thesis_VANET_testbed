import math
import queue
from dronekit import connect, LocationGlobalRelative
from numpy import arctan2
import drone


class Handler:
    """
        The Handler object uses information passed from SUMO through TraCI to create pairings between drones and
        simulated vehicles, as well as keeping track of active vehicles.
        :param step_length is used to calculate how often waypoints should be queued for drones
        :type step_length: str
        :param step_length Contains information about the SUMO simulation
        """
    # Default variables
    start_points_reached = 0
    drones_list = queue.Queue(maxsize=0)
    sync_edges = []
    step_length = 1
    send_interval = 2
    vehicle_list = []
    drone_threads = []
    simulation_end = False
    step_length = -1
    drones_list_altitude = queue.Queue(maxsize=0)
    available_drones = 0

    """
    Step length must be equal to the steplength in traci.
    """

    def __init__(self, step_length, traci):
        """
        Inits Handler with a traci object, as well as step length
        :param step_length: length of simulation step
        :param traci: traci object
        """

        self.traci = traci
        self.step_length = step_length
        self.start_points_reached = 0
        self.all_startpoints_reached = False
        with open('drones.conf', 'r') as drone_conf:
            for line in drone_conf:
                connection_string, altitude = line.split(" ")
                self.drones_list.put(connection_string.strip())
                self.drones_list_altitude.put(altitude.strip())
                self.available_drones += 1


    def update_start_point_reached(self):
        self.start_points_reached += 1
        print("HEI")
        print(len(self.vehicle_list))
        print(self.start_points_reached)
        if self.start_points_reached == len(self.vehicle_list):
            self.all_startpoints_reached = True

        else:
            self.all_startpoints_reached = False

    def get_start_points_reached_indicator(self):
        return self.all_startpoints_reached

    def _get_bearing(self, lat1, long1, lat2, long2):
        """
        Gets the bearing in degrees between two (latitude,longditude) coordinates on the WGS84 format
        :param lat1: latitude of first coordinate
        :param long1: longitude of first coordinate
        :param lat2: latitude of second coordinate
        :param long2: longitude of second coordinate
        :return:
        """
        dLon = (long2 - long1)
        x = math.cos(math.radians(lat2)) * math.sin(math.radians(dLon))
        y = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) - math.sin(math.radians(lat1)) * math.cos(
            math.radians(lat2)) * math.cos(math.radians(dLon))
        brng = arctan2(x, y)

        return math.degrees(brng)

    def _send_position(self, traci, sim_vehicle, cur_lon, cur_lat, straight_indicator):

        """
        Adds a waypoint to the queue of a specific drone
        :param traci: traci object
        :param sim_vehicle: Drone object to queue the location for
        :param cur_lon: longitude position at last time step
        :param cur_lat: latitude position at last time step
        :param straight_indicator: Indicated wheter the vehicle is running in a straight line. Information is used by the drones to speed up the path testing
        :return:
        """
        sim_vehicle.prev_location = [cur_lon, cur_lat]
        x, y = traci.vehicle.getPosition(sim_vehicle.name)
        lon, lat = traci.simulation.convertGeo(x, y)
        current_location = LocationGlobalRelative(lat, lon, sim_vehicle.drone_default_alt)
        sim_vehicle.locationQueue.put([current_location, straight_indicator])

    def step(self, traci):
        """
        Should be run every time traci.simulationstep() is executed. This functions takes care of pairing drones and vehicles.
        updatating the location queue of each drone as well as destroying finished vehicles.
        :param traci: traci object
        :return:
        """
        self.traci = traci
        self.send_interval = round(float(1 / float(self.step_length)))

        arrived_vehicles = traci.simulation.getArrivedIDList()
        for arrived_vehicle in arrived_vehicles:
            for v in self.vehicle_list:
                if v.name == arrived_vehicle:
                    self.vehicle_list.remove(v)

        for sim_vehicle in self.vehicle_list:
            sim_vehicle.next_step = False
            x, y = traci.vehicle.getPosition(sim_vehicle.name)
            cur_lon, cur_lat = traci.simulation.convertGeo(x, y)
            if len(sim_vehicle.prev_location) != 0:
                prev_lon = sim_vehicle.prev_location[0]
                prev_lat = sim_vehicle.prev_location[1]

            if len(sim_vehicle.prev_location) == 0:
                sim_vehicle.prev_location = [cur_lon, cur_lat]
                sim_vehicle.next_step = True
                sim_vehicle.set_prev_bearing = True

            # First checks if vehicle has initialized bearing calculation, then checks wheter it is going in a
            # straight line or not.
            if not sim_vehicle.next_step:

                if sim_vehicle.prev_bearing != 0:
                    sim_vehicle.current_bearing = self._get_bearing(prev_lat, prev_lon, cur_lat, cur_lon)
                    if abs(sim_vehicle.prev_bearing - sim_vehicle.current_bearing) > 5:
                        # We are in a turn, make sure to include the waypoint(s)
                        sim_vehicle.drone_turning = True
                        traci.vehicle.setColor(sim_vehicle.name, (255, 0, 0))
                        self._send_position(traci, sim_vehicle, cur_lon, cur_lat, 0)
                    else:
                        # Drone is running in a straight line, send waypoints rarely
                        traci.vehicle.setColor(sim_vehicle.name, (255, 0, 255))

                        if sim_vehicle.drone_turning:
                            # Drone has just turned, reset cycle
                            self._send_position(traci, sim_vehicle, cur_lon, cur_lat, 1)
                            sim_vehicle.drone_straight_cycle = 0
                            sim_vehicle.drone_turning = False
                            sim_vehicle.drone_straight_cycle += 1

                        elif sim_vehicle.drone_straight_cycle % self.send_interval == 0:
                            self._send_position(traci, sim_vehicle, cur_lon, cur_lat, 1)
                            sim_vehicle.drone_straight_cycle += 1

                        else:
                            sim_vehicle.drone_straight_cycle += 1

                    sim_vehicle.prev_bearing = self._get_bearing \
                        (prev_lat, prev_lon, cur_lat, cur_lon)

                else:
                    sim_vehicle.prev_bearing = self._get_bearing(prev_lat, prev_lon, cur_lat, cur_lon)

        new_vehicles = traci.simulation.getLoadedIDList()

        for new_vehicle in new_vehicles:
            self.available_drones -= 1
            if self.available_drones < 0 or self.drones_list.empty():
                break
            # If number of available drones is less than the number of simulated vehicles, we continue with the once
            # we have.
            if self.drones_list.empty():
                break

            # Set max speed for simulated vehicles, change to fit scenario
            traci.vehicle.setMaxSpeed(new_vehicle, 10)

            new_drone_connection_string = self.drones_list.get()
            new_drone_instance = connect(new_drone_connection_string, wait_ready=False)
            instance = drone.Vehicle(new_vehicle, new_drone_instance)
            self.vehicle_list.append(instance)
            instance.drone_default_alt = int(self.drones_list_altitude.get())
            instance.start(self)

            print(self.drone_threads)
