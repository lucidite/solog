# simplog
Simple standalone log server

### Requirements
- Install [Docker](https://www.docker.com)
- Docker Desktop for desktops
  - www.docker.com/products/docker-desktop

### How to run
Use docker-compose commands:

- Build service
  `$ docker-compose build`
- Start service
  - create and start containers: 
    `$ docker-compose up -d`
  - build images and start containers:  
    `$ docker-compose up -d --build`   
- Stop service
  - stop services (containers will not be removed)
    `$ docker-compose stop`
  - Stop and remove containers, networks, images, and volumes
    `$ docker-compose down` 

docker-compose command help `$ docker-compose --help`