"""
游戏管理系统 - 负责游戏分类、脚本组织和导入导出功能
"""
import os
import json
import uuid
import zipfile
import shutil
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class ScriptInfo:
    """脚本信息"""
    id: str
    name: str
    description: str
    script_type: str  # 'startup', 'exception', 'basic', 'custom'
    content: Dict[str, Any]
    templates: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    enabled: bool = True

@dataclass
class GameInfo:
    """游戏信息"""
    id: str
    name: str
    description: str
    platform: str  # 'android', 'windows', 'ios'
    package_name: str = ""
    icon_path: str = ""
    scripts: Dict[str, ScriptInfo] = field(default_factory=dict)
    templates_dir: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    enabled: bool = True

class GameManager:
    """游戏管理器"""
    
    def __init__(self, games_dir: str = "games", templates_dir: str = "templates"):
        self.games_dir = games_dir
        self.templates_dir = templates_dir
        self.games: Dict[str, GameInfo] = {}
        self._ensure_directories()
        self.load_games()
    
    def _ensure_directories(self):
        """确保目录存在"""
        os.makedirs(self.games_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)
    
    def create_game(self, name: str, description: str, platform: str, 
                   package_name: str = "") -> str:
        """创建新游戏"""
        game_id = str(uuid.uuid4())
        
        # 创建游戏目录
        game_dir = os.path.join(self.games_dir, game_id)
        os.makedirs(game_dir, exist_ok=True)
        
        # 创建模板目录
        templates_dir = os.path.join(game_dir, "templates")
        os.makedirs(templates_dir, exist_ok=True)
        
        # 创建基础脚本
        scripts = {}
        
        # 启动脚本
        startup_script = ScriptInfo(
            id=str(uuid.uuid4()),
            name="启动脚本",
            description="游戏启动时执行的脚本",
            script_type="startup",
            content=self._get_default_startup_script(platform, package_name)
        )
        scripts[startup_script.id] = startup_script
        
        # 异常处理脚本
        exception_script = ScriptInfo(
            id=str(uuid.uuid4()),
            name="异常处理脚本",
            description="异常情况下执行的脚本",
            script_type="exception",
            content=self._get_default_exception_script(platform)
        )
        scripts[exception_script.id] = exception_script
        
        # 基础脚本
        basic_script = ScriptInfo(
            id=str(uuid.uuid4()),
            name="基础脚本",
            description="游戏基础操作脚本",
            script_type="basic",
            content=self._get_default_basic_script(platform)
        )
        scripts[basic_script.id] = basic_script
        
        # 创建游戏信息
        game = GameInfo(
            id=game_id,
            name=name,
            description=description,
            platform=platform,
            package_name=package_name,
            scripts=scripts,
            templates_dir=templates_dir
        )
        
        self.games[game_id] = game
        self.save_game(game_id)
        
        logger.info(f"创建游戏: {name} (ID: {game_id})")
        return game_id
    
    def _get_default_startup_script(self, platform: str, package_name: str) -> Dict[str, Any]:
        """获取默认启动脚本"""
        if platform == "android":
            return {
                "actions": [
                    {
                        "type": "plugin_action",
                        "plugin": "scrcpy",
                        "action": "connect",
                        "params": {},
                        "description": "连接Android设备"
                    },
                    {
                        "type": "plugin_action",
                        "plugin": "scrcpy", 
                        "action": "start_app",
                        "params": {"package_name": package_name},
                        "description": f"启动应用: {package_name}"
                    }
                ]
            }
        else:
            return {
                "actions": [
                    {
                        "type": "plugin_action",
                        "plugin": "windows",
                        "action": "start_program",
                        "params": {"program_path": ""},
                        "description": "启动程序"
                    }
                ]
            }
    
    def _get_default_exception_script(self, platform: str) -> Dict[str, Any]:
        """获取默认异常处理脚本"""
        return {
            "actions": [
                {
                    "type": "plugin_action",
                    "plugin": "scrcpy" if platform == "android" else "windows",
                    "action": "take_screenshot",
                    "params": {"output_path": "exception_screenshot.png"},
                    "description": "异常时截图"
                },
                {
                    "type": "condition",
                    "condition_type": "template_match",
                    "template_path": "error_dialog.png",
                    "threshold": 0.8,
                    "on_true": [
                        {
                            "type": "plugin_action",
                            "plugin": "scrcpy" if platform == "android" else "windows",
                            "action": "press_key",
                            "params": {"key_code": 4},  # 返回键
                            "description": "点击返回键"
                        }
                    ],
                    "on_false": [
                        {
                            "type": "restart_script",
                            "description": "重启脚本"
                        }
                    ]
                }
            ]
        }
    
    def _get_default_basic_script(self, platform: str) -> Dict[str, Any]:
        """获取默认基础脚本"""
        return {
            "actions": [
                {
                    "type": "polling_loop",
                    "interval": 1.0,
                    "max_iterations": 100,
                    "actions": [
                        {
                            "type": "plugin_action",
                            "plugin": "scrcpy" if platform == "android" else "windows",
                            "action": "take_screenshot",
                            "params": {"output_path": "current_screen.png"},
                            "description": "截取当前屏幕",
                            "store_result": "screenshot"
                        },
                        {
                            "type": "condition",
                            "condition_type": "template_match",
                            "template_path": "target_button.png",
                            "threshold": 0.8,
                            "input_image": "$screenshot",
                            "on_true": [
                                {
                                    "type": "plugin_action",
                                    "plugin": "scrcpy" if platform == "android" else "windows",
                                    "action": "click",
                                    "params": {"x": "$match_x", "y": "$match_y"},
                                    "description": "点击目标按钮"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    
    def add_script(self, game_id: str, name: str, description: str, 
                  script_type: str = "custom", content: Dict[str, Any] = None) -> str:
        """添加脚本到游戏"""
        if game_id not in self.games:
            raise ValueError(f"游戏 {game_id} 不存在")
        
        script_id = str(uuid.uuid4())
        script = ScriptInfo(
            id=script_id,
            name=name,
            description=description,
            script_type=script_type,
            content=content if content is not None else {"actions": []}
        )
        
        self.games[game_id].scripts[script_id] = script
        self.games[game_id].updated_at = datetime.now().isoformat()
        self.save_game(game_id)
        
        logger.info(f"添加脚本: {name} 到游戏 {self.games[game_id].name}")
        return script_id
    
    def update_script(self, game_id: str, script_id: str, **kwargs) -> bool:
        """更新脚本"""
        if game_id not in self.games:
            return False
        
        if script_id not in self.games[game_id].scripts:
            return False
        
        script = self.games[game_id].scripts[script_id]
        
        for key, value in kwargs.items():
            if hasattr(script, key):
                setattr(script, key, value)
        
        script.updated_at = datetime.now().isoformat()
        self.games[game_id].updated_at = datetime.now().isoformat()
        self.save_game(game_id)
        
        logger.info(f"更新脚本: {script.name}")
        return True
    
    def delete_script(self, game_id: str, script_id: str) -> bool:
        """删除脚本"""
        if game_id not in self.games:
            return False
        
        if script_id not in self.games[game_id].scripts:
            return False
        
        script_name = self.games[game_id].scripts[script_id].name
        del self.games[game_id].scripts[script_id]
        self.games[game_id].updated_at = datetime.now().isoformat()
        self.save_game(game_id)
        
        logger.info(f"删除脚本: {script_name}")
        return True
    
    def get_game_scripts(self, game_id: str, script_type: str = None) -> List[ScriptInfo]:
        """获取游戏的脚本列表"""
        if game_id not in self.games:
            return []
        
        scripts = list(self.games[game_id].scripts.values())
        
        if script_type:
            scripts = [s for s in scripts if s.script_type == script_type]
        
        return sorted(scripts, key=lambda x: x.created_at)
    
    def save_game(self, game_id: str):
        """保存游戏信息到文件"""
        if game_id not in self.games:
            return
        
        game_file = os.path.join(self.games_dir, game_id, "game.json")
        os.makedirs(os.path.dirname(game_file), exist_ok=True)
        
        game_data = asdict(self.games[game_id])
        
        with open(game_file, 'w', encoding='utf-8') as f:
            json.dump(game_data, f, ensure_ascii=False, indent=2)
    
    def load_games(self):
        """从文件加载所有游戏"""
        if not os.path.exists(self.games_dir):
            return
        
        for item in os.listdir(self.games_dir):
            game_dir = os.path.join(self.games_dir, item)
            if os.path.isdir(game_dir):
                game_file = os.path.join(game_dir, "game.json")
                if os.path.exists(game_file):
                    try:
                        with open(game_file, 'r', encoding='utf-8') as f:
                            game_data = json.load(f)
                        
                        # 转换脚本数据
                        scripts = {}
                        for script_id, script_data in game_data.get('scripts', {}).items():
                            scripts[script_id] = ScriptInfo(**script_data)
                        
                        game_data['scripts'] = scripts
                        game = GameInfo(**game_data)
                        self.games[game.id] = game
                        
                    except Exception as e:
                        logger.error(f"加载游戏失败 {game_file}: {str(e)}")
        
        logger.info(f"加载了 {len(self.games)} 个游戏")
    
    def get_games_by_platform(self, platform: str) -> List[GameInfo]:
        """按平台获取游戏列表"""
        return [game for game in self.games.values() if game.platform == platform]
    
    def export_game(self, game_id: str, export_path: str) -> bool:
        """导出游戏（包含脚本和模板）"""
        if game_id not in self.games:
            return False
        
        try:
            game = self.games[game_id]
            game_dir = os.path.join(self.games_dir, game_id)
            
            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 添加游戏配置文件
                game_file = os.path.join(game_dir, "game.json")
                if os.path.exists(game_file):
                    zipf.write(game_file, "game.json")
                
                # 添加模板文件
                templates_dir = os.path.join(game_dir, "templates")
                if os.path.exists(templates_dir):
                    for root, dirs, files in os.walk(templates_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arc_path = os.path.relpath(file_path, game_dir)
                            zipf.write(file_path, arc_path)
            
            logger.info(f"导出游戏: {game.name} 到 {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出游戏失败: {str(e)}")
            return False
    
    def import_game(self, import_path: str) -> Optional[str]:
        """导入游戏（从压缩包）"""
        if not os.path.exists(import_path):
            return None
        
        try:
            temp_dir = os.path.join(self.games_dir, "temp_import")
            os.makedirs(temp_dir, exist_ok=True)
            
            # 解压文件
            with zipfile.ZipFile(import_path, 'r') as zipf:
                zipf.extractall(temp_dir)
            
            # 读取游戏配置
            game_file = os.path.join(temp_dir, "game.json")
            if not os.path.exists(game_file):
                shutil.rmtree(temp_dir)
                return None
            
            with open(game_file, 'r', encoding='utf-8') as f:
                game_data = json.load(f)
            
                         # 生成新的游戏ID
             new_id = str(uuid.uuid4())
            game_data['id'] = new_id
            game_data['updated_at'] = datetime.now().isoformat()
            
            # 创建新游戏目录
            new_game_dir = os.path.join(self.games_dir, new_id)
            os.makedirs(new_game_dir, exist_ok=True)
            
            # 移动文件
            for item in os.listdir(temp_dir):
                src = os.path.join(temp_dir, item)
                dst = os.path.join(new_game_dir, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            
            # 清理临时目录
            shutil.rmtree(temp_dir)
            
            # 重新保存游戏配置
            game_file = os.path.join(new_game_dir, "game.json")
            with open(game_file, 'w', encoding='utf-8') as f:
                json.dump(game_data, f, ensure_ascii=False, indent=2)
            
            # 加载游戏到内存
            scripts = {}
            for script_id, script_data in game_data.get('scripts', {}).items():
                scripts[script_id] = ScriptInfo(**script_data)
            
            game_data['scripts'] = scripts
            game = GameInfo(**game_data)
            self.games[new_id] = game
            
            logger.info(f"导入游戏: {game.name} (ID: {new_id})")
            return new_id
            
        except Exception as e:
            logger.error(f"导入游戏失败: {str(e)}")
            return None
    
    def delete_game(self, game_id: str) -> bool:
        """删除游戏"""
        if game_id not in self.games:
            return False
        
        try:
            game_name = self.games[game_id].name
            
            # 删除游戏目录
            game_dir = os.path.join(self.games_dir, game_id)
            if os.path.exists(game_dir):
                shutil.rmtree(game_dir)
            
            # 从内存中删除
            del self.games[game_id]
            
            logger.info(f"删除游戏: {game_name}")
            return True
            
        except Exception as e:
            logger.error(f"删除游戏失败: {str(e)}")
            return False