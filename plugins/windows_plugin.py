"""
Windows插件
用于Windows桌面应用程序自动化
"""
import time
import os
import subprocess
from typing import Dict, Any, List, Optional
from loguru import logger
import pyautogui
import psutil
from core.plugin_manager import BasePlugin

# Windows特定导入
try:
    import win32gui
    import win32con
    import win32api
    import win32process
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


class WindowsPlugin(BasePlugin):
    """Windows桌面自动化插件"""
    
    def __init__(self, engine):
        """初始化Windows插件"""
        super().__init__(engine)
        self.name = "windows"
        self.version = "1.0.0"
        self.description = "Windows桌面应用程序自动化插件"
        self.author = "AutoScript Team"
        
        self.process_timeout = self.engine.get_config('plugins.windows.process_timeout', 10)
        
        # 禁用pyautogui的安全检查
        pyautogui.FAILSAFE = False
        
    def initialize(self) -> bool:
        """初始化插件"""
        try:
            # 检查是否在Windows系统上
            if os.name != 'nt':
                logger.warning("Windows插件只能在Windows系统上运行")
                return False
            
            logger.info("Windows插件正在初始化...")
            return True
            
        except Exception as e:
            logger.error(f"Windows插件初始化失败: {e}")
            return False
    
    def cleanup(self):
        """清理插件资源"""
        try:
            logger.info("Windows插件资源已清理")
        except Exception as e:
            logger.error(f"清理Windows插件资源失败: {e}")
    
    def get_actions(self) -> List[str]:
        """获取支持的动作列表"""
        return [
            'launch_app',
            'kill_app',
            'find_window',
            'activate_window',
            'close_window',
            'maximize_window',
            'minimize_window',
            'click',
            'double_click',
            'right_click',
            'drag',
            'type_text',
            'key_press',
            'key_combination',
            'screenshot',
            'wait',
            'get_window_list',
            'get_process_list',
            'move_mouse',
            'scroll',
            'get_clipboard',
            'set_clipboard'
        ]
    
    def execute_action(self, action: Dict[str, Any]) -> Any:
        """执行动作"""
        action_type = action.get('type', '')
        
        try:
            if action_type == 'launch_app':
                return self._launch_app(action)
            elif action_type == 'kill_app':
                return self._kill_app(action)
            elif action_type == 'find_window':
                return self._find_window(action)
            elif action_type == 'activate_window':
                return self._activate_window(action)
            elif action_type == 'close_window':
                return self._close_window(action)
            elif action_type == 'maximize_window':
                return self._maximize_window(action)
            elif action_type == 'minimize_window':
                return self._minimize_window(action)
            elif action_type == 'click':
                return self._click(action)
            elif action_type == 'double_click':
                return self._double_click(action)
            elif action_type == 'right_click':
                return self._right_click(action)
            elif action_type == 'drag':
                return self._drag(action)
            elif action_type == 'type_text':
                return self._type_text(action)
            elif action_type == 'key_press':
                return self._key_press(action)
            elif action_type == 'key_combination':
                return self._key_combination(action)
            elif action_type == 'screenshot':
                return self._screenshot(action)
            elif action_type == 'wait':
                return self._wait(action)
            elif action_type == 'get_window_list':
                return self._get_window_list(action)
            elif action_type == 'get_process_list':
                return self._get_process_list(action)
            elif action_type == 'move_mouse':
                return self._move_mouse(action)
            elif action_type == 'scroll':
                return self._scroll(action)
            elif action_type == 'get_clipboard':
                return self._get_clipboard(action)
            elif action_type == 'set_clipboard':
                return self._set_clipboard(action)
            else:
                raise ValueError(f"不支持的动作类型: {action_type}")
                
        except Exception as e:
            logger.error(f"执行Windows动作失败: {action_type} - {e}")
            raise
    
    def _launch_app(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """启动应用程序"""
        app_path = action.get('app_path', '')
        args = action.get('args', [])
        working_dir = action.get('working_dir', None)
        
        if not app_path:
            raise ValueError("应用程序路径不能为空")
        
        try:
            # 构建命令
            cmd = [app_path] + args
            
            # 启动进程
            process = subprocess.Popen(
                cmd,
                cwd=working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            logger.info(f"应用程序启动成功: {app_path} (PID: {process.pid})")
            return {
                'success': True,
                'pid': process.pid,
                'app_path': app_path
            }
            
        except Exception as e:
            logger.error(f"启动应用程序失败: {app_path} - {e}")
            raise
    
    def _kill_app(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """终止应用程序"""
        process_name = action.get('process_name', '')
        pid = action.get('pid', None)
        
        if not process_name and not pid:
            raise ValueError("必须指定进程名或PID")
        
        try:
            killed_processes = []
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if (process_name and proc.info['name'].lower() == process_name.lower()) or \
                       (pid and proc.info['pid'] == pid):
                        proc.terminate()
                        killed_processes.append(proc.info)
                        logger.info(f"终止进程: {proc.info['name']} (PID: {proc.info['pid']})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {
                'success': True,
                'killed_processes': killed_processes
            }
            
        except Exception as e:
            logger.error(f"终止应用程序失败: {e}")
            raise
    
    def _find_window(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """查找窗口"""
        if not WIN32_AVAILABLE:
            raise Exception("需要pywin32库来支持窗口操作")
        
        title = action.get('title', '')
        class_name = action.get('class_name', '')
        
        if not title and not class_name:
            raise ValueError("必须指定窗口标题或类名")
        
        try:
            hwnd = win32gui.FindWindow(class_name or None, title or None)
            
            if hwnd:
                # 获取窗口信息
                window_text = win32gui.GetWindowText(hwnd)
                class_name = win32gui.GetClassName(hwnd)
                rect = win32gui.GetWindowRect(hwnd)
                
                logger.info(f"找到窗口: {window_text} (HWND: {hwnd})")
                return {
                    'success': True,
                    'hwnd': hwnd,
                    'title': window_text,
                    'class_name': class_name,
                    'rect': rect
                }
            else:
                logger.warning(f"未找到窗口: {title or class_name}")
                return {'success': False}
                
        except Exception as e:
            logger.error(f"查找窗口失败: {e}")
            raise
    
    def _activate_window(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """激活窗口"""
        if not WIN32_AVAILABLE:
            raise Exception("需要pywin32库来支持窗口操作")
        
        hwnd = action.get('hwnd', None)
        title = action.get('title', '')
        
        if not hwnd and not title:
            raise ValueError("必须指定窗口句柄或标题")
        
        try:
            if not hwnd:
                hwnd = win32gui.FindWindow(None, title)
                if not hwnd:
                    raise Exception(f"未找到窗口: {title}")
            
            # 激活窗口
            win32gui.SetForegroundWindow(hwnd)
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            
            logger.info(f"窗口激活成功: HWND {hwnd}")
            return {'success': True, 'hwnd': hwnd}
            
        except Exception as e:
            logger.error(f"激活窗口失败: {e}")
            raise
    
    def _close_window(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """关闭窗口"""
        if not WIN32_AVAILABLE:
            raise Exception("需要pywin32库来支持窗口操作")
        
        hwnd = action.get('hwnd', None)
        title = action.get('title', '')
        
        if not hwnd and not title:
            raise ValueError("必须指定窗口句柄或标题")
        
        try:
            if not hwnd:
                hwnd = win32gui.FindWindow(None, title)
                if not hwnd:
                    raise Exception(f"未找到窗口: {title}")
            
            # 关闭窗口
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            
            logger.info(f"窗口关闭成功: HWND {hwnd}")
            return {'success': True, 'hwnd': hwnd}
            
        except Exception as e:
            logger.error(f"关闭窗口失败: {e}")
            raise
    
    def _maximize_window(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """最大化窗口"""
        if not WIN32_AVAILABLE:
            raise Exception("需要pywin32库来支持窗口操作")
        
        hwnd = action.get('hwnd', None)
        title = action.get('title', '')
        
        if not hwnd and not title:
            raise ValueError("必须指定窗口句柄或标题")
        
        try:
            if not hwnd:
                hwnd = win32gui.FindWindow(None, title)
                if not hwnd:
                    raise Exception(f"未找到窗口: {title}")
            
            # 最大化窗口
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            
            logger.info(f"窗口最大化成功: HWND {hwnd}")
            return {'success': True, 'hwnd': hwnd}
            
        except Exception as e:
            logger.error(f"最大化窗口失败: {e}")
            raise
    
    def _minimize_window(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """最小化窗口"""
        if not WIN32_AVAILABLE:
            raise Exception("需要pywin32库来支持窗口操作")
        
        hwnd = action.get('hwnd', None)
        title = action.get('title', '')
        
        if not hwnd and not title:
            raise ValueError("必须指定窗口句柄或标题")
        
        try:
            if not hwnd:
                hwnd = win32gui.FindWindow(None, title)
                if not hwnd:
                    raise Exception(f"未找到窗口: {title}")
            
            # 最小化窗口
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            
            logger.info(f"窗口最小化成功: HWND {hwnd}")
            return {'success': True, 'hwnd': hwnd}
            
        except Exception as e:
            logger.error(f"最小化窗口失败: {e}")
            raise
    
    def _click(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """点击"""
        x = action.get('x', 0)
        y = action.get('y', 0)
        button = action.get('button', 'left')
        
        try:
            pyautogui.click(x, y, button=button)
            
            logger.info(f"点击成功: ({x}, {y}) {button}")
            return {'success': True, 'x': x, 'y': y, 'button': button}
            
        except Exception as e:
            logger.error(f"点击失败: {e}")
            raise
    
    def _double_click(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """双击"""
        x = action.get('x', 0)
        y = action.get('y', 0)
        
        try:
            pyautogui.doubleClick(x, y)
            
            logger.info(f"双击成功: ({x}, {y})")
            return {'success': True, 'x': x, 'y': y}
            
        except Exception as e:
            logger.error(f"双击失败: {e}")
            raise
    
    def _right_click(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """右击"""
        x = action.get('x', 0)
        y = action.get('y', 0)
        
        try:
            pyautogui.rightClick(x, y)
            
            logger.info(f"右击成功: ({x}, {y})")
            return {'success': True, 'x': x, 'y': y}
            
        except Exception as e:
            logger.error(f"右击失败: {e}")
            raise
    
    def _drag(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """拖拽"""
        from_x = action.get('from_x', 0)
        from_y = action.get('from_y', 0)
        to_x = action.get('to_x', 0)
        to_y = action.get('to_y', 0)
        duration = action.get('duration', 0.5)
        
        try:
            pyautogui.drag(to_x - from_x, to_y - from_y, duration=duration, button='left')
            
            logger.info(f"拖拽成功: ({from_x}, {from_y}) -> ({to_x}, {to_y})")
            return {
                'success': True,
                'from_x': from_x,
                'from_y': from_y,
                'to_x': to_x,
                'to_y': to_y
            }
            
        except Exception as e:
            logger.error(f"拖拽失败: {e}")
            raise
    
    def _type_text(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """输入文本"""
        text = action.get('text', '')
        interval = action.get('interval', 0.01)
        
        try:
            pyautogui.typewrite(text, interval=interval)
            
            logger.info(f"输入文本成功: {text}")
            return {'success': True, 'text': text}
            
        except Exception as e:
            logger.error(f"输入文本失败: {e}")
            raise
    
    def _key_press(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """按键"""
        key = action.get('key', '')
        presses = action.get('presses', 1)
        interval = action.get('interval', 0.1)
        
        if not key:
            raise ValueError("按键不能为空")
        
        try:
            pyautogui.press(key, presses=presses, interval=interval)
            
            logger.info(f"按键成功: {key} x{presses}")
            return {'success': True, 'key': key, 'presses': presses}
            
        except Exception as e:
            logger.error(f"按键失败: {e}")
            raise
    
    def _key_combination(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """组合键"""
        keys = action.get('keys', [])
        
        if not keys:
            raise ValueError("组合键不能为空")
        
        try:
            pyautogui.hotkey(*keys)
            
            logger.info(f"组合键成功: {'+'.join(keys)}")
            return {'success': True, 'keys': keys}
            
        except Exception as e:
            logger.error(f"组合键失败: {e}")
            raise
    
    def _screenshot(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """截图"""
        path = action.get('path', 'screenshot.png')
        region = action.get('region', None)
        
        try:
            screenshot = pyautogui.screenshot(region=region)
            screenshot.save(path)
            
            logger.info(f"截图成功: {path}")
            return {'success': True, 'path': path}
            
        except Exception as e:
            logger.error(f"截图失败: {e}")
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
    
    def _get_window_list(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """获取窗口列表"""
        if not WIN32_AVAILABLE:
            raise Exception("需要pywin32库来支持窗口操作")
        
        try:
            windows = []
            
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_text = win32gui.GetWindowText(hwnd)
                    if window_text:
                        class_name = win32gui.GetClassName(hwnd)
                        rect = win32gui.GetWindowRect(hwnd)
                        windows.append({
                            'hwnd': hwnd,
                            'title': window_text,
                            'class_name': class_name,
                            'rect': rect
                        })
            
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            logger.info(f"获取窗口列表成功: {len(windows)} 个窗口")
            return {'success': True, 'windows': windows}
            
        except Exception as e:
            logger.error(f"获取窗口列表失败: {e}")
            raise
    
    def _get_process_list(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """获取进程列表"""
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            logger.info(f"获取进程列表成功: {len(processes)} 个进程")
            return {'success': True, 'processes': processes}
            
        except Exception as e:
            logger.error(f"获取进程列表失败: {e}")
            raise
    
    def _move_mouse(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """移动鼠标"""
        x = action.get('x', 0)
        y = action.get('y', 0)
        duration = action.get('duration', 0.5)
        
        try:
            pyautogui.moveTo(x, y, duration=duration)
            
            logger.info(f"移动鼠标成功: ({x}, {y})")
            return {'success': True, 'x': x, 'y': y}
            
        except Exception as e:
            logger.error(f"移动鼠标失败: {e}")
            raise
    
    def _scroll(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """滚动"""
        x = action.get('x', None)
        y = action.get('y', None)
        clicks = action.get('clicks', 3)
        
        try:
            pyautogui.scroll(clicks, x=x, y=y)
            
            logger.info(f"滚动成功: {clicks} 次")
            return {'success': True, 'clicks': clicks}
            
        except Exception as e:
            logger.error(f"滚动失败: {e}")
            raise
    
    def _get_clipboard(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """获取剪贴板内容"""
        try:
            import pyperclip
            text = pyperclip.paste()
            
            logger.info("获取剪贴板内容成功")
            return {'success': True, 'text': text}
            
        except Exception as e:
            logger.error(f"获取剪贴板内容失败: {e}")
            raise
    
    def _set_clipboard(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """设置剪贴板内容"""
        text = action.get('text', '')
        
        try:
            import pyperclip
            pyperclip.copy(text)
            
            logger.info("设置剪贴板内容成功")
            return {'success': True, 'text': text}
            
        except Exception as e:
            logger.error(f"设置剪贴板内容失败: {e}")
            raise