"""
游戏自动化脚本核心模块
"""

__version__ = "1.0.0"
__author__ = "AutoScript Team"

from .engine import AutoScriptEngine
from .plugin_manager import PluginManager
from .script_queue import ScriptQueue
from .config_manager import ConfigManager
from .template_matcher import TemplateMatcher
from .ocr_engine import OCREngine

__all__ = [
    'AutoScriptEngine',
    'PluginManager', 
    'ScriptQueue',
    'ConfigManager',
    'TemplateMatcher',
    'OCREngine'
]