import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Progress, Empty, Typography } from 'antd';
import { engineApi } from '@/services/api';
import socketService from '@/services/socket';
import type { RunningTask, SystemStatus } from '@/types';

const { Title, Text } = Typography;

const Dashboard: React.FC = () => {
  const [runningTasks, setRunningTasks] = useState<RunningTask[]>([]);
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    const handleStatusUpdate = (status: SystemStatus) => {
      setRunningTasks(status.running_tasks || []);
    };

    const handleConnect = () => {
      addLog('已连接到服务器');
    };

    const handleDisconnect = () => {
      addLog('与服务器断开连接');
    };

    const handleActionResult = (data: any) => {
      addLog(`动作执行结果: ${JSON.stringify(data)}`);
    };

    const handleError = (data: { message: string }) => {
      addLog(`错误: ${data.message}`);
    };

    socketService.on('status_update', handleStatusUpdate);
    socketService.on('real_time_status', handleStatusUpdate);
    socketService.on('connect', handleConnect);
    socketService.on('disconnect', handleDisconnect);
    socketService.on('action_result', handleActionResult);
    socketService.on('error', handleError);

    // 初始加载数据
    loadInitialData();

    return () => {
      socketService.off('status_update', handleStatusUpdate);
      socketService.off('real_time_status', handleStatusUpdate);
      socketService.off('connect', handleConnect);
      socketService.off('disconnect', handleDisconnect);
      socketService.off('action_result', handleActionResult);
      socketService.off('error', handleError);
    };
  }, []);

  const loadInitialData = async () => {
    try {
      const response = await engineApi.getStatus();
      if (response.success && response.data) {
        // 初始状态加载
        addLog('系统初始化完成');
      }
    } catch (error) {
      addLog('系统初始化失败');
    }
  };

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    const logMessage = `[${timestamp}] ${message}`;
    setLogs(prev => [...prev.slice(-99), logMessage]); // 保留最近100条日志
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return '#52c41a';
      case 'pending':
        return '#faad14';
      case 'completed':
        return '#1890ff';
      case 'failed':
        return '#ff4d4f';
      default:
        return '#d9d9d9';
    }
  };

  return (
    <div>
      <Title level={2}>仪表盘</Title>
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="运行中的任务" style={{ height: '400px' }}>
            {runningTasks.length === 0 ? (
              <Empty description="暂无运行中的任务" />
            ) : (
              <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                {runningTasks.map((task) => (
                  <Card
                    key={task.id}
                    size="small"
                    style={{ marginBottom: '8px' }}
                    bodyStyle={{ padding: '12px' }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <Text strong>{task.name}</Text>
                      <Text style={{ color: getStatusColor(task.status) }}>
                        {task.status}
                      </Text>
                    </div>
                    <Progress
                      percent={task.progress}
                      size="small"
                      strokeColor={getStatusColor(task.status)}
                    />
                  </Card>
                ))}
              </div>
            )}
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="系统日志" style={{ height: '400px' }}>
            <div className="log-container" style={{ height: '300px' }}>
              {logs.length === 0 ? (
                <Text type="secondary">等待日志...</Text>
              ) : (
                logs.map((log, index) => (
                  <div key={index}>{log}</div>
                ))
              )}
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;