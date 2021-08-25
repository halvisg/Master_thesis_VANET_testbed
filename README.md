# Master_thesis_VANET_testbed
This repository provides code and installation instruction to complement my master thesis. 

# Installation instructions:

This installation instruction only covers setup and execution of simulated scenarios. The approach for using it with real drones is quite similar. There are two differences. When using real drones, there is no need for running ArduPilot SITL. The other difference is that MAVProxy needs to be started manually for each drone when real drones are used. For drones simulated with ArduPilot SITL, MAVProxy is automatically started for each drone instance. Also, these installation instructions are as of now only made for systems running Linux.

This guide has been tested on a clean image of Ubuntu 18.04.3.

There are several prerequisites needed for using this testbed:

## 1. Clone this repo

## 2. Download and install SUMO

SUMO can be installed either by downloading a binary from SUMO's [home page](https://sumo.dlr.de/docs/Downloads.php).
Alternatively, SUMO and related packages, like TraCI and netedit, can be installed using pip. We recommend installing with pip, as this guide created for that.

Install SUMO through pip:

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

To utilize TraCI, we have to add SUMO to the PYTHONPATH environment variable:


```console
foo@bar:~$ export PYTHONPATH="$SUMO_HOME/tools:$PYTHONPATH"
```

Now, SUMO should be installed, and TraCI should be ready for use.

## 3. Install dronekit and numpy
dronekit and numpy as neccessary packages that needs to be installed.
both packages can be installed directly through pip:

```console
foo@bar:~$ pip3 install dronekit
```
```console
foo@bar:~$ pip3 install numpy
```

## 4. Install necessary Python-packages:


4. Clone and install ArduPilot/ArduPilot SITL
These instructions have been concretisized from the [installation page](https://ardupilot.org/dev/docs/building-setup-linux.html#building-setup-linux) provided by ArduPilot.


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

## 5. Install QGroundControl
The installation instructions from this step is taken from QGroundControl's [documentation](https://docs.qgroundcontrol.com/master/en/getting_started/download_and_install.html).

Some initial setup is required for QGroundControl to run correctly:

```console
foo@bar:~$ sudo usermod -a -G dialout $USER
foo@bar:~$ sudo apt-get remove modemmanager -y
foo@bar:~$ sudo apt install gstreamer1.0-plugins-bad gstreamer1.0-libav gstreamer1.0-gl -y
```

The download link for QGroundControl can be found [here](https://s3-us-west-2.amazonaws.com/qgroundcontrol/latest/QGroundControl.AppImage) (direct [link](https://s3-us-west-2.amazonaws.com/qgroundcontrol/latest/QGroundControl.AppImage)).

After downloading, we may have to add execute-permissions:


```console
foo@bar:~$ cd ~/Downloads
foo@bar:~$ chmod u+x QGroundControl.AppImage
```
Now, QGroundControl can be launched:

```console
foo@bar:~$ ~/Downloads/QGroundControl.AppImage
```

## 6. Configure ArduPilot SITL

Now, we have downloaded and installed all the required software and tools to run our testbed.



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

TODO: Add correct path to scenario and sumo-gui
