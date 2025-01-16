#!/bin/bash

# 停止服务
./scripts/stop_server.sh

# 等待进程完全停止
sleep 2

# 启动服务
./scripts/start_server.sh 