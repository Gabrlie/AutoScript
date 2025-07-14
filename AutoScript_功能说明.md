# AutoScript 2.0 - 游戏自动化脚本管理系统

## 🎯 项目简介

AutoScript 2.0 是一个全新设计的游戏自动化脚本管理系统，专门用于解决游戏脚本的管理、执行和调度问题。系统采用现代化的架构设计，支持多平台、多插件、多游戏的统一管理。

## ✨ 主要功能

### 🔧 问题解决

#### ✅ 插件管理识别修复
- 修复了scrcpy插件无法识别的问题
- 实现了智能插件发现和加载机制
- 支持插件热加载和动态管理
- 提供插件状态监控和错误处理

#### 🎮 游戏分类管理
- **按游戏分类**：每个游戏独立管理，包含完整的脚本和模板
- **游戏信息管理**：支持游戏名称、描述、平台、包名等信息
- **模板目录**：每个游戏拥有独立的模板存储目录
- **脚本组织**：游戏内的脚本按类型分类（启动、异常、基础、自定义）

#### 📋 游戏内队列系统
- **独立队列**：每个游戏都有自己的执行队列
- **优先级调度**：支持脚本优先级设置和智能调度
- **状态管理**：实时监控队列状态和脚本执行进度
- **并发控制**：支持多游戏队列并行执行

#### 📦 导入导出功能
- **压缩包导入**：支持完整游戏数据的zip格式导入
- **数据导出**：一键导出游戏的所有脚本和模板
- **版本兼容**：自动处理导入数据的版本兼容性
- **数据完整性**：确保导入导出过程中数据的完整性

### 🚀 脚本系统重构

#### 💡 扩展性增强
- **动作返回值**：支持动作执行结果的捕获和传递
- **变量系统**：实现脚本间的数据共享和状态传递
- **结果存储**：自动存储执行结果供后续步骤使用
- **数据流转**：支持复杂的数据处理和传递逻辑

#### 🔍 智能识别功能
- **模板匹配**：集成高精度的图像模板匹配
- **OCR识别**：支持多语言文字识别
- **区域识别**：支持指定区域的精确识别
- **置信度控制**：可调节的识别阈值和精度控制

#### 🔀 条件判断系统
- **模板条件**：基于图像匹配结果的条件判断
- **变量比较**：支持数值、字符串等多种比较操作
- **逻辑分支**：支持复杂的条件分支和嵌套判断
- **动态执行**：根据条件结果动态选择执行路径

#### ⏱️ 轮询调度机制
- **检测即执行**：摆脱串行执行，实现检测到即执行
- **轮询间隔**：可配置的检测间隔和执行频率
- **最大迭代**：防止无限循环的安全机制
- **跳出条件**：支持条件满足时的智能跳出

#### 🚨 异常检测处理
- **超时检测**：超过1分钟无动作自动触发异常处理
- **异常脚本**：每个游戏可配置专门的异常处理脚本
- **自动恢复**：支持异常情况下的自动恢复机制
- **错误截图**：异常时自动截图保存现场

#### 🔌 多插件支持
- **平台适配**：一个脚本可调用多个插件实现跨平台
- **插件切换**：动态选择最适合的插件执行
- **功能互补**：不同插件提供互补功能
- **统一接口**：标准化的插件调用接口

#### 📝 新增脚本功能
- **游戏单位创建**：以游戏为单位进行脚本创建
- **三脚本模板**：自动创建启动、异常、基础三个脚本
- **模板展示**：实时展示对应的模板文件
- **可视化编辑**：提供友好的脚本编辑界面

## 🏗️ 系统架构

### 📁 项目结构
```
AutoScript/
├── core/                     # 核心模块
│   ├── __init__.py
│   ├── engine.py            # 主引擎
│   ├── plugin_manager.py    # 插件管理器
│   ├── game_manager.py      # 游戏管理器
│   ├── script_executor.py   # 脚本执行器
│   ├── script_queue.py      # 队列管理器
│   ├── config_manager.py    # 配置管理器
│   ├── template_matcher.py  # 模板匹配器
│   └── ocr_engine.py        # OCR引擎
├── plugins/                  # 插件目录
│   ├── __init__.py
│   ├── scrcpy_plugin.py     # Android控制插件
│   ├── windows_plugin.py    # Windows控制插件
│   └── playwright_plugin.py # Web自动化插件
├── web/                      # Web界面
│   ├── app.py               # Flask应用
│   └── templates/
│       └── index.html       # 主界面
├── configs/                  # 配置文件
│   └── config.yaml          # 主配置
├── games/                    # 游戏数据
├── templates/                # 全局模板
├── logs/                     # 日志文件
├── temp/                     # 临时文件
├── main.py                   # 程序入口
├── requirements.txt          # 依赖列表
├── pyproject.toml           # 项目配置
└── README.md                # 项目说明
```

### 🔧 核心模块

#### AutoScriptEngine (主引擎)
- 系统的核心控制器
- 负责各模块的初始化和协调
- 提供统一的系统状态管理
- 处理系统级的配置和生命周期

#### PluginManager (插件管理器)
- 智能插件发现和加载
- 插件生命周期管理
- 插件间通信和协调
- 错误处理和状态监控

#### GameManager (游戏管理器)
- 游戏信息的CRUD操作
- 脚本组织和管理
- 导入导出功能实现
- 模板文件管理

#### ScriptExecutor (脚本执行器)
- 高级脚本执行引擎
- 支持复杂的动作流程
- 变量管理和数据传递
- 异常检测和处理

#### ScriptQueueManager (队列管理器)
- 多游戏队列管理
- 优先级调度算法
- 并发执行控制
- 状态监控和统计

## 📋 脚本动作类型

### 🔌 插件动作 (plugin_action)
```json
{
    "type": "plugin_action",
    "plugin": "scrcpy",
    "action": "click",
    "params": {"x": 100, "y": 200},
    "description": "点击坐标",
    "store_result": "click_result"
}
```

### 🔍 条件判断 (condition)
```json
{
    "type": "condition",
    "condition_type": "template_match",
    "template_path": "button.png",
    "threshold": 0.8,
    "input_image": "$screenshot",
    "on_true": [...],
    "on_false": [...]
}
```

### ⭕ 轮询循环 (polling_loop)
```json
{
    "type": "polling_loop",
    "interval": 1.0,
    "max_iterations": 100,
    "actions": [...],
    "break_on_true": true
}
```

### 🖼️ 模板匹配 (template_match)
```json
{
    "type": "template_match",
    "template_path": "target.png",
    "input_image": "$current_screen",
    "threshold": 0.8,
    "store_result": "match_info"
}
```

### 📝 OCR识别 (ocr_text)
```json
{
    "type": "ocr_text",
    "input_image": "$screenshot",
    "region": [100, 100, 200, 50],
    "store_result": "recognized_text"
}
```

### ⏳ 等待延迟 (wait)
```json
{
    "type": "wait",
    "duration": 2.0,
    "description": "等待2秒"
}
```

### 📊 变量设置 (set_variable)
```json
{
    "type": "set_variable",
    "name": "retry_count",
    "value": 0
}
```

## 🌐 Web界面功能

### 📊 仪表板
- 系统状态概览
- 实时统计数据
- 快速访问入口
- 性能监控图表

### 🎮 游戏管理
- 游戏列表展示
- 创建/编辑/删除游戏
- 游戏信息管理
- 平台分类筛选

### 📜 脚本管理
- 按游戏查看脚本
- 脚本编辑器
- 模板关联管理
- 脚本类型分类

### 📋 执行队列
- 实时队列状态
- 执行进度监控
- 队列控制操作
- 历史记录查看

### 🔌 插件管理
- 插件状态监控
- 插件功能测试
- 配置参数管理
- 错误日志查看

## 🚀 使用指南

### 📦 安装部署

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **启动Web界面**
```bash
python main.py --mode web --host 0.0.0.0 --port 5000
```

3. **启动命令行模式**
```bash
python main.py --mode cli
```

### 🎮 创建游戏

1. **通过Web界面创建**
   - 访问Web界面
   - 点击"新建游戏"
   - 填写游戏信息
   - 系统自动创建基础脚本

2. **通过命令行创建**
```bash
AutoScript> create-game "示例游戏" android "游戏描述"
```

### 📝 编写脚本

1. **基础脚本结构**
```json
{
    "actions": [
        {
            "type": "plugin_action",
            "plugin": "scrcpy",
            "action": "take_screenshot",
            "params": {"output_path": "current.png"},
            "store_result": "screenshot"
        },
        {
            "type": "condition",
            "condition_type": "template_match",
            "template_path": "start_button.png",
            "input_image": "$screenshot",
            "threshold": 0.8,
            "on_true": [
                {
                    "type": "plugin_action",
                    "plugin": "scrcpy",
                    "action": "click",
                    "params": {"x": "$match_x", "y": "$match_y"}
                }
            ]
        }
    ]
}
```

### 📦 导入导出

1. **导出游戏**
   - 选择目标游戏
   - 点击导出按钮
   - 下载zip文件

2. **导入游戏**
   - 点击导入按钮
   - 选择zip文件
   - 系统自动解析和导入

## ⚙️ 配置说明

### 🔧 系统配置 (config.yaml)

```yaml
system:
  log_level: INFO              # 日志级别
  max_log_size: 10MB          # 最大日志大小
  auto_save_interval: 300     # 自动保存间隔(秒)

plugins:
  auto_load: true             # 自动加载插件
  plugin_dirs: [plugins]      # 插件目录

games:
  games_dir: games            # 游戏数据目录
  templates_dir: templates    # 模板目录
  auto_backup: true          # 自动备份

execution:
  default_timeout: 30        # 默认超时时间
  exception_timeout: 60      # 异常检测超时
  max_concurrent_scripts: 5  # 最大并发脚本数

ocr:
  engine: paddleocr          # OCR引擎
  language: ch               # 识别语言
  use_gpu: false            # 是否使用GPU

web:
  host: 127.0.0.1           # Web服务地址
  port: 5000                # Web服务端口
  debug: false              # 调试模式
```

## 🔌 插件开发

### 📝 插件基类
```python
from core.plugin_manager import BasePlugin

class MyPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "my_plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "我的自定义插件"
    
    @property
    def supported_platforms(self) -> List[str]:
        return ["windows", "android"]
    
    def initialize(self) -> bool:
        # 初始化逻辑
        return True
    
    def execute_action(self, action: str, params: Dict[str, Any]) -> Any:
        # 动作执行逻辑
        if action == "my_action":
            return self._my_action(params)
    
    def is_available(self) -> bool:
        # 检查插件是否可用
        return True
```

## 🎯 使用场景

### 🎮 游戏自动化
- 日常任务自动化
- 资源收集脚本
- 战斗辅助功能
- 升级练级自动化

### 🧪 应用测试
- UI自动化测试
- 功能回归测试
- 性能压力测试
- 兼容性测试

### 📱 移动端自动化
- App功能测试
- 界面遍历测试
- 性能监控
- 用户行为模拟

### 🖥️ 桌面应用自动化
- 办公软件自动化
- 系统管理脚本
- 数据处理自动化
- 定时任务执行

## 🔧 故障排除

### ❌ 常见问题

1. **插件无法加载**
   - 检查插件文件名是否以 `_plugin.py` 结尾
   - 确认插件类继承自 `BasePlugin`
   - 查看日志文件获取详细错误信息

2. **脚本执行失败**
   - 检查脚本JSON格式是否正确
   - 确认所需的模板文件存在
   - 验证插件是否可用

3. **Web界面无法访问**
   - 检查端口是否被占用
   - 确认防火墙设置
   - 查看启动日志

### 📋 日志分析
- 日志文件位置：`AutoScript/logs/autoscript.log`
- 日志级别可通过配置文件调整
- 支持日志轮转和压缩

## 🚀 未来规划

### 🎯 短期目标
- [ ] 可视化脚本编辑器
- [ ] 更多内置插件支持
- [ ] 性能优化和稳定性提升
- [ ] 移动端Web界面适配

### 🌟 长期目标
- [ ] AI辅助脚本生成
- [ ] 云端脚本市场
- [ ] 分布式执行支持
- [ ] 跨平台客户端

## 📄 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来改进项目！

---

**AutoScript 2.0** - 让游戏自动化更简单、更强大！