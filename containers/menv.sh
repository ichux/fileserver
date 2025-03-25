#!/bin/bash

# Define variables
PC_USER=$(whoami)

ENV_FILE=".env"

mkdir -p ${HOME}/offloads

cp env.example .env
sed -i "s/^PC_USER=.*/PC_USER=$PC_USER/" "$ENV_FILE"
