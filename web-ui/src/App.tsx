import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import Layout from './components/Layout';
import 'dayjs/locale/zh-cn';

function App() {
  return (
    <ConfigProvider 
      locale={zhCN}
      theme={{
        token: {
          colorPrimary: '#667eea',
        },
      }}
    >
      <Layout />
    </ConfigProvider>
  );
}

export default App;