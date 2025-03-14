# Cloudflare R2 Django 文件管理系统

这是一个基于Django和Cloudflare R2的文件管理系统，提供文件上传、查看、下载和管理功能。

## 功能特点

- 文件上传：支持单文件和多文件上传
- 文件浏览：查看已上传的所有文件
- 文件下载：下载已上传的文件
- 文件管理：删除不需要的文件
- 文件预览：支持图片、PDF等文件的在线预览
- 用户认证：基本的用户登录和权限管理

## 功能展示
<img src="https://alist.icenturyw.com/d/website/20250314163622.png" alt="功能">
<img src="https://alist.icenturyw.com/d/website/20250314164006.png" alt="功能">
<img src="https://alist.icenturyw.com/d/website/20250314163946.png" alt="功能">


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

## 最近更新

### 2025-03-14
- 修复了模板语法错误：
  - 问题：在模板中使用 `startswith` 方法导致 `TemplateSyntaxError: Unused 'image/' at end of if expression` 错误
  - 解决方案：使用 Django 模板过滤器 `slice` 替代 Python 的 `startswith` 方法，例如 `content_type|slice:":6" == 'image/'`
- 修复了文件预览功能在使用Cloudflare R2存储时的错误：
  - 问题：当使用R2存储时，`file.file.path`方法不可用，导致`NotImplementedError: This backend doesn't support absolute paths.`错误
  - 解决方案：修改了`file_preview`和`serve_file`视图，使用文件URL而不是本地路径
  - 更新了模板以直接使用文件URL进行预览和下载
- 修复了Django DeleteView警告：将FileDeleteView和CategoryDeleteView中的自定义删除逻辑从delete()方法移至form_valid()方法，符合Django最佳实践。
- 原因：Django的DeleteView使用FormMixin处理POST请求，因此任何自定义删除逻辑应该放在form_valid()方法中，而不是delete()方法中。

### 2025-03-14
- 修复了文件删除功能的问题：
  - 问题：删除文件时只从数据库中删除了记录，但没有从Cloudflare R2存储桶中删除实际文件
  - 解决方案：
    - 修改了`FileDeleteView`类的`form_valid`方法，添加了从R2存储桶删除文件的逻辑
    - 修改了`CategoryDeleteView`类的`form_valid`方法，确保在删除分类时也删除关联的文件
    - 修改了`FileUpdateView`类的`form_valid`方法，确保在更新文件时，如果上传了新文件，旧文件会被删除
  - 实现方式：使用Django Storage API的`delete`方法删除存储中的文件

## 注意事项

### 使用Cloudflare R2存储的限制

当使用Cloudflare R2作为存储后端时，有一些需要注意的限制：

1. **无法使用本地文件路径**：R2存储不支持`path()`方法，因此不能使用`file.file.path`获取文件的本地路径
2. **文本文件预览限制**：由于无法直接读取R2存储中的文本内容，文本文件预览功能有限制
3. **文件操作**：所有文件操作都需要通过URL进行，而不是本地文件系统操作

### 最佳实践

1. 始终使用`file.file.url`获取文件URL，而不是`file.file.path`
2. 对于需要读取文件内容的操作，考虑使用临时下载或流式处理
3. 确保正确配置R2存储的访问权限和URL过期时间 