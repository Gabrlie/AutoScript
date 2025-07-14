"""
配置管理器
负责管理系统配置和用户设置
"""
import os
import yaml
from typing import Any, Dict
from loguru import logger


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = "configs/config.yaml"):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f) or {}
                logger.info(f"配置文件加载成功: {self.config_path}")
            else:
                self.config = self._get_default_config()
                self.save_config()
                logger.info(f"配置文件不存在，已创建默认配置: {self.config_path}")
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            self.config = self._get_default_config()
    
    def save_config(self):
        """保存配置文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"配置文件保存成功: {self.config_path}")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        设置配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键
            value: 配置值
        """
        keys = key.split('.')
        config = self.config
        
        # 创建嵌套字典结构
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'engine': {
                'max_workers': 4,
                'queue_size': 100,
                'timeout': 30
            },
            'template_matcher': {
                'threshold': 0.8,
                'method': 'cv2.TM_CCOEFF_NORMED',
                'max_results': 10
            },
            'ocr': {
                'engine': 'tesseract',
                'lang': 'chi_sim+eng',
                'config': '--psm 8'
            },
            'web': {
                'host': '0.0.0.0',
                'port': 5000,
                'debug': False
            },
            'plugins': {
                'enabled': ['playwright', 'windows', 'scrcpy'],
                'playwright': {
                    'browser': 'chromium',
                    'headless': False,
                    'timeout': 30000
                },
                'windows': {
                    'process_timeout': 10
                },
                'scrcpy': {
                    'max_size': 1920,
                    'bit_rate': '8M'
                }
            },
            'logging': {
                'level': 'INFO',
                'file': 'logs/autoscript.log',
                'rotation': '10 MB',
                'retention': '30 days'
            }
        }
    
    def reload(self):
        """重新加载配置"""
        self.load_config()
    
    def reset_to_default(self):
        """重置为默认配置"""
        self.config = self._get_default_config()
        self.save_config()
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self.config.copy()