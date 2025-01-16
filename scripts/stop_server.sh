#!/bin/bash

# 初始化 conda
eval "$(conda shell.bash hook)"
conda activate f5-tts

PID_FILE="$(pwd)/f5_tts.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null; then
        kill "$PID"
        rm "$PID_FILE"
        echo "F5 TTS Server (PID: $PID) has been stopped"
    else
        echo "F5 TTS Server is not running"
        rm "$PID_FILE"
    fi
else
    echo "PID file not found"
fi 