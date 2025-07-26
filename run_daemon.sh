#!/bin/bash

# Define the path to the daemon Python script
DAEMON_PATH="./src/daemon_process.py"
# Define the name of the daemon process
DAEMON_NAME="DaemonProcess"
# Define the log file path
LOG_DIR="./logs"
LOG_FILE="$LOG_DIR/$DAEMON_NAME.log"
# Define the PID file path
RUN_DIR="./run"
PID_FILE="$RUN_DIR/$DAEMON_NAME.pid"

# Ensure log and run directories exist
mkdir -p "$LOG_DIR"
mkdir -p "$RUN_DIR"

# Function to start the daemon process
start() {
    echo "Starting $DAEMON_NAME..."
    nohup python3 $DAEMON_PATH > $LOG_FILE 2>&1 &
    echo $! > $PID_FILE
    echo "$DAEMON_NAME started. (PID: $(cat $PID_FILE))"
}

# Function to stop the daemon process
stop() {
    if [ -f $PID_FILE ]; then
        PID=$(cat $PID_FILE)
        echo "Stopping $DAEMON_NAME..."
        kill $PID
        echo "$DAEMON_NAME stopped."
        rm $PID_FILE
    else
        echo "$DAEMON_NAME is not running."
    fi
}

# Function to check the status of the daemon process
status() {
    if [ -f $PID_FILE ]; then
        PID=$(cat $PID_FILE)
        if ps -p $PID > /dev/null
        then
           echo "$DAEMON_NAME is running. (PID: $PID)"
        else
           echo "$DAEMON_NAME is not running, but PID file exists."
        fi
    else
        echo "$DAEMON_NAME is not running."
    fi
}

# Function to restart the daemon process
restart() {
    stop
    start
}

# Command line argument handling
case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    status)
        status
        ;;
    restart)
        restart
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart}"
        exit 1
esac 