"""
AutoScript Web界面
"""
import os
import sys
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import uuid

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.engine import get_engine
from core.script_queue import QueuedScript, ScriptStatus

app = Flask(__name__)
app.config['SECRET_KEY'] = 'autoscript_secret_key'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 获取引擎实例
engine = get_engine()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """系统状态API"""
    try:
        status = engine.get_system_status()
        return jsonify({'success': True, 'data': status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/games', methods=['GET'])
def api_get_games():
    """获取游戏列表"""
    try:
        platform = request.args.get('platform')
        games = engine.get_games(platform)
        
        # 转换为可序列化的格式
        games_data = []
        for game in games:
            game_data = {
                'id': game.id,
                'name': game.name,
                'description': game.description,
                'platform': game.platform,
                'package_name': game.package_name,
                'enabled': game.enabled,
                'created_at': game.created_at,
                'script_count': len(game.scripts)
            }
            games_data.append(game_data)
        
        return jsonify({'success': True, 'data': games_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/games', methods=['POST'])
def api_create_game():
    """创建游戏"""
    try:
        data = request.get_json()
        
        name = data.get('name')
        description = data.get('description', '')
        platform = data.get('platform')
        package_name = data.get('package_name', '')
        
        if not name or not platform:
            return jsonify({'success': False, 'error': '游戏名称和平台不能为空'})
        
        game_id = engine.create_game(name, description, platform, package_name)
        
        if game_id:
            return jsonify({'success': True, 'data': {'game_id': game_id}})
        else:
            return jsonify({'success': False, 'error': '创建游戏失败'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/games/<game_id>/scripts', methods=['GET'])
def api_get_game_scripts(game_id):
    """获取游戏脚本列表"""
    try:
        script_type = request.args.get('type')
        scripts = engine.game_manager.get_game_scripts(game_id, script_type)
        
        scripts_data = []
        for script in scripts:
            script_data = {
                'id': script.id,
                'name': script.name,
                'description': script.description,
                'script_type': script.script_type,
                'enabled': script.enabled,
                'created_at': script.created_at,
                'updated_at': script.updated_at
            }
            scripts_data.append(script_data)
        
        return jsonify({'success': True, 'data': scripts_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/games/<game_id>/scripts', methods=['POST'])
def api_create_script(game_id):
    """创建脚本"""
    try:
        data = request.get_json()
        
        name = data.get('name')
        description = data.get('description', '')
        script_type = data.get('script_type', 'custom')
        content = data.get('content', {'actions': []})
        
        if not name:
            return jsonify({'success': False, 'error': '脚本名称不能为空'})
        
        script_id = engine.game_manager.add_script(
            game_id, name, description, script_type, content
        )
        
        return jsonify({'success': True, 'data': {'script_id': script_id}})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/games/<game_id>/scripts/<script_id>', methods=['GET'])
def api_get_script(game_id, script_id):
    """获取脚本详情"""
    try:
        if game_id not in engine.game_manager.games:
            return jsonify({'success': False, 'error': '游戏不存在'})
        
        game = engine.game_manager.games[game_id]
        if script_id not in game.scripts:
            return jsonify({'success': False, 'error': '脚本不存在'})
        
        script = game.scripts[script_id]
        script_data = {
            'id': script.id,
            'name': script.name,
            'description': script.description,
            'script_type': script.script_type,
            'content': script.content,
            'templates': script.templates,
            'enabled': script.enabled,
            'created_at': script.created_at,
            'updated_at': script.updated_at
        }
        
        return jsonify({'success': True, 'data': script_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/games/<game_id>/scripts/<script_id>', methods=['PUT'])
def api_update_script(game_id, script_id):
    """更新脚本"""
    try:
        data = request.get_json()
        
        success = engine.game_manager.update_script(game_id, script_id, **data)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': '更新脚本失败'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/games/<game_id>/scripts/<script_id>', methods=['DELETE'])
def api_delete_script(game_id, script_id):
    """删除脚本"""
    try:
        success = engine.game_manager.delete_script(game_id, script_id)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': '删除脚本失败'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/queue/status')
def api_queue_status():
    """获取队列状态"""
    try:
        if not engine.queue_manager:
            return jsonify({'success': False, 'error': '队列管理器未初始化'})
        
        status = engine.queue_manager.get_all_queue_status()
        return jsonify({'success': True, 'data': status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/queue/<game_id>/add', methods=['POST'])
def api_add_to_queue(game_id):
    """添加脚本到队列"""
    try:
        data = request.get_json()
        script_id = data.get('script_id')
        priority = data.get('priority', 0)
        
        if not script_id:
            return jsonify({'success': False, 'error': '脚本ID不能为空'})
        
        # 获取脚本信息
        if game_id not in engine.game_manager.games:
            return jsonify({'success': False, 'error': '游戏不存在'})
        
        game = engine.game_manager.games[game_id]
        if script_id not in game.scripts:
            return jsonify({'success': False, 'error': '脚本不存在'})
        
        script = game.scripts[script_id]
        
        # 创建队列脚本
        queued_script = QueuedScript(
            id=str(uuid.uuid4()),
            game_id=game_id,
            script_id=script_id,
            script_name=script.name,
            script_content=script.content,
            priority=priority
        )
        
        success = engine.queue_manager.add_script_to_queue(queued_script)
        
        if success:
            return jsonify({'success': True, 'data': {'queued_script_id': queued_script.id}})
        else:
            return jsonify({'success': False, 'error': '添加到队列失败'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/plugins')
def api_get_plugins():
    """获取插件列表"""
    try:
        plugins = engine.plugin_manager.get_available_plugins()
        return jsonify({'success': True, 'data': plugins})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/plugins/<plugin_name>/execute', methods=['POST'])
def api_execute_plugin_action(plugin_name):
    """执行插件动作"""
    try:
        data = request.get_json()
        action = data.get('action')
        params = data.get('params', {})
        
        if not action:
            return jsonify({'success': False, 'error': '动作名称不能为空'})
        
        result = engine.execute_plugin_action(plugin_name, action, params)
        return jsonify({'success': True, 'data': result})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/games/<game_id>/export')
def api_export_game(game_id):
    """导出游戏"""
    try:
        if game_id not in engine.game_manager.games:
            return jsonify({'success': False, 'error': '游戏不存在'})
        
        game = engine.game_manager.games[game_id]
        export_path = f"AutoScript/temp/{game.name}_{game_id}.zip"
        
        # 确保临时目录存在
        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        
        success = engine.game_manager.export_game(game_id, export_path)
        
        if success:
            return send_file(export_path, as_attachment=True, 
                           download_name=f"{game.name}.zip")
        else:
            return jsonify({'success': False, 'error': '导出失败'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/games/import', methods=['POST'])
def api_import_game():
    """导入游戏"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有上传文件'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '文件名为空'})
        
        if file and file.filename.endswith('.zip'):
            filename = secure_filename(file.filename)
            upload_path = f"AutoScript/temp/{filename}"
            
            # 确保临时目录存在
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            
            file.save(upload_path)
            
            game_id = engine.game_manager.import_game(upload_path)
            
            # 清理临时文件
            if os.path.exists(upload_path):
                os.remove(upload_path)
            
            if game_id:
                # 为导入的游戏创建队列
                game = engine.game_manager.games[game_id]
                engine.queue_manager.create_game_queue(game_id, game.name)
                
                return jsonify({'success': True, 'data': {'game_id': game_id}})
            else:
                return jsonify({'success': False, 'error': '导入失败'})
        else:
            return jsonify({'success': False, 'error': '文件格式不支持'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': '接口不存在'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': '服务器内部错误'}), 500

if __name__ == '__main__':
    config = engine.config_manager
    host = config.get('web.host', '127.0.0.1')
    port = config.get('web.port', 5000)
    debug = config.get('web.debug', False)
    
    print(f"AutoScript Web界面启动: http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)