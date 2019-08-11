#!/bin/bash
# if [ "$#" = 0 ]
# then
#     echo "Usage $0 plus command"
#     exit 1
# fi

# service=$1

service="s4.serveo.net:80:localhost:5000 serveo.net"

echo $service

is_running=`ps aux | grep "$service" | grep "ssh -R" | wc -l | awk '{print $1}'`
echo "Running $is_running"

if [ $is_running = "1" ] ;
then
    echo "Service is running $service"
else
    echo "Startint $service"

    initd=`ssh -R $service`
    echo "init $initd"

    # if [ $initd = "1" ];
    # then
    # startup=`ls /etc/init.d/ | grep $service`
    # echo -n "Found startap script /etc/init.d/${startup}. Start it? Y/n ? "
    # read answer

    #     if [ $answer = "y" -o $answer = "Y" ];
    #     then
    #     echo "Starting service..."
    #     /etc/init.d/${startup} start
    #     fi

    # fi

fi