"""
插件管理器
负责加载、管理和调度插件
"""
import os
import importlib
import importlib.util
from typing import Dict, List, Any, Optional, Type
from loguru import logger
from abc import ABC, abstractmethod


class BasePlugin(ABC):
    """插件基类"""
    
    def __init__(self, engine):
        """
        初始化插件
        
        Args:
            engine: AutoScript引擎实例
        """
        self.engine = engine
        self.name = ""
        self.version = "1.0.0"
        self.description = ""
        self.author = ""
        self.enabled = True
        
    @abstractmethod
    def initialize(self) -> bool:
        """
        初始化插件
        
        Returns:
            是否初始化成功
        """
        pass
    
    @abstractmethod
    def cleanup(self):
        """清理插件资源"""
        pass
    
    @abstractmethod
    def get_actions(self) -> List[str]:
        """
        获取插件支持的动作列表
        
        Returns:
            动作名称列表
        """
        pass
    
    @abstractmethod
    def execute_action(self, action: Dict[str, Any]) -> Any:
        """
        执行动作
        
        Args:
            action: 动作配置
            
        Returns:
            执行结果
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """获取插件信息"""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'enabled': self.enabled,
            'actions': self.get_actions()
        }


class PluginManager:
    """插件管理器"""
    
    def __init__(self, engine):
        """
        初始化插件管理器
        
        Args:
            engine: AutoScript引擎实例
        """
        self.engine = engine
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugins_dir = "plugins"
        
        # 确保插件目录存在
        os.makedirs(self.plugins_dir, exist_ok=True)
        
        # 加载内置插件
        self._load_builtin_plugins()
        
        # 加载外部插件
        self._load_external_plugins()
        
        logger.info(f"插件管理器初始化完成，已加载 {len(self.plugins)} 个插件")
    
    def _load_builtin_plugins(self):
        """加载内置插件"""
        builtin_plugins = [
            ('playwright', 'plugins.playwright_plugin', 'PlaywrightPlugin'),
            ('windows', 'plugins.windows_plugin', 'WindowsPlugin'),
            ('scrcpy', 'plugins.scrcpy_plugin', 'ScrcpyPlugin')
        ]
        
        for plugin_name, module_name, class_name in builtin_plugins:
            try:
                # 检查是否在配置中启用
                enabled_plugins = self.engine.get_config('plugins.enabled', [])
                if plugin_name not in enabled_plugins:
                    logger.info(f"插件 {plugin_name} 未启用，跳过加载")
                    continue
                
                # 动态导入模块
                module = importlib.import_module(module_name)
                plugin_class = getattr(module, class_name)
                
                # 实例化插件
                plugin = plugin_class(self.engine)
                
                # 初始化插件
                if plugin.initialize():
                    self.plugins[plugin_name] = plugin
                    logger.info(f"内置插件加载成功: {plugin_name}")
                else:
                    logger.error(f"内置插件初始化失败: {plugin_name}")
                    
            except Exception as e:
                logger.error(f"加载内置插件失败: {plugin_name} - {e}")
    
    def _load_external_plugins(self):
        """加载外部插件"""
        if not os.path.exists(self.plugins_dir):
            return
        
        for item in os.listdir(self.plugins_dir):
            item_path = os.path.join(self.plugins_dir, item)
            
            # 检查是否是Python文件
            if item.endswith('.py') and not item.startswith('__'):
                self._load_plugin_file(item_path)
            
            # 检查是否是插件目录
            elif os.path.isdir(item_path) and not item.startswith('__'):
                plugin_file = os.path.join(item_path, 'plugin.py')
                if os.path.exists(plugin_file):
                    self._load_plugin_file(plugin_file)
    
    def _load_plugin_file(self, plugin_file: str):
        """
        加载插件文件
        
        Args:
            plugin_file: 插件文件路径
        """
        try:
            # 生成模块名
            module_name = os.path.splitext(os.path.basename(plugin_file))[0]
            
            # 动态加载模块
            spec = importlib.util.spec_from_file_location(module_name, plugin_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找插件类
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, BasePlugin) and 
                    attr != BasePlugin):
                    plugin_class = attr
                    break
            
            if plugin_class:
                # 实例化插件
                plugin = plugin_class(self.engine)
                
                # 初始化插件
                if plugin.initialize():
                    self.plugins[plugin.name] = plugin
                    logger.info(f"外部插件加载成功: {plugin.name}")
                else:
                    logger.error(f"外部插件初始化失败: {plugin.name}")
            else:
                logger.warning(f"在文件中未找到插件类: {plugin_file}")
                
        except Exception as e:
            logger.error(f"加载外部插件失败: {plugin_file} - {e}")
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """
        获取插件实例
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            插件实例
        """
        return self.plugins.get(plugin_name)
    
    def get_all_plugins(self) -> Dict[str, BasePlugin]:
        """获取所有插件"""
        return self.plugins.copy()
    
    def get_enabled_plugins(self) -> Dict[str, BasePlugin]:
        """获取启用的插件"""
        return {name: plugin for name, plugin in self.plugins.items() if plugin.enabled}
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """
        启用插件
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            是否成功启用
        """
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            if not plugin.enabled:
                plugin.enabled = True
                logger.info(f"插件已启用: {plugin_name}")
                return True
            return True
        return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """
        禁用插件
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            是否成功禁用
        """
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            if plugin.enabled:
                plugin.enabled = False
                logger.info(f"插件已禁用: {plugin_name}")
                return True
            return True
        return False
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """
        重新加载插件
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            是否成功重新加载
        """
        try:
            if plugin_name in self.plugins:
                # 清理旧插件
                old_plugin = self.plugins[plugin_name]
                old_plugin.cleanup()
                del self.plugins[plugin_name]
            
            # 重新加载插件
            self._load_builtin_plugins()
            self._load_external_plugins()
            
            logger.info(f"插件重新加载成功: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"重新加载插件失败: {plugin_name} - {e}")
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        卸载插件
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            是否成功卸载
        """
        try:
            if plugin_name in self.plugins:
                plugin = self.plugins[plugin_name]
                plugin.cleanup()
                del self.plugins[plugin_name]
                logger.info(f"插件已卸载: {plugin_name}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"卸载插件失败: {plugin_name} - {e}")
            return False
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """
        获取插件信息
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            插件信息
        """
        if plugin_name in self.plugins:
            return self.plugins[plugin_name].get_info()
        return None
    
    def get_all_plugin_info(self) -> Dict[str, Dict[str, Any]]:
        """获取所有插件信息"""
        return {name: plugin.get_info() for name, plugin in self.plugins.items()}
    
    def get_available_actions(self) -> Dict[str, List[str]]:
        """获取所有可用动作"""
        actions = {}
        for name, plugin in self.plugins.items():
            if plugin.enabled:
                actions[name] = plugin.get_actions()
        return actions
    
    def execute_action(self, plugin_name: str, action: Dict[str, Any]) -> Any:
        """
        执行插件动作
        
        Args:
            plugin_name: 插件名称
            action: 动作配置
            
        Returns:
            执行结果
        """
        if plugin_name not in self.plugins:
            raise Exception(f"插件不存在: {plugin_name}")
        
        plugin = self.plugins[plugin_name]
        if not plugin.enabled:
            raise Exception(f"插件未启用: {plugin_name}")
        
        return plugin.execute_action(action)
    
    def install_plugin(self, plugin_path: str) -> bool:
        """
        安装插件
        
        Args:
            plugin_path: 插件文件路径
            
        Returns:
            是否安装成功
        """
        try:
            import shutil
            
            # 复制插件文件到插件目录
            filename = os.path.basename(plugin_path)
            target_path = os.path.join(self.plugins_dir, filename)
            shutil.copy2(plugin_path, target_path)
            
            # 加载新插件
            self._load_plugin_file(target_path)
            
            logger.info(f"插件安装成功: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"安装插件失败: {plugin_path} - {e}")
            return False
    
    def cleanup(self):
        """清理插件管理器"""
        for plugin in self.plugins.values():
            try:
                plugin.cleanup()
            except Exception as e:
                logger.error(f"清理插件失败: {plugin.name} - {e}")
        
        self.plugins.clear()
        logger.info("插件管理器已清理")
    
    def get_plugin_status(self) -> Dict[str, Any]:
        """获取插件状态"""
        return {
            'total_plugins': len(self.plugins),
            'enabled_plugins': len(self.get_enabled_plugins()),
            'disabled_plugins': len(self.plugins) - len(self.get_enabled_plugins()),
            'plugin_list': list(self.plugins.keys())
        }