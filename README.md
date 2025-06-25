# 数据表处理系统

基于 Streamlit 和 Polars 构建的专业数据表处理工具，提供数据合并、清理、验证和导出功能。

## 🚀 功能特性

- **📊 数据合并**: 支持多个 CSV/Excel 文件的智能合并
- **🔍 数据预览**: 实时数据预览和统计信息展示
- **🎯 字段选择**: 灵活的字段选择和导出配置
- **⚙️ 数据预处理**: 支持去重、数据清理等预处理功能
- **📤 数据导出**: 高性能的 Excel 格式导出
- **🔧 模块化架构**: 易于扩展的插件化设计
- **🎨 清晰UI**: 侧边栏应用选择，主区域功能展示
- **🔄 组件独立**: 各应用内部独立管理文件上传、预处理等功能

## 🏗️ 系统架构

```
table_data/
│
├── app/                        # 应用核心代码
│   ├── run.py                  # 应用主编排器（依赖注入、服务注册）
│   ├── base/                   # 基础接口定义
│   ├── core/                   # 核心服务层（容器、注册管理、全局服务）
│   ├── state/                  # 状态管理
│   ├── handlers/               # 业务处理层
│   ├── components/             # 可复用UI组件
│   ├── ui/                     # 主UI界面（侧边栏+主内容区）
│   ├── merge_extract/          # 数据合并应用（内含文件上传、预处理）
│   └── utils/                  # 通用工具
├── config/                     # 配置管理
├── main.py                     # 项目主入口
└── pyproject.toml              # 项目配置
```

## 🛠️ 技术栈

- **前端框架**: Streamlit - 快速构建数据应用
- **数据处理**: Polars - 高性能数据处理库
- **文件处理**: 支持 CSV、Excel (.xlsx/.xls) 格式
- **架构模式**: 依赖注入、策略模式、组件化设计

## 📦 安装与运行

### 环境要求

- Python >= 3.13
- Windows 10/11 (当前配置)

### 安装依赖

```bash
# 安装项目依赖
pip install -e .

# 或者直接安装依赖
pip install streamlit polars openpyxl pandas pyarrow
```

### 启动应用

```bash
# 方式一：直接运行主入口
streamlit run main.py

# 方式二：使用 Python 模块方式
python -m streamlit run main.py

# 方式三：使用 uv 模式启动
uv run streamlit run main.py
```

## 💡 使用指南

### 基本使用流程

1. **选择应用**: 在左侧边栏选择"数据合并"应用
2. **上传文件**: 在"文件上传"标签页中上传一个或多个 CSV/Excel 文件
3. **配置预处理**: 在同一标签页中可选择启用去重、数据清理等功能
4. **预览数据**: 在"数据预览"标签页查看合并后的数据概览和统计信息
5. **选择字段**: 在"字段选择"标签页选择需要导出的数据字段
6. **导出数据**: 在"导出数据"标签页生成并下载 Excel 格式的处理结果

### UI界面说明

- **侧边栏**: 应用选择器 + 项目介绍和使用说明
- **主内容区**: 根据选择的应用显示相应功能界面
- **标签页设计**: 每个应用内部使用标签页组织不同功能模块
- **独立操作**: 每个应用独立管理其所需的文件上传、预处理等功能

### 支持的文件格式

- **CSV 文件**: .csv
- **Excel 文件**: .xlsx, .xls
- **多工作表**: 自动读取 Excel 文件的所有工作表

### 数据处理功能

- **智能合并**: 基于共同列自动合并多个数据表
- **数据清理**: 移除空行、清理字符串空格
- **去重处理**: 移除重复数据行
- **列标准化**: 自动标准化列名格式

## 🔧 扩展开发

### 添加新应用

1. 在 `app/` 目录下创建新的应用模块
2. 继承 `BaseApp` 接口并实现必要方法
3. 在 `AppOrchestrator` 中注册新应用

```python
from app.base.base_app import BaseApp

class YourNewApp(BaseApp):
    def get_name(self) -> str:
        return "新应用名称"
    
    def get_description(self) -> str:
        return "应用描述"
    
    def render(self) -> None:
        # 实现UI渲染逻辑
        pass
    
    def validate_input(self, data) -> bool:
        # 实现数据验证逻辑
        return True
```

### 添加新组件

在 `app/components/` 目录下创建新的UI组件，遵循组件化设计原则。

## 🐛 故障排除

### 常见问题

1. **导入错误**: 确保已安装所有依赖项
2. **文件读取失败**: 检查文件格式和编码
3. **内存不足**: 对于大文件，建议启用数据清理和去重功能

### 日志查看

应用运行时的日志信息会显示在 Streamlit 界面中，便于调试和故障排除。

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 👥 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

---

**作者**: lijianqiao  
**邮箱**: lijianqiao2906@live.com  
**版本**: 1.0.0