#!/bin/bash

# 初始化 conda
eval "$(conda shell.bash hook)"
conda activate f5-tts

# 设置环境变量
export F5_WORK_DIR=$(pwd)
export F5_CACHE_DIR="${F5_WORK_DIR}/cache"
export F5_CHARACTER_DIR="${F5_WORK_DIR}/characters"
export F5_MODEL_PATH="${F5_WORK_DIR}/models/model.pt"
export F5_LOG_DIR="${F5_WORK_DIR}/logs"

# 创建必要的目录
mkdir -p "$F5_CACHE_DIR"
mkdir -p "$F5_CHARACTER_DIR"
mkdir -p "$F5_LOG_DIR"

# 检查是否已经运行
PID_FILE="${F5_WORK_DIR}/f5_tts.pid"
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null; then
        echo "F5 TTS Server is already running with PID $PID"
        exit 1
    else
        rm "$PID_FILE"
    fi
fi

# 启动服务器
nohup python -m f5_tts.api_server \
    --host 0.0.0.0 \
    --port 6006 \
    --cache-dir "$F5_CACHE_DIR" \
    --character-dir "$F5_CHARACTER_DIR" \
    > "${F5_LOG_DIR}/f5_tts.log" 2>&1 &

# 保存 PID
echo $! > "$PID_FILE"

echo "F5 TTS Server has been started with PID $!"
echo "Check logs at ${F5_LOG_DIR}/f5_tts.log" 