# AutoScript Web UI

基于 React + Vite + Antd 构建的 AutoScript 游戏自动化脚本平台前端界面。

## 功能特性

- 🎯 **仪表盘** - 实时监控系统状态和运行中的任务
- 🔌 **插件管理** - 管理和配置各种自动化插件
- 📝 **脚本管理** - 创建、执行和监控自动化脚本
- 🛠️ **工具箱** - 模板匹配和OCR文字识别工具
- ⚙️ **系统设置** - 配置系统参数和选项
- 📊 **实时状态** - Socket.IO实时状态更新
- 🎨 **现代UI** - 基于Antd的美观界面设计

## 技术栈

- **React 18** - 前端框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **Antd 5** - UI组件库
- **Axios** - HTTP客户端
- **Socket.IO** - 实时通信
- **Day.js** - 日期处理

## 项目结构

```
web-ui/
├── src/
│   ├── components/          # 组件目录
│   │   ├── Layout/         # 布局组件
│   │   ├── Dashboard/      # 仪表盘
│   │   ├── PluginManager/  # 插件管理
│   │   ├── ScriptManager/  # 脚本管理
│   │   ├── Toolbox/        # 工具箱
│   │   ├── Settings/       # 设置
│   │   └── SystemStatus/   # 系统状态
│   ├── services/           # 服务层
│   │   ├── api.ts         # API接口
│   │   └── socket.ts      # Socket.IO服务
│   ├── types/             # 类型定义
│   │   └── index.ts       # 主要类型
│   ├── App.tsx            # 根组件
│   ├── main.tsx          # 入口文件
│   └── index.css         # 全局样式
├── package.json          # 项目配置
├── vite.config.ts       # Vite配置
├── tsconfig.json        # TypeScript配置
└── index.html           # HTML模板
```

## 快速开始

### 安装依赖

```bash
cd web-ui
npm install
```

### 开发模式

```bash
npm run dev
```

应用将在 http://localhost:3000 启动，并代理API请求到后端服务器 (http://localhost:5000)。

### 构建生产版本

```bash
npm run build
```

### 预览生产版本

```bash
npm run preview
```

## 开发说明

### API代理配置

开发模式下，Vite会将以下请求代理到后端服务器：
- `/api/*` -> `http://localhost:5000/api/*`
- `/socket.io/*` -> `http://localhost:5000/socket.io/*`

### 组件开发规范

1. 所有组件使用TypeScript编写
2. 使用函数组件和React Hooks
3. 遵循Antd设计规范
4. 使用统一的类型定义

### 状态管理

- 使用React内置的useState和useEffect
- Socket.IO实现实时数据同步
- API层统一管理后端接口调用

### 样式约定

- 使用Antd内置样式系统
- 自定义样式写在index.css中
- 支持CSS-in-JS内联样式

## API接口

应用与后端Flask服务器通过以下接口通信：

- **引擎控制**: `/api/engine/*`
- **插件管理**: `/api/plugins/*`
- **脚本管理**: `/api/scripts/*`
- **队列管理**: `/api/queue/*`
- **工具接口**: `/api/templates/*`, `/api/ocr/*`
- **配置管理**: `/api/config`
- **实时通信**: Socket.IO

## 部署说明

1. 构建生产版本
2. 将dist目录部署到静态文件服务器
3. 配置反向代理将API请求转发到后端服务器
4. 确保Socket.IO连接正常工作

## 浏览器支持

- Chrome/Edge 88+
- Firefox 85+
- Safari 14+

## 许可证

MIT License