#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoScript 主应用程序
游戏自动化脚本平台
"""

import os
import sys
import argparse
from pathlib import Path
from loguru import logger

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from core import AutoScriptEngine
from web.app import WebApp


def setup_logging():
    """设置日志"""
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 配置loguru
    logger.remove()  # 移除默认处理器
    
    # 控制台输出
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True
    )
    
    # 文件输出
    logger.add(
        log_dir / "autoscript.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )


def create_directories():
    """创建必要的目录"""
    directories = [
        "logs",
        "configs",
        "templates",
        "scripts",
        "debug",
        "plugins"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.debug(f"确保目录存在: {directory}")


def main():
    """主函数"""
    # 设置日志
    setup_logging()
    
    # 创建必要目录
    create_directories()
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="AutoScript - 万能游戏自动化脚本平台",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s                    # 启动Web界面
  %(prog)s --mode cli         # 命令行模式
  %(prog)s --host 0.0.0.0     # 指定监听地址
  %(prog)s --port 8080        # 指定监听端口
  %(prog)s --debug            # 启用调试模式
        """
    )
    
    parser.add_argument(
        '--mode', 
        choices=['web', 'cli'],
        default='web',
        help='运行模式 (默认: web)'
    )
    
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Web服务器监听地址 (默认: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Web服务器监听端口 (默认: 5000)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式'
    )
    
    parser.add_argument(
        '--config',
        default='configs/config.yaml',
        help='配置文件路径 (默认: configs/config.yaml)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='AutoScript v1.0.0'
    )
    
    args = parser.parse_args()
    
    # 显示启动信息
    logger.info("=" * 60)
    logger.info("AutoScript - 万能游戏自动化脚本平台")
    logger.info("版本: v1.0.0")
    logger.info("模式: " + args.mode)
    logger.info("=" * 60)
    
    try:
        if args.mode == 'web':
            # Web模式
            logger.info("启动Web界面...")
            web_app = WebApp()
            web_app.run(
                host=args.host,
                port=args.port,
                debug=args.debug
            )
        elif args.mode == 'cli':
            # CLI模式
            logger.info("启动命令行界面...")
            run_cli_mode(args.config)
        
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序运行失败: {e}")
        sys.exit(1)


def run_cli_mode(config_path: str):
    """运行CLI模式"""
    logger.info("初始化AutoScript引擎...")
    
    # 初始化引擎
    engine = AutoScriptEngine(config_path)
    
    # 启动引擎
    engine.start()
    
    logger.info("AutoScript引擎已启动")
    logger.info("输入 'help' 获取帮助信息")
    
    try:
        while True:
            try:
                command = input("\nAutoScript> ").strip()
                if not command:
                    continue
                
                # 处理命令
                process_cli_command(engine, command)
                
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\n使用 'quit' 命令退出")
                continue
    
    finally:
        # 清理资源
        engine.stop()
        engine.plugin_manager.cleanup()
        logger.info("AutoScript引擎已停止")


def process_cli_command(engine, command: str):
    """处理CLI命令"""
    parts = command.split()
    if not parts:
        return
    
    cmd = parts[0].lower()
    
    if cmd == 'help':
        print_help()
    elif cmd == 'quit' or cmd == 'exit':
        sys.exit(0)
    elif cmd == 'status':
        show_status(engine)
    elif cmd == 'plugins':
        show_plugins(engine)
    elif cmd == 'scripts':
        show_scripts(engine)
    elif cmd == 'templates':
        show_templates(engine)
    elif cmd == 'config':
        show_config(engine)
    elif cmd == 'run':
        if len(parts) < 2:
            print("用法: run <脚本名称>")
            return
        run_script(engine, parts[1])
    elif cmd == 'screenshot':
        take_screenshot()
    elif cmd == 'find':
        if len(parts) < 2:
            print("用法: find <模板名称>")
            return
        find_template(engine, parts[1])
    elif cmd == 'ocr':
        if len(parts) < 2:
            print("用法: ocr <图片路径>")
            return
        recognize_text(engine, parts[1])
    else:
        print(f"未知命令: {cmd}")
        print("输入 'help' 获取帮助信息")


def print_help():
    """打印帮助信息"""
    help_text = """
可用命令:
  help            显示此帮助信息
  quit/exit       退出程序
  status          显示系统状态
  plugins         显示插件列表
  scripts         显示脚本列表
  templates       显示模板列表
  config          显示配置信息
  run <script>    运行脚本
  screenshot      截图
  find <template> 查找模板
  ocr <image>     OCR识别
"""
    print(help_text)


def show_status(engine):
    """显示系统状态"""
    print("\n=== 系统状态 ===")
    print(f"引擎状态: {'运行中' if engine.is_running() else '已停止'}")
    
    queue_status = engine.script_queue.get_queue_status()
    print(f"队列状态: {'已暂停' if queue_status['paused'] else '运行中'}")
    print(f"总任务数: {queue_status['total_tasks']}")
    print(f"等待任务: {queue_status['pending_tasks']}")
    print(f"运行任务: {queue_status['running_tasks']}")
    print(f"完成任务: {queue_status['completed_tasks']}")
    print(f"失败任务: {queue_status['failed_tasks']}")
    
    plugin_status = engine.plugin_manager.get_plugin_status()
    print(f"插件总数: {plugin_status['total_plugins']}")
    print(f"启用插件: {plugin_status['enabled_plugins']}")
    print(f"禁用插件: {plugin_status['disabled_plugins']}")


def show_plugins(engine):
    """显示插件列表"""
    print("\n=== 插件列表 ===")
    plugins = engine.plugin_manager.get_all_plugin_info()
    
    if not plugins:
        print("暂无插件")
        return
    
    for name, plugin in plugins.items():
        status = "启用" if plugin['enabled'] else "禁用"
        print(f"{name}: {plugin['description']} ({status})")
        print(f"  版本: {plugin['version']}")
        print(f"  作者: {plugin['author']}")
        print(f"  动作: {', '.join(plugin['actions'])}")
        print()


def show_scripts(engine):
    """显示脚本列表"""
    print("\n=== 脚本列表 ===")
    tasks = engine.script_queue.get_all_tasks()
    
    if not tasks:
        print("暂无脚本")
        return
    
    for task in tasks:
        print(f"{task.id}: {task.name} - {task.status.value}")
        print(f"  创建时间: {task.created_at}")
        if task.started_at:
            print(f"  开始时间: {task.started_at}")
        if task.completed_at:
            print(f"  完成时间: {task.completed_at}")
        if task.error_message:
            print(f"  错误信息: {task.error_message}")
        print(f"  进度: {task.progress:.1f}%")
        print()


def show_templates(engine):
    """显示模板列表"""
    print("\n=== 模板列表 ===")
    templates = engine.template_matcher.get_template_list()
    
    if not templates:
        print("暂无模板")
        return
    
    for template in templates:
        print(f"- {template}")


def show_config(engine):
    """显示配置信息"""
    print("\n=== 配置信息 ===")
    config = engine.config_manager.get_all()
    
    import json
    print(json.dumps(config, indent=2, ensure_ascii=False))


def run_script(engine, script_name: str):
    """运行脚本"""
    print(f"\n执行脚本: {script_name}")
    
    # 这里可以实现从文件加载脚本配置
    script_data = {
        'name': script_name,
        'plugin_name': 'windows',  # 示例
        'actions': [
            {'type': 'screenshot', 'path': 'test.png'}
        ]
    }
    
    task_id = engine.execute_script(script_data)
    if task_id:
        print(f"脚本已添加到队列，任务ID: {task_id}")
    else:
        print("脚本添加失败")


def take_screenshot():
    """截图"""
    try:
        import pyautogui
        screenshot = pyautogui.screenshot()
        screenshot.save('screenshot.png')
        print("截图已保存为 screenshot.png")
    except Exception as e:
        print(f"截图失败: {e}")


def find_template(engine, template_name: str):
    """查找模板"""
    print(f"\n查找模板: {template_name}")
    
    result = engine.find_template(template_name)
    if result:
        print(f"找到模板!")
        print(f"置信度: {result.confidence:.2f}")
        print(f"位置: {result.location}")
        print(f"中心点: {result.center}")
    else:
        print("模板未找到")


def recognize_text(engine, image_path: str):
    """OCR识别"""
    print(f"\n识别图片: {image_path}")
    
    if not os.path.exists(image_path):
        print("图片文件不存在")
        return
    
    text = engine.recognize_text(image_path)
    if text:
        print(f"识别结果: {text}")
    else:
        print("未识别到文本")


if __name__ == '__main__':
    main()