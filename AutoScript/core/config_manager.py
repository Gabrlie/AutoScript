"""
配置管理器 - 负责系统配置的加载和管理
"""
import os
import json
import yaml
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "configs/config.yaml"):
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> bool:
        """加载配置文件"""
        try:
            if not os.path.exists(self.config_file):
                logger.warning(f"配置文件不存在: {self.config_file}，将创建默认配置")
                self._create_default_config()
                return True
            
            # 根据文件扩展名选择解析方式
            if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f) or {}
            elif self.config_file.endswith('.json'):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                logger.error(f"不支持的配置文件格式: {self.config_file}")
                return False
            
            logger.info(f"配置文件加载成功: {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            self._create_default_config()
            return False
    
    def save_config(self) -> bool:
        """保存配置文件"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            elif self.config_file.endswith('.json'):
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, ensure_ascii=False, indent=2)
            
            logger.info(f"配置文件保存成功: {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"保存配置文件失败: {str(e)}")
            return False
    
    def _create_default_config(self):
        """创建默认配置"""
        self.config = {
            'system': {
                'log_level': 'INFO',
                'max_log_size': '10MB',
                'backup_count': 5,
                'auto_save_interval': 300  # 秒
            },
            'plugins': {
                'auto_load': True,
                'plugin_dirs': ['plugins'],
                'disabled_plugins': []
            },
            'games': {
                'games_dir': 'games',
                'templates_dir': 'templates',
                'auto_backup': True,
                'backup_interval': 3600  # 秒
            },
            'execution': {
                'default_timeout': 30,
                'exception_timeout': 60,
                'max_concurrent_scripts': 5,
                'screenshot_quality': 90
            },
            'ocr': {
                'engine': 'paddleocr',
                'language': 'ch',
                'use_gpu': False
            },
            'template_matching': {
                'default_threshold': 0.8,
                'max_scale_factor': 1.2,
                'min_scale_factor': 0.8
            },
            'web': {
                'host': '127.0.0.1',
                'port': 5000,
                'debug': False
            }
        }
        
        self.save_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔的路径，如 'system.log_level'
            default: 默认值
            
        Returns:
            配置值
        """
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception:
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """
        设置配置值
        
        Args:
            key: 配置键，支持点号分隔的路径
            value: 配置值
            
        Returns:
            是否设置成功
        """
        try:
            keys = key.split('.')
            config = self.config
            
            # 导航到最后一级的父级
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # 设置值
            config[keys[-1]] = value
            
            return True
            
        except Exception as e:
            logger.error(f"设置配置失败: {key} = {value}, {str(e)}")
            return False
    
    def update(self, updates: Dict[str, Any]) -> bool:
        """
        批量更新配置
        
        Args:
            updates: 更新的配置字典
            
        Returns:
            是否更新成功
        """
        try:
            def deep_update(base_dict, update_dict):
                for key, value in update_dict.items():
                    if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                        deep_update(base_dict[key], value)
                    else:
                        base_dict[key] = value
            
            deep_update(self.config, updates)
            return True
            
        except Exception as e:
            logger.error(f"批量更新配置失败: {str(e)}")
            return False
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        获取配置段
        
        Args:
            section: 配置段名称
            
        Returns:
            配置段字典
        """
        return self.config.get(section, {})
    
    def reload(self) -> bool:
        """重新加载配置"""
        return self.load_config()
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self.config.copy()