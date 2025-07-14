import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Button, Switch, Typography, Tag, Space, message } from 'antd';
import { SettingOutlined } from '@ant-design/icons';
import { pluginApi } from '@/services/api';
import type { Plugin } from '@/types';

const { Title, Text, Paragraph } = Typography;

const PluginManager: React.FC = () => {
  const [plugins, setPlugins] = useState<Record<string, Plugin>>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadPlugins();
  }, []);

  const loadPlugins = async () => {
    setLoading(true);
    try {
      const response = await pluginApi.getAll();
      if (response.success && response.data) {
        setPlugins(response.data);
      }
    } catch (error) {
      message.error('加载插件列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleTogglePlugin = async (pluginName: string, enabled: boolean) => {
    try {
      const response = enabled 
        ? await pluginApi.disable(pluginName)
        : await pluginApi.enable(pluginName);
      
      if (response.success) {
        message.success(response.message);
        loadPlugins(); // 重新加载插件列表
      } else {
        message.error(response.message || '操作失败');
      }
    } catch (error) {
      message.error('操作失败');
    }
  };

  const handleShowActions = async (pluginName: string) => {
    try {
      const response = await pluginApi.getActions(pluginName);
      if (response.success && response.data) {
        // 这里可以显示一个模态框展示动作详情
        message.info(`插件 ${pluginName} 支持 ${response.data.length} 个动作`);
      }
    } catch (error) {
      message.error('获取动作列表失败');
    }
  };

  return (
    <div>
      <Title level={2}>插件管理</Title>
      <Row gutter={[16, 16]}>
        {Object.entries(plugins).map(([name, plugin]) => (
          <Col xs={24} lg={12} xl={8} key={name}>
            <Card
              loading={loading}
              className="hover-card"
              title={
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span>{plugin.name}</span>
                  <Switch
                    checked={plugin.enabled}
                    onChange={(checked) => handleTogglePlugin(name, !checked)}
                    checkedChildren="启用"
                    unCheckedChildren="禁用"
                  />
                </div>
              }
              extra={
                <Button
                  type="text"
                  icon={<SettingOutlined />}
                  onClick={() => handleShowActions(name)}
                />
              }
              style={{ height: '300px' }}
            >
              <Space direction="vertical" style={{ width: '100%' }}>
                <Paragraph
                  ellipsis={{ rows: 2, expandable: false }}
                  style={{ marginBottom: '8px' }}
                >
                  {plugin.description}
                </Paragraph>
                
                <div>
                  <Text type="secondary">版本: </Text>
                  <Text>{plugin.version}</Text>
                </div>
                
                <div>
                  <Text type="secondary">作者: </Text>
                  <Text>{plugin.author}</Text>
                </div>
                
                <div>
                  <Text type="secondary">支持的动作: </Text>
                  <div style={{ marginTop: '4px' }}>
                    {plugin.actions.slice(0, 3).map((action) => (
                      <Tag key={action} color="blue" style={{ marginBottom: '4px' }}>
                        {action}
                      </Tag>
                    ))}
                    {plugin.actions.length > 3 && (
                      <Tag color="default">+{plugin.actions.length - 3}</Tag>
                    )}
                  </div>
                </div>
              </Space>
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
};

export default PluginManager;