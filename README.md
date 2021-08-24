# Master_thesis_VANET_testbed
This repository provides code and installation instruction to complement my master thesis. 

Installation instructions:

This installation instruction only covers setup and execution of simulated scenarios. The approach for using it with real drones is quite similar. There are two differences. When using real drones, there is no need for running ArduPilot SITL. The other difference is that MAVProxy needs to be started manually for each drone when real drones are used. For drones simulated with ArduPilot SITL, MAVProxy is automatically started for each drone instance. Also, these installation instructions are as of now only made for systems running Linux.

There are several prerequisites needed for using this testbed:

1. Download and install SUMO

SUMO can be installed either by downloading a binary from SUMO's [home page](https://sumo.dlr.de/docs/Downloads.php).
Alternatively, SUMO and related packages, like TraCI and netedit, can be installed using pip:

```console
foo@bar:~$ pip3 install eclipse-sumo
```
2. Download and install ArduPilot SITL
To install ArduPilot SITL, follow the instructions provided by ArduPilot, [found here](https://ardupilot.org/dev/docs/setting-up-sitl-on-linux.html)

3. Clone this git repository

```console
foo@bar:~$ git clone https://github.com/halvisg/Master_thesis_VANET_testbed.git
```

4. Configure virtual drones

5. Run example
An example scenario is included in the /code folder. Scenarios like this can be created with for instance netedit. 

