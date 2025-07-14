"""
脚本执行引擎 - 支持扩展性、条件判断、轮询调度等功能
"""
import time
import threading
import asyncio
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
import logging
# import cv2
# import numpy as np
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ExecutionContext:
    """执行上下文"""
    variables: Dict[str, Any]
    plugin_manager: Any
    template_matcher: Any
    ocr_engine: Any
    game_id: str
    script_id: str
    execution_id: str
    start_time: datetime
    last_action_time: datetime
    exception_script_id: Optional[str] = None

class ActionResult:
    """动作执行结果"""
    def __init__(self, success: bool, data: Any = None, error: str = None):
        self.success = success
        self.data = data
        self.error = error
        self.timestamp = datetime.now()

class ScriptExecutor:
    """脚本执行器"""
    
    def __init__(self, plugin_manager, template_matcher, ocr_engine):
        self.plugin_manager = plugin_manager
        self.template_matcher = template_matcher
        self.ocr_engine = ocr_engine
        
        self.running_scripts: Dict[str, threading.Thread] = {}
        self.execution_contexts: Dict[str, ExecutionContext] = {}
        self.should_stop: Dict[str, threading.Event] = {}
        
        # 异常检测定时器
        self.exception_check_interval = 60  # 60秒
        self.exception_timer = None
        self.start_exception_monitoring()
    
    def start_exception_monitoring(self):
        """启动异常监控"""
        def check_exceptions():
            while True:
                current_time = datetime.now()
                for execution_id, context in list(self.execution_contexts.items()):
                    # 检查是否超过1分钟没有执行动作
                    if (current_time - context.last_action_time).total_seconds() > 60:
                        logger.warning(f"检测到脚本异常: {execution_id}, 启动异常处理")
                        self._handle_script_exception(execution_id, context)
                
                time.sleep(self.exception_check_interval)
        
        self.exception_timer = threading.Thread(target=check_exceptions, daemon=True)
        self.exception_timer.start()
    
    def execute_script(self, game_id: str, script_id: str, script_content: Dict[str, Any], 
                      exception_script_id: Optional[str] = None) -> str:
        """执行脚本"""
        execution_id = f"{game_id}_{script_id}_{int(time.time())}"
        
        # 创建执行上下文
        context = ExecutionContext(
            variables={},
            plugin_manager=self.plugin_manager,
            template_matcher=self.template_matcher,
            ocr_engine=self.ocr_engine,
            game_id=game_id,
            script_id=script_id,
            execution_id=execution_id,
            start_time=datetime.now(),
            last_action_time=datetime.now(),
            exception_script_id=exception_script_id
        )
        
        self.execution_contexts[execution_id] = context
        self.should_stop[execution_id] = threading.Event()
        
        # 在新线程中执行脚本
        thread = threading.Thread(
            target=self._execute_script_thread,
            args=(execution_id, script_content),
            daemon=True
        )
        
        self.running_scripts[execution_id] = thread
        thread.start()
        
        logger.info(f"开始执行脚本: {execution_id}")
        return execution_id
    
    def _execute_script_thread(self, execution_id: str, script_content: Dict[str, Any]):
        """在线程中执行脚本"""
        try:
            context = self.execution_contexts[execution_id]
            actions = script_content.get('actions', [])
            
            for action in actions:
                if self.should_stop[execution_id].is_set():
                    break
                
                result = self._execute_action(context, action)
                context.last_action_time = datetime.now()
                
                if not result.success:
                    logger.error(f"动作执行失败: {result.error}")
                    break
            
        except Exception as e:
            logger.error(f"脚本执行异常: {str(e)}", exc_info=True)
        finally:
            self._cleanup_execution(execution_id)
    
    def _execute_action(self, context: ExecutionContext, action: Dict[str, Any]) -> ActionResult:
        """执行单个动作"""
        action_type = action.get('type')
        
        try:
            if action_type == 'plugin_action':
                return self._execute_plugin_action(context, action)
            elif action_type == 'condition':
                return self._execute_condition(context, action)
            elif action_type == 'polling_loop':
                return self._execute_polling_loop(context, action)
            elif action_type == 'template_match':
                return self._execute_template_match(context, action)
            elif action_type == 'ocr_text':
                return self._execute_ocr_text(context, action)
            elif action_type == 'wait':
                return self._execute_wait(context, action)
            elif action_type == 'set_variable':
                return self._execute_set_variable(context, action)
            elif action_type == 'restart_script':
                return self._execute_restart_script(context, action)
            else:
                return ActionResult(False, error=f"不支持的动作类型: {action_type}")
                
        except Exception as e:
            logger.error(f"执行动作时出错: {str(e)}", exc_info=True)
            return ActionResult(False, error=str(e))
    
    def _execute_plugin_action(self, context: ExecutionContext, action: Dict[str, Any]) -> ActionResult:
        """执行插件动作"""
        plugin_name = action.get('plugin')
        action_name = action.get('action')
        params = action.get('params', {})
        store_result = action.get('store_result')
        
        # 处理参数中的变量替换
        params = self._resolve_variables(context, params)
        
        try:
            result = context.plugin_manager.execute_action(plugin_name, action_name, params)
            
            # 存储结果到变量
            if store_result:
                context.variables[store_result] = result
            
            # 如果结果包含坐标信息，存储为特殊变量
            if isinstance(result, dict):
                if 'x' in result and 'y' in result:
                    context.variables['match_x'] = result['x']
                    context.variables['match_y'] = result['y']
                if 'screenshot_path' in result:
                    context.variables['screenshot'] = result['screenshot_path']
            
            return ActionResult(True, result)
            
        except Exception as e:
            return ActionResult(False, error=str(e))
    
    def _execute_condition(self, context: ExecutionContext, action: Dict[str, Any]) -> ActionResult:
        """执行条件判断"""
        condition_type = action.get('condition_type')
        on_true = action.get('on_true', [])
        on_false = action.get('on_false', [])
        
        condition_result = False
        
        if condition_type == 'template_match':
            template_path = action.get('template_path')
            threshold = action.get('threshold', 0.8)
            input_image = action.get('input_image')
            
            # 解析输入图像
            if input_image and input_image.startswith('$'):
                var_name = input_image[1:]
                input_image = context.variables.get(var_name)
            
            if input_image and template_path:
                match_result = context.template_matcher.match_template(
                    input_image, template_path, threshold
                )
                condition_result = match_result['found']
                
                if condition_result:
                    context.variables['match_x'] = match_result['x']
                    context.variables['match_y'] = match_result['y']
                    context.variables['match_confidence'] = match_result['confidence']
        
                 elif condition_type == 'variable_compare':
             var_name = action.get('variable')
             compare_value = action.get('value')
             operator = action.get('operator', '==')
             
             if var_name:
                 var_value = context.variables.get(var_name)
                 
                 if operator == '==':
                     condition_result = var_value == compare_value
                 elif operator == '!=':
                     condition_result = var_value != compare_value
                 elif operator == '>' and var_value is not None and compare_value is not None:
                     condition_result = var_value > compare_value
                 elif operator == '<' and var_value is not None and compare_value is not None:
                     condition_result = var_value < compare_value
                 elif operator == '>=' and var_value is not None and compare_value is not None:
                     condition_result = var_value >= compare_value
                 elif operator == '<=' and var_value is not None and compare_value is not None:
                     condition_result = var_value <= compare_value
        
        # 执行对应的动作序列
        actions_to_execute = on_true if condition_result else on_false
        
        for sub_action in actions_to_execute:
            if context.execution_id in self.should_stop and self.should_stop[context.execution_id].is_set():
                break
            
            result = self._execute_action(context, sub_action)
            if not result.success:
                return result
        
        return ActionResult(True, {'condition_result': condition_result})
    
    def _execute_polling_loop(self, context: ExecutionContext, action: Dict[str, Any]) -> ActionResult:
        """执行轮询循环"""
        interval = action.get('interval', 1.0)
        max_iterations = action.get('max_iterations', 100)
        actions = action.get('actions', [])
        
        for i in range(max_iterations):
            if context.execution_id in self.should_stop and self.should_stop[context.execution_id].is_set():
                break
            
            # 执行循环内的动作
            for sub_action in actions:
                if context.execution_id in self.should_stop and self.should_stop[context.execution_id].is_set():
                    break
                
                result = self._execute_action(context, sub_action)
                context.last_action_time = datetime.now()
                
                # 如果是条件判断且条件为真，可以选择跳出循环
                if (sub_action.get('type') == 'condition' and 
                    result.success and 
                    result.data and 
                    result.data.get('condition_result') and
                    sub_action.get('break_on_true', False)):
                    return ActionResult(True, {'iterations': i + 1, 'break_reason': 'condition_true'})
            
            # 等待下一次循环
            if i < max_iterations - 1:
                time.sleep(interval)
        
        return ActionResult(True, {'iterations': max_iterations})
    
    def _execute_template_match(self, context: ExecutionContext, action: Dict[str, Any]) -> ActionResult:
        """执行模板匹配"""
        template_path = action.get('template_path')
        input_image = action.get('input_image')
        threshold = action.get('threshold', 0.8)
        store_result = action.get('store_result')
        
        # 解析输入图像
        if input_image and input_image.startswith('$'):
            var_name = input_image[1:]
            input_image = context.variables.get(var_name)
        
        if not input_image or not template_path:
            return ActionResult(False, error="缺少输入图像或模板路径")
        
        try:
            result = context.template_matcher.match_template(input_image, template_path, threshold)
            
            if store_result:
                context.variables[store_result] = result
            
            if result['found']:
                context.variables['match_x'] = result['x']
                context.variables['match_y'] = result['y']
                context.variables['match_confidence'] = result['confidence']
            
            return ActionResult(True, result)
            
        except Exception as e:
            return ActionResult(False, error=str(e))
    
    def _execute_ocr_text(self, context: ExecutionContext, action: Dict[str, Any]) -> ActionResult:
        """执行OCR文字识别"""
        input_image = action.get('input_image')
        region = action.get('region')  # [x, y, width, height]
        store_result = action.get('store_result')
        
        # 解析输入图像
        if input_image and input_image.startswith('$'):
            var_name = input_image[1:]
            input_image = context.variables.get(var_name)
        
        if not input_image:
            return ActionResult(False, error="缺少输入图像")
        
                 try:
             # 执行OCR（这里需要根据实际的OCR引擎实现）
             text = context.ocr_engine.extract_text(input_image, region)
             
             if store_result:
                 context.variables[store_result] = text
             
             return ActionResult(True, {'text': text})
             
         except Exception as e:
             return ActionResult(False, error=str(e))
    
    def _execute_wait(self, context: ExecutionContext, action: Dict[str, Any]) -> ActionResult:
        """执行等待"""
        duration = action.get('duration', 1.0)
        time.sleep(duration)
        return ActionResult(True)
    
    def _execute_set_variable(self, context: ExecutionContext, action: Dict[str, Any]) -> ActionResult:
        """设置变量"""
        var_name = action.get('name')
        var_value = action.get('value')
        
        if var_name:
            context.variables[var_name] = self._resolve_variables(context, var_value)
            return ActionResult(True)
        
        return ActionResult(False, error="缺少变量名")
    
    def _execute_restart_script(self, context: ExecutionContext, action: Dict[str, Any]) -> ActionResult:
        """重启脚本"""
        # 标记当前脚本停止
        if context.execution_id in self.should_stop:
            self.should_stop[context.execution_id].set()
        
        return ActionResult(True, {'action': 'restart'})
    
    def _resolve_variables(self, context: ExecutionContext, value: Any) -> Any:
        """解析变量引用"""
        if isinstance(value, str) and value.startswith('$'):
            var_name = value[1:]
            return context.variables.get(var_name, value)
        elif isinstance(value, dict):
            return {k: self._resolve_variables(context, v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._resolve_variables(context, item) for item in value]
        else:
            return value
    
    def _handle_script_exception(self, execution_id: str, context: ExecutionContext):
        """处理脚本异常"""
        if context.exception_script_id:
            logger.info(f"启动异常处理脚本: {context.exception_script_id}")
            # 这里可以启动异常处理脚本
            # 由于需要game_manager的引用，这个功能可能需要在更高层次实现
        
        # 停止当前脚本
        self.stop_script(execution_id)
    
    def stop_script(self, execution_id: str):
        """停止脚本执行"""
        if execution_id in self.should_stop:
            self.should_stop[execution_id].set()
            logger.info(f"停止脚本: {execution_id}")
    
    def stop_all_scripts(self):
        """停止所有脚本执行"""
        for execution_id in list(self.should_stop.keys()):
            self.stop_script(execution_id)
    
    def _cleanup_execution(self, execution_id: str):
        """清理执行相关资源"""
        if execution_id in self.running_scripts:
            del self.running_scripts[execution_id]
        
        if execution_id in self.execution_contexts:
            del self.execution_contexts[execution_id]
        
        if execution_id in self.should_stop:
            del self.should_stop[execution_id]
        
        logger.info(f"清理执行资源: {execution_id}")
    
    def get_running_scripts(self) -> List[Dict[str, Any]]:
        """获取正在运行的脚本列表"""
        running = []
        current_time = datetime.now()
        
        for execution_id, context in self.execution_contexts.items():
            if execution_id in self.running_scripts:
                thread = self.running_scripts[execution_id]
                running.append({
                    'execution_id': execution_id,
                    'game_id': context.game_id,
                    'script_id': context.script_id,
                    'start_time': context.start_time.isoformat(),
                    'last_action_time': context.last_action_time.isoformat(),
                    'running_time': (current_time - context.start_time).total_seconds(),
                    'is_alive': thread.is_alive()
                })
        
        return running