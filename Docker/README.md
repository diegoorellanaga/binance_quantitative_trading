# Docker instructions

This docker repository is a modification of the respository belonging to [appcelerator-archive](https://github.com/appcelerator-archive/docker-grafana).


## Instructions

To run Docker files and related extensions (docker-compose) you first need to install docker:

### Docker installation:

Follow the instructions found in this [link](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04).

### Docker-compose installation:

Follow the instructions found in this link [link](https://docs.docker.com/compose/install/#install-compose)

### Run influxdb-grafana

Once docker and docker-compose are installed do the following:

To run grafana and influxdb run the following command:

 - cd to folder containing docker-compose.yml in my case ~/docker-grafana/
 - sudo -s
 - type the root password
 - docker-compose up -d

The last command should download and run the necessary images. Then you will have influxdb and grafana running on your pc.
You should be able to access grafana by typing ***http://localhost:3000*** in your browser.

For information about parameters settings and data storage location go to this [link](https://github.com/diegoorellanaga/binance_quantitative_trading/tree/master/Docker/docker-grafana).

