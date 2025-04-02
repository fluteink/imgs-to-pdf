import logging
import threading
import time
import webbrowser
from io import BytesIO
import uvicorn
from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

app = FastAPI()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTML前端页面
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>图片转PDF转换器</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }

        .container {
            border: 2px dashed #ccc;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }

        #file-input {
            display: none;
        }

        .upload-btn {
            background-color: #4CAF50;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px;
        }

        .upload-btn:hover {
            background-color: #45a049;
        }

        #file-list {
            margin: 20px 0;
            text-align: left;
        }

        #status {
            margin-top: 20px;
            color: #666;
        }

        .loading {
            display: none;
            margin: 20px 0;
        }

        .error {
            color: #ff4444;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>图片转PDF转换器</h2>

        <input type="file" id="file-input" multiple accept="image/*">
        <button class="upload-btn" onclick="document.getElementById('file-input').click()">
            选择图片文件
        </button>

        <div id="file-list"></div>

        <div class="loading" id="loading">
            <img src="https://cdnjs.cloudflare.com/ajax/libs/galleriffic/2.0.1/css/loader.gif" alt="加载中...">
            <p>正在生成PDF，请稍候...</p>
        </div>

        <button class="upload-btn" onclick="uploadFiles()" id="convert-btn" disabled>
            开始转换
        </button>

        <div id="status"></div>
        <div class="error" id="error"></div>
    </div>

    <script>
        let selectedFiles = [];

        // 文件选择处理
        document.getElementById('file-input').addEventListener('change', function(e) {
            selectedFiles = Array.from(e.target.files);
            updateFileList();
            document.getElementById('convert-btn').disabled = selectedFiles.length === 0;
        });

        // 更新文件列表显示
        function updateFileList() {
            const fileList = document.getElementById('file-list');
            fileList.innerHTML = '<strong>已选文件：</strong>';

            selectedFiles.forEach((file, index) => {
                fileList.innerHTML += `
                    <div>
                        ${index + 1}. ${file.name}
                        <span style="color: #666;">(${(file.size/1024).toFixed(1)}KB)</span>
                    </div>
                `;
            });
        }

        // 上传文件
        async function uploadFiles() {
            const loading = document.getElementById('loading');
            const status = document.getElementById('status');
            const error = document.getElementById('error');

            if (selectedFiles.length === 0) {
                showError('请先选择至少一个图片文件');
                return;
            }

            try {
                // 显示加载状态
                loading.style.display = 'block';
                status.textContent = '';
                error.textContent = '';

                // 准备表单数据
                const formData = new FormData();
                selectedFiles.forEach(file => {
                    formData.append('files', file);
                });

                // 发送请求
                const response = await fetch('/convert-to-pdf', {
                    method: 'POST',
                    body: formData
                });

                // 处理响应
                if (response.ok) {
                    const pdfBlob = await response.blob();
                    downloadPDF(pdfBlob);
                    status.textContent = 'PDF生成成功！';
                } else {
                    const errorData = await response.json();
                    showError(`转换失败：${errorData.detail || response.statusText}`);
                }
            } catch (err) {
                showError(`请求失败：${err.message}`);
            } finally {
                loading.style.display = 'none';
            }
        }

        // 下载PDF
        function downloadPDF(blob) {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'converted.pdf';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }

        // 显示错误信息
        function showError(message) {
            document.getElementById('error').textContent = message;
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    return HTML_CONTENT

@app.post("/convert-to-pdf")
async def convert_images_to_pdf(files: list[UploadFile] = File(...)):
    # 验证文件类型
    allowed_types = {'image/jpeg', 'image/png', 'image/gif', 'image/bmp'}
    for file in files:
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type} for {file.filename}"
            )

    # 创建内存PDF缓冲区
    pdf_buffer = BytesIO()
    try:
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        width, height = letter

        for index, file in enumerate(files):
            try:
                # 读取文件内容
                contents = await file.read()
                img_buffer = BytesIO(contents)

                # 处理图片
                with Image.open(img_buffer) as img:
                    # 转换RGBA格式
                    if img.mode == 'RGBA':
                        img = img.convert('RGB')

                    # 计算尺寸比例
                    img_width, img_height = img.size
                    aspect_ratio = img_height / img_width

                    # 调整页面尺寸
                    if aspect_ratio > height / width:
                        new_height = height
                        new_width = int(new_height / aspect_ratio)
                    else:
                        new_width = width
                        new_height = int(new_width * aspect_ratio)

                    # 处理分页
                    if index != 0:
                        c.showPage()

                    # 设置页面并绘制图片
                    c.setPageSize((new_width, new_height))
                    img_reader = ImageReader(img)
                    c.drawImage(img_reader, 0, 0, width=new_width, height=new_height)

            except Exception as e:
                logging.error(f"Error processing {file.filename}: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to process {file.filename}: {str(e)}"
                )

        c.save()
        pdf_buffer.seek(0)

        # 返回PDF文件
        return Response(
            content=pdf_buffer.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=converted.pdf"}
        )

    except Exception as e:
        logging.error(f"PDF generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="PDF generation failed")
def open_browser():
    # 等待服务器启动
    time.sleep(1)
    # 打开浏览器
    webbrowser.open("http://localhost:9041")

if __name__ == "__main__":
    # 在启动服务器前创建并启动浏览器线程
    threading.Thread(target=open_browser).start()
    uvicorn.run(app, host="127.0.0.1", port=9041)