"""
插件管理器 - 负责加载和管理所有插件
"""
import os
import sys
import importlib
import inspect
from typing import Dict, List, Any, Type, Optional
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class BasePlugin(ABC):
    """插件基类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """插件名称"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """插件版本"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """插件描述"""
        pass
    
    @property
    @abstractmethod
    def supported_platforms(self) -> List[str]:
        """支持的平台列表"""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """初始化插件"""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """清理插件资源"""
        pass
    
    @abstractmethod
    def execute_action(self, action: str, params: Dict[str, Any]) -> Any:
        """执行动作"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查插件是否可用"""
        pass
    
    def get_actions(self) -> List[str]:
        """获取插件支持的动作列表"""
        return []

class PluginManager:
    """插件管理器"""
    
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = plugins_dir
        self.plugins: Dict[str, BasePlugin] = {}
        self.initialized = False
        
    def discover_plugins(self) -> List[str]:
        """发现插件"""
        plugin_files = []
        
        # 获取插件目录的绝对路径
        if not os.path.isabs(self.plugins_dir):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            plugins_path = os.path.join(os.path.dirname(current_dir), self.plugins_dir)
        else:
            plugins_path = self.plugins_dir
            
        logger.info(f"正在搜索插件目录: {plugins_path}")
        
        if not os.path.exists(plugins_path):
            logger.warning(f"插件目录不存在: {plugins_path}")
            return plugin_files
            
        # 扫描插件文件
        for file in os.listdir(plugins_path):
            if file.endswith('_plugin.py') and not file.startswith('__'):
                plugin_files.append(file[:-3])  # 移除.py扩展名
                logger.info(f"发现插件文件: {file}")
                
        return plugin_files
    
    def load_plugin(self, plugin_name: str) -> bool:
        """加载单个插件"""
        try:
            # 动态导入插件模块
            module_name = f"plugins.{plugin_name}"
            logger.info(f"正在加载插件模块: {module_name}")
            
            # 重新加载模块以确保获取最新版本
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
            
            module = importlib.import_module(module_name)
            
            # 查找插件类
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BasePlugin) and 
                    obj != BasePlugin):
                    plugin_class = obj
                    break
            
            if plugin_class is None:
                logger.error(f"在模块 {module_name} 中未找到插件类")
                return False
            
            # 实例化插件
            plugin_instance = plugin_class()
            
            # 检查插件是否可用
            if not plugin_instance.is_available():
                logger.warning(f"插件 {plugin_instance.name} 不可用")
                return False
            
            # 初始化插件
            if plugin_instance.initialize():
                self.plugins[plugin_instance.name] = plugin_instance
                logger.info(f"成功加载插件: {plugin_instance.name} v{plugin_instance.version}")
                return True
            else:
                logger.error(f"插件 {plugin_instance.name} 初始化失败")
                return False
                
        except Exception as e:
            logger.error(f"加载插件 {plugin_name} 时出错: {str(e)}", exc_info=True)
            return False
    
    def load_all_plugins(self) -> None:
        """加载所有插件"""
        logger.info("开始加载所有插件...")
        
        plugin_files = self.discover_plugins()
        
        if not plugin_files:
            logger.warning("未发现任何插件文件")
            return
        
        for plugin_file in plugin_files:
            self.load_plugin(plugin_file)
        
        logger.info(f"插件加载完成，共加载 {len(self.plugins)} 个插件")
        self.initialized = True
    
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """获取插件实例"""
        return self.plugins.get(name)
    
    def get_available_plugins(self) -> Dict[str, Dict[str, Any]]:
        """获取可用插件信息"""
        available = {}
        for name, plugin in self.plugins.items():
            if plugin.is_available():
                available[name] = {
                    'version': plugin.version,
                    'description': plugin.description,
                    'platforms': plugin.supported_platforms,
                    'actions': plugin.get_actions()
                }
        return available
    
    def execute_action(self, plugin_name: str, action: str, params: Dict[str, Any]) -> Any:
        """通过插件执行动作"""
        plugin = self.get_plugin(plugin_name)
        if plugin is None:
            raise ValueError(f"插件 '{plugin_name}' 未找到")
        
        if not plugin.is_available():
            raise RuntimeError(f"插件 '{plugin_name}' 不可用")
        
        return plugin.execute_action(action, params)
    
    def cleanup_all(self) -> None:
        """清理所有插件"""
        for plugin in self.plugins.values():
            try:
                plugin.cleanup()
            except Exception as e:
                logger.error(f"清理插件时出错: {str(e)}")
        
        self.plugins.clear()
        self.initialized = False
    
    def reload_plugins(self) -> None:
        """重新加载所有插件"""
        self.cleanup_all()
        self.load_all_plugins()