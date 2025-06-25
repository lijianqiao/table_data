# 数据表处理系统完整设计文档

## 1. 系统架构

### 1.1 总体架构

```
table_data/
│
├── app/                        # 应用核心代码
│   ├── run.py                  # 应用主编排器：管理状态、串联UI与业务逻辑
│   ├── base/                   # 基础接口定义
│   │   ├── base_app.py         # 应用基础接口
│   │   ├── base_processor.py   # 处理器基础接口
│   │   └── base_exporter.py    # 导出器基础接口
│   ├── core/                   # 核心服务层
│   │   ├── container.py        # 依赖注入容器
│   │   └── registry.py         # 应用注册管理
│   ├── state/                  # 状态管理
│   │   └── session_manager.py  # 会话状态管理
│   ├── handlers/               # 业务处理层
│   │   ├── file_handler.py     # 文件处理
│   │   ├── data_processor.py   # 数据处理
│   │   └── export_handler.py   # 导出处理
│   ├── components/             # 可复用的底层核心组件
│   │   ├── file_uploader.py    # 文件上传组件
│   │   ├── data_preview.py     # 数据预览组件
│   │   ├── column_selector.py  # 字段选择组件
│   │   ├── export_panel.py     # 导出面板组件
│   │   ├── error_handler.py    # 错误处理组件
│   │   └── layout_manager.py   # 布局管理组件
│   ├── pipeline/               # 数据流水线
│   │   └── data_pipeline.py    # 数据处理流水线
│   ├── plugins/                # 插件系统
│   │   └── plugin_manager.py   # 插件管理器
│   ├── merge_extract/          # 应用1: 合并与提取
│   │   ├── merge.py            #    - 负责合并的业务逻辑
│   │   └── extract.py          #    - 负责提取的业务逻辑
│   ├── application/            # 应用2: (占位)
│   ├── ui/                     # UI界面层
│   │   └── ui.py               #    - 主页面 UI
│   └── utils/                  # 通用工具
│       ├── validators.py       #    - 数据验证
│       ├── logger.py           #    - 日志
│       ├── memory_manager.py   #    - 内存管理
│       ├── file_validator.py   #    - 文件验证
│       └── generate_key.py     #    - 其他工具
├── docs/
│   ├── merge_extract/          # 应用1: 合并与提取 文档
│   │   └── 设计文档.md
│   └── application/            # 应用2: (占位)
├── config/                     # 配置管理
│   ├── __init__.py
│   ├── app_config.py           # 应用配置
│   ├── file_config.py          # 文件配置
│   └── ui_config.py            # UI配置
├── main.py                     # 项目主入口
├── .env                        # 环境变量
├── pyproject.toml              # 项目依赖与配置 (PEP 621)
├── README.MD
└── uv.lock
```

## 2. 基础接口设计

### 2.1 BaseApp 应用基础接口

```python
from abc import ABC, abstractmethod
import polars as pl


class BaseApp(ABC):
    @abstractmethod
    def get_name(self) -> str:
        """获取应用名称"""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """获取应用描述"""
        pass

    @abstractmethod
    def render(self) -> None:
        """渲染应用界面"""
        pass

    @abstractmethod
    def validate_input(self, data: pl.DataFrame) -> bool:
        """验证输入数据"""
        pass

    def get_config(self) -> dict:
        """获取应用配置"""
        return {}
```

### 2.2 BaseProcessor 处理器基础接口

```python
from abc import ABC, abstractmethod
import polars as pl


class BaseProcessor(ABC):
    @abstractmethod
    def process(self, df: pl.DataFrame) -> pl.DataFrame:
        """处理数据"""
        pass

    @abstractmethod
    def validate(self, df: pl.DataFrame) -> bool:
        """验证数据"""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """获取处理器描述"""
        pass
```

### 2.3 BaseExporter 导出器基础接口

```python
from abc import ABC, abstractmethod
import polars as pl


class BaseExporter(ABC):
    @abstractmethod
    def export(self, df: pl.DataFrame, **kwargs) -> bytes:
        """导出数据"""
        pass

    @abstractmethod
    def get_mime_type(self) -> str:
        """获取MIME类型"""
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """获取文件扩展名"""
        pass
```

## 3. 核心服务层设计

### 3.1 依赖注入容器

```python
from typing import Any


class Container:
    def __init__(self):
        self._services = {}
        self._singletons = {}

    def register(self, name: str, service_class, singleton: bool = False) -> None:
        """注册服务"""
        self._services[name] = (service_class, singleton)

    def get(self, name: str) -> Any:
        """获取服务实例"""
        if name not in self._services:
            raise ValueError(f"Service {name} not registered")

        service_class, is_singleton = self._services[name]

        if is_singleton:
            if name not in self._singletons:
                self._singletons[name] = service_class()
            return self._singletons[name]

        return service_class()

    def clear(self) -> None:
        """清空容器"""
        self._services.clear()
        self._singletons.clear()
```

### 3.2 应用注册管理

```python
from app.base.base_app import BaseApp


class AppRegistry:
    def __init__(self):
        self._apps = {}

    def register_app(self, app_class: BaseApp) -> None:
        """注册应用"""
        app_instance = app_class()
        self._apps[app_instance.get_name()] = app_class

    def get_available_apps(self) -> dict:
        """获取可用应用列表"""
        return {name: cls().get_description() for name, cls in self._apps.items()}

    def load_app(self, name: str) -> BaseApp:
        """加载应用实例"""
        if name not in self._apps:
            raise ValueError(f"App {name} not registered")
        return self._apps[name]()

    def get_app_names(self) -> list[str]:
        """获取应用名称列表"""
        return list(self._apps.keys())
```

## 4. 状态管理设计

### 4.1 会话状态管理

```python
import streamlit as st
from typing import Any


class SessionManager:
    # 缓存键命名规则
    CACHE_KEYS = {
        'uploaded_files': 'files_{session_id}',
        'processed_data': 'data_{file_hash}',
        'user_selections': 'selections_{app_name}',
        'current_app': 'current_app',
        'processing_status': 'processing_status'
    }

    @staticmethod
    def init_session_state() -> None:
        """初始化会话状态"""
        default_states = {
            'current_app': None,
            'uploaded_files': [],
            'processed_data': None,
            'selected_columns': [],
            'processing_status': 'idle',
            'error_message': None
        }

        for key, value in default_states.items():
            if key not in st.session_state:
                st.session_state[key] = value

    @staticmethod
    def get_state(key: str) -> Any:
        """获取状态值"""
        return st.session_state.get(key)

    @staticmethod
    def set_state(key: str, value: Any) -> None:
        """设置状态值"""
        st.session_state[key] = value

    @staticmethod
    def clear_state(keys: list[str] = None) -> None:
        """清空指定状态或全部状态"""
        if keys:
            for key in keys:
                if key in st.session_state:
                    del st.session_state[key]
        else:
            st.session_state.clear()

    @staticmethod
    def get_cache_key(template: str, **kwargs) -> str:
        """生成缓存键"""
        return template.format(**kwargs)
```

## 5. 核心处理器设计

### 5.1 FileHandler 文件处理器

```python
import polars as pl
from typing import List


class FileHandler:
    def __init__(self):
        self.supported_formats = ['.csv', '.xlsx', '.xls']

    def detect_file_type(self, file) -> str:
        """检测文件类型"""
        filename = file.name.lower()
        for fmt in self.supported_formats:
            if filename.endswith(fmt):
                return fmt
        raise ValueError(f"Unsupported file format: {filename}")

    def read_csv(self, file) -> pl.DataFrame:
        """读取CSV文件"""
        try:
            return pl.read_csv(file)
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {str(e)}")

    def read_excel(self, file) -> list[pl.DataFrame]:
        """读取Excel文件，支持多工作表"""
        try:
            # 读取所有工作表
            excel_data = pl.read_excel(file, sheet_id=None)
            if isinstance(excel_data, dict):
                return list(excel_data.values())
            return [excel_data]
        except Exception as e:
            raise ValueError(f"Error reading Excel file: {str(e)}")

    def read_file(self, file) -> list[pl.DataFrame]:
        """统一文件读取接口"""
        file_type = self.detect_file_type(file)

        if file_type == '.csv':
            return [self.read_csv(file)]
        elif file_type in ['.xlsx', '.xls']:
            return self.read_excel(file)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
```

### 5.2 DataProcessor 数据处理器

```python
import polars as pl
from typing import List


class DataProcessor:
    def __init__(self):
        self.processing_steps = []

    def merge_dataframes(self, dfs: list[pl.DataFrame]) -> pl.DataFrame:
        """
        合并多个DataFrame。
        当前策略: 基于共同列进行纵向合并(concat)。
        未来可扩展: 支持基于key的横向合并(join)等多种策略。
        """
        if not dfs:
            raise ValueError("No dataframes to merge")

        if len(dfs) == 1:
            return dfs[0]

        # 获取共同列
        common_columns = self.get_common_columns(dfs)

        # 标准化列名并合并
        standardized_dfs = []
        for df in dfs:
            std_df = self.standardize_columns(df)
            # 只保留共同列
            std_df = std_df.select(common_columns)
            standardized_dfs.append(std_df)

        return pl.concat(standardized_dfs)

    def get_common_columns(self, dfs: list[pl.DataFrame]) -> list[str]:
        """获取共同列"""
        if not dfs:
            return []

        common_cols = set(dfs[0].columns)
        for df in dfs[1:]:
            common_cols &= set(df.columns)

        return list(common_cols)

    def standardize_columns(self, df: pl.DataFrame) -> pl.DataFrame:
        """标准化列名"""
        # 去除空格，转换为小写
        column_mapping = {
            col: col.strip().lower().replace(' ', '_')
            for col in df.columns
        }
        return df.rename(column_mapping)

    def validate_data(self, df: pl.DataFrame) -> dict:
        """验证数据质量"""
        return {
            'row_count': len(df),
            'column_count': len(df.columns),
            'null_counts': df.null_count().to_dict(),
            'data_types': {col: str(dtype) for col, dtype in zip(df.columns, df.dtypes)},
            'memory_usage': df.estimated_size()
        }

    def deduplicate(self, df: pl.DataFrame) -> pl.DataFrame:
        """去重"""
        return df.unique()

    def clean_data(self, df: pl.DataFrame) -> pl.DataFrame:
        """数据清理"""
        # 移除全空行
        df = df.filter(~pl.all_horizontal(pl.all().is_null()))

        # 字符串列去除前后空格
        string_cols = [col for col, dtype in zip(df.columns, df.dtypes) if dtype == pl.Utf8]
        for col in string_cols:
            df = df.with_columns(pl.col(col).str.strip())

        return df
```

### 5.3 ExportHandler 导出处理器 (已优化)

```python
import polars as pl
from io import BytesIO


class ExportHandler:
    def __init__(self):
        self.supported_formats = ['.xlsx']  # 简化为只支持xlsx以获得更好性能

    def export_excel(self, df: pl.DataFrame, columns: list[str] = None) -> bytes:
        """
        使用Polars直接导出Excel格式，避免Pandas转换，提升性能。
        """
        if columns:
            df_to_export = df.select(columns)
        else:
            df_to_export = df

        output = BytesIO()
        df_to_export.write_excel(output)

        return output.getvalue()

    def get_export_summary(self, df: pl.DataFrame, selected_columns: list[str] = None) -> dict:
        """获取导出摘要信息"""
        export_df = df.select(selected_columns) if selected_columns else df

        return {
            'total_rows': len(export_df),
            'total_columns': len(export_df.columns),
            'selected_columns': selected_columns or df.columns,
            'estimated_size': f"{export_df.estimated_size() / 1024 / 1024:.2f} MB"
        }
```

## 6. UI组件设计

### 6.1 ErrorHandler 错误处理组件

```python
import streamlit as st
from typing import Callable, Any


class ErrorHandler:
    @staticmethod
    def show_error(message: str, details: str = None) -> None:
        """显示错误信息"""
        st.error(f"❌ {message}")
        if details:
            with st.expander("错误详情"):
                st.code(details)

    @staticmethod
    def show_warning(message: str) -> None:
        """显示警告信息"""
        st.warning(f"⚠️ {message}")

    @staticmethod
    def show_success(message: str) -> None:
        """显示成功信息"""
        st.success(f"✅ {message}")

    @staticmethod
    def validate_and_execute(func: Callable, *args, **kwargs) -> Any:
        """安全执行函数并处理错误"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ErrorHandler.show_error(f"操作失败", str(e))
            return None
```

### 6.2 LayoutManager 布局管理组件

```python
import streamlit as st


class LayoutManager:
    @staticmethod
    def create_main_layout():
        """创建主布局"""
        # 设置页面配置
        st.set_page_config(
            page_title="数据表处理系统",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # 主标题
        st.title("📊 数据表处理系统")
        st.markdown("---")

    @staticmethod
    def create_sidebar():
        """创建侧边栏"""
        with st.sidebar:
            st.header("🔧 系统控制")
            return st.container()

    @staticmethod
    def show_progress_bar(progress: float, text: str = "处理中...") -> None:
        """显示进度条"""
        progress_bar = st.progress(0)
        status_text = st.empty()

        progress_bar.progress(progress)
        status_text.text(f"{text} {progress * 100:.1f}%")

    @staticmethod
    def create_collapsible_section(title: str, expanded: bool = True):
        """创建可折叠区域"""
        return st.expander(title, expanded=expanded)

    @staticmethod
    def create_columns(ratios: list[int]):
        """创建多列布局"""
        return st.columns(ratios)
```

### 6.3 FileUploader 文件上传组件

```python
import streamlit as st


class FileUploader:
    def __init__(self, file_validator):
        self.file_validator = file_validator

    def render(self) -> list:
        """渲染文件上传界面"""
        uploaded_files = st.file_uploader(
            "📁 选择文件",
            type=['csv', 'xlsx', 'xls'],
            accept_multiple_files=True,
            help="支持 CSV、Excel 格式，可多选"
        )

        if uploaded_files:
            validation_results = self.validate_files(uploaded_files)
            self.show_upload_status(uploaded_files, validation_results)

            # 只返回验证通过的文件
            return [f for f, result in zip(uploaded_files, validation_results) if result['valid']]

        return []

    def validate_files(self, files: list) -> list[dict]:
        """验证文件"""
        results = []
        for file in files:
            result = {
                'valid': True,
                'errors': [],
                'warnings': []
            }

            # 文件格式验证
            if not self.file_validator.validate_file_format(file):
                result['valid'] = False
                result['errors'].append("不支持的文件格式")

            # 文件大小验证
            if not self.file_validator.validate_file_size(file):
                result['valid'] = False
                result['errors'].append("文件大小超过限制")

            results.append(result)

        return results

    def show_upload_status(self, files: list, validation_results: list[dict]) -> None:
        """显示上传状态"""
        for file, result in zip(files, validation_results):
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.text(f"📄 {file.name}")

            with col2:
                if result['valid']:
                    st.success("✅")
                else:
                    st.error("❌")

            with col3:
                file_info = self.file_validator.get_file_info(file)
                st.caption(f"{file_info['size']}")

            # 显示错误信息
            if result['errors']:
                for error in result['errors']:
                    st.error(f"  • {error}")
```

### 6.4 DataPreview 数据预览组件

```python
import streamlit as st
import polars as pl


class DataPreview:
    def __init__(self, max_rows: int = 100):
        self.max_rows = max_rows

    def render_summary(self, df: pl.DataFrame) -> None:
        """渲染数据摘要"""
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("总行数", f"{len(df):,}")

        with col2:
            st.metric("总列数", len(df.columns))

        with col3:
            st.metric("内存使用", f"{df.estimated_size() / 1024 / 1024:.2f} MB")

        with col4:
            null_count = df.null_count().sum_horizontal().item()
            st.metric("空值数量", f"{null_count:,}")

    def render_sample_data(self, df: pl.DataFrame, rows: int = None) -> None:
        """渲染样本数据"""
        display_rows = rows or self.max_rows

        st.subheader("📋 数据预览")

        if len(df) > display_rows:
            st.info(f"显示前 {display_rows} 行数据，共 {len(df)} 行")
            st.dataframe(df.head(display_rows), use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)

    def render_column_info(self, df: pl.DataFrame) -> None:
        """渲染列信息"""
        st.subheader("📊 列信息")

        column_info = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            null_count = df[col].null_count()
            unique_count = df[col].n_unique()

            column_info.append({
                '列名': col,
                '数据类型': dtype,
                '空值数': null_count,
                '唯一值数': unique_count,
                '空值比例': f"{null_count / len(df) * 100:.1f}%"
            })

        info_df = pl.DataFrame(column_info)
        st.dataframe(info_df, use_container_width=True)
```

### 6.5 ColumnSelector 字段选择组件 (已优化)

```python
import streamlit as st
import polars as pl


class ColumnSelector:
    def render(self, available_columns: list[str], default_selected: list[str] = None) -> list[str]:
        """渲染字段选择界面，交互已优化"""
        st.subheader("🎯 选择导出字段")

        # 使用 st.checkbox 实现全选/取消全选，交互更友好
        select_all = st.checkbox("全选/取消全选", value=True)

        if select_all:
            default_selection = available_columns
        else:
            default_selection = []

        # 字段选择
        selected_columns = st.multiselect(
            "选择要导出的字段：",
            options=available_columns,
            default=default_selection,
            help="选择需要导出的数据字段"
        )

        # 显示选择摘要
        if selected_columns:
            st.info(f"已选择 {len(selected_columns)} / {len(available_columns)} 个字段")
        else:
            st.warning("请至少选择一个字段")

        return selected_columns

    def render_with_preview(self, df: pl.DataFrame, max_preview_rows: int = 5) -> list[str]:
        """带预览的字段选择"""
        selected_columns = self.render(df.columns)

        if selected_columns:
            st.subheader("👀 选择字段预览")
            preview_df = df.select(selected_columns).head(max_preview_rows)
            st.dataframe(preview_df, use_container_width=True)

        return selected_columns
```

## 7. 配置管理设计

### 7.1 文件配置

```python
# config/file_config.py
class FileConfig:
    # 支持的文件格式
    SUPPORTED_FORMATS = ['.csv', '.xlsx', '.xls']

    # 文件大小限制 (100MB)
    MAX_FILE_SIZE = 100 * 1024 * 1024

    # CSV读取配置
    CSV_CONFIG = {
        'encoding': 'utf-8',
        'separator': ',',
        'has_header': True,
        'null_values': ['', 'NULL', 'null', 'NA', 'na']
    }

    # Excel读取配置
    EXCEL_CONFIG = {
        'read_all_sheets': True,
        'header_row': 0
    }
```

### 7.2 UI配置

```python
# config/ui_config.py
class UIConfig:
    # 数据预览配置
    PREVIEW_ROWS = 100
    MAX_PREVIEW_ROWS = 1000

    # 布局配置
    SIDEBAR_WIDTH = 300
    MAIN_CONTENT_WIDTH = 800

    # 组件配置
    PROGRESS_BAR_HEIGHT = 20
    ERROR_MESSAGE_DURATION = 5000

    # 导出配置
    DEFAULT_EXPORT_FORMAT = 'xlsx'
    EXPORT_FORMATS = ['xlsx']

    # 颜色主题
    COLORS = {
        'primary': '#1f77b4',
        'success': '#2ca02c',
        'warning': '#ff7f0e',
        'danger': '#d62728',
        'info': '#17a2b8'
    }
```

### 7.3 应用配置

```python
# config/app_config.py
class AppConfig:
    # 应用元信息
    APP_NAME = "数据表处理系统"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "专业的数据表处理工具"

    # 性能配置
    MAX_MEMORY_USAGE = 0.8  # 最大内存使用率
    CHUNK_SIZE = 10000  # 批处理大小

    # 缓存配置
    CACHE_TTL = 3600  # 缓存生存时间（秒）
    MAX_CACHE_SIZE = 100  # 最大缓存项数

    # 日志配置
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## 8. 工具类设计

### 8.1 内存管理器

```python
# app/utils/memory_manager.py
import psutil
import polars as pl


class MemoryManager:
    @staticmethod
    def get_memory_usage() -> float:
        """获取当前内存使用率"""
        return psutil.virtual_memory().percent / 100

    @staticmethod
    def check_memory_available(required_mb: float) -> bool:
        """检查是否有足够内存"""
        available_mb = psutil.virtual_memory().available / 1024 / 1024
        return available_mb > required_mb

    @staticmethod
    def optimize_dataframe(df: pl.DataFrame) -> pl.DataFrame:
        """优化DataFrame内存使用"""
        # 转换数据类型以节省内存
        optimized_df = df

        for col in df.columns:
            if df[col].dtype == pl.Utf8:
                # 尝试转换为分类类型
                if len(df) > 0:  # 避免除零错误
                    unique_ratio = df[col].n_unique() / len(df)
                    if unique_ratio < 0.5:  # 如果唯一值比例小于50%
                        optimized_df = optimized_df.with_columns(
                            pl.col(col).cast(pl.Categorical)
                        )

        return optimized_df

    @staticmethod
    def estimate_processing_memory(df: pl.DataFrame, factor: float = 2.0) -> float:
        """估算处理所需内存 (MB)"""
        current_size = df.estimated_size() / 1024 / 1024
        return current_size * factor
```

### 8.2 文件验证器 (已优化)

```python
# app/utils/file_validator.py
import os
import polars as pl
from typing import Dict, Any
from config.file_config import FileConfig


class FileValidator:
    def __init__(self, max_size: int = FileConfig.MAX_FILE_SIZE):
        """构造函数从配置模块读取最大文件大小"""
        self.max_size = max_size
        self.supported_formats = FileConfig.SUPPORTED_FORMATS

    def validate_file_format(self, file) -> bool:
        """验证文件格式"""
        filename = file.name.lower()
        return any(filename.endswith(fmt) for fmt in self.supported_formats)

    def validate_file_size(self, file) -> bool:
        """验证文件大小"""
        return file.size <= self.max_size

    def get_file_info(self, file) -> Dict[str, Any]:
        """获取文件信息"""
        size_mb = file.size / 1024 / 1024

        return {
            'name': file.name,
            'size': f"{size_mb:.2f} MB",
            'size_bytes': file.size,
            'type': file.type,
            'extension': os.path.splitext(file.name)[1].lower()
        }

    def validate_file_content(self, file) -> Dict[str, Any]:
        """
        验证文件内容。
        未来可扩展: 使用 pl.read_csv(n_rows=5) 包装在 try-except 中，
        进行更可靠的内容格式验证。
        """
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }

        try:
            # 简单的内容检查
            file.seek(0)
            first_bytes = file.read(1024)
            file.seek(0)

            # 检查是否为空文件
            if len(first_bytes) == 0:
                validation_result['valid'] = False
                validation_result['errors'].append("文件为空")

        except Exception as e:
            validation_result['valid'] = False
            validation_result['errors'].append(f"文件内容验证失败: {str(e)}")

        return validation_result
```

## 9. 数据流水线设计

### 9.1 数据处理流水线

```python
# app/pipeline/data_pipeline.py
from typing import Callable, Any, List, Dict
import polars as pl
import time


class DataPipeline:
    def __init__(self):
        self.steps = []
        self.execution_stats = {}

    def add_step(self, name: str, func: Callable[[pl.DataFrame], pl.DataFrame],
                 description: str = "") -> 'DataPipeline':
        """添加处理步骤"""
        self.steps.append({
            'name': name,
            'func': func,
            'description': description
        })
        return self

    def execute(self, data: pl.DataFrame, progress_callback: Callable = None) -> pl.DataFrame:
        """执行流水线"""
        current_data = data
        total_steps = len(self.steps)

        self.execution_stats = {
            'start_time': time.time(),
            'steps': [],
            'total_steps': total_steps
        }

        for i, step in enumerate(self.steps):
            step_start = time.time()

            try:
                # 执行步骤
                current_data = step['func'](current_data)

                step_end = time.time()
                step_stats = {
                    'name': step['name'],
                    'description': step['description'],
                    'duration': step_end - step_start,
                    'input_rows': len(data) if i == 0 else len(current_data),
                    'output_rows': len(current_data),
                    'success': True
                }

                self.execution_stats['steps'].append(step_stats)

                # 更新进度
                if progress_callback:
                    progress = (i + 1) / total_steps
                    progress_callback(progress, f"完成步骤: {step['name']}")

            except Exception as e:
                step_stats = {
                    'name': step['name'],
                    'description': step['description'],
                    'error': str(e),
                    'success': False
                }
                self.execution_stats['steps'].append(step_stats)
                raise Exception(f"步骤 '{step['name']}' 执行失败: {str(e)}")

        self.execution_stats['end_time'] = time.time()
        self.execution_stats['total_duration'] = (
                self.execution_stats['end_time'] - self.execution_stats['start_time']
        )

        return current_data

    def get_execution_stats(self) -> Dict:
        """获取执行统计信息"""
        return self.execution_stats

    def clear_steps(self) -> None:
        """清空处理步骤"""
        self.steps.clear()
        self.execution_stats.clear()
```

## 10. 插件系统设计

### 10.1 插件管理器

```python
# app/plugins/plugin_manager.py
import importlib
import os
from typing import Dict, List, Any
from app.base.base_app import BaseApp


class PluginManager:
    def __init__(self):
        self.plugins = {}
        self.plugin_paths = []

    def add_plugin_path(self, path: str) -> None:
        """添加插件搜索路径"""
        if path not in self.plugin_paths:
            self.plugin_paths.append(path)

    def discover_plugins(self) -> List[str]:
        """发现可用插件"""
        discovered = []

        for path in self.plugin_paths:
            if os.path.exists(path):
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    if os.path.isdir(item_path) and not item.startswith('_'):
                        # 检查是否包含插件文件
                        plugin_file = os.path.join(item_path, 'plugin.py')
                        if os.path.exists(plugin_file):
                            discovered.append(item)

        return discovered

    def load_plugin(self, plugin_name: str) -> BaseApp:
        """加载插件"""
        try:
            # 动态导入插件模块
            module_path = f"plugins.{plugin_name}.plugin"
            plugin_module = importlib.import_module(module_path)

            # 获取插件主类
            if hasattr(plugin_module, 'Plugin'):
                plugin_class = getattr(plugin_module, 'Plugin')
                if issubclass(plugin_class, BaseApp):
                    plugin_instance = plugin_class()
                    self.plugins[plugin_name] = plugin_instance
                    return plugin_instance
                else:
                    raise ValueError(f"Plugin {plugin_name} does not inherit from BaseApp")
            else:
                raise ValueError(f"Plugin {plugin_name} does not have a Plugin class")

        except Exception as e:
            raise Exception(f"Failed to load plugin {plugin_name}: {str(e)}")

    def get_loaded_plugins(self) -> Dict[str, BaseApp]:
        """获取已加载的插件"""
        return self.plugins.copy()

    def unload_plugin(self, plugin_name: str) -> None:
        """卸载插件"""
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]

    def register_plugin(self, plugin_name: str, plugin_instance: BaseApp) -> None:
        """手动注册插件"""
        self.plugins[plugin_name] = plugin_instance
```

## 11. 主应用编排器设计 (已优化)

### 11.1 应用主编排器

```python
# app/run.py
import streamlit as st
import polars as pl
from app.core.container import Container
from app.core.registry import AppRegistry
from app.state.session_manager import SessionManager
from app.components.layout_manager import LayoutManager
from app.components.error_handler import ErrorHandler
from app.handlers.file_handler import FileHandler
from app.handlers.data_processor import DataProcessor
from app.handlers.export_handler import ExportHandler
from app.utils.file_validator import FileValidator
from app.components.file_uploader import FileUploader
from app.pipeline.data_pipeline import DataPipeline


class AppOrchestrator:
    def __init__(self):
        self.container = Container()
        self.app_registry = AppRegistry()
        self._setup_dependencies()
        self._register_apps()

    def _setup_dependencies(self):
        """设置依赖注入"""
        self.container.register('file_handler', FileHandler, singleton=True)
        self.container.register('data_processor', DataProcessor, singleton=True)
        self.container.register('export_handler', ExportHandler, singleton=True)
        self.container.register('file_validator', FileValidator, singleton=True)
        self.container.register('file_uploader',
                                lambda: FileUploader(self.container.get('file_validator')))

    def _register_apps(self):
        """注册应用"""
        try:
            from app.merge_extract.merge import MergeApp
            from app.merge_extract.extract import ExtractApp
            self.app_registry.register_app(MergeApp)
            self.app_registry.register_app(ExtractApp)
        except ImportError as e:
            ErrorHandler.show_warning(f"部分应用加载失败: {str(e)}")

    def run(self):
        """运行主应用"""
        SessionManager.init_session_state()
        LayoutManager.create_main_layout()
        sidebar = LayoutManager.create_sidebar()

        with sidebar:
            self._render_app_selector()
            st.markdown("---")
            uploaded_files = self._render_file_upload()
            st.markdown("---")
            self._render_preprocessing_options()

        self._render_main_content(uploaded_files)

    def _render_app_selector(self):
        """渲染应用选择器 (逻辑优化)"""
        st.subheader("🎯 选择应用")
        available_apps = self.app_registry.get_available_apps()
        app_names = list(available_apps.keys())

        if not app_names:
            st.error("没有可用的应用")
            return

        selected_app_name = st.selectbox(
            "选择要使用的应用：",
            options=app_names,
            format_func=lambda x: f"{x} - {available_apps[x]}",
            key="selected_app_name"
        )

        # 只有当选择的应用发生变化时，才更新状态并清空相关数据
        if selected_app_name != SessionManager.get_state('current_app'):
            SessionManager.set_state('current_app', selected_app_name)
            SessionManager.clear_state(['selected_columns'])  # 不清空processed_data

    def _render_file_upload(self):
        """渲染文件上传区域"""
        st.subheader("📁 文件上传")
        file_uploader = self.container.get('file_uploader')
        uploaded_files = file_uploader.render()
        if uploaded_files:
            SessionManager.set_state('uploaded_files', uploaded_files)
        return uploaded_files

    def _render_preprocessing_options(self):
        """渲染预处理选项"""
        st.subheader("⚙️ 数据预处理")
        is_process = st.checkbox("启用数据预处理", value=False, key="is_process")
        if is_process:
            st.checkbox("去除重复行", value=True, key="is_deduplication")
            st.checkbox("数据清理", value=True, help="移除空行，清理字符串空格", key="is_clean")

    def _render_main_content(self, uploaded_files):
        """渲染主内容区域"""
        current_app_name = SessionManager.get_state('current_app')

        if not current_app_name:
            st.info("👈 请先选择一个应用")
            return
        if not uploaded_files:
            st.info("👈 请先上传文件")
            return

        try:
            # 整合文件处理和缓存
            processed_data = self._get_processed_data(uploaded_files)
            if processed_data is not None:
                SessionManager.set_state('processed_data', processed_data)

                # 加载并运行当前应用
                app_instance = self.app_registry.load_app(current_app_name)
                if app_instance.validate_input(processed_data):
                    self._show_data_summary(processed_data)
                    app_instance.render()
                else:
                    ErrorHandler.show_error("数据验证失败", "当前数据不符合应用要求")

        except Exception as e:
            ErrorHandler.show_error("应用处理失败", str(e))

    def _get_processed_data(self, uploaded_files):
        """获取经过处理和缓存的数据"""
        # 为缓存创建唯一的标识
        file_ids = [f.file_id for f in uploaded_files]
        is_process = SessionManager.get_state('is_process')
        is_deduplication = SessionManager.get_state('is_deduplication')
        is_clean = SessionManager.get_state('is_clean')

        # 将所有影响结果的参数作为缓存的key
        cache_key = (tuple(file_ids), is_process, is_deduplication, is_clean)

        # 静态方法或全局函数才能使用st.cache_data, 这里模拟其逻辑
        # 实际应用中需要将 _cached_process_files 提取为独立函数
        return self._cached_process_files(cache_key, uploaded_files)

    # 注意：为了能在类中使用，这里是示意代码。
    # 在实际项目中, @st.cache_data 最好用于独立的函数。
    @st.cache_data(show_spinner="正在处理数据...")
    def _cached_process_files(_self, cache_key, uploaded_files):
        """实际处理文件的函数，结果将被缓存"""
        file_handler = _self.container.get('file_handler')
        data_processor = _self.container.get('data_processor')

        all_dataframes = []
        for file in uploaded_files:
            dfs = file_handler.read_file(file)
            all_dataframes.extend(dfs)

        if not all_dataframes:
            ErrorHandler.show_error("没有成功读取任何数据")
            return None

        merged_data = data_processor.merge_dataframes(all_dataframes)

        if SessionManager.get_state('is_process'):
            pipeline = _self._create_preprocessing_pipeline(data_processor)
            merged_data = pipeline.execute(merged_data)

        return merged_data

    def _create_preprocessing_pipeline(self, data_processor):
        """创建预处理流水线"""
        pipeline = DataPipeline()
        if SessionManager.get_state('is_deduplication'):
            pipeline.add_step('deduplication', data_processor.deduplicate, "去除重复行")
        if SessionManager.get_state('is_clean'):
            pipeline.add_step('clean_data', data_processor.clean_data, "数据清理")
        return pipeline

    def _show_data_summary(self, df):
        """显示数据摘要"""
        from app.components.data_preview import DataPreview
        with st.expander("📊 数据概览", expanded=True):
            preview = DataPreview()
            preview.render_summary(df)
            preview.render_sample_data(df, rows=10)
```

## 12. 主入口设计

### 12.1 项目主入口

```python
# main.py
import streamlit as st
from app.run import AppOrchestrator


def main():
    """主函数"""
    try:
        # 创建并运行应用编排器
        orchestrator = AppOrchestrator()
        orchestrator.run()

    except Exception as e:
        st.error(f"系统启动失败: {str(e)}")
        st.exception(e)


if __name__ == "__main__":
    main()
```

## 13. 示例应用实现

### 13.1 合并应用示例

```python
# app/merge_extract/merge.py
import streamlit as st
import polars as pl
from app.base.base_app import BaseApp
from app.state.session_manager import SessionManager
from app.components.column_selector import ColumnSelector
from app.components.data_preview import DataPreview
from app.components.export_panel import ExportPanel


class MergeApp(BaseApp):
    def get_name(self) -> str:
        return "数据合并"

    def get_description(self) -> str:
        return "合并多个数据表为一个统一的数据表"

    def validate_input(self, data: pl.DataFrame) -> bool:
        """验证输入数据"""
        return data is not None and len(data) > 0

    def render(self) -> None:
        """渲染应用界面"""
        st.header("🔗 数据合并工具")
        st.markdown("将多个数据表合并为一个统一的数据表")

        processed_data = SessionManager.get_state('processed_data')
        if processed_data is None:
            st.warning("没有可用的数据")
            return

        tab1, tab2, tab3 = st.tabs(["📋 数据预览", "🎯 字段选择", "📤 导出数据"])

        with tab1:
            self._render_data_preview(processed_data)
        with tab2:
            selected_columns = self._render_column_selection(processed_data)
            SessionManager.set_state('selected_columns', selected_columns)
        with tab3:
            self._render_export_panel(processed_data)

    def _render_data_preview(self, df: pl.DataFrame):
        """渲染数据预览"""
        preview = DataPreview()
        st.subheader("📊 合并结果预览")
        with st.expander("📋 详细数据预览", expanded=False):
            preview.render_sample_data(df)
        with st.expander("📊 字段详情", expanded=False):
            preview.render_column_info(df)

    def _render_column_selection(self, df: pl.DataFrame):
        """渲染字段选择"""
        selector = ColumnSelector()
        return selector.render_with_preview(df)

    def _render_export_panel(self, df: pl.DataFrame):
        """渲染导出面板"""
        selected_columns = SessionManager.get_state('selected_columns')
        if not selected_columns:
            st.warning("请先在“字段选择”标签页中选择要导出的字段")
            return

        export_panel = ExportPanel()
        export_panel.render(df, selected_columns)

```

### 13.2 导出面板组件 (已优化)

```python
# app/components/export_panel.py
import streamlit as st
import polars as pl
from datetime import datetime
from app.handlers.export_handler import ExportHandler
from app.components.error_handler import ErrorHandler


class ExportPanel:
    def __init__(self):
        self.export_handler = ExportHandler()

    def render(self, df: pl.DataFrame, selected_columns: list[str]):
        """渲染导出面板"""
        st.subheader("📤 导出数据")

        default_filename = f"export_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        filename = st.text_input("文件名：", value=default_filename, help="不需要包含文件扩展名")

        # 导出格式固定为xlsx
        export_format = 'xlsx'

        export_summary = self.export_handler.get_export_summary(df, selected_columns)
        st.info(f"""
        **导出摘要：**
        - 总行数: {export_summary['total_rows']:,}
        - 总列数: {export_summary['total_columns']}
        - 预估大小: {export_summary['estimated_size']}
        """)

        with st.expander("📋 导出字段列表"):
            st.write(selected_columns)

        if st.button("🚀 生成导出文件", type="primary", use_container_width=True):
            self._handle_export(df, selected_columns, filename, export_format)

    def _handle_export(self, df: pl.DataFrame, columns: list[str], filename: str, file_format: str):
        """处理导出操作"""
        with st.spinner("正在生成导出文件..."):
            try:
                export_data = self.export_handler.export_excel(df, columns)
                download_filename = f"{filename}.{file_format}"

                # 直接显示下载按钮
                st.download_button(
                    label="💾 下载文件",
                    data=export_data,
                    file_name=download_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="download_button"
                )
                ErrorHandler.show_success("文件已生成，请点击上方按钮下载。")

            except Exception as e:
                ErrorHandler.show_error("导出失败", str(e))
```

## 14. 性能优化和最佳实践

### 14.1 缓存策略

```python
# 在主编排器（AppOrchestrator）中，将文件处理逻辑封装成一个可缓存的函数
# 注意: @st.cache_data 必须用于顶级函数或静态/类方法。
# 这里是其在类中应用的简化逻辑。

@st.cache_data(show_spinner="正在读取和处理文件...")
def cached_process_files(file_ids, preproc_options):
    """
    缓存文件加载和处理结果。
    file_ids: 文件唯一ID列表，确保文件内容改变时缓存失效。
    preproc_options: 预处理选项的元组，确保选项改变时缓存失效。
    """
    # ... 内部执行文件读取、合并、预处理的逻辑 ...
    # 返回处理好的 Polars DataFrame
    pass

# 在 AppOrchestrator 中调用
# file_ids = [f.id for f in uploaded_files]
# options = (is_process, is_dedup, is_clean)
# processed_data = cached_process_files(file_ids, options)
```

### 14.2 内存管理

```python
# 在处理大文件时的内存优化
def process_large_file(file_path, chunk_size=100000):
    """分块处理大文件，可使用Polars的scan_csv/scan_parquet"""
    # 使用流式处理，仅当内存不足时考虑
    # Polars本身对内存管理非常高效，通常不需要手动分块
    q = (
        pl.scan_csv(file_path)
        .filter(pl.col("value") > 10)
        .group_by("category")
        .agg(pl.all().sum())
    )
    # collect()会触发计算并加载到内存
    df = q.collect()
    return df
```

## 15. 总结

### 15.1 架构优势

- **模块化设计**: 每个组件职责单一，易于维护和扩展
- **依赖注入**: 降低组件间耦合，提高可测试性
- **插件化架构**: 支持动态加载新应用
- **统一接口**: 标准化的基础接口，便于扩展

### 15.2 用户体验

- **直观的UI**: 侧边栏控制，主内容区展示
- **友好的错误处理**: 完善的错误提示和异常处理
- **进度反馈**: 实时的处理进度显示
- **响应式设计**: 适配不同屏幕尺寸

### 15.3 性能优化

- **内存管理**: 智能的内存使用和优化
- **缓存机制**: 通过 `@st.cache_data` 减少重复计算
- **流水线处理**: 高效的数据处理流程
- **原生库性能**: 直接使用Polars进行IO操作，避免不必要的库间转换

### 15.4 可扩展性

- **应用注册系统**: 轻松添加新应用
- **配置管理**: 灵活的配置选项
- **插件系统**: 支持第三方扩展
- **标准化接口**: 便于集成新功能
