# Cloudflare R2 Django 文件管理系统

这是一个基于Django和Cloudflare R2的文件管理系统，提供文件上传、查看、下载和管理功能。

## 功能特点

- 文件上传：支持单文件和多文件上传
- 文件浏览：查看已上传的所有文件
- 文件下载：下载已上传的文件
- 文件管理：删除不需要的文件
- 文件预览：支持图片、文本等文件的在线预览
- 用户认证：基本的用户登录和权限管理

## 功能展示
<img src="https://alist.icenturyw.com/d/website_ali/img/20250314163622.png" alt="功能">
<img src="https://alist.icenturyw.com/d/website_ali/img/20250314164006.png" alt="功能">
<img src="https://alist.icenturyw.com/d/website_ali/img/20250314163946.png" alt="功能">


## 技术栈

- Django: Web框架
- Cloudflare R2: 对象存储服务
- django-storages: Django存储后端
- boto3: AWS S3兼容的Python SDK
- Bootstrap: 前端UI框架

## 安装和配置

### 前提条件

- Python 3.8+
- Cloudflare账户和R2存储桶
- R2 Access Key和Secret Key

### 安装步骤

1. 克隆仓库
```bash
git clone <repository-url>
cd cloudflare-r2-django
```

2. 创建虚拟环境并安装依赖
```bash
python -m venv venv
source venv/bin/activate  # 在Windows上使用: venv\Scripts\activate
pip install -r requirements.txt
```

3. 配置环境变量
创建`.env`文件并添加以下内容：
```
SECRET_KEY=your_django_secret_key
DEBUG=True
AWS_ACCESS_KEY_ID=your_r2_access_key
AWS_SECRET_ACCESS_KEY=your_r2_secret_key
AWS_STORAGE_BUCKET_NAME=your_r2_bucket_name
AWS_S3_ENDPOINT_URL=https://your_account_id.r2.cloudflarestorage.com
```

4. 运行数据库迁移
```bash
python manage.py migrate
```

5. 创建超级用户
```bash
python manage.py createsuperuser
```

6. 启动开发服务器
```bash
python manage.py runserver
```

## 使用方法

1. 访问 `http://localhost:8000/admin` 使用超级用户登录管理后台
2. 访问 `http://localhost:8000/files` 使用文件管理功能
   - 上传文件：点击"上传文件"按钮选择文件上传
   - 查看文件：在文件列表中查看所有已上传文件
   - 下载文件：点击文件名或下载按钮下载文件
   - 删除文件：点击删除按钮删除文件

## 项目结构

```
cloudflare_r2_django/
├── core/                  # 核心应用
│   ├── migrations/        # 数据库迁移文件
│   ├── templates/         # HTML模板
│   ├── admin.py           # 管理后台配置
│   ├── models.py          # 数据模型
│   ├── urls.py            # URL路由
│   ├── views.py           # 视图函数
│   └── ...
├── file_manager/          # 文件管理应用
│   ├── migrations/        # 数据库迁移文件
│   ├── templates/         # HTML模板
│   ├── admin.py           # 管理后台配置
│   ├── models.py          # 数据模型
│   ├── urls.py            # URL路由
│   ├── views.py           # 视图函数
│   └── ...
├── cloudflare_r2_django/  # 项目配置
│   ├── settings.py        # 项目设置
│   ├── urls.py            # 主URL路由
│   ├── wsgi.py            # WSGI配置
│   └── ...
├── static/                # 静态文件
├── media/                 # 本地媒体文件（开发环境）
├── manage.py              # Django管理脚本
├── requirements.txt       # 项目依赖
└── README.md              # 项目说明
```

## 配置说明

### Django设置

主要的R2存储配置位于`settings.py`：

```python
# Cloudflare R2存储设置
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL')
AWS_S3_REGION_NAME = 'auto'
AWS_S3_ADDRESSING_STYLE = 'virtual'
AWS_DEFAULT_ACL = 'private'
AWS_QUERYSTRING_AUTH = True
AWS_QUERYSTRING_EXPIRE = 3600  # 签名URL的过期时间（秒）
```

## 许可证

MIT

## 贡献

欢迎提交问题和拉取请求！

## 联系方式

如有任何问题，请联系项目维护者。 