"""
Scrcpy插件
用于Android设备自动化控制
"""
import subprocess
import time
import threading
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger
import pyautogui
from core.plugin_manager import BasePlugin


class ScrcpyPlugin(BasePlugin):
    """Scrcpy Android设备控制插件"""
    
    def __init__(self, engine):
        """初始化Scrcpy插件"""
        super().__init__(engine)
        self.name = "scrcpy"
        self.version = "1.0.0"
        self.description = "Android设备自动化控制插件，基于scrcpy"
        self.author = "AutoScript Team"
        
        self.scrcpy_process = None
        self.device_id = None
        self.screen_size = None
        self.scale_factor = 1.0
        
        # 配置参数
        self.max_size = self.engine.get_config('plugins.scrcpy.max_size', 1920)
        self.bit_rate = self.engine.get_config('plugins.scrcpy.bit_rate', '8M')
        
    def initialize(self) -> bool:
        """初始化插件"""
        try:
            # 检查scrcpy是否可用
            try:
                result = subprocess.run(['scrcpy', '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode != 0:
                    logger.error("scrcpy不可用，请确保已安装scrcpy")
                    return False
            except FileNotFoundError:
                logger.error("未找到scrcpy命令，请确保已安装scrcpy并添加到PATH")
                return False
            except subprocess.TimeoutExpired:
                logger.error("scrcpy命令超时")
                return False
            
            # 检查ADB是否可用
            try:
                result = subprocess.run(['adb', 'version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode != 0:
                    logger.error("ADB不可用，请确保已安装ADB")
                    return False
            except FileNotFoundError:
                logger.error("未找到ADB命令，请确保已安装ADB并添加到PATH")
                return False
            except subprocess.TimeoutExpired:
                logger.error("ADB命令超时")
                return False
            
            logger.info("Scrcpy插件初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"Scrcpy插件初始化失败: {e}")
            return False
    
    def cleanup(self):
        """清理插件资源"""
        try:
            if self.scrcpy_process:
                self.scrcpy_process.terminate()
                self.scrcpy_process.wait(timeout=5)
                self.scrcpy_process = None
            logger.info("Scrcpy插件资源已清理")
        except Exception as e:
            logger.error(f"清理Scrcpy插件资源失败: {e}")
    
    def get_actions(self) -> List[str]:
        """获取支持的动作列表"""
        return [
            'connect_device',
            'disconnect_device',
            'start_scrcpy',
            'stop_scrcpy',
            'get_devices',
            'click',
            'tap',
            'swipe',
            'scroll',
            'type_text',
            'key_press',
            'key_combination',
            'screenshot',
            'install_apk',
            'uninstall_app',
            'start_app',
            'stop_app',
            'get_app_list',
            'push_file',
            'pull_file',
            'shell_command',
            'get_device_info',
            'wait'
        ]
    
    def execute_action(self, action: Dict[str, Any]) -> Any:
        """执行动作"""
        action_type = action.get('type', '')
        
        try:
            if action_type == 'connect_device':
                return self._connect_device(action)
            elif action_type == 'disconnect_device':
                return self._disconnect_device(action)
            elif action_type == 'start_scrcpy':
                return self._start_scrcpy(action)
            elif action_type == 'stop_scrcpy':
                return self._stop_scrcpy(action)
            elif action_type == 'get_devices':
                return self._get_devices(action)
            elif action_type == 'click':
                return self._click(action)
            elif action_type == 'tap':
                return self._tap(action)
            elif action_type == 'swipe':
                return self._swipe(action)
            elif action_type == 'scroll':
                return self._scroll(action)
            elif action_type == 'type_text':
                return self._type_text(action)
            elif action_type == 'key_press':
                return self._key_press(action)
            elif action_type == 'key_combination':
                return self._key_combination(action)
            elif action_type == 'screenshot':
                return self._screenshot(action)
            elif action_type == 'install_apk':
                return self._install_apk(action)
            elif action_type == 'uninstall_app':
                return self._uninstall_app(action)
            elif action_type == 'start_app':
                return self._start_app(action)
            elif action_type == 'stop_app':
                return self._stop_app(action)
            elif action_type == 'get_app_list':
                return self._get_app_list(action)
            elif action_type == 'push_file':
                return self._push_file(action)
            elif action_type == 'pull_file':
                return self._pull_file(action)
            elif action_type == 'shell_command':
                return self._shell_command(action)
            elif action_type == 'get_device_info':
                return self._get_device_info(action)
            elif action_type == 'wait':
                return self._wait(action)
            else:
                raise ValueError(f"不支持的动作类型: {action_type}")
                
        except Exception as e:
            logger.error(f"执行Scrcpy动作失败: {action_type} - {e}")
            raise
    
    def _connect_device(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """连接设备"""
        device_ip = action.get('device_ip', '')
        port = action.get('port', 5555)
        
        if not device_ip:
            raise ValueError("设备IP不能为空")
        
        try:
            # 连接设备
            cmd = ['adb', 'connect', f'{device_ip}:{port}']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.device_id = f'{device_ip}:{port}'
                logger.info(f"设备连接成功: {self.device_id}")
                return {'success': True, 'device_id': self.device_id}
            else:
                raise Exception(f"连接失败: {result.stderr}")
                
        except Exception as e:
            logger.error(f"连接设备失败: {e}")
            raise
    
    def _disconnect_device(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """断开设备连接"""
        device_id = action.get('device_id', self.device_id)
        
        try:
            if device_id:
                cmd = ['adb', 'disconnect', device_id]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    logger.info(f"设备断开连接成功: {device_id}")
                    if device_id == self.device_id:
                        self.device_id = None
                    return {'success': True}
                else:
                    raise Exception(f"断开连接失败: {result.stderr}")
            else:
                logger.warning("没有设备需要断开连接")
                return {'success': True}
                
        except Exception as e:
            logger.error(f"断开设备连接失败: {e}")
            raise
    
    def _start_scrcpy(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """启动scrcpy"""
        device_id = action.get('device_id', self.device_id)
        
        try:
            if self.scrcpy_process:
                logger.warning("Scrcpy已在运行")
                return {'success': True}
            
            # 构建scrcpy命令
            cmd = ['scrcpy']
            
            if device_id:
                cmd.extend(['-s', device_id])
            
            cmd.extend([
                '--max-size', str(self.max_size),
                '--bit-rate', self.bit_rate,
                '--no-audio'
            ])
            
            # 添加额外参数
            if action.get('fullscreen', False):
                cmd.append('--fullscreen')
            
            if action.get('always_on_top', False):
                cmd.append('--always-on-top')
            
            # 启动scrcpy
            self.scrcpy_process = subprocess.Popen(cmd, 
                                                  stdout=subprocess.PIPE,
                                                  stderr=subprocess.PIPE)
            
            # 等待scrcpy启动
            time.sleep(2)
            
            logger.info(f"Scrcpy启动成功")
            return {'success': True}
            
        except Exception as e:
            logger.error(f"启动scrcpy失败: {e}")
            raise
    
    def _stop_scrcpy(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """停止scrcpy"""
        try:
            if self.scrcpy_process:
                self.scrcpy_process.terminate()
                self.scrcpy_process.wait(timeout=5)
                self.scrcpy_process = None
                logger.info("Scrcpy已停止")
            else:
                logger.warning("Scrcpy未在运行")
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"停止scrcpy失败: {e}")
            raise
    
    def _get_devices(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """获取设备列表"""
        try:
            cmd = ['adb', 'devices']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                devices = []
                lines = result.stdout.strip().split('\n')[1:]  # 跳过标题行
                
                for line in lines:
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            devices.append({
                                'id': parts[0],
                                'status': parts[1]
                            })
                
                logger.info(f"获取设备列表成功: {len(devices)} 个设备")
                return {'success': True, 'devices': devices}
            else:
                raise Exception(f"获取设备列表失败: {result.stderr}")
                
        except Exception as e:
            logger.error(f"获取设备列表失败: {e}")
            raise
    
    def _click(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """点击（通过scrcpy窗口）"""
        x = action.get('x', 0)
        y = action.get('y', 0)
        
        try:
            # 在scrcpy窗口中点击
            pyautogui.click(x, y)
            
            logger.info(f"点击成功: ({x}, {y})")
            return {'success': True, 'x': x, 'y': y}
            
        except Exception as e:
            logger.error(f"点击失败: {e}")
            raise
    
    def _tap(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """点击（通过ADB）"""
        x = action.get('x', 0)
        y = action.get('y', 0)
        device_id = action.get('device_id', self.device_id)
        
        try:
            cmd = ['adb']
            if device_id:
                cmd.extend(['-s', device_id])
            cmd.extend(['shell', 'input', 'tap', str(x), str(y)])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logger.info(f"点击成功: ({x}, {y})")
                return {'success': True, 'x': x, 'y': y}
            else:
                raise Exception(f"点击失败: {result.stderr}")
                
        except Exception as e:
            logger.error(f"点击失败: {e}")
            raise
    
    def _swipe(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """滑动"""
        from_x = action.get('from_x', 0)
        from_y = action.get('from_y', 0)
        to_x = action.get('to_x', 0)
        to_y = action.get('to_y', 0)
        duration = action.get('duration', 1000)
        device_id = action.get('device_id', self.device_id)
        
        try:
            cmd = ['adb']
            if device_id:
                cmd.extend(['-s', device_id])
            cmd.extend(['shell', 'input', 'swipe', 
                       str(from_x), str(from_y), str(to_x), str(to_y), str(duration)])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logger.info(f"滑动成功: ({from_x}, {from_y}) -> ({to_x}, {to_y})")
                return {
                    'success': True,
                    'from_x': from_x,
                    'from_y': from_y,
                    'to_x': to_x,
                    'to_y': to_y
                }
            else:
                raise Exception(f"滑动失败: {result.stderr}")
                
        except Exception as e:
            logger.error(f"滑动失败: {e}")
            raise
    
    def _scroll(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """滚动"""
        x = action.get('x', 500)
        y = action.get('y', 500)
        direction = action.get('direction', 'down')
        device_id = action.get('device_id', self.device_id)
        
        try:
            # 根据方向计算滚动距离
            if direction == 'up':
                to_y = y - 500
            elif direction == 'down':
                to_y = y + 500
            elif direction == 'left':
                to_x = x - 500
                to_y = y
            elif direction == 'right':
                to_x = x + 500
                to_y = y
            else:
                raise ValueError(f"不支持的滚动方向: {direction}")
            
            # 如果是上下滚动
            if direction in ['up', 'down']:
                to_x = x
            
            cmd = ['adb']
            if device_id:
                cmd.extend(['-s', device_id])
            cmd.extend(['shell', 'input', 'swipe', str(x), str(y), str(to_x), str(to_y)])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logger.info(f"滚动成功: {direction}")
                return {'success': True, 'direction': direction}
            else:
                raise Exception(f"滚动失败: {result.stderr}")
                
        except Exception as e:
            logger.error(f"滚动失败: {e}")
            raise
    
    def _type_text(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """输入文本"""
        text = action.get('text', '')
        device_id = action.get('device_id', self.device_id)
        
        if not text:
            raise ValueError("文本不能为空")
        
        try:
            # 转义特殊字符
            escaped_text = text.replace(' ', '%s').replace('&', '\\&')
            
            cmd = ['adb']
            if device_id:
                cmd.extend(['-s', device_id])
            cmd.extend(['shell', 'input', 'text', escaped_text])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logger.info(f"输入文本成功: {text}")
                return {'success': True, 'text': text}
            else:
                raise Exception(f"输入文本失败: {result.stderr}")
                
        except Exception as e:
            logger.error(f"输入文本失败: {e}")
            raise
    
    def _key_press(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """按键"""
        key = action.get('key', '')
        device_id = action.get('device_id', self.device_id)
        
        if not key:
            raise ValueError("按键不能为空")
        
        try:
            cmd = ['adb']
            if device_id:
                cmd.extend(['-s', device_id])
            cmd.extend(['shell', 'input', 'keyevent', key])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logger.info(f"按键成功: {key}")
                return {'success': True, 'key': key}
            else:
                raise Exception(f"按键失败: {result.stderr}")
                
        except Exception as e:
            logger.error(f"按键失败: {e}")
            raise
    
    def _key_combination(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """组合键"""
        keys = action.get('keys', [])
        device_id = action.get('device_id', self.device_id)
        
        if not keys:
            raise ValueError("组合键不能为空")
        
        try:
            # 执行多个按键
            for key in keys:
                cmd = ['adb']
                if device_id:
                    cmd.extend(['-s', device_id])
                cmd.extend(['shell', 'input', 'keyevent', key])
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    raise Exception(f"按键失败: {key} - {result.stderr}")
            
            logger.info(f"组合键成功: {'+'.join(keys)}")
            return {'success': True, 'keys': keys}
            
        except Exception as e:
            logger.error(f"组合键失败: {e}")
            raise
    
    def _screenshot(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """截图"""
        path = action.get('path', 'screenshot.png')
        device_id = action.get('device_id', self.device_id)
        
        try:
            # 在设备上截图
            cmd = ['adb']
            if device_id:
                cmd.extend(['-s', device_id])
            cmd.extend(['shell', 'screencap', '/sdcard/screenshot.png'])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                raise Exception(f"设备截图失败: {result.stderr}")
            
            # 拉取截图到本地
            cmd = ['adb']
            if device_id:
                cmd.extend(['-s', device_id])
            cmd.extend(['pull', '/sdcard/screenshot.png', path])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                raise Exception(f"拉取截图失败: {result.stderr}")
            
            logger.info(f"截图成功: {path}")
            return {'success': True, 'path': path}
            
        except Exception as e:
            logger.error(f"截图失败: {e}")
            raise
    
    def _install_apk(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """安装APK"""
        apk_path = action.get('apk_path', '')
        device_id = action.get('device_id', self.device_id)
        
        if not apk_path:
            raise ValueError("APK路径不能为空")
        
        try:
            cmd = ['adb']
            if device_id:
                cmd.extend(['-s', device_id])
            cmd.extend(['install', apk_path])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info(f"APK安装成功: {apk_path}")
                return {'success': True, 'apk_path': apk_path}
            else:
                raise Exception(f"APK安装失败: {result.stderr}")
                
        except Exception as e:
            logger.error(f"APK安装失败: {e}")
            raise
    
    def _uninstall_app(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """卸载应用"""
        package_name = action.get('package_name', '')
        device_id = action.get('device_id', self.device_id)
        
        if not package_name:
            raise ValueError("包名不能为空")
        
        try:
            cmd = ['adb']
            if device_id:
                cmd.extend(['-s', device_id])
            cmd.extend(['uninstall', package_name])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"应用卸载成功: {package_name}")
                return {'success': True, 'package_name': package_name}
            else:
                raise Exception(f"应用卸载失败: {result.stderr}")
                
        except Exception as e:
            logger.error(f"应用卸载失败: {e}")
            raise
    
    def _start_app(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """启动应用"""
        package_name = action.get('package_name', '')
        activity_name = action.get('activity_name', '')
        device_id = action.get('device_id', self.device_id)
        
        if not package_name:
            raise ValueError("包名不能为空")
        
        try:
            cmd = ['adb']
            if device_id:
                cmd.extend(['-s', device_id])
            
            if activity_name:
                cmd.extend(['shell', 'am', 'start', '-n', f'{package_name}/{activity_name}'])
            else:
                cmd.extend(['shell', 'monkey', '-p', package_name, '-c', 'android.intent.category.LAUNCHER', '1'])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logger.info(f"应用启动成功: {package_name}")
                return {'success': True, 'package_name': package_name}
            else:
                raise Exception(f"应用启动失败: {result.stderr}")
                
        except Exception as e:
            logger.error(f"应用启动失败: {e}")
            raise
    
    def _stop_app(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """停止应用"""
        package_name = action.get('package_name', '')
        device_id = action.get('device_id', self.device_id)
        
        if not package_name:
            raise ValueError("包名不能为空")
        
        try:
            cmd = ['adb']
            if device_id:
                cmd.extend(['-s', device_id])
            cmd.extend(['shell', 'am', 'force-stop', package_name])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logger.info(f"应用停止成功: {package_name}")
                return {'success': True, 'package_name': package_name}
            else:
                raise Exception(f"应用停止失败: {result.stderr}")
                
        except Exception as e:
            logger.error(f"应用停止失败: {e}")
            raise
    
    def _get_app_list(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """获取应用列表"""
        device_id = action.get('device_id', self.device_id)
        
        try:
            cmd = ['adb']
            if device_id:
                cmd.extend(['-s', device_id])
            cmd.extend(['shell', 'pm', 'list', 'packages'])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                apps = []
                for line in result.stdout.strip().split('\n'):
                    if line.startswith('package:'):
                        package_name = line.replace('package:', '')
                        apps.append(package_name)
                
                logger.info(f"获取应用列表成功: {len(apps)} 个应用")
                return {'success': True, 'apps': apps}
            else:
                raise Exception(f"获取应用列表失败: {result.stderr}")
                
        except Exception as e:
            logger.error(f"获取应用列表失败: {e}")
            raise
    
    def _push_file(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """推送文件到设备"""
        local_path = action.get('local_path', '')
        remote_path = action.get('remote_path', '')
        device_id = action.get('device_id', self.device_id)
        
        if not local_path or not remote_path:
            raise ValueError("本地路径和远程路径不能为空")
        
        try:
            cmd = ['adb']
            if device_id:
                cmd.extend(['-s', device_id])
            cmd.extend(['push', local_path, remote_path])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info(f"文件推送成功: {local_path} -> {remote_path}")
                return {'success': True, 'local_path': local_path, 'remote_path': remote_path}
            else:
                raise Exception(f"文件推送失败: {result.stderr}")
                
        except Exception as e:
            logger.error(f"文件推送失败: {e}")
            raise
    
    def _pull_file(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """从设备拉取文件"""
        remote_path = action.get('remote_path', '')
        local_path = action.get('local_path', '')
        device_id = action.get('device_id', self.device_id)
        
        if not remote_path or not local_path:
            raise ValueError("远程路径和本地路径不能为空")
        
        try:
            cmd = ['adb']
            if device_id:
                cmd.extend(['-s', device_id])
            cmd.extend(['pull', remote_path, local_path])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info(f"文件拉取成功: {remote_path} -> {local_path}")
                return {'success': True, 'remote_path': remote_path, 'local_path': local_path}
            else:
                raise Exception(f"文件拉取失败: {result.stderr}")
                
        except Exception as e:
            logger.error(f"文件拉取失败: {e}")
            raise
    
    def _shell_command(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """执行Shell命令"""
        command = action.get('command', '')
        device_id = action.get('device_id', self.device_id)
        
        if not command:
            raise ValueError("命令不能为空")
        
        try:
            cmd = ['adb']
            if device_id:
                cmd.extend(['-s', device_id])
            cmd.extend(['shell', command])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            logger.info(f"Shell命令执行完成: {command}")
            return {
                'success': True,
                'command': command,
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode
            }
            
        except Exception as e:
            logger.error(f"Shell命令执行失败: {e}")
            raise
    
    def _get_device_info(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """获取设备信息"""
        device_id = action.get('device_id', self.device_id)
        
        try:
            info = {}
            
            # 获取设备型号
            cmd = ['adb']
            if device_id:
                cmd.extend(['-s', device_id])
            cmd.extend(['shell', 'getprop', 'ro.product.model'])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                info['model'] = result.stdout.strip()
            
            # 获取Android版本
            cmd = ['adb']
            if device_id:
                cmd.extend(['-s', device_id])
            cmd.extend(['shell', 'getprop', 'ro.build.version.release'])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                info['android_version'] = result.stdout.strip()
            
            # 获取屏幕分辨率
            cmd = ['adb']
            if device_id:
                cmd.extend(['-s', device_id])
            cmd.extend(['shell', 'wm', 'size'])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                output = result.stdout.strip()
                if 'Physical size:' in output:
                    size_part = output.split('Physical size:')[1].strip()
                    info['screen_size'] = size_part
            
            logger.info(f"获取设备信息成功: {info}")
            return {'success': True, 'info': info}
            
        except Exception as e:
            logger.error(f"获取设备信息失败: {e}")
            raise
    
    def _wait(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """等待"""
        duration = action.get('duration', 1)
        
        try:
            time.sleep(duration)
            
            logger.info(f"等待完成: {duration}秒")
            return {'success': True, 'duration': duration}
            
        except Exception as e:
            logger.error(f"等待失败: {e}")
            raise