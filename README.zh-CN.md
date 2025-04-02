# 图片转PDF转换器

一个基于FastAPI的图片转PDF转换工具，支持网页界面和API调用，保持原始宽高比和图片质量。

## 功能特性

✅ 支持JPEG/PNG/GIF/BMP格式转换  
✅ 保持原始图片宽高比  
✅ 自动适配页面方向（纵向/横向）  
✅ 网页可视化操作界面  
✅ 提供RESTful API接口  
✅ 跨平台支持（Windows/macOS/Linux）

## 快速开始

### 环境要求

- Python 3.7+
- Pillow
- ReportLab
- FastAPI

### 安装依赖

```bash
pip install fastapi uvicorn python-multipart pillow reportlab
```

### 启动服务

```bash
python main.py
```

服务启动后会自动打开浏览器访问：http://localhost:9041

## 使用方法

### 网页界面

1. 访问 http://localhost:9041
2. 点击"选择图片文件"按钮上传图片
3. 确认文件列表后点击"开始转换"
4. 自动下载生成的PDF文件
![image](https://github.com/user-attachments/assets/99742a8a-83c8-4cdf-9ec6-57abbf1307f5)


### API调用

**端点**  
`POST /convert-to-pdf`

**请求格式**  

- Content-Type: `multipart/form-data`
- Body: 图片文件数组（字段名`files`）

**示例（cURL）**

```bash
curl -X POST "http://localhost:9041/convert-to-pdf" \
  -F "files=@image1.jpg" \
  -F "files=@image2.png" \
  --output result.pdf
```

**示例（Python）**

```python
import requests

url = "http://localhost:9041/convert-to-pdf"
files = [('files', open('image.jpg', 'rb'))]
response = requests.post(url, files=files)

with open('output.pdf', 'wb') as f:
    f.write(response.content)
```

**响应参数**

- 成功：返回PDF文件（application/pdf）
- 失败：返回JSON错误信息

**状态码**

- 200 OK：转换成功
- 400 Bad Request：无效文件类型
- 500 Internal Server Error：处理失败

## 高级配置

### 修改服务端口

```python
uvicorn.run(app, host="127.0.0.1", port=9041)  # 修改port参数
```

### 支持的文件类型

```python
allowed_types = {'image/jpeg', 'image/png', 'image/gif', 'image/bmp'}
```

### 页面尺寸调整

```python
width, height = letter  # 默认使用A4尺寸
```

## 注意事项

1. 建议单次转换不超过50张图片
2. 超大图片（超过5000x5000像素）可能影响生成速度
3. 透明背景图片会自动转换为白色背景
4. 输出PDF页面尺寸基于第一张图片的比例

## 贡献指南

欢迎提交Issue和PR！建议遵循以下规范：

1. 新功能开发请创建特性分支
2. 保持代码风格统一
3. 添加必要的单元测试
4. 更新相关文档说明

