# Image to PDF Converter

A FastAPI-based tool for converting images to PDF while preserving original aspect ratio and quality.

## Features

✔️ Supports JPEG/PNG/GIF/BMP formats  
✔️ Maintains original image aspect ratio  
✔️ Auto-adjusts page orientation (Portrait/Landscape)  
✔️ Web-based interface  
✔️ RESTful API endpoint  
✔️ Cross-platform support (Windows/macOS/Linux)

## Quick Start

### Prerequisites

- Python 3.7+
- Pillow
- ReportLab
- FastAPI

### Install Dependencies

```bash
pip install fastapi uvicorn python-multipart pillow reportlab
```

### Run Service

```bash
python main.py
```

The service will automatically open your browser at: http://localhost:9041

## Usage

### Web Interface

1. Visit http://localhost:9041
2. Click "Choose Image Files" to upload images
3. Confirm file list and click "Convert"
4. Download generated PDF automatically

![image](https://github.com/user-attachments/assets/99742a8a-83c8-4cdf-9ec6-57abbf1307f5)

### API Documentation

**Endpoint**  
`POST /convert-to-pdf`

**Request Format**  

- Content-Type: `multipart/form-data`
- Body: Image files array (field name `files`)

**cURL Example**

```bash
curl -X POST "http://localhost:9041/convert-to-pdf" \
  -F "files=@image1.jpg" \
  -F "files=@image2.png" \
  --output result.pdf
```

**Python Example**

```python
import requests

url = "http://localhost:9041/convert-to-pdf"
files = [('files', open('image.jpg', 'rb'))]
response = requests.post(url, files=files)

with open('output.pdf', 'wb') as f:
    f.write(response.content)
```

**Response**

- Success: PDF file (application/pdf)
- Error: JSON error message

**Status Codes**

- 200 OK: Conversion successful
- 400 Bad Request: Invalid file type
- 500 Internal Server Error: Processing failure

## Configuration

### Change Port

```python
uvicorn.run(app, host="127.0.0.1", port=9041)  # Modify port value
```

### Supported File Types

```python
allowed_types = {'image/jpeg', 'image/png', 'image/gif', 'image/bmp'}
```

### Page Size Adjustment

```python
width, height = letter  # Default A4 size
```

## Notes

1. Recommended maximum 50 images per conversion
2. Large images (>5000x5000px) may affect performance
3. Transparent images will be converted to white background
4. PDF page size determined by first image's aspect ratio

## Contributing

We welcome issues and PRs! Please follow these guidelines:

1. Create feature branches for new developments
2. Maintain consistent code style
3. Add relevant unit tests
4. Update documentation accordingly
