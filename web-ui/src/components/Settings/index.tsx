import React, { useState, useEffect } from 'react';
import { Card, Form, Input, Button, message, Typography, Space, Divider } from 'antd';
import { SaveOutlined, ReloadOutlined } from '@ant-design/icons';
import { configApi } from '@/services/api';
import type { Config } from '@/types';

const { Title } = Typography;
const { TextArea } = Input;

const Settings: React.FC = () => {
  const [form] = Form.useForm();
  const [config, setConfig] = useState<Config>({});
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    setLoading(true);
    try {
      const response = await configApi.get();
      if (response.success && response.data) {
        setConfig(response.data);
        form.setFieldsValue(response.data);
      }
    } catch (error) {
      message.error('加载配置失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (values: any) => {
    setSaving(true);
    try {
      const response = await configApi.update(values);
      if (response.success) {
        message.success('配置保存成功');
        setConfig(values);
      } else {
        message.error(response.message || '配置保存失败');
      }
    } catch (error) {
      message.error('配置保存失败');
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    form.setFieldsValue(config);
    message.info('已重置为当前配置');
  };

  return (
    <div>
      <Title level={2}>系统设置</Title>
      <Card loading={loading}>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSave}
          initialValues={config}
        >
          <Title level={4}>基础配置</Title>
          
          <Form.Item
            name="log_level"
            label="日志级别"
            tooltip="控制系统日志的详细程度"
          >
            <Input placeholder="INFO" />
          </Form.Item>

          <Form.Item
            name="max_concurrent_tasks"
            label="最大并发任务数"
            tooltip="同时运行的最大任务数量"
          >
            <Input placeholder="5" type="number" />
          </Form.Item>

          <Form.Item
            name="task_timeout"
            label="任务超时时间(秒)"
            tooltip="单个任务的最大执行时间"
          >
            <Input placeholder="300" type="number" />
          </Form.Item>

          <Divider />

          <Title level={4}>插件配置</Title>

          <Form.Item
            name="plugin_directory"
            label="插件目录"
            tooltip="插件文件的存储目录"
          >
            <Input placeholder="plugins/" />
          </Form.Item>

          <Form.Item
            name="auto_load_plugins"
            label="自动加载插件"
            tooltip="启动时是否自动加载所有插件"
          >
            <Input placeholder="true" />
          </Form.Item>

          <Divider />

          <Title level={4}>模板配置</Title>

          <Form.Item
            name="template_directory"
            label="模板目录"
            tooltip="模板文件的存储目录"
          >
            <Input placeholder="templates/" />
          </Form.Item>

          <Form.Item
            name="template_match_threshold"
            label="模板匹配阈值"
            tooltip="模板匹配的最小置信度"
          >
            <Input placeholder="0.8" type="number" step="0.1" />
          </Form.Item>

          <Divider />

          <Title level={4}>高级配置</Title>

          <Form.Item
            name="custom_config"
            label="自定义配置"
            tooltip="JSON格式的自定义配置项"
          >
            <TextArea
              rows={6}
              placeholder='输入JSON格式的配置，例如：
{
  "ocr_engine": "tesseract",
  "screenshot_format": "png",
  "retry_count": 3
}'
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0 }}>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                icon={<SaveOutlined />}
                loading={saving}
              >
                保存配置
              </Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={handleReset}
                disabled={saving}
              >
                重置
              </Button>
            </Space>
          </Form.Item>
        </Form>

        {Object.keys(config).length > 0 && (
          <div style={{ marginTop: '24px' }}>
            <Title level={4}>当前配置预览</Title>
            <div
              style={{
                background: '#f5f5f5',
                padding: '12px',
                borderRadius: '6px',
                fontFamily: 'monospace',
                fontSize: '12px',
                maxHeight: '200px',
                overflowY: 'auto'
              }}
            >
              <pre>{JSON.stringify(config, null, 2)}</pre>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
};

export default Settings;