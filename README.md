# 3D Studio

一个功能强大的3D模型查看和转换工具，支持多种3D文件格式的上传、预览、分析和转换。

---

# 3D Studio

A powerful 3D model viewing and conversion tool that supports uploading, previewing, analyzing, and converting multiple 3D file formats.

---

![image](https://github.com/BrepMaster/3D-Studio/raw/main/1.png)

## ✨ 功能特性 | Features

### 核心功能 | Core Features
- **模型上传**：支持拖拽上传和点击上传，优化的文件上传流程
- **模型上传** | **Model Upload**: Support drag-and-drop and click upload with optimized file upload process
- **3D预览**：实时渲染3D模型，支持流畅的旋转、缩放、平移操作
- **3D预览** | **3D Preview**: Real-time 3D model rendering with smooth rotation, zoom, and pan operations
- **模型信息快速查看**：无需完全加载模型，即可快速查看文件大小、格式、大致尺寸等基本信息
- **模型信息快速查看** | **Quick Model Info**: View basic information such as file size, format, and dimensions without fully loading the model
- **模型分析**：显示三角面数、几何面、边、顶点数量和模型尺寸
- **模型分析** | **Model Analysis**: Display triangle count, geometry faces, edges, vertices count, and model dimensions
- **物理属性分析**：计算模型体积、表面积、重心和惯性矩
- **物理属性分析** | **Physical Properties Analysis**: Calculate volume, surface area, center of mass, and moment of inertia
- **质量评估报告**：评估模型质量，提供改进建议
- **质量评估报告** | **Quality Assessment Report**: Evaluate model quality and provide improvement suggestions
- **材质调整**：修改模型颜色、金属感、粗糙度
- **材质调整** | **Material Adjustment**: Modify model color, metallicness, and roughness
- **灯光控制**：调整环境光强度，切换阴影效果
- **灯光控制** | **Lighting Control**: Adjust ambient light intensity and toggle shadow effects
- **背景设置**：多种背景风格选择
- **背景设置** | **Background Settings**: Multiple background style options
- **剖切平面**：支持X、Y、Z轴的模型剖切，实时预览剖切效果，可导出剖切图片
- **剖切平面** | **Section Plane**: Support X, Y, Z axis sectioning with real-time preview and export
- **文件历史**：保存最近20个模型文件，支持缩略图预览
- **文件历史** | **File History**: Save last 20 model files with thumbnail preview
- **历史记录搜索**：支持按文件名和格式搜索历史记录
- **历史记录搜索** | **History Search**: Search history by filename and format
- **历史模型版本管理**：自动跟踪文件版本，支持查看和加载历史版本
- **历史模型版本管理** | **Version Management**: Auto-track file versions with view and load support
- **历史记录导出备份**：支持导出和备份历史记录，以及从备份恢复
- **历史记录导出备份** | **History Export & Backup**: Support export, backup, and restore of history records
- **格式转换**：支持多种3D格式之间的转换
- **格式转换** | **Format Conversion**: Convert between multiple 3D formats
- **批量转换**：支持多个文件的批量转换
- **批量转换** | **Batch Conversion**: Batch convert multiple files
- **STEP转BIN**：将STEP文件转换为BIN格式（用于机器学习）
- **STEP转BIN** | **STEP to BIN**: Convert STEP files to BIN format (for machine learning)
- **暗色模式**：支持亮色/暗色主题切换，自动记忆用户偏好
- **暗色模式** | **Dark Mode**: Light/dark theme toggle with auto-save preference
- **12节气主题**：提供12个节气对应的柔和主题配色
- **12节气主题** | **Solar Terms Themes**: 12 soft color themes based on Chinese solar terms
- **布局设置**：支持控制面板位置调整（右侧、左侧、底部），透明度和宽度调整，自动记忆用户偏好
- **布局设置** | **Layout Settings**: Control panel position adjustment (right, left, bottom), transparency, width with auto-save
- **三视图**：自动生成模型的前视、顶视、右视三个视角的缩略图，支持悬停缩放和点击下载
- **三视图** | **Orthographic Views**: Auto-generate front, top, right view thumbnails with hover zoom and download

### 支持的格式 | Supported Formats
- **输入格式**：STEP (.step, .stp)、IGES (.iges, .igs)、STL (.stl)、OBJ (.obj)、3MF (.3mf)
- **输入格式** | **Input Formats**: STEP (.step, .stp), IGES (.iges, .igs), STL (.stl), OBJ (.obj), 3MF (.3mf)
- **输出格式**：STL、OBJ、STEP、IGES、GLTF、BIN
- **输出格式** | **Output Formats**: STL, OBJ, STEP, IGES, GLTF, BIN

---

## 🛠️ 安装要求 | Installation Requirements

### 系统要求 | System Requirements
- Windows 10/11
- Python 3.7+
- 浏览器：Chrome 90+ / Firefox 88+ / Edge 90+
- Browser: Chrome 90+ / Firefox 88+ / Edge 90+

### 依赖包 | Dependencies
```bash
# 基础依赖 | Basic dependencies
pip install Flask pythonocc-core numpy

# 可选依赖（用于STEP转BIN功能） | Optional dependencies (for STEP to BIN)
pip install dgl torch occwl networkx

# 缩略图生成依赖 | Thumbnail generation
pip install Pillow
```

---

## 🚀 快速开始 | Quick Start

### 1. 克隆项目 | Clone Repository
```bash
git clone <repository-url>
cd 3D-Studio
```

### 2. 安装依赖 | Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. 启动服务器 | Start Server
```bash
python main.py
```

### 4. 访问应用 | Access Application
在浏览器中打开 | Open in browser:
```
http://localhost:5000
```

---

## 📖 使用指南 | Usage Guide

### 上传模型 | Upload Model
1. 拖拽文件到上传区域，或点击上传区域选择文件 | Drag file to upload area or click to select file
2. 等待模型加载完成 | Wait for model to load
3. 模型会自动显示在3D视图中 | Model will display in 3D view automatically

### 3D视图操作 | 3D View Controls
- **鼠标左键**：旋转模型 | **Left Click**: Rotate model
- **鼠标右键**：平移模型 | **Right Click**: Pan model
- **鼠标滚轮**：缩放模型 | **Mouse Wheel**: Zoom model
- **R键**：重置视角 | **R Key**: Reset view
- **C键**：清除模型 | **C Key**: Clear model
- **W键**：切换线框模式 | **W Key**: Toggle wireframe mode
- **A键**：切换自动旋转 | **A Key**: Toggle auto-rotate
- **F键**：全屏模式 | **F Key**: Fullscreen mode
- **S键**：加载示例模型 | **S Key**: Load sample model

### 剖切平面 | Section Plane
1. 在左侧控制面板中找到"剖切平面"功能区 | Find "Section Plane" panel on the left
2. 点击开关按钮启用/禁用相应轴（X、Y、Z）的剖切 | Click toggle to enable/disable axis (X, Y, Z)
3. 使用滑块调整剖切位置（-100% 到 +100%） | Use slider to adjust section position (-100% to +100%)
4. 状态标签会实时显示当前剖切状态（已启用/已禁用） | Status label shows current section state
5. 点击"导出剖切"按钮将当前剖切状态保存为PNG图片 | Click "Export Section" to save as PNG
6. 点击"重置所有剖切"按钮恢复默认状态 | Click "Reset All" to restore default

### 文件历史记录 | File History
1. 点击顶部导航栏的"文件历史"按钮 | Click "History" button in top navigation
2. 查看最近加载的模型列表，每个记录都有缩略图预览 | View recently loaded models with thumbnails
3. 点击历史记录项重新加载模型 | Click history item to reload model
4. 点击删除按钮删除单个历史记录 | Click delete button to remove single record
5. 点击"清空"按钮删除所有历史记录 | Click "Clear All" to delete all records

### 历史记录搜索和过滤 | History Search & Filter
1. 在历史记录面板中，使用搜索框输入关键词搜索历史记录 | Use search box to find records
2. 使用格式过滤器按文件格式过滤历史记录 | Use format filter to sort by format
3. 点击"重置"按钮清除搜索和过滤条件 | Click "Reset" to clear filters

### 历史模型版本管理 | Version Management
1. 在历史记录面板中，点击文件旁边的版本图标查看版本历史 | Click version icon next to file
2. 在版本历史模态框中，查看文件的所有版本 | View all versions in modal
3. 点击特定版本加载该版本的模型 | Click specific version to load

### 历史记录导出和备份 | History Export & Backup
1. 在历史记录面板中，点击"导出"按钮导出历史记录 | Click "Export" to export history
2. 点击"备份"按钮备份所有历史记录 | Click "Backup" to backup all records
3. 点击"恢复"按钮从备份文件恢复历史记录 | Click "Restore" to restore from backup

### 暗色模式 | Dark Mode
1. 点击顶部导航栏的"暗色模式"按钮切换主题 | Click "Dark Mode" button to toggle theme
2. 系统会自动记忆你的主题偏好 | System auto-saves your preference
3. 3D场景背景会随主题自动调整 | 3D scene background adjusts with theme

### 12节气主题 | Solar Terms Themes
1. 点击顶部导航栏的"更多"按钮 | Click "More" button in navigation
2. 选择"主题"打开主题设置面板 | Select "Themes" to open panel
3. 选择12个节气主题中的任意一个 | Choose from 12 solar term themes
4. 主题会立即应用并自动保存 | Theme applies immediately and auto-saves
5. 刷新浏览器后会恢复到默认亮色主题 | Refresh browser to return to default light theme

### 布局设置 | Layout Settings
1. 点击顶部导航栏的"更多"按钮 | Click "More" button in navigation
2. 选择"布局"打开布局设置面板 | Select "Layout" to open panel
3. 选择控制面板的位置：右侧（默认）、左侧或底部 | Choose panel position: Right (default), Left, or Bottom
4. 调整控制面板的透明度和宽度 | Adjust panel transparency and width
5. 点击"保存"按钮保存布局设置 | Click "Save" to save settings
6. 点击"重置"按钮恢复默认布局 | Click "Reset" to restore default
7. 系统会自动记忆你的布局偏好 | System auto-saves your preference

### 快捷键 | Keyboard Shortcuts
1. 点击顶部导航栏的"更多"按钮 | Click "More" button in navigation
2. 选择"快捷键"查看所有可用的快捷键 | Select "Shortcuts" to view all shortcuts
3. 点击"自定义快捷键"按钮进入自定义面板 | Click "Customize" to enter panel
4. 按照提示修改快捷键 | Follow prompts to modify shortcuts
5. 点击"保存"按钮保存设置 | Click "Save" to save

### 帮助 | Help
1. 点击顶部导航栏的"更多"按钮 | Click "More" button in navigation
2. 选择"帮助"查看使用指南 | Select "Help" to view guide
3. 帮助面板会显示详细的功能说明和操作步骤 | Help panel shows detailed instructions

### 格式转换 | Format Conversion
1. 点击顶部导航栏的"格式转换"按钮 | Click "Convert" button in navigation
2. 上传模型文件 | Upload model file
3. 选择目标格式（支持 STL、OBJ、STEP、IGES、GLTF、BIN） | Select target format
4. 点击"开始转换"按钮 | Click "Convert" button
5. 下载转换后的文件 | Download converted file

### 批量转换 | Batch Conversion
1. 进入格式转换页面 | Go to conversion page
2. 选择多个模型文件 | Select multiple files
3. 选择目标格式 | Select target format
4. 选择下载方式（单独下载或压缩包下载） | Choose download method (individual or ZIP)
5. 点击"开始转换"按钮 | Click "Convert" button
6. 下载转换后的文件或ZIP包 | Download files or ZIP package

---

## 🔧 API文档 | API Documentation

### 健康检查 | Health Check
- **GET /api/health** - 检查系统状态 | Check system status

### 示例模型 | Sample Models
- **GET /api/sample?type=box** - 获取示例立方体模型 | Get sample box model
- **GET /api/sample?type=cylinder** - 获取示例圆柱体模型 | Get sample cylinder model
- **GET /api/sample?type=sphere** - 获取示例球体模型 | Get sample sphere model

### 历史记录 | History
- **GET /api/history** - 获取历史记录列表 | Get history list
- **GET /api/history/search** - 搜索和过滤历史记录 | Search and filter history
- **GET /api/history/versions/<filename>** - 获取文件的版本历史 | Get file version history
- **GET /api/history/version/<filename>/<version>** - 获取文件的特定版本 | Get specific version
- **GET /api/history/<id>** - 下载历史模型文件 | Download history model file
- **GET /api/history/thumbnail/<id>** - 获取历史模型缩略图 | Get history thumbnail
- **POST /api/history/save** - 保存文件到历史记录 | Save file to history
- **POST /api/history/export** - 导出历史记录 | Export history
- **GET /api/history/backup** - 备份历史记录 | Backup history
- **POST /api/history/restore** - 从备份恢复历史记录 | Restore from backup
- **DELETE /api/history/<id>** - 删除单个历史记录 | Delete single history record
- **DELETE /api/history** - 清空所有历史记录 | Clear all history

### 模型转换 | Model Conversion
- **POST /api/upload** - 上传和转换模型（支持 STL、OBJ、STEP、IGES、GLTF、BIN 格式） | Upload and convert model
- **POST /api/model-info** - 获取模型信息 | Get model info
- **POST /api/model-info-quick** - 快速获取模型基本信息（无需完全加载模型） | Get quick model info
- **POST /api/model-physical** - 获取模型物理属性 | Get physical properties
- **POST /api/model-quality** - 获取模型质量评估报告 | Get quality report
- **POST /api/convert-settings** - 保存转换设置 | Save conversion settings
- **POST /api/batch-upload** - 批量上传和转换模型 | Batch upload and convert

### 剖切功能 | Section
- **POST /api/section-slice** - 获取剖切切片数据 | Get section slice data
- **POST /api/section-export** - 导出剖切后模型 | Export sectioned model

---

## 📁 项目结构 | Project Structure

```
3D-Studio/
├── app/                    # 应用核心模块 | Application core
│   ├── __init__.py          # 应用包初始化 | Package init
│   ├── routes.py            # Flask 路由定义 | Flask routes
│   ├── temp_file_manager.py # 临时文件管理器 | Temp file manager
│   ├── config/              # 配置模块 | Config module
│   │   ├── __init__.py       # 配置模块入口 | Config init
│   │   ├── app_config.py     # 应用配置 | App config
│   │   ├── file_config.py    # 文件路径配置 | File path config
│   │   └── logging_config.py # 日志配置 | Logging config
│   ├── api/                # API 蓝图模块 | API blueprint
│   │   ├── __init__.py       # API 模块入口 | API init
│   │   ├── conversion.py     # 文件转换 API | Conversion API
│   │   ├── history.py        # 历史记录 API | History API
│   │   ├── model.py          # 模型分析 API | Model API
│   │   └── section.py        # 剖切功能 API | Section API
│   ├── core/               # 核心功能模块 | Core module
│   │   ├── __init__.py       # 核心模块入口 | Core init
│   │   ├── readers.py        # 文件读取模块 | File readers
│   │   ├── readers_3mf.py    # 3MF 文件读取模块 | 3MF reader
│   │   ├── exporters.py      # 文件导出模块 | File exporters
│   │   └── section.py        # 剖切功能核心 | Section core
│   ├── repository/         # 数据访问层 | Repository layer
│   │   ├── __init__.py       # 数据访问层入口 | Repository init
│   │   └── history_repo.py   # 历史记录数据访问 | History repo
│   ├── services/           # 业务逻辑层 | Service layer
│   │   ├── __init__.py       # 服务层入口 | Service init
│   │   ├── conversion_service.py # 转换服务 | Conversion service
│   │   ├── history_service.py    # 历史记录服务 | History service
│   │   ├── model_service.py      # 模型分析服务 | Model service
│   │   └── section_service.py    # 剖切服务 | Section service
│   └── utils/              # 工具函数模块 | Utils module
│       ├── __init__.py       # 工具模块入口 | Utils init
│       ├── file_utils.py     # 文件工具函数 | File utilities
│       ├── response_utils.py # 响应工具函数 | Response utilities
│       └── task_utils.py     # 任务工具函数 | Task utilities
├── templates/              # HTML 模板 | HTML templates
│   ├── index.html          # 主页面模板 | Main page
│   └── convert.html        # 格式转换页面模板 | Conversion page
├── history/                # 历史记录文件存储目录 | History storage
├── tests/                  # 测试文件目录 | Tests
│   ├── __init__.py          # 测试模块入口 | Tests init
│   ├── conftest.py          # 测试配置 | Test config
│   ├── test_history.py      # 历史记录模块测试 | History tests
│   └── test_validators.py   # 验证器模块测试 | Validator tests
├── main.py                 # 应用入口文件 | Entry file
├── requirements.txt        # 依赖列表 | Dependencies
├── TESTING.md              # 功能测试文档 | Testing documentation
└── README.md               # 项目说明文档 | README
```

### 模块说明 | Module Description

| 模块 | 说明 | 主要功能 |
|------|------|----------|
| `app/config/` | 配置管理 | 应用配置、日志配置、文件路径配置 |
| `app/config/` | Config Management | App config, logging config, file path config |
| `app/api/` | REST API | 提供 RESTful API 接口 |
| `app/api/` | REST API | Provide RESTful API endpoints |
| `app/core/` | 核心功能 | 文件读写、格式转换、剖切算法 |
| `app/core/` | Core Features | File I/O, format conversion, section algorithm |
| `app/repository/` | 数据访问 | 历史记录持久化操作 |
| `app/repository/` | Data Access | History persistence operations |
| `app/services/` | 业务逻辑 | 协调各模块，处理业务流程 |
| `app/services/` | Business Logic | Coordinate modules, handle workflows |
| `app/utils/` | 工具函数 | 通用工具方法 |
| `app/utils/` | Utilities | Common utility functions |

---

## 📝 注意事项 | Notes

1. **文件大小限制**：单个文件大小限制为 100MB | **File Size Limit**: 100MB per file
2. **性能考虑**：大型模型可能需要较长的处理时间 | **Performance**: Large models may take time to process
3. **错误处理**：如果转换失败，系统会尝试回退到 STL 格式 | **Error Handling**: Falls back to STL if conversion fails
4. **浏览器兼容性**：建议使用 Chrome、Firefox 或 Edge | **Browser Compatibility**: Chrome, Firefox, or Edge recommended
5. **历史记录**：系统自动保存最近20个模型文件 | **History**: Auto-saves last 20 model files
6. **BIN格式转换**：需要安装 dgl、torch、occwl、networkx 依赖包 | **BIN Conversion**: Requires dgl, torch, occwl, networkx

---

## 🤝 贡献指南 | Contributing

1. Fork 本项目 | Fork the project
2. 创建功能分支 | Create feature branch (`git checkout -b feature/AmazingFeature`)
3. 提交更改 | Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 | Push to branch (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request | Open Pull Request

---

## 📄 许可证 | License

本项目采用 MIT 许可证 - 详情请参阅 LICENSE 文件 | This project is licensed under the MIT License - see LICENSE file for details

---

## 📞 联系信息 | Contact

- 作者：<BrepMaster> | Author: <BrepMaster>

---

**享受 3D 模型查看和转换的乐趣！** 🎉
**Enjoy 3D model viewing and conversion!** 🎉
