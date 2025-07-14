"""
AutoScript 主引擎
负责协调各个模块的工作，提供统一的API接口
"""
from typing import Dict, Any, Optional, List
import threading
import time
from loguru import logger

from .plugin_manager import PluginManager
from .script_queue import ScriptQueue
from .config_manager import ConfigManager
from .template_matcher import TemplateMatcher
from .ocr_engine import OCREngine


class AutoScriptEngine:
    """游戏自动化脚本主引擎"""
    
    def __init__(self, config_path: str = "configs/config.yaml"):
        """
        初始化引擎
        
        Args:
            config_path: 配置文件路径
        """
        self.config_manager = ConfigManager(config_path)
        self.plugin_manager = PluginManager(self)
        self.script_queue = ScriptQueue(self)
        self.template_matcher = TemplateMatcher(self)
        self.ocr_engine = OCREngine(self)
        
        self._running = False
        self._main_thread = None
        
        logger.info("AutoScript引擎初始化完成")
    
    def start(self):
        """启动引擎"""
        if self._running:
            logger.warning("引擎已经在运行中")
            return
            
        self._running = True
        self._main_thread = threading.Thread(target=self._main_loop, daemon=True)
        self._main_thread.start()
        logger.info("AutoScript引擎已启动")
    
    def stop(self):
        """停止引擎"""
        self._running = False
        if self._main_thread:
            self._main_thread.join(timeout=5)
        logger.info("AutoScript引擎已停止")
    
    def _main_loop(self):
        """主循环"""
        while self._running:
            try:
                # 处理脚本队列
                self.script_queue.process_queue()
                time.sleep(0.1)  # 避免CPU占用过高
            except Exception as e:
                logger.error(f"主循环出现错误: {e}")
    
    def get_plugin(self, plugin_name: str):
        """获取插件实例"""
        return self.plugin_manager.get_plugin(plugin_name)
    
    def execute_script(self, script_data: Dict[str, Any]) -> bool:
        """
        执行脚本
        
        Args:
            script_data: 脚本数据
            
        Returns:
            执行是否成功
        """
        return self.script_queue.add_script(script_data)
    
    def find_template(self, template_name: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        查找模板
        
        Args:
            template_name: 模板名称
            **kwargs: 其他参数
            
        Returns:
            匹配结果
        """
        return self.template_matcher.find_template(template_name, **kwargs)
    
    def recognize_text(self, image_path: str = None, region: tuple = None) -> str:
        """
        识别文本
        
        Args:
            image_path: 图片路径
            region: 识别区域 (x, y, width, height)
            
        Returns:
            识别的文本
        """
        return self.ocr_engine.recognize_text(image_path, region)
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置"""
        return self.config_manager.get(key, default)
    
    def set_config(self, key: str, value: Any):
        """设置配置"""
        self.config_manager.set(key, value)
    
    def is_running(self) -> bool:
        """检查引擎是否在运行"""
        return self._running