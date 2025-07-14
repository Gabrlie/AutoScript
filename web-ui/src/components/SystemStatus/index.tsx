import React, { useState, useEffect } from 'react';
import { Card, Button, Space, Statistic, Divider, message } from 'antd';
import {
  PlayCircleOutlined,
  StopOutlined,
  PauseOutlined,
  DeleteOutlined,
  CameraOutlined,
} from '@ant-design/icons';
import { engineApi, queueApi, screenshotApi } from '@/services/api';
import socketService from '@/services/socket';
import type { SystemStatus as SystemStatusType } from '@/types';

const SystemStatus: React.FC = () => {
  const [systemStatus, setSystemStatus] = useState<SystemStatusType>({
    engine_running: false,
    queue_status: {
      paused: false,
      running_tasks: 0,
      completed_tasks: 0,
      pending_tasks: 0,
    },
    running_tasks: [],
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // 监听状态更新
    const handleStatusUpdate = (status: SystemStatusType) => {
      setSystemStatus(status);
    };

    socketService.on('status_update', handleStatusUpdate);
    socketService.on('real_time_status', handleStatusUpdate);

    // 初始加载状态
    loadStatus();

    // 定期获取状态
    const interval = setInterval(() => {
      if (socketService.connected) {
        socketService.getRealTimeStatus();
      }
    }, 5000);

    return () => {
      socketService.off('status_update', handleStatusUpdate);
      socketService.off('real_time_status', handleStatusUpdate);
      clearInterval(interval);
    };
  }, []);

  const loadStatus = async () => {
    try {
      const response = await engineApi.getStatus();
      if (response.success && response.data) {
        setSystemStatus({
          engine_running: response.data.running,
          queue_status: response.data.queue_status,
          running_tasks: [],
        });
      }
    } catch (error) {
      console.error('加载状态失败:', error);
    }
  };

  const handleStartEngine = async () => {
    setLoading(true);
    try {
      const response = await engineApi.start();
      if (response.success) {
        message.success('引擎启动成功');
      } else {
        message.error(response.message || '引擎启动失败');
      }
    } catch (error) {
      message.error('引擎启动失败');
    } finally {
      setLoading(false);
    }
  };

  const handleStopEngine = async () => {
    setLoading(true);
    try {
      const response = await engineApi.stop();
      if (response.success) {
        message.success('引擎停止成功');
      } else {
        message.error(response.message || '引擎停止失败');
      }
    } catch (error) {
      message.error('引擎停止失败');
    } finally {
      setLoading(false);
    }
  };

  const handlePauseQueue = async () => {
    try {
      const response = await queueApi.pause();
      if (response.success) {
        message.success('队列已暂停');
      } else {
        message.error(response.message || '暂停失败');
      }
    } catch (error) {
      message.error('暂停失败');
    }
  };

  const handleResumeQueue = async () => {
    try {
      const response = await queueApi.resume();
      if (response.success) {
        message.success('队列已恢复');
      } else {
        message.error(response.message || '恢复失败');
      }
    } catch (error) {
      message.error('恢复失败');
    }
  };

  const handleClearQueue = async () => {
    try {
      const response = await queueApi.clear();
      if (response.success) {
        message.success('队列已清理');
      } else {
        message.error(response.message || '清理失败');
      }
    } catch (error) {
      message.error('清理失败');
    }
  };

  const handleTakeScreenshot = async () => {
    try {
      const blob = await screenshotApi.take();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `screenshot_${Date.now()}.png`;
      a.click();
      URL.revokeObjectURL(url);
      message.success('截图成功');
    } catch (error) {
      message.error('截图失败');
    }
  };

  return (
    <Space direction="vertical" size="middle" style={{ width: '100%' }}>
      {/* 系统状态 */}
      <Card title="系统状态" size="small">
        <Space direction="vertical" style={{ width: '100%' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>引擎状态:</span>
            <span>
              <span className={`status-indicator ${systemStatus.engine_running ? 'status-running' : 'status-stopped'}`} />
              {systemStatus.engine_running ? '运行中' : '已停止'}
            </span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>队列状态:</span>
            <span>{systemStatus.queue_status.paused ? '已暂停' : '运行中'}</span>
          </div>
          <Divider style={{ margin: '8px 0' }} />
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <Statistic title="运行任务" value={systemStatus.queue_status.running_tasks} />
            <Statistic title="已完成" value={systemStatus.queue_status.completed_tasks} />
          </div>
        </Space>
      </Card>

      {/* 引擎控制 */}
      <Card title="引擎控制" size="small">
        <Space direction="vertical" style={{ width: '100%' }}>
          <Button
            type="primary"
            icon={<PlayCircleOutlined />}
            onClick={handleStartEngine}
            loading={loading}
            disabled={systemStatus.engine_running}
            block
          >
            启动引擎
          </Button>
          <Button
            danger
            icon={<StopOutlined />}
            onClick={handleStopEngine}
            loading={loading}
            disabled={!systemStatus.engine_running}
            block
          >
            停止引擎
          </Button>
        </Space>
      </Card>

      {/* 快速操作 */}
      <Card title="快速操作" size="small">
        <Space direction="vertical" style={{ width: '100%' }}>
          <Button
            icon={<PauseOutlined />}
            onClick={systemStatus.queue_status.paused ? handleResumeQueue : handlePauseQueue}
            block
          >
            {systemStatus.queue_status.paused ? '恢复队列' : '暂停队列'}
          </Button>
          <Button
            icon={<DeleteOutlined />}
            onClick={handleClearQueue}
            block
          >
            清理队列
          </Button>
          <Button
            icon={<CameraOutlined />}
            onClick={handleTakeScreenshot}
            block
          >
            截图
          </Button>
        </Space>
      </Card>
    </Space>
  );
};

export default SystemStatus;