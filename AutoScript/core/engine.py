"""
AutoScript主引擎 - 整合所有模块
"""
import os
import sys
import logging
from typing import Dict, Any, Optional

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.plugin_manager import PluginManager
from core.game_manager import GameManager
from core.config_manager import ConfigManager
from core.template_matcher import TemplateMatcher
from core.ocr_engine import OCREngine
from core.script_queue import ScriptQueueManager

logger = logging.getLogger(__name__)

class AutoScriptEngine:
    """AutoScript主引擎"""
    
    def __init__(self, config_file: str = "AutoScript/configs/config.yaml"):
        self.config_manager = ConfigManager(config_file)
        self.plugin_manager = None
        self.game_manager = None
        self.template_matcher = None
        self.ocr_engine = None
        self.queue_manager = None
        self.initialized = False
        
        self._setup_logging()
    
    def _setup_logging(self):
        """设置日志"""
        log_level = self.config_manager.get('system.log_level', 'INFO')
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('AutoScript/logs/autoscript.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        logger.info("日志系统初始化完成")
    
    def initialize(self) -> bool:
        """初始化引擎"""
        try:
            logger.info("开始初始化AutoScript引擎...")
            
            # 初始化模板匹配器
            self.template_matcher = TemplateMatcher()
            logger.info("模板匹配器初始化完成")
            
            # 初始化OCR引擎
            self.ocr_engine = OCREngine()
            if not self.ocr_engine.initialize():
                logger.warning("OCR引擎初始化失败，部分功能可能不可用")
            
            # 初始化插件管理器
            plugins_dirs = self.config_manager.get('plugins.plugin_dirs', ['plugins'])
            self.plugin_manager = PluginManager(plugins_dirs[0] if plugins_dirs else 'plugins')
            self.plugin_manager.load_all_plugins()
            
            # 初始化游戏管理器
            games_dir = self.config_manager.get('games.games_dir', 'AutoScript/games')
            templates_dir = self.config_manager.get('games.templates_dir', 'AutoScript/templates')
            self.game_manager = GameManager(games_dir, templates_dir)
            
            # 初始化队列管理器
            self.queue_manager = ScriptQueueManager(None)  # 稍后设置script_executor
            
            # 为所有现有游戏创建队列
            for game_id, game in self.game_manager.games.items():
                self.queue_manager.create_game_queue(game_id, game.name)
            
            self.initialized = True
            logger.info("AutoScript引擎初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"引擎初始化失败: {str(e)}", exc_info=True)
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        if not self.initialized:
            return {'status': 'not_initialized'}
        
        return {
            'status': 'running',
            'plugins': self.plugin_manager.get_available_plugins(),
            'games': len(self.game_manager.games),
            'queues': self.queue_manager.get_all_queue_status() if self.queue_manager else [],
            'config': {
                'ocr_engine': self.config_manager.get('ocr.engine'),
                'web_port': self.config_manager.get('web.port'),
                'log_level': self.config_manager.get('system.log_level')
            }
        }
    
    def create_game(self, name: str, description: str, platform: str, 
                   package_name: str = "") -> Optional[str]:
        """创建新游戏"""
        if not self.initialized:
            return None
        
        game_id = self.game_manager.create_game(name, description, platform, package_name)
        
        # 为新游戏创建队列
        if self.queue_manager:
            self.queue_manager.create_game_queue(game_id, name)
        
        return game_id
    
    def get_games(self, platform: str = None) -> list:
        """获取游戏列表"""
        if not self.initialized:
            return []
        
        if platform:
            return self.game_manager.get_games_by_platform(platform)
        else:
            return list(self.game_manager.games.values())
    
    def execute_plugin_action(self, plugin_name: str, action: str, params: Dict[str, Any]) -> Any:
        """执行插件动作"""
        if not self.initialized:
            raise RuntimeError("引擎未初始化")
        
        return self.plugin_manager.execute_action(plugin_name, action, params)
    
    def shutdown(self):
        """关闭引擎"""
        logger.info("正在关闭AutoScript引擎...")
        
        if self.queue_manager:
            self.queue_manager.cleanup()
        
        if self.plugin_manager:
            self.plugin_manager.cleanup_all()
        
        logger.info("AutoScript引擎已关闭")

# 全局引擎实例
engine = None

def get_engine() -> AutoScriptEngine:
    """获取引擎实例"""
    global engine
    if engine is None:
        engine = AutoScriptEngine()
        engine.initialize()
    return engine