# Master_thesis_VANET_testbed

This README.md provides code and installation instruction to complement my master thesis. 
Also included in this file, are instructions on how to run an example traffic scenario that is included in this repository.

## Installation instructions:

This installation instruction only covers setup and execution of simulated scenarios. The approach for using it with real drones is quite similar. There are two differences. When using real drones, there is no need for running ArduPilot SITL. The other difference is that MAVProxy needs to be started manually for each drone when real drones are used. For drones simulated with ArduPilot SITL, MAVProxy is automatically started for each drone instance. Also, these installation instructions are as of now only made for systems running Linux.

First we present the installation process. Then, we describe how to execute an example traffic scenario with two drones, that is included in this repository.

This guide has been tested on a clean image of Ubuntu 18.04.3.

There are several prerequisites needed for using this testbed:

### 1. Clone this repo

```console
foo@bar:~$ git clone https://github.com/halvisg/Master_thesis_VANET_testbed.git
```

### 2. Download and install SUMO

SUMO can be installed either by downloading a binary from SUMO's [home page](https://sumo.dlr.de/docs/Downloads.php), however, this is not the approach we recommend.
SUMO and related packages, like TraCI and netedit, can also be installed directly from apt. We recommend installation using apt, as this guide created for that.

Install SUMO through apt:

```console
foo@bar:~$ sudo apt-get install sumo sumo-tools sumo-doc
```
**Note**: If this does not work, you may have to add the SUMO repository before installing the packages, with the commands below. The try to install again.

```console
foo@bar:~$ sudo add-apt-repository ppa:sumo/stable
foo@bar:~$ sudo apt-get update
```

After installation, it is important to add export the SUMO_HOME environment variable. If installing from binary, the path might not be the same:

```console
foo@bar:~$ export SUMO_HOME=/usr/share/sumo
```

Then, make the environment variable permanent (Skipping this step may cause trouble later):

```console
foo@bar:~$ echo "export SUMO_HOME=/usr/share/sumo" >> ~/.bashrc
```

To utilize TraCI, we have to add SUMO to the PYTHONPATH environment variable:

```console
foo@bar:~$ export PYTHONPATH="$SUMO_HOME/tools:$PYTHONPATH"
```

Again, make the environment variable permanent (Skipping this step may cause trouble later):

```console
foo@bar:~$ echo 'export PYTHONPATH="$SUMO_HOME/tools:$PYTHONPATH"' >> ~/.bashrc
```

Now, SUMO should be installed, and TraCI should be ready for use.

### 3. Install dronekit and numpy
dronekit and numpy as neccessary packages that needs to be installed.
both packages can be installed directly through pip:

```console
foo@bar:~$ pip3 install dronekit
```
```console
foo@bar:~$ pip3 install numpy
```

### 4. Clone and install ArduPilot/ArduPilot SITL
These instructions have been boiled down from the [installation documentation,](https://ardupilot.org/dev/docs/building-setup-linux.html#building-setup-linux) provided by ArduPilot.


```console
foo@bar:~$ git clone https://github.com/ArduPilot/ardupilot.git
foo@bar:~$ cd ardupilot
foo@bar:~$ git submodule update --init --recursive
```

Now that we have cloned ArduPilot, we have to install some required packages.
From the ardupilot directory, run:

```console
foo@bar:~$ Tools/environment_install/install-prereqs-ubuntu.sh -y
```

### 5. Install QGroundControl
The installation instructions from this step is taken from QGroundControl's [documentation](https://docs.qgroundcontrol.com/master/en/getting_started/download_and_install.html).

Some initial setup is required for QGroundControl to run correctly:

```console
foo@bar:~$ sudo usermod -a -G dialout $USER
foo@bar:~$ sudo apt-get remove modemmanager -y
foo@bar:~$ sudo apt install gstreamer1.0-plugins-bad gstreamer1.0-libav gstreamer1.0-gl -y
```

The download link for QGroundControl can be found [here](https://s3-us-west-2.amazonaws.com/qgroundcontrol/latest/QGroundControl.AppImage) (direct [link](https://s3-us-west-2.amazonaws.com/qgroundcontrol/latest/QGroundControl.AppImage)).

After downloading, we need to add execute-permissions to the binary:

```console
foo@bar:~$ cd ~/Downloads
foo@bar:~$ chmod u+x QGroundControl.AppImage
```
QGroundControl can now be launched:

```console
foo@bar:~$ ~/Downloads/QGroundControl.AppImage
```

### 6. Install MAVProxy

MAVProxy is used to split data stream so that we can connect to the drones from multiple sources. In our case QGroundControl and the testbed.
The following instructions were extraced from ArduPilot [documentation](https://ardupilot.org/mavproxy/docs/getting_started/download_and_installation.html).

install MAVProxy and add it to the *PATH*.

```console
foo@bar:~$ pip3 install PyYAML mavproxy --user
foo@bar:~$ echo "export PATH=$PATH:$HOME/.local/bin" >> ~/.bashrc
```


### 6. Configure ArduPilot SITL

Now, we have downloaded and installed all the required software and tools to run our testbed.
Next, we need to configure our virtual drones. Here, as an example, we will configure two drones.
The approach shown here can be extended to more than two drones, we will just use two as an example.
The instructions have been adapted from ArduPilot [documentation](https://ardupilot.org/dev/docs/using-sitl-for-ardupilot-testing.html).


#### 6.1 Add origin

The simulated drones need to know where on earth they will be located when initialized. 
In this example, the drones will have their home location set to Udduvoll Airfield in Trondheim.

We add this location to a configuration file, defined by ardupilot.
From the ardupilot folder:

```console
foo@bar:~$ echo "UDD=63.319511,10.272135,0,60" >> Tools/autotest/locations.txt
```

#### 6.2 Set unique value SYSID_THISMAV

For the MAVLink data streams to be routed correctly, each drone needs a unique SYS_THISMAV (MAVLink ID).
To do this, we need to make a parameter file for each drone, that will be during initialization.
We create one parameter file for each drone.

Again, from the ardupilot folder:

```console
foo@bar:~$ echo SYSID_THISMAV 1 > Tools/autotest/default_params/drone1.parm
```
```console
foo@bar:~$ echo SYSID_THISMAV 2 > Tools/autotest/default_params/drone2.parm
```

## Run the example

We have included a sample scenario, in the directory called example_traffic_scenario.
To run this example, there are a couple of steps that are needed.
First, we need to start our simulated UAVs. Then we tell our testbed how it should connect to them.
Then, we need to start QGroundControl, and connect to the drones from here as well. This is to get a visual overview of the drones on a map.
Finally, we can start our testbed. 

### 1. Initialize simulated UAVs
ArduPilot provides a script called *sim_vehicle.py*, that initializes an instance of MAVProxy

Again, from the ardupilot folder run the following command to start the first drone:

***Note*** that the first time a drone is initialized with ArduPilot SITL, it will take some time to compile needed libraries. Please be patient. 

```console
foo@bar:~$ Tools/autotest/sim_vehicle.py -L UDD -v ArduCopter --console --add-param-file Tools/autotest/default_params/drone1.parm -I1 --out=tcpin:0.0.0.0:8901 --out=127.0.0.1:9001
```
In another console, initialize the other drone: 
```console
foo@bar:~$ Tools/autotest/sim_vehicle.py -L UDD -v ArduCopter --console --add-param-file Tools/autotest/default_params/drone2.parm -I2 --out=tcpin:0.0.0.0:8902 --out=127.0.0.1:9002
```

For each drone, this will start a MAVPRoxy instance, this instance listens on the following ports for each drone:

- drone 1: tcp:127.0.0.1:8901, udp:127.0.0.1:9001
- drone 2: tcp:127.0.0.1:8902, udp:127.0.0.1:9002

### 2. Connect via QGroundControl

The next to last step is to connect QGroundControl to the drones.
To do this, we need to define communication links the QGroundControl uses.

We will use the following ports:

- drone 1: tcp:8901
- drone 2: tcp:8902

1. Start QGroundControl.AppImage
2. Clik the QGroundControl logo located in the upper left corner of the screen
3. Click ***Application Settings***
4. Click ***Comm Links***,located in menu on the left
5. Click ***Add***

![QGC GUI](https://home.samfundet.no/~halvogro/ting/bilder/drone1.png)

6. Insert the same information from the image above into the fields.
7. Click ***Ok***
8. Repeat steps 5, 6 and 7 for the second drone, using the correct port number, and a different *Name*.
9. In turn, click the rows that were added to QGroundControl and click ***Connect***, in the bottom of the screen.
10. Exit back to the map by clicking ***Back*** in the top left of the screen.

QGroundControl should now have connected to both drones, and they should be visible on the map.
It should look something like this:

![QGC GUI](https://home.samfundet.no/~halvogro/ting/bilder/dronefinish.png)

### 3. Configure the testbed

The last step is do provide the testbed with information on how to connect to the drones, as well as their altitude.

We tell the testbed to connect to the drones ont he following ports:

- drone 1: udp:8901
- drone 2: udp:8902

The altitude at which each drone will fly is, in this example:

- drone 1: 10
- drone 2: 5

Navigate to the directory where this repository was cloned, and find the, located inside this pro and edit the file *drones.conf* to contain this informati

Edit 
```console
foo@bar:~$ cd Master_thesis_VANET_testbed/code
```

Verify that the file *drones.conf* contains the following lines:

```console
foo@bar:~$ cat drones.conf

udp:127.0.0.1:9001 10
udp:127.0.0.1:9002 5
```

### 4. Execute the tesbed

Finally, we can execute the testbed.
In a new terminal, ***make sure*** that you are located in the *Master_thesis_VANET_testbed/code* directory.
Then, initialize the testbed:

```console
foo@bar:~$ python3 traci-script.py
```

SUMO will open, and initialize the traffic scenario.
The final step is to press the play button in SUMO, shown in the image below. 

![QGC GUI](https://home.samfundet.no/~halvogro/ting/bilder/route.png)

This will start the simulated simulated in SUMO as well as the drones.
In QGroundControl, the drones can be observed on a map, as well as other information like their speed and altitude.
