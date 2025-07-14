"""
脚本队列管理器 - 负责脚本执行队列和调度
"""
import time
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ScriptStatus(Enum):
    """脚本状态"""
    PENDING = "pending"      # 等待执行
    RUNNING = "running"      # 正在执行
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 执行失败
    CANCELLED = "cancelled"  # 已取消

@dataclass
class QueuedScript:
    """队列中的脚本"""
    id: str
    game_id: str
    script_id: str
    script_name: str
    script_content: Dict[str, Any]
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: ScriptStatus = ScriptStatus.PENDING
    execution_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

class GameQueue:
    """游戏内脚本队列"""
    
    def __init__(self, game_id: str, game_name: str):
        self.game_id = game_id
        self.game_name = game_name
        self.scripts: List[QueuedScript] = []
        self.running_script: Optional[QueuedScript] = None
        self.enabled = True
        self.lock = threading.Lock()
    
    def add_script(self, script: QueuedScript):
        """添加脚本到队列"""
        with self.lock:
            # 按优先级插入（高优先级在前）
            inserted = False
            for i, existing_script in enumerate(self.scripts):
                if script.priority > existing_script.priority:
                    self.scripts.insert(i, script)
                    inserted = True
                    break
            
            if not inserted:
                self.scripts.append(script)
            
            logger.info(f"脚本添加到游戏队列 {self.game_name}: {script.script_name}")
    
    def get_next_script(self) -> Optional[QueuedScript]:
        """获取下一个要执行的脚本"""
        with self.lock:
            if not self.enabled or self.running_script:
                return None
            
            current_time = datetime.now()
            
            for i, script in enumerate(self.scripts):
                if (script.status == ScriptStatus.PENDING and 
                    (script.scheduled_at is None or script.scheduled_at <= current_time)):
                    
                    # 移出队列并标记为运行中
                    script = self.scripts.pop(i)
                    script.status = ScriptStatus.RUNNING
                    script.started_at = current_time
                    self.running_script = script
                    
                    return script
            
            return None
    
    def complete_script(self, script_id: str, success: bool, result: Any = None, error: str = None):
        """完成脚本执行"""
        with self.lock:
            if (self.running_script and 
                self.running_script.id == script_id):
                
                script = self.running_script
                script.completed_at = datetime.now()
                script.status = ScriptStatus.COMPLETED if success else ScriptStatus.FAILED
                script.result = result
                script.error = error
                
                # 如果失败且还有重试次数，重新加入队列
                if not success and script.retry_count < script.max_retries:
                    script.retry_count += 1
                    script.status = ScriptStatus.PENDING
                    script.started_at = None
                    script.scheduled_at = datetime.now()  # 立即重试，或者可以设置延迟
                    self.add_script(script)
                    logger.info(f"脚本重试 ({script.retry_count}/{script.max_retries}): {script.script_name}")
                
                self.running_script = None
                logger.info(f"脚本完成: {script.script_name}, 成功: {success}")
    
    def cancel_script(self, script_id: str) -> bool:
        """取消脚本"""
        with self.lock:
            # 取消队列中的脚本
            for script in self.scripts:
                if script.id == script_id:
                    script.status = ScriptStatus.CANCELLED
                    self.scripts.remove(script)
                    logger.info(f"取消队列脚本: {script.script_name}")
                    return True
            
            # 取消正在运行的脚本
            if (self.running_script and 
                self.running_script.id == script_id):
                self.running_script.status = ScriptStatus.CANCELLED
                # 这里需要通知脚本执行器停止执行
                logger.info(f"取消运行脚本: {self.running_script.script_name}")
                return True
            
            return False
    
    def get_queue_status(self) -> Dict[str, Any]:
        """获取队列状态"""
        with self.lock:
            return {
                'game_id': self.game_id,
                'game_name': self.game_name,
                'enabled': self.enabled,
                'queue_length': len(self.scripts),
                'running_script': {
                    'id': self.running_script.id,
                    'name': self.running_script.script_name,
                    'started_at': self.running_script.started_at.isoformat()
                } if self.running_script else None,
                'pending_scripts': [
                    {
                        'id': script.id,
                        'name': script.script_name,
                        'priority': script.priority,
                        'scheduled_at': script.scheduled_at.isoformat() if script.scheduled_at else None
                    }
                    for script in self.scripts if script.status == ScriptStatus.PENDING
                ]
            }

class ScriptQueueManager:
    """脚本队列管理器"""
    
    def __init__(self, script_executor):
        self.script_executor = script_executor
        self.game_queues: Dict[str, GameQueue] = {}
        self.global_enabled = True
        self.scheduler_thread = None
        self.running = False
        self.lock = threading.Lock()
        
        self.start_scheduler()
    
    def create_game_queue(self, game_id: str, game_name: str):
        """创建游戏队列"""
        with self.lock:
            if game_id not in self.game_queues:
                self.game_queues[game_id] = GameQueue(game_id, game_name)
                logger.info(f"创建游戏队列: {game_name}")
    
    def add_script_to_queue(self, queued_script: QueuedScript):
        """添加脚本到队列"""
        game_id = queued_script.game_id
        
        with self.lock:
            if game_id not in self.game_queues:
                logger.warning(f"游戏队列不存在: {game_id}")
                return False
            
            self.game_queues[game_id].add_script(queued_script)
            return True
    
    def start_scheduler(self):
        """启动调度器"""
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        logger.info("脚本队列调度器已启动")
    
    def stop_scheduler(self):
        """停止调度器"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("脚本队列调度器已停止")
    
    def _scheduler_loop(self):
        """调度器主循环"""
        while self.running:
            try:
                if self.global_enabled:
                    self._process_queues()
                time.sleep(1)  # 每秒检查一次
            except Exception as e:
                logger.error(f"调度器错误: {str(e)}", exc_info=True)
    
    def _process_queues(self):
        """处理所有游戏队列"""
        with self.lock:
            for game_queue in self.game_queues.values():
                if not game_queue.enabled:
                    continue
                
                # 获取下一个要执行的脚本
                script = game_queue.get_next_script()
                if script:
                    self._execute_script(script)
    
    def _execute_script(self, script: QueuedScript):
        """执行脚本"""
        try:
            # 启动脚本执行
            execution_id = self.script_executor.execute_script(
                script.game_id,
                script.script_id,
                script.script_content
            )
            
            script.execution_id = execution_id
            logger.info(f"开始执行脚本: {script.script_name} (execution_id: {execution_id})")
            
            # 这里需要异步监控脚本执行完成
            # 可以通过回调或者定期检查的方式
            
        except Exception as e:
            logger.error(f"执行脚本失败: {script.script_name}, {str(e)}")
            game_queue = self.game_queues[script.game_id]
            game_queue.complete_script(script.id, False, error=str(e))
    
    def complete_script(self, game_id: str, script_id: str, success: bool, 
                       result: Any = None, error: str = None):
        """标记脚本完成"""
        with self.lock:
            if game_id in self.game_queues:
                self.game_queues[game_id].complete_script(script_id, success, result, error)
    
    def cancel_script(self, game_id: str, script_id: str) -> bool:
        """取消脚本"""
        with self.lock:
            if game_id in self.game_queues:
                return self.game_queues[game_id].cancel_script(script_id)
            return False
    
    def pause_game_queue(self, game_id: str):
        """暂停游戏队列"""
        with self.lock:
            if game_id in self.game_queues:
                self.game_queues[game_id].enabled = False
                logger.info(f"暂停游戏队列: {game_id}")
    
    def resume_game_queue(self, game_id: str):
        """恢复游戏队列"""
        with self.lock:
            if game_id in self.game_queues:
                self.game_queues[game_id].enabled = True
                logger.info(f"恢复游戏队列: {game_id}")
    
    def pause_all_queues(self):
        """暂停所有队列"""
        self.global_enabled = False
        logger.info("暂停所有脚本队列")
    
    def resume_all_queues(self):
        """恢复所有队列"""
        self.global_enabled = True
        logger.info("恢复所有脚本队列")
    
    def get_all_queue_status(self) -> List[Dict[str, Any]]:
        """获取所有队列状态"""
        with self.lock:
            return [queue.get_queue_status() for queue in self.game_queues.values()]
    
    def get_game_queue_status(self, game_id: str) -> Optional[Dict[str, Any]]:
        """获取指定游戏队列状态"""
        with self.lock:
            if game_id in self.game_queues:
                return self.game_queues[game_id].get_queue_status()
            return None
    
    def cleanup(self):
        """清理资源"""
        self.stop_scheduler()
        with self.lock:
            self.game_queues.clear()