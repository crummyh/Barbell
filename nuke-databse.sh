#!/bin/bash
echo -e "\e[1;31mAre you sure you want to remove the dev database?\e[0m"
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    docker volume rm $(docker volume ls -qf name=postgres_data)
fi
