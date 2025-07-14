"""
Web界面应用程序
提供可视化的操作界面和API接口
"""
import os
import json
import threading
from typing import Dict, Any, List
from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit, join_room, leave_room
from loguru import logger
from core import AutoScriptEngine


class WebApp:
    """Web应用程序类"""
    
    def __init__(self):
        """初始化Web应用"""
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'autoscript-secret-key'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # 初始化引擎
        self.engine = AutoScriptEngine()
        
        # 设置路由
        self._setup_routes()
        self._setup_socketio()
        
        logger.info("Web应用程序初始化完成")
    
    def _setup_routes(self):
        """设置路由"""
        
        @self.app.route('/')
        def index():
            """主页"""
            return render_template('index.html')
        
        @self.app.route('/api/engine/start', methods=['POST'])
        def start_engine():
            """启动引擎"""
            try:
                self.engine.start()
                return jsonify({'success': True, 'message': '引擎启动成功'})
            except Exception as e:
                logger.error(f"启动引擎失败: {e}")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/engine/stop', methods=['POST'])
        def stop_engine():
            """停止引擎"""
            try:
                self.engine.stop()
                return jsonify({'success': True, 'message': '引擎停止成功'})
            except Exception as e:
                logger.error(f"停止引擎失败: {e}")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/engine/status', methods=['GET'])
        def get_engine_status():
            """获取引擎状态"""
            try:
                status = {
                    'running': self.engine.is_running(),
                    'queue_status': self.engine.script_queue.get_queue_status(),
                    'plugin_status': self.engine.plugin_manager.get_plugin_status()
                }
                return jsonify({'success': True, 'data': status})
            except Exception as e:
                logger.error(f"获取引擎状态失败: {e}")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/plugins', methods=['GET'])
        def get_plugins():
            """获取插件列表"""
            try:
                plugins = self.engine.plugin_manager.get_all_plugin_info()
                return jsonify({'success': True, 'data': plugins})
            except Exception as e:
                logger.error(f"获取插件列表失败: {e}")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/plugins/<plugin_name>/enable', methods=['POST'])
        def enable_plugin(plugin_name):
            """启用插件"""
            try:
                result = self.engine.plugin_manager.enable_plugin(plugin_name)
                if result:
                    return jsonify({'success': True, 'message': f'插件 {plugin_name} 已启用'})
                else:
                    return jsonify({'success': False, 'message': f'插件 {plugin_name} 不存在'})
            except Exception as e:
                logger.error(f"启用插件失败: {e}")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/plugins/<plugin_name>/disable', methods=['POST'])
        def disable_plugin(plugin_name):
            """禁用插件"""
            try:
                result = self.engine.plugin_manager.disable_plugin(plugin_name)
                if result:
                    return jsonify({'success': True, 'message': f'插件 {plugin_name} 已禁用'})
                else:
                    return jsonify({'success': False, 'message': f'插件 {plugin_name} 不存在'})
            except Exception as e:
                logger.error(f"禁用插件失败: {e}")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/plugins/<plugin_name>/actions', methods=['GET'])
        def get_plugin_actions(plugin_name):
            """获取插件支持的动作"""
            try:
                plugin = self.engine.plugin_manager.get_plugin(plugin_name)
                if plugin:
                    actions = plugin.get_actions()
                    return jsonify({'success': True, 'data': actions})
                else:
                    return jsonify({'success': False, 'message': f'插件 {plugin_name} 不存在'})
            except Exception as e:
                logger.error(f"获取插件动作失败: {e}")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/scripts', methods=['POST'])
        def create_script():
            """创建脚本"""
            try:
                script_data = request.json
                task_id = self.engine.execute_script(script_data)
                if task_id:
                    return jsonify({'success': True, 'task_id': task_id})
                else:
                    return jsonify({'success': False, 'message': '脚本创建失败'})
            except Exception as e:
                logger.error(f"创建脚本失败: {e}")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/scripts/<task_id>', methods=['GET'])
        def get_script(task_id):
            """获取脚本状态"""
            try:
                task = self.engine.script_queue.get_task(task_id)
                if task:
                    return jsonify({'success': True, 'data': {
                        'id': task.id,
                        'name': task.name,
                        'status': task.status.value,
                        'progress': task.progress,
                        'created_at': task.created_at.isoformat(),
                        'started_at': task.started_at.isoformat() if task.started_at else None,
                        'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                        'error_message': task.error_message,
                        'result': task.result
                    }})
                else:
                    return jsonify({'success': False, 'message': '任务不存在'})
            except Exception as e:
                logger.error(f"获取脚本状态失败: {e}")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/scripts/<task_id>/cancel', methods=['POST'])
        def cancel_script(task_id):
            """取消脚本"""
            try:
                result = self.engine.script_queue.cancel_task(task_id)
                if result:
                    return jsonify({'success': True, 'message': '任务已取消'})
                else:
                    return jsonify({'success': False, 'message': '任务不存在或无法取消'})
            except Exception as e:
                logger.error(f"取消脚本失败: {e}")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/scripts', methods=['GET'])
        def get_scripts():
            """获取脚本列表"""
            try:
                tasks = self.engine.script_queue.get_all_tasks()
                data = []
                for task in tasks:
                    data.append({
                        'id': task.id,
                        'name': task.name,
                        'status': task.status.value,
                        'progress': task.progress,
                        'created_at': task.created_at.isoformat(),
                        'started_at': task.started_at.isoformat() if task.started_at else None,
                        'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                        'error_message': task.error_message
                    })
                return jsonify({'success': True, 'data': data})
            except Exception as e:
                logger.error(f"获取脚本列表失败: {e}")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/queue/pause', methods=['POST'])
        def pause_queue():
            """暂停队列"""
            try:
                self.engine.script_queue.pause_queue()
                return jsonify({'success': True, 'message': '队列已暂停'})
            except Exception as e:
                logger.error(f"暂停队列失败: {e}")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/queue/resume', methods=['POST'])
        def resume_queue():
            """恢复队列"""
            try:
                self.engine.script_queue.resume_queue()
                return jsonify({'success': True, 'message': '队列已恢复'})
            except Exception as e:
                logger.error(f"恢复队列失败: {e}")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/queue/clear', methods=['POST'])
        def clear_queue():
            """清理队列"""
            try:
                self.engine.script_queue.clear_completed()
                return jsonify({'success': True, 'message': '队列已清理'})
            except Exception as e:
                logger.error(f"清理队列失败: {e}")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/templates', methods=['GET'])
        def get_templates():
            """获取模板列表"""
            try:
                templates = self.engine.template_matcher.get_template_list()
                return jsonify({'success': True, 'data': templates})
            except Exception as e:
                logger.error(f"获取模板列表失败: {e}")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/templates/find', methods=['POST'])
        def find_template():
            """查找模板"""
            try:
                data = request.json
                template_name = data.get('template_name', '')
                result = self.engine.find_template(template_name, **data)
                if result:
                    return jsonify({'success': True, 'data': {
                        'template_name': result.template_name,
                        'confidence': result.confidence,
                        'location': result.location,
                        'size': result.size,
                        'center': result.center
                    }})
                else:
                    return jsonify({'success': False, 'message': '模板未找到'})
            except Exception as e:
                logger.error(f"查找模板失败: {e}")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/ocr/recognize', methods=['POST'])
        def recognize_text():
            """识别文本"""
            try:
                data = request.json
                result = self.engine.recognize_text(
                    data.get('image_path'),
                    data.get('region')
                )
                return jsonify({'success': True, 'data': result})
            except Exception as e:
                logger.error(f"识别文本失败: {e}")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/config', methods=['GET'])
        def get_config():
            """获取配置"""
            try:
                config = self.engine.config_manager.get_all()
                return jsonify({'success': True, 'data': config})
            except Exception as e:
                logger.error(f"获取配置失败: {e}")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/config', methods=['POST'])
        def update_config():
            """更新配置"""
            try:
                data = request.json
                for key, value in data.items():
                    self.engine.set_config(key, value)
                return jsonify({'success': True, 'message': '配置更新成功'})
            except Exception as e:
                logger.error(f"更新配置失败: {e}")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/screenshot', methods=['POST'])
        def take_screenshot():
            """截图"""
            try:
                import pyautogui
                screenshot = pyautogui.screenshot()
                screenshot_path = 'temp_screenshot.png'
                screenshot.save(screenshot_path)
                return send_file(screenshot_path, as_attachment=True)
            except Exception as e:
                logger.error(f"截图失败: {e}")
                return jsonify({'success': False, 'message': str(e)})
    
    def _setup_socketio(self):
        """设置SocketIO事件"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """客户端连接"""
            logger.info(f"客户端连接: {request.sid}")
            join_room('main')
            emit('connected', {'message': '连接成功'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """客户端断开连接"""
            logger.info(f"客户端断开连接: {request.sid}")
            leave_room('main')
        
        @self.socketio.on('execute_action')
        def handle_execute_action(data):
            """执行动作"""
            try:
                plugin_name = data.get('plugin_name', '')
                action = data.get('action', {})
                
                plugin = self.engine.plugin_manager.get_plugin(plugin_name)
                if plugin:
                    result = plugin.execute_action(action)
                    emit('action_result', {
                        'success': True,
                        'plugin_name': plugin_name,
                        'action': action,
                        'result': result
                    })
                else:
                    emit('action_result', {
                        'success': False,
                        'message': f'插件 {plugin_name} 不存在'
                    })
            except Exception as e:
                logger.error(f"执行动作失败: {e}")
                emit('action_result', {
                    'success': False,
                    'message': str(e)
                })
        
        @self.socketio.on('get_real_time_status')
        def handle_get_real_time_status():
            """获取实时状态"""
            try:
                status = {
                    'engine_running': self.engine.is_running(),
                    'queue_status': self.engine.script_queue.get_queue_status(),
                    'running_tasks': [
                        {
                            'id': task.id,
                            'name': task.name,
                            'progress': task.progress,
                            'status': task.status.value
                        }
                        for task in self.engine.script_queue.get_running_tasks()
                    ]
                }
                emit('real_time_status', status)
            except Exception as e:
                logger.error(f"获取实时状态失败: {e}")
                emit('error', {'message': str(e)})
    
    def broadcast_status_update(self):
        """广播状态更新"""
        try:
            status = {
                'engine_running': self.engine.is_running(),
                'queue_status': self.engine.script_queue.get_queue_status(),
                'running_tasks': [
                    {
                        'id': task.id,
                        'name': task.name,
                        'progress': task.progress,
                        'status': task.status.value
                    }
                    for task in self.engine.script_queue.get_running_tasks()
                ]
            }
            self.socketio.emit('status_update', status, room='main')
        except Exception as e:
            logger.error(f"广播状态更新失败: {e}")
    
    def start_status_broadcaster(self):
        """启动状态广播器"""
        def broadcaster():
            import time
            while True:
                self.broadcast_status_update()
                time.sleep(1)  # 每秒更新一次
        
        thread = threading.Thread(target=broadcaster, daemon=True)
        thread.start()
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """运行Web应用"""
        try:
            # 启动状态广播器
            self.start_status_broadcaster()
            
            # 启动引擎
            self.engine.start()
            
            logger.info(f"Web应用程序启动: http://{host}:{port}")
            self.socketio.run(self.app, host=host, port=port, debug=debug)
        except KeyboardInterrupt:
            logger.info("Web应用程序被中断")
        except Exception as e:
            logger.error(f"Web应用程序运行失败: {e}")
        finally:
            # 清理资源
            self.engine.stop()
            self.engine.plugin_manager.cleanup()


def create_app():
    """创建Web应用实例"""
    return WebApp()


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)