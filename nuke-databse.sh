#!/bin/bash

docker volume rm $(docker volume ls -qf name=postgres_data)
