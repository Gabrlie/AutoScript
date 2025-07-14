"""
脚本队列管理器
负责管理脚本的执行队列和调度
"""
import time
import threading
from typing import Dict, Any, List, Optional
from enum import Enum
from queue import Queue, Empty
from loguru import logger
from dataclasses import dataclass
from datetime import datetime


class ScriptStatus(Enum):
    """脚本状态枚举"""
    PENDING = "pending"      # 待执行
    RUNNING = "running"      # 执行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败
    CANCELLED = "cancelled"  # 已取消
    PAUSED = "paused"       # 已暂停


@dataclass
class ScriptTask:
    """脚本任务"""
    id: str
    name: str
    plugin_name: str
    actions: List[Dict[str, Any]]
    priority: int = 0
    status: ScriptStatus = ScriptStatus.PENDING
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    progress: float = 0.0
    result: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class ScriptQueue:
    """脚本队列管理器"""
    
    def __init__(self, engine):
        """
        初始化脚本队列
        
        Args:
            engine: AutoScript引擎实例
        """
        self.engine = engine
        self.queue = Queue()
        self.tasks: Dict[str, ScriptTask] = {}
        self.running_tasks: Dict[str, ScriptTask] = {}
        self.completed_tasks: Dict[str, ScriptTask] = {}
        
        self._paused = False
        self._max_concurrent = self.engine.get_config('engine.max_workers', 4)
        self._lock = threading.Lock()
        
        logger.info("脚本队列初始化完成")
    
    def add_script(self, script_data: Dict[str, Any]) -> str:
        """
        添加脚本到队列
        
        Args:
            script_data: 脚本数据
            
        Returns:
            任务ID
        """
        try:
            task = ScriptTask(
                id=self._generate_task_id(),
                name=script_data.get('name', 'Untitled Script'),
                plugin_name=script_data.get('plugin_name', ''),
                actions=script_data.get('actions', []),
                priority=script_data.get('priority', 0)
            )
            
            with self._lock:
                self.tasks[task.id] = task
                self.queue.put(task)
            
            logger.info(f"脚本已添加到队列: {task.name} ({task.id})")
            return task.id
            
        except Exception as e:
            logger.error(f"添加脚本到队列失败: {e}")
            return ""
    
    def process_queue(self):
        """处理队列中的脚本"""
        if self._paused:
            return
            
        # 检查是否有空闲工作线程
        if len(self.running_tasks) >= self._max_concurrent:
            return
            
        try:
            # 获取下一个任务
            task = self.queue.get_nowait()
            
            with self._lock:
                if task.id in self.tasks and task.status == ScriptStatus.PENDING:
                    # 更新任务状态
                    task.status = ScriptStatus.RUNNING
                    task.started_at = datetime.now()
                    self.running_tasks[task.id] = task
                    
                    # 启动执行线程
                    thread = threading.Thread(
                        target=self._execute_script,
                        args=(task,),
                        daemon=True
                    )
                    thread.start()
                    
                    logger.info(f"开始执行脚本: {task.name} ({task.id})")
                    
        except Empty:
            # 队列为空，继续等待
            pass
        except Exception as e:
            logger.error(f"处理脚本队列时出错: {e}")
    
    def _execute_script(self, task: ScriptTask):
        """
        执行脚本任务
        
        Args:
            task: 脚本任务
        """
        try:
            # 获取插件
            plugin = self.engine.get_plugin(task.plugin_name)
            if not plugin:
                raise Exception(f"插件 {task.plugin_name} 不存在")
            
            # 执行动作序列
            result = {}
            total_actions = len(task.actions)
            
            for i, action in enumerate(task.actions):
                # 检查是否需要暂停或取消
                if task.status == ScriptStatus.CANCELLED:
                    logger.info(f"脚本任务已取消: {task.name}")
                    return
                    
                if self._paused:
                    task.status = ScriptStatus.PAUSED
                    logger.info(f"脚本任务已暂停: {task.name}")
                    return
                
                # 执行动作
                action_result = plugin.execute_action(action)
                result[f"action_{i}"] = action_result
                
                # 更新进度
                task.progress = (i + 1) / total_actions * 100
                
                logger.debug(f"动作执行完成: {action.get('type', 'unknown')}")
            
            # 任务完成
            task.status = ScriptStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result
            task.progress = 100.0
            
            logger.info(f"脚本执行完成: {task.name} ({task.id})")
            
        except Exception as e:
            # 任务失败
            task.status = ScriptStatus.FAILED
            task.completed_at = datetime.now()
            task.error_message = str(e)
            task.progress = 0.0
            
            logger.error(f"脚本执行失败: {task.name} ({task.id}) - {e}")
            
        finally:
            # 清理运行中的任务
            with self._lock:
                if task.id in self.running_tasks:
                    del self.running_tasks[task.id]
                self.completed_tasks[task.id] = task
    
    def get_task(self, task_id: str) -> Optional[ScriptTask]:
        """
        获取任务信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务信息
        """
        with self._lock:
            if task_id in self.tasks:
                return self.tasks[task_id]
            return None
    
    def get_all_tasks(self) -> List[ScriptTask]:
        """获取所有任务"""
        with self._lock:
            return list(self.tasks.values())
    
    def get_running_tasks(self) -> List[ScriptTask]:
        """获取正在运行的任务"""
        with self._lock:
            return list(self.running_tasks.values())
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功取消
        """
        with self._lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                if task.status in [ScriptStatus.PENDING, ScriptStatus.RUNNING, ScriptStatus.PAUSED]:
                    task.status = ScriptStatus.CANCELLED
                    task.completed_at = datetime.now()
                    logger.info(f"任务已取消: {task.name} ({task_id})")
                    return True
        return False
    
    def pause_queue(self):
        """暂停队列"""
        self._paused = True
        logger.info("脚本队列已暂停")
    
    def resume_queue(self):
        """恢复队列"""
        self._paused = False
        logger.info("脚本队列已恢复")
    
    def clear_completed(self):
        """清理已完成的任务"""
        with self._lock:
            to_remove = []
            for task_id, task in self.tasks.items():
                if task.status in [ScriptStatus.COMPLETED, ScriptStatus.FAILED, ScriptStatus.CANCELLED]:
                    to_remove.append(task_id)
            
            for task_id in to_remove:
                del self.tasks[task_id]
                if task_id in self.completed_tasks:
                    del self.completed_tasks[task_id]
            
            logger.info(f"已清理 {len(to_remove)} 个已完成的任务")
    
    def get_queue_status(self) -> Dict[str, Any]:
        """获取队列状态"""
        with self._lock:
            return {
                'paused': self._paused,
                'total_tasks': len(self.tasks),
                'pending_tasks': len([t for t in self.tasks.values() if t.status == ScriptStatus.PENDING]),
                'running_tasks': len(self.running_tasks),
                'completed_tasks': len([t for t in self.tasks.values() if t.status == ScriptStatus.COMPLETED]),
                'failed_tasks': len([t for t in self.tasks.values() if t.status == ScriptStatus.FAILED]),
                'max_concurrent': self._max_concurrent
            }
    
    def _generate_task_id(self) -> str:
        """生成任务ID"""
        import uuid
        return str(uuid.uuid4())[:8]