import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Table, 
  Button, 
  Modal, 
  Form, 
  Input, 
  Select, 
  message, 
  Tag, 
  Progress,
  Typography,
  Space
} from 'antd';
import { PlusOutlined, StopOutlined } from '@ant-design/icons';
import { scriptApi, pluginApi } from '@/services/api';
import type { Task, Plugin, CreateScriptRequest } from '@/types';
import dayjs from 'dayjs';

const { Title } = Typography;
const { TextArea } = Input;

const ScriptManager: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [plugins, setPlugins] = useState<Record<string, Plugin>>({});
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    loadTasks();
    loadPlugins();
  }, []);

  const loadTasks = async () => {
    setLoading(true);
    try {
      const response = await scriptApi.getAll();
      if (response.success && response.data) {
        setTasks(response.data);
      }
    } catch (error) {
      message.error('加载脚本列表失败');
    } finally {
      setLoading(false);
    }
  };

  const loadPlugins = async () => {
    try {
      const response = await pluginApi.getAll();
      if (response.success && response.data) {
        setPlugins(response.data);
      }
    } catch (error) {
      message.error('加载插件列表失败');
    }
  };

  const handleCreateScript = async (values: any) => {
    try {
      let actions;
      try {
        actions = JSON.parse(values.actions);
      } catch (error) {
        message.error('动作配置格式错误，请输入有效的JSON');
        return;
      }

      const scriptData: CreateScriptRequest = {
        name: values.name,
        plugin_name: values.plugin_name,
        actions: actions,
        priority: values.priority || 0,
      };

      const response = await scriptApi.create(scriptData);
      if (response.success) {
        message.success('脚本创建成功');
        setModalVisible(false);
        form.resetFields();
        loadTasks();
      } else {
        message.error(response.message || '脚本创建失败');
      }
    } catch (error) {
      message.error('脚本创建失败');
    }
  };

  const handleCancelTask = async (taskId: string) => {
    try {
      const response = await scriptApi.cancel(taskId);
      if (response.success) {
        message.success('任务已取消');
        loadTasks();
      } else {
        message.error(response.message || '取消失败');
      }
    } catch (error) {
      message.error('取消失败');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'gold';
      case 'running':
        return 'blue';
      case 'completed':
        return 'green';
      case 'failed':
        return 'red';
      case 'cancelled':
        return 'default';
      default:
        return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending':
        return '等待中';
      case 'running':
        return '运行中';
      case 'completed':
        return '已完成';
      case 'failed':
        return '失败';
      case 'cancelled':
        return '已取消';
      default:
        return status;
    }
  };

  const columns = [
    {
      title: '脚本名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>
          {getStatusText(status)}
        </Tag>
      ),
    },
    {
      title: '进度',
      dataIndex: 'progress',
      key: 'progress',
      render: (progress: number, record: Task) => (
        record.status === 'running' ? (
          <Progress percent={progress} size="small" />
        ) : (
          '-'
        )
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (time: string) => dayjs(time).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: '完成时间',
      dataIndex: 'completed_at',
      key: 'completed_at',
      render: (time: string) => time ? dayjs(time).format('YYYY-MM-DD HH:mm:ss') : '-',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Task) => (
        <Space>
          {record.status === 'running' && (
            <Button
              type="text"
              danger
              icon={<StopOutlined />}
              onClick={() => handleCancelTask(record.id)}
            >
              取消
            </Button>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <Title level={2}>脚本管理</Title>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setModalVisible(true)}
        >
          新建脚本
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          dataSource={tasks}
          rowKey="id"
          loading={loading}
          expandable={{
            expandedRowRender: (record) => (
              <div>
                {record.error_message && (
                  <div style={{ color: '#ff4d4f', marginBottom: '8px' }}>
                    <strong>错误信息：</strong> {record.error_message}
                  </div>
                )}
                {record.result && (
                  <div>
                    <strong>执行结果：</strong>
                    <pre style={{ 
                      background: '#f5f5f5', 
                      padding: '8px', 
                      borderRadius: '4px',
                      marginTop: '4px'
                    }}>
                      {JSON.stringify(record.result, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            ),
          }}
        />
      </Card>

      <Modal
        title="新建脚本"
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
        }}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateScript}
        >
          <Form.Item
            name="name"
            label="脚本名称"
            rules={[{ required: true, message: '请输入脚本名称' }]}
          >
            <Input placeholder="请输入脚本名称" />
          </Form.Item>

          <Form.Item
            name="plugin_name"
            label="选择插件"
            rules={[{ required: true, message: '请选择插件' }]}
          >
            <Select placeholder="请选择插件">
              {Object.entries(plugins)
                .filter(([, plugin]) => plugin.enabled)
                .map(([name, plugin]) => (
                  <Select.Option key={name} value={name}>
                    {plugin.name}
                  </Select.Option>
                ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="actions"
            label="动作配置"
            rules={[{ required: true, message: '请输入动作配置' }]}
          >
            <TextArea
              rows={10}
              placeholder='请输入JSON格式的动作配置，例如：
[
  {
    "type": "click",
    "position": [100, 200]
  },
  {
    "type": "wait",
    "duration": 1000
  }
]'
            />
          </Form.Item>

          <Form.Item
            name="priority"
            label="优先级"
            initialValue={0}
          >
            <Select>
              <Select.Option value={0}>普通</Select.Option>
              <Select.Option value={1}>高</Select.Option>
              <Select.Option value={2}>最高</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item style={{ marginBottom: 0 }}>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
              >
                创建
              </Button>
              <Button
                onClick={() => {
                  setModalVisible(false);
                  form.resetFields();
                }}
              >
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ScriptManager;