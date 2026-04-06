# 3D Studio - 专业级CAD可视化与转换系统

## 项目简介

3D Studio 是一个专业级的 CAD 模型可视化与格式转换系统，基于 Flask 和 PythonOCC 开发。该系统提供了直观的 Web 界面，支持多种 3D 模型格式的转换、可视化和分析。

## 功能特性

### 核心功能
- **多格式支持**：支持 STEP、STP、IGES、IGS、STL、OBJ 等多种 3D 模型格式
- **格式转换**：在不同 3D 格式之间进行转换，包括 STL、OBJ、STEP、IGES、GLTF 等
- **3D 可视化**：使用 Three.js 实现高质量的 3D 模型渲染
- **模型分析**：计算模型的三角面数、几何面、边、顶点等信息
- **批量转换**：支持多个文件的批量转换，并打包为 ZIP 文件下载
- **STEP 转 BIN**：将 STEP 文件转换为 DGL 图格式，用于机器学习应用

### 界面特性
- **直观的 Web 界面**：现代化的响应式设计
- **材质与光照控制**：可调整模型颜色、金属感、粗糙度和环境光
- **视角控制**：支持旋转、缩放、自动旋转等操作
- **场景背景**：提供多种预设背景风格
- **截图功能**：可将当前视图保存为 PNG 图片

## 技术栈

### 后端
- Python 3
- Flask - Web 框架
- PythonOCC - CAD 模型处理库
- NumPy - 数值计算
- DGL (Deep Graph Library) - 用于 STEP 转 BIN 功能

### 前端
- HTML5 / CSS3
- JavaScript
- Three.js - 3D 渲染库
- Font Awesome - 图标库

## 安装指南

### 系统要求
- Python 3.7 或更高版本
- Windows 操作系统

### 依赖安装

```bash
pip install flask numpy OCC dgl torch
```



## 快速开始

1. 启动 Flask 服务器：

```bash
python main.py
```

2. 打开浏览器访问：

```
http://localhost:5000
```

## 使用说明

### 基本操作

1. **上传模型**：
   - 点击或拖拽文件到上传区域
   - 支持的格式：STEP、STP、IGES、IGS、STL、OBJ

2. **查看模型**：
   - 上传后模型会自动显示在 3D 视图中
   - 可以使用鼠标进行旋转、缩放操作

3. **调整参数**：
   - 材质设置：调整颜色、金属感、粗糙度
   - 光照设置：调整环境光强度
   - 背景设置：选择不同的背景风格

4. **分析模型**：
   - 系统会自动计算并显示模型的几何信息
   - 包括三角面数、几何面、边、顶点数量
   - 显示模型的尺寸信息

5. **格式转换**：
   - 点击顶部导航栏的"格式转换"按钮
   - 上传文件并选择目标格式
   - 点击"转换"按钮下载转换后的文件

### 批量转换

1. 点击"格式转换"页面
2. 选择"批量上传"选项
3. 选择多个文件（支持的格式）
4. 选择目标格式
5. 点击"批量转换"按钮
6. 系统会生成一个 ZIP 文件包含所有转换后的文件

### STEP 转 BIN（用于机器学习）

1. 点击"格式转换"页面
2. 选择"STEP 转 BIN"选项
3. 上传 STEP 文件
4. 点击"转换"按钮
5. 系统会生成一个 BIN 文件，包含模型的图结构信息

## API 文档

### 健康检查

```
GET /api/health
```

返回系统状态信息。

### 获取示例模型

```
GET /api/sample?type=<shape_type>
```

- `shape_type`：可选值为 box、sphere、cylinder、cone、torus、wedge、prism
- 返回：STL 格式的示例模型文件

### 上传并转换文件

```
POST /api/upload
```

- Form 数据：
  - `file`：要上传的文件
  - `output_format`：目标格式（stl、obj、step、gltf、igs）
  - `linear_deflection`：线性偏差（默认 0.1）
  - `angular_deflection`：角度偏差（默认 0.5）
- 返回：转换后的文件

### 批量上传并转换

```
POST /api/batch-upload
```

- Form 数据：
  - `files`：多个要上传的文件
  - `output_format`：目标格式
  - `linear_deflection`：线性偏差
  - `angular_deflection`：角度偏差
- 返回：包含所有转换后文件的 ZIP 文件

### STEP 转 BIN

```
POST /api/step-to-bin
```

- Form 数据：
  - `file`：要上传的 STEP 文件
- 返回：DGL 图格式的 BIN 文件

### 获取模型信息

```
POST /api/model-info
```

- Form 数据：
  - `file`：要分析的文件
- 返回：包含模型几何信息的 JSON

## 注意事项

1. **文件大小限制**：单个文件大小限制为 100MB

2. **格式支持**：
   - 输入格式：STEP、STP、IGES、IGS、STL
   - 输出格式：STL、OBJ、STEP、IGES、GLTF、3MF

3. **3MF 格式**：由于 3MF 格式的复杂性，系统会生成 STL 内容但使用 .3mf 扩展名，建议使用专业工具进行进一步转换

4. **性能考虑**：
   - 大型模型可能需要较长的处理时间
   - 建议在性能较好的机器上运行

5. **错误处理**：
   - 如果转换失败，系统会尝试回退到 STL 格式
   - 详细错误信息会记录在日志中

## 故障排除

### 常见问题

1. **后端未启动**：
   - 确保已运行 `python main.py`
   - 检查端口 5000 是否被占用

2. **模型加载失败**：
   - 检查文件格式是否受支持
   - 检查文件大小是否超过限制
   - 查看浏览器控制台的错误信息

3. **转换失败**：
   - 检查模型是否有几何错误
   - 尝试调整线性偏差和角度偏差参数

4. **STEP 转 BIN 失败**：
   - 确保已安装 DGL 和 PyTorch
   - 检查 STEP 文件是否有效

## 许可证

本项目采用 MIT 许可证。

## 贡献

欢迎提交问题和改进建议！

---

**3D Studio** - 专业级 CAD 可视化与转换系统

© 2026 版权所有