#!/bin/bash
# 启动CRM系统

cd "$(dirname "$0")"

# 检查端口是否被占用
PORT=${PORT:-5001}
PID=$(lsof -ti:$PORT 2>/dev/null)

if [ ! -z "$PID" ]; then
    echo "端口 $PORT 已被进程 $PID 占用，正在终止..."
    kill -9 $PID 2>/dev/null
    sleep 2
fi

# 启动应用
echo "启动CRM系统，端口: $PORT"
python3 app.py --port $PORT

# 或者如果app.py支持环境变量
# export PORT=$PORT
# python3 app.py