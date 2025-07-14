import React, { useState, useEffect } from 'react';
import { Layout as AntLayout, Menu, theme } from 'antd';
import {
  DashboardOutlined,
  ApiOutlined,
  FileTextOutlined,
  ToolOutlined,
  SettingOutlined,
  RobotOutlined,
} from '@ant-design/icons';
import Dashboard from '../Dashboard';
import PluginManager from '../PluginManager';
import ScriptManager from '../ScriptManager';
import Toolbox from '../Toolbox';
import Settings from '../Settings';
import SystemStatus from '../SystemStatus';
import socketService from '@/services/socket';

const { Header, Content, Sider } = AntLayout;

type MenuItem = {
  key: string;
  icon: React.ReactNode;
  label: string;
  component: React.ReactNode;
};

const menuItems: MenuItem[] = [
  {
    key: 'dashboard',
    icon: <DashboardOutlined />,
    label: '仪表盘',
    component: <Dashboard />,
  },
  {
    key: 'plugins',
    icon: <ApiOutlined />,
    label: '插件管理',
    component: <PluginManager />,
  },
  {
    key: 'scripts',
    icon: <FileTextOutlined />,
    label: '脚本管理',
    component: <ScriptManager />,
  },
  {
    key: 'tools',
    icon: <ToolOutlined />,
    label: '工具箱',
    component: <Toolbox />,
  },
  {
    key: 'settings',
    icon: <SettingOutlined />,
    label: '设置',
    component: <Settings />,
  },
];

const Layout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [selectedKey, setSelectedKey] = useState('dashboard');
  const {
    token: { colorBgContainer },
  } = theme.useToken();

  useEffect(() => {
    // 连接Socket.IO
    socketService.connect();

    return () => {
      socketService.disconnect();
    };
  }, []);

  const currentComponent = menuItems.find(item => item.key === selectedKey)?.component;

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Header style={{ 
        display: 'flex', 
        alignItems: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '0 24px',
      }}>
        <div style={{ 
          color: 'white', 
          fontSize: '20px', 
          fontWeight: 'bold',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <RobotOutlined />
          AutoScript
        </div>
      </Header>
      <AntLayout>
        <Sider 
          collapsible 
          collapsed={collapsed} 
          onCollapse={setCollapsed}
          theme="light"
          style={{ background: colorBgContainer }}
        >
          <Menu
            mode="inline"
            selectedKeys={[selectedKey]}
            style={{ height: '100%', borderRight: 0 }}
            items={menuItems.map(item => ({
              key: item.key,
              icon: item.icon,
              label: item.label,
            }))}
            onClick={({ key }) => setSelectedKey(key)}
          />
        </Sider>
        <AntLayout style={{ padding: '0 24px 24px' }}>
          <div style={{ display: 'flex', gap: '24px', height: '100%' }}>
            <div style={{ flex: 1, minHeight: '280px' }}>
              <Content
                style={{
                  padding: 24,
                  margin: 0,
                  minHeight: 280,
                  background: colorBgContainer,
                  borderRadius: '8px',
                  marginTop: '24px',
                }}
              >
                {currentComponent}
              </Content>
            </div>
            <div style={{ width: '300px', marginTop: '24px' }}>
              <SystemStatus />
            </div>
          </div>
        </AntLayout>
      </AntLayout>
    </AntLayout>
  );
};

export default Layout;