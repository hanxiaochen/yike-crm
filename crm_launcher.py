#!/usr/bin/env python3
"""
CRM系统启动器
"""

import os
import sys
import signal
import subprocess
import time

def start_crm(port=5001):
    """启动CRM系统"""
    # 修改环境变量
    env = os.environ.copy()
    env['PORT'] = str(port)
    
    # 查找占用端口的进程并终止
    try:
        # 使用lsof查找端口占用
        result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
        if result.returncode == 0:
            pids = result.stdout.strip().split()
            for pid in pids:
                print(f"终止进程 {pid} (占用端口 {port})")
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    time.sleep(1)
                except ProcessLookupError:
                    pass
    except Exception as e:
        print(f"检查端口占用时出错: {e}")
    
    # 启动应用
    print(f"启动CRM系统，端口: {port}")
    print(f"访问地址: http://0.0.0.0:{port}")
    
    # 导入app并运行
    sys.path.insert(0, os.path.dirname(__file__))
    
    # 修改app的端口设置
    import app as crm_app
    
    # 直接运行，但需要修改app.py的最后一行
    # 临时方案：创建修改后的副本
    import tempfile
    import shutil
    
    # 读取原始app.py内容
    app_path = os.path.join(os.path.dirname(__file__), 'app.py')
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换端口设置
    if 'port=5000' in content:
        content = content.replace('port=5000', f'port={port}')
    elif 'port = 5000' in content:
        content = content.replace('port = 5000', f'port = {port}')
    
    # 创建临时文件
    temp_dir = tempfile.mkdtemp()
    temp_app_path = os.path.join(temp_dir, 'app_temp.py')
    
    with open(temp_app_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 导入临时模块
    import importlib.util
    spec = importlib.util.spec_from_file_location('crm_app_temp', temp_app_path)
    module = importlib.util.module_from_spec(spec)
    
    # 替换sys.modules中的app
    sys.modules['app'] = module
    
    try:
        # 执行模块
        spec.loader.exec_module(module)
        
        # 查找app实例并运行
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, crm_app.Flask):
                print("找到Flask应用，正在启动...")
                attr.run(host='0.0.0.0', port=port, debug=True)
                break
    finally:
        # 清理临时文件
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='启动CRM系统')
    parser.add_argument('--port', type=int, default=5001, help='端口号')
    args = parser.parse_args()
    
    start_crm(args.port)