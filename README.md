# AutoScript - 万能游戏自动化脚本平台

> 一个功能强大、可扩展的游戏自动化脚本平台，支持多种平台和设备的自动化操作。

## 🚀 特性

### 核心功能
- **模板匹配** - 基于OpenCV的高精度图像模板匹配
- **OCR识别** - 支持中英文的光学字符识别
- **脚本队列** - 多任务并发执行和智能调度
- **网页可视化** - 现代化的Web界面，实时监控和控制
- **统一设置管理** - 集中式配置管理系统

### 默认插件
- **Playwright插件** - 网页自动化操作，支持多浏览器
- **Windows插件** - Windows桌面应用程序自动化
- **Scrcpy插件** - Android设备远程控制

### 插件系统
- **插件管理器** - 动态加载和管理插件
- **插件工具箱** - 完整的插件开发工具集
- **模板管理** - 插件专用模板和资源管理
- **流程管理** - 自动化流程设计和执行

## 📦 安装

### 环境要求
- Python 3.8+
- Windows/Linux/macOS

### 安装依赖
```bash
pip install -r requirements.txt
```

### 安装Playwright浏览器
```bash
playwright install
```

### 安装Tesseract OCR
- **Windows**: 下载安装包：https://github.com/UB-Mannheim/tesseract/wiki
- **macOS**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

### 安装中文语言包
```bash
# 下载中文语言包
sudo apt-get install tesseract-ocr-chi-sim tesseract-ocr-chi-tra
```

## 🎯 快速开始

### 1. 启动Web界面
```bash
python main.py
```
访问 http://localhost:5000

### 2. 命令行模式
```bash
python main.py --mode cli
```

### 3. 指定配置参数
```bash
python main.py --host 0.0.0.0 --port 8080 --debug
```

## 📖 使用说明

### 项目结构
```
AutoScript/
├── core/                   # 核心模块
│   ├── engine.py          # 主引擎
│   ├── plugin_manager.py  # 插件管理器
│   ├── script_queue.py    # 脚本队列
│   ├── config_manager.py  # 配置管理
│   ├── template_matcher.py # 模板匹配
│   └── ocr_engine.py      # OCR引擎
├── plugins/               # 插件目录
│   ├── playwright_plugin.py # Playwright插件
│   ├── windows_plugin.py    # Windows插件
│   └── scrcpy_plugin.py     # Scrcpy插件
├── web/                   # Web界面
│   ├── app.py            # Flask应用
│   └── templates/        # HTML模板
├── configs/              # 配置文件
├── templates/            # 模板图片
├── scripts/              # 脚本文件
└── main.py               # 主程序入口
```

### 配置文件
系统会自动创建 `configs/config.yaml` 配置文件，包含：
- 引擎配置
- 插件配置
- 模板匹配参数
- OCR设置
- Web服务配置

### 创建脚本
脚本采用JSON格式定义，示例：
```json
{
  "name": "示例脚本",
  "plugin_name": "windows",
  "actions": [
    {"type": "screenshot", "path": "screen.png"},
    {"type": "click", "x": 100, "y": 200},
    {"type": "wait", "duration": 2}
  ],
  "priority": 0
}
```

### 插件开发
1. 继承 `BasePlugin` 类
2. 实现必要的方法
3. 定义支持的动作
4. 放置到 `plugins/` 目录

```python
from core.plugin_manager import BasePlugin

class MyPlugin(BasePlugin):
    def __init__(self, engine):
        super().__init__(engine)
        self.name = "my_plugin"
        self.description = "我的插件"
    
    def initialize(self) -> bool:
        return True
    
    def get_actions(self) -> List[str]:
        return ["my_action"]
    
    def execute_action(self, action: Dict[str, Any]) -> Any:
        # 执行动作逻辑
        pass
```

## 🛠️ 插件详情

### Playwright插件
支持网页自动化操作：
- 打开/关闭浏览器
- 页面导航
- 元素点击、输入
- 等待元素/文本
- 截图、获取文本
- JavaScript执行

### Windows插件
支持桌面应用自动化：
- 启动/终止应用程序
- 窗口管理
- 鼠标键盘操作
- 截图
- 剪贴板操作

### Scrcpy插件
支持Android设备控制：
- 设备连接管理
- 触摸、滑动操作
- 文本输入
- 按键操作
- 应用安装/卸载
- 文件传输

## 🎨 Web界面

### 主要功能
- **仪表盘** - 实时系统状态监控
- **插件管理** - 插件启用/禁用、状态查看
- **脚本管理** - 脚本创建、执行、监控
- **工具箱** - 模板匹配、OCR识别工具
- **系统设置** - 配置管理

### 实时更新
- WebSocket连接实时推送状态
- 任务进度实时显示
- 系统日志实时输出

## 🔧 高级功能

### 模板匹配
- 支持多种匹配算法
- 非极大值抑制
- 自定义匹配阈值
- 区域限制匹配

### OCR识别
- 支持中英文识别
- 图像预处理优化
- 文本相似度匹配
- 批量识别

### 脚本队列
- 多任务并发执行
- 优先级调度
- 任务状态管理
- 错误处理

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🆘 支持

如果你遇到问题或有建议，请：
1. 查看 [FAQ](docs/FAQ.md)
2. 创建 [Issue](https://github.com/your-username/AutoScript/issues)
3. 加入我们的讨论群

## 🎯 路线图

- [ ] 更多平台支持 (macOS, iOS)
- [ ] 机器学习模板匹配
- [ ] 分布式执行
- [ ] 云端部署支持
- [ ] 插件市场

## 📊 统计

![GitHub stars](https://img.shields.io/github/stars/your-username/AutoScript?style=social)
![GitHub forks](https://img.shields.io/github/forks/your-username/AutoScript?style=social)
![GitHub issues](https://img.shields.io/github/issues/your-username/AutoScript)
![GitHub license](https://img.shields.io/github/license/your-username/AutoScript)

---

**AutoScript** - 让游戏自动化变得简单 🎮
