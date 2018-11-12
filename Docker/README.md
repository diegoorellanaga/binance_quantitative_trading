# Docker instructions

This docker repository is a modification of the respository belonging to [appcelerator-archive](https://github.com/appcelerator-archive/docker-grafana).


## Instructions

To run grafana and influxdb run the following command:

 - cd to folder containing docker-compose.yml in my case ~/docker-grafana/
 - sudo -s
 - type the root password
 - docker-compose up -d

The last command should download and run the necessary images. Then you will have influxdb and grafana running on your pc.
You should be able to access grafana by typing ***http://localhost:3000*** in your browser


