#!/bin/bash

# Start all services in parallel
python api.py &
python agent.py dev &
python ./outboundService/entry.py dev &

# Keep script running until all background jobs exit
wait
