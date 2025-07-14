#!/usr/bin/env python3
"""
AutoScript 主程序入口
"""
import sys
import os
import argparse
import logging

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.engine import AutoScriptEngine
from web.app import app

def setup_directories():
    """设置必要的目录"""
    directories = [
        'AutoScript/logs',
        'AutoScript/configs',
        'AutoScript/games',
        'AutoScript/templates',
        'AutoScript/temp'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AutoScript - 游戏自动化脚本管理系统')
    parser.add_argument('--config', default='AutoScript/configs/config.yaml', 
                       help='配置文件路径')
    parser.add_argument('--mode', choices=['web', 'cli'], default='web',
                       help='运行模式: web(Web界面) 或 cli(命令行)')
    parser.add_argument('--host', default='127.0.0.1', help='Web服务器主机地址')
    parser.add_argument('--port', type=int, default=5000, help='Web服务器端口')
    parser.add_argument('--debug', action='store_true', help='调试模式')
    
    args = parser.parse_args()
    
    # 设置目录
    setup_directories()
    
    print("=" * 60)
    print("AutoScript - 游戏自动化脚本管理系统 v2.0.0")
    print("=" * 60)
    
    try:
        # 初始化引擎
        print("正在初始化系统...")
        engine = AutoScriptEngine(args.config)
        
        if not engine.initialize():
            print("❌ 系统初始化失败")
            return 1
        
        print("✅ 系统初始化成功")
        
        if args.mode == 'web':
            # Web模式
            config = engine.config_manager
            host = args.host or config.get('web.host', '127.0.0.1')
            port = args.port or config.get('web.port', 5000)
            debug = args.debug or config.get('web.debug', False)
            
            print(f"\n🌐 启动Web界面...")
            print(f"📍 访问地址: http://{host}:{port}")
            print(f"🔧 调试模式: {'开启' if debug else '关闭'}")
            print("\n按 Ctrl+C 停止服务")
            
            try:
                app.run(host=host, port=port, debug=debug)
            except KeyboardInterrupt:
                print("\n正在停止服务...")
            
        else:
            # CLI模式
            print(f"\n🖥️  命令行模式启动")
            print("输入 'help' 查看可用命令，输入 'exit' 退出")
            
            while True:
                try:
                    command = input("\nAutoScript> ").strip()
                    
                    if command == 'exit':
                        break
                    elif command == 'help':
                        print_cli_help()
                    elif command == 'status':
                        print_system_status(engine)
                    elif command == 'games':
                        print_games_list(engine)
                    elif command == 'plugins':
                        print_plugins_list(engine)
                    elif command == 'queue':
                        print_queue_status(engine)
                    elif command.startswith('create-game'):
                        handle_create_game(engine, command)
                    else:
                        print(f"未知命令: {command}，输入 'help' 查看帮助")
                        
                except KeyboardInterrupt:
                    print("\n正在退出...")
                    break
                except Exception as e:
                    print(f"命令执行错误: {e}")
        
        # 清理资源
        print("正在清理资源...")
        engine.shutdown()
        print("✅ 系统已安全退出")
        return 0
        
    except Exception as e:
        print(f"❌ 系统启动失败: {e}")
        logging.exception("系统启动失败")
        return 1

def print_cli_help():
    """打印CLI帮助信息"""
    help_text = """
可用命令:
  help           - 显示此帮助信息
  status         - 显示系统状态
  games          - 显示游戏列表
  plugins        - 显示插件列表
  queue          - 显示队列状态
  create-game    - 创建新游戏 (格式: create-game <名称> <平台>)
  exit           - 退出程序
"""
    print(help_text)

def print_system_status(engine):
    """打印系统状态"""
    try:
        status = engine.get_system_status()
        print(f"\n系统状态: {status['status']}")
        print(f"游戏数量: {status['games']}")
        print(f"可用插件: {len(status['plugins'])}")
        print(f"执行队列: {len(status['queues'])}")
    except Exception as e:
        print(f"获取系统状态失败: {e}")

def print_games_list(engine):
    """打印游戏列表"""
    try:
        games = engine.get_games()
        if not games:
            print("\n暂无游戏")
            return
        
        print(f"\n游戏列表 (共 {len(games)} 个):")
        print("-" * 60)
        for game in games:
            print(f"名称: {game.name}")
            print(f"平台: {game.platform}")
            print(f"描述: {game.description or '暂无描述'}")
            print(f"脚本数量: {len(game.scripts)}")
            print("-" * 60)
    except Exception as e:
        print(f"获取游戏列表失败: {e}")

def print_plugins_list(engine):
    """打印插件列表"""
    try:
        plugins = engine.plugin_manager.get_available_plugins()
        if not plugins:
            print("\n暂无可用插件")
            return
        
        print(f"\n可用插件 (共 {len(plugins)} 个):")
        print("-" * 60)
        for name, plugin in plugins.items():
            print(f"名称: {name}")
            print(f"版本: {plugin['version']}")
            print(f"描述: {plugin['description']}")
            print(f"支持平台: {', '.join(plugin['platforms'])}")
            print(f"可用动作: {len(plugin['actions'])} 个")
            print("-" * 60)
    except Exception as e:
        print(f"获取插件列表失败: {e}")

def print_queue_status(engine):
    """打印队列状态"""
    try:
        if not engine.queue_manager:
            print("\n队列管理器未初始化")
            return
        
        queues = engine.queue_manager.get_all_queue_status()
        if not queues:
            print("\n暂无执行队列")
            return
        
        print(f"\n执行队列状态 (共 {len(queues)} 个):")
        print("-" * 60)
        for queue in queues:
            print(f"游戏: {queue['game_name']}")
            print(f"状态: {'运行中' if queue['enabled'] else '已停止'}")
            print(f"当前执行: {queue['running_script']['name'] if queue['running_script'] else '无'}")
            print(f"等待队列: {queue['queue_length']} 个")
            print("-" * 60)
    except Exception as e:
        print(f"获取队列状态失败: {e}")

def handle_create_game(engine, command):
    """处理创建游戏命令"""
    try:
        parts = command.split()
        if len(parts) < 3:
            print("用法: create-game <名称> <平台> [描述]")
            print("平台: android, windows, ios")
            return
        
        name = parts[1]
        platform = parts[2]
        description = " ".join(parts[3:]) if len(parts) > 3 else ""
        
        if platform not in ['android', 'windows', 'ios']:
            print("错误: 平台必须是 android, windows 或 ios")
            return
        
        game_id = engine.create_game(name, description, platform)
        if game_id:
            print(f"✅ 游戏创建成功: {name} (ID: {game_id})")
        else:
            print("❌ 游戏创建失败")
    except Exception as e:
        print(f"创建游戏失败: {e}")

if __name__ == '__main__':
    sys.exit(main())