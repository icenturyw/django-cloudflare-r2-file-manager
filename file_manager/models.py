from django.db import models
from django.utils import timezone
from django.urls import reverse
import os
import uuid

def get_file_path(instance, filename):
    """生成唯一的文件路径，避免文件名冲突"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('uploads', filename)

class FileCategory(models.Model):
    """文件分类模型"""
    name = models.CharField(max_length=100, verbose_name="分类名称")
    description = models.TextField(blank=True, null=True, verbose_name="分类描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "文件分类"
        verbose_name_plural = "文件分类"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('file_manager:category_detail', kwargs={'pk': self.pk})

class File(models.Model):
    """文件模型"""
    title = models.CharField(max_length=255, verbose_name="文件标题")
    description = models.TextField(blank=True, null=True, verbose_name="文件描述")
    file = models.FileField(upload_to=get_file_path, verbose_name="文件")
    file_size = models.PositiveIntegerField(default=0, verbose_name="文件大小(字节)")
    file_type = models.CharField(max_length=50, blank=True, null=True, verbose_name="文件类型")
    category = models.ForeignKey(FileCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='files', verbose_name="分类")
    uploaded_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='uploaded_files', verbose_name="上传者")
    upload_date = models.DateTimeField(default=timezone.now, verbose_name="上传时间")
    is_public = models.BooleanField(default=False, verbose_name="是否公开")
    download_count = models.PositiveIntegerField(default=0, verbose_name="下载次数")
    
    class Meta:
        verbose_name = "文件"
        verbose_name_plural = "文件"
        ordering = ['-upload_date']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('file_manager:file_detail', kwargs={'pk': self.pk})
    
    def filename(self):
        return os.path.basename(self.file.name)
    
    def extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension
    
    def save(self, *args, **kwargs):
        # 如果是新创建的文件，设置文件大小和类型
        if self.pk is None and self.file:
            self.file_size = self.file.size
            name, extension = os.path.splitext(self.file.name)
            self.file_type = extension[1:].lower()  # 去掉点号
        super().save(*args, **kwargs)
