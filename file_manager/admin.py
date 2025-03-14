from django.contrib import admin
from .models import FileCategory, File

@admin.register(FileCategory)
class FileCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'file_type', 'file_size_display', 'uploaded_by', 'upload_date', 'is_public', 'download_count')
    list_filter = ('category', 'file_type', 'upload_date', 'is_public', 'uploaded_by')
    search_fields = ('title', 'description', 'file')
    date_hierarchy = 'upload_date'
    readonly_fields = ('file_size', 'file_type', 'download_count')
    
    def file_size_display(self, obj):
        """以人类可读的方式显示文件大小"""
        size_bytes = obj.file_size
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
    
    file_size_display.short_description = '文件大小'
