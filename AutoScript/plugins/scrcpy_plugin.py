"""
Scrcpy插件 - 用于Android设备控制
"""
import subprocess
import time
import os
import logging
from typing import Dict, List, Any, Tuple
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.plugin_manager import BasePlugin

logger = logging.getLogger(__name__)

class ScrcpyPlugin(BasePlugin):
    """Scrcpy插件类"""
    
    def __init__(self):
        self._process = None
        self._device_id = None
        self._is_connected = False
        
    @property
    def name(self) -> str:
        return "scrcpy"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Android设备镜像和控制插件，基于scrcpy工具"
    
    @property
    def supported_platforms(self) -> List[str]:
        return ["android"]
    
    def initialize(self) -> bool:
        """初始化插件"""
        try:
            # 检查scrcpy是否可用
            result = subprocess.run(['scrcpy', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info("Scrcpy工具检测成功")
                return True
            else:
                logger.error("Scrcpy工具不可用")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.error(f"Scrcpy初始化失败: {str(e)}")
            return False
    
    def cleanup(self) -> None:
        """清理插件资源"""
        if self._process and self._process.poll() is None:
            self._process.terminate()
            self._process = None
        self._is_connected = False
    
    def is_available(self) -> bool:
        """检查插件是否可用"""
        try:
            # 检查scrcpy命令是否存在
            result = subprocess.run(['which', 'scrcpy'], 
                                  capture_output=True, text=True, timeout=3)
            return result.returncode == 0
        except:
            return False
    
    def get_actions(self) -> List[str]:
        """获取支持的动作列表"""
        return [
            'connect',
            'disconnect', 
            'click',
            'swipe',
            'input_text',
            'press_key',
            'take_screenshot',
            'get_device_info',
            'start_app',
            'stop_app',
            'install_apk',
            'uninstall_app'
        ]
    
    def execute_action(self, action: str, params: Dict[str, Any]) -> Any:
        """执行动作"""
        action_map = {
            'connect': self._connect,
            'disconnect': self._disconnect,
            'click': self._click,
            'swipe': self._swipe,
            'input_text': self._input_text,
            'press_key': self._press_key,
            'take_screenshot': self._take_screenshot,
            'get_device_info': self._get_device_info,
            'start_app': self._start_app,
            'stop_app': self._stop_app,
            'install_apk': self._install_apk,
            'uninstall_app': self._uninstall_app
        }
        
        if action not in action_map:
            raise ValueError(f"不支持的动作: {action}")
        
        return action_map[action](params)
    
    def _connect(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """连接设备"""
        device_id = params.get('device_id', '')
        
        try:
            # 检查ADB设备
            cmd = ['adb', 'devices']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return {'success': False, 'error': 'ADB命令执行失败'}
            
            # 解析设备列表
            devices = []
            lines = result.stdout.strip().split('\n')[1:]  # 跳过标题行
            for line in lines:
                if '\tdevice' in line:
                    devices.append(line.split('\t')[0])
            
            if not devices:
                return {'success': False, 'error': '未找到可用的Android设备'}
            
            # 如果没有指定设备ID，使用第一个设备
            if not device_id:
                device_id = devices[0]
            elif device_id not in devices:
                return {'success': False, 'error': f'设备 {device_id} 未连接'}
            
            self._device_id = device_id
            self._is_connected = True
            
            logger.info(f"成功连接到设备: {device_id}")
            return {
                'success': True, 
                'device_id': device_id,
                'available_devices': devices
            }
            
        except Exception as e:
            logger.error(f"连接设备失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _disconnect(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """断开设备连接"""
        self.cleanup()
        return {'success': True}
    
    def _adb_command(self, cmd: List[str]) -> subprocess.CompletedProcess:
        """执行ADB命令"""
        if not self._is_connected:
            raise RuntimeError("设备未连接")
        
        full_cmd = ['adb']
        if self._device_id:
            full_cmd.extend(['-s', self._device_id])
        full_cmd.extend(cmd)
        
        return subprocess.run(full_cmd, capture_output=True, text=True, timeout=30)
    
    def _click(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """点击坐标"""
        x = params.get('x')
        y = params.get('y')
        
        if x is None or y is None:
            return {'success': False, 'error': '缺少坐标参数'}
        
        try:
            result = self._adb_command(['shell', 'input', 'tap', str(x), str(y)])
            
            if result.returncode == 0:
                logger.info(f"点击坐标: ({x}, {y})")
                return {'success': True}
            else:
                return {'success': False, 'error': result.stderr}
                
        except Exception as e:
            logger.error(f"点击操作失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _swipe(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """滑动操作"""
        start_x = params.get('start_x')
        start_y = params.get('start_y')
        end_x = params.get('end_x')
        end_y = params.get('end_y')
        duration = params.get('duration', 300)
        
        if any(param is None for param in [start_x, start_y, end_x, end_y]):
            return {'success': False, 'error': '缺少滑动坐标参数'}
        
        try:
            result = self._adb_command([
                'shell', 'input', 'swipe', 
                str(start_x), str(start_y), str(end_x), str(end_y), str(duration)
            ])
            
            if result.returncode == 0:
                logger.info(f"滑动: ({start_x},{start_y}) -> ({end_x},{end_y})")
                return {'success': True}
            else:
                return {'success': False, 'error': result.stderr}
                
        except Exception as e:
            logger.error(f"滑动操作失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _input_text(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """输入文本"""
        text = params.get('text', '')
        
        if not text:
            return {'success': False, 'error': '文本内容为空'}
        
        try:
            # 转义特殊字符
            escaped_text = text.replace(' ', '%s').replace('&', '\&')
            result = self._adb_command(['shell', 'input', 'text', escaped_text])
            
            if result.returncode == 0:
                logger.info(f"输入文本: {text}")
                return {'success': True}
            else:
                return {'success': False, 'error': result.stderr}
                
        except Exception as e:
            logger.error(f"输入文本失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _press_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """按键操作"""
        key_code = params.get('key_code')
        
        if key_code is None:
            return {'success': False, 'error': '缺少按键代码'}
        
        try:
            result = self._adb_command(['shell', 'input', 'keyevent', str(key_code)])
            
            if result.returncode == 0:
                logger.info(f"按键: {key_code}")
                return {'success': True}
            else:
                return {'success': False, 'error': result.stderr}
                
        except Exception as e:
            logger.error(f"按键操作失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _take_screenshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """截图"""
        output_path = params.get('output_path', 'temp_screenshot.png')
        
        try:
            # 在设备上截图
            result = self._adb_command(['shell', 'screencap', '/sdcard/screenshot.png'])
            if result.returncode != 0:
                return {'success': False, 'error': '设备截图失败'}
            
            # 拉取截图到本地
            result = self._adb_command(['pull', '/sdcard/screenshot.png', output_path])
            if result.returncode != 0:
                return {'success': False, 'error': '拉取截图失败'}
            
            # 删除设备上的临时文件
            self._adb_command(['shell', 'rm', '/sdcard/screenshot.png'])
            
            logger.info(f"截图保存到: {output_path}")
            return {'success': True, 'screenshot_path': output_path}
            
        except Exception as e:
            logger.error(f"截图操作失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _get_device_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取设备信息"""
        try:
            info = {}
            
            # 获取设备型号
            result = self._adb_command(['shell', 'getprop', 'ro.product.model'])
            if result.returncode == 0:
                info['model'] = result.stdout.strip()
            
            # 获取Android版本
            result = self._adb_command(['shell', 'getprop', 'ro.build.version.release'])
            if result.returncode == 0:
                info['android_version'] = result.stdout.strip()
            
            # 获取屏幕分辨率
            result = self._adb_command(['shell', 'wm', 'size'])
            if result.returncode == 0:
                size_line = result.stdout.strip()
                if 'Physical size:' in size_line:
                    resolution = size_line.split(': ')[1]
                    info['resolution'] = resolution
            
            return {'success': True, 'device_info': info}
            
        except Exception as e:
            logger.error(f"获取设备信息失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _start_app(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """启动应用"""
        package_name = params.get('package_name')
        activity = params.get('activity')
        
        if not package_name:
            return {'success': False, 'error': '缺少应用包名'}
        
        try:
            cmd = ['shell', 'am', 'start']
            if activity:
                cmd.extend(['-n', f"{package_name}/{activity}"])
            else:
                cmd.extend(['-n', package_name])
            
            result = self._adb_command(cmd)
            
            if result.returncode == 0:
                logger.info(f"启动应用: {package_name}")
                return {'success': True}
            else:
                return {'success': False, 'error': result.stderr}
                
        except Exception as e:
            logger.error(f"启动应用失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _stop_app(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """停止应用"""
        package_name = params.get('package_name')
        
        if not package_name:
            return {'success': False, 'error': '缺少应用包名'}
        
        try:
            result = self._adb_command(['shell', 'am', 'force-stop', package_name])
            
            if result.returncode == 0:
                logger.info(f"停止应用: {package_name}")
                return {'success': True}
            else:
                return {'success': False, 'error': result.stderr}
                
        except Exception as e:
            logger.error(f"停止应用失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _install_apk(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """安装APK"""
        apk_path = params.get('apk_path')
        
        if not apk_path or not os.path.exists(apk_path):
            return {'success': False, 'error': 'APK文件不存在'}
        
        try:
            result = self._adb_command(['install', apk_path])
            
            if result.returncode == 0:
                logger.info(f"安装APK: {apk_path}")
                return {'success': True}
            else:
                return {'success': False, 'error': result.stderr}
                
        except Exception as e:
            logger.error(f"安装APK失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _uninstall_app(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """卸载应用"""
        package_name = params.get('package_name')
        
        if not package_name:
            return {'success': False, 'error': '缺少应用包名'}
        
        try:
            result = self._adb_command(['uninstall', package_name])
            
            if result.returncode == 0:
                logger.info(f"卸载应用: {package_name}")
                return {'success': True}
            else:
                return {'success': False, 'error': result.stderr}
                
        except Exception as e:
            logger.error(f"卸载应用失败: {str(e)}")
            return {'success': False, 'error': str(e)}