from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, FileResponse, Http404
from django.contrib import messages
from django.views.decorators.http import require_POST

from .models import File, FileCategory
from .forms import FileUploadForm, FileCategoryForm, FileSearchForm

import os
import mimetypes
from wsgiref.util import FileWrapper

class FileListView(ListView):
    """文件列表视图"""
    model = File
    template_name = 'file_manager/file_list.html'
    context_object_name = 'files'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = File.objects.all()
        
        # 如果用户未登录，只显示公开文件
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_public=True)
        
        # 处理搜索查询
        form = self.get_search_form()
        if form.is_valid():
            query = form.cleaned_data.get('query')
            category = form.cleaned_data.get('category')
            file_type = form.cleaned_data.get('file_type')
            
            if query:
                queryset = queryset.filter(
                    Q(title__icontains=query) | 
                    Q(description__icontains=query)
                )
            
            if category:
                queryset = queryset.filter(category=category)
            
            if file_type:
                queryset = queryset.filter(file_type=file_type)
        
        return queryset
    
    def get_search_form(self):
        # 获取所有不同的文件类型
        file_types = File.objects.values_list('file_type', flat=True).distinct()
        
        # 创建搜索表单
        return FileSearchForm(self.request.GET or None, file_types=file_types)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = self.get_search_form()
        context['categories'] = FileCategory.objects.all()
        return context

class FileDetailView(DetailView):
    """文件详情视图"""
    model = File
    template_name = 'file_manager/file_detail.html'
    context_object_name = 'file'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 如果用户未登录，只显示公开文件
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_public=True)
        
        return queryset

class FileUploadView(LoginRequiredMixin, CreateView):
    """文件上传视图"""
    model = File
    form_class = FileUploadForm
    template_name = 'file_manager/file_upload.html'
    success_url = reverse_lazy('file_manager:file_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, '文件上传成功！')
        return super().form_valid(form)

class FileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """文件更新视图"""
    model = File
    form_class = FileUploadForm
    template_name = 'file_manager/file_update.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def test_func(self):
        file = self.get_object()
        return self.request.user == file.uploaded_by or self.request.user.is_staff
    
    def form_valid(self, form):
        messages.success(self.request, '文件更新成功！')
        return super().form_valid(form)

class FileDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """文件删除视图"""
    model = File
    template_name = 'file_manager/file_confirm_delete.html'
    success_url = reverse_lazy('file_manager:file_list')
    
    def test_func(self):
        file = self.get_object()
        return self.request.user == file.uploaded_by or self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '文件已删除！')
        return super().delete(request, *args, **kwargs)

class CategoryListView(ListView):
    """分类列表视图"""
    model = FileCategory
    template_name = 'file_manager/category_list.html'
    context_object_name = 'categories'

class CategoryDetailView(DetailView):
    """分类详情视图"""
    model = FileCategory
    template_name = 'file_manager/category_detail.html'
    context_object_name = 'category'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 获取该分类下的文件
        files = self.object.files.all()
        
        # 如果用户未登录，只显示公开文件
        if not self.request.user.is_authenticated:
            files = files.filter(is_public=True)
        
        context['files'] = files
        return context

class CategoryCreateView(LoginRequiredMixin, CreateView):
    """分类创建视图"""
    model = FileCategory
    form_class = FileCategoryForm
    template_name = 'file_manager/category_form.html'
    success_url = reverse_lazy('file_manager:category_list')
    
    def form_valid(self, form):
        messages.success(self.request, '分类创建成功！')
        return super().form_valid(form)

class CategoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """分类更新视图"""
    model = FileCategory
    form_class = FileCategoryForm
    template_name = 'file_manager/category_form.html'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def form_valid(self, form):
        messages.success(self.request, '分类更新成功！')
        return super().form_valid(form)

class CategoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """分类删除视图"""
    model = FileCategory
    template_name = 'file_manager/category_confirm_delete.html'
    success_url = reverse_lazy('file_manager:category_list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '分类已删除！')
        return super().delete(request, *args, **kwargs)

@login_required
@require_POST
def download_file(request, pk):
    """下载文件"""
    file = get_object_or_404(File, pk=pk)
    
    # 检查权限
    if not file.is_public and request.user != file.uploaded_by and not request.user.is_staff:
        raise Http404("您没有权限下载此文件")
    
    # 增加下载计数
    file.download_count += 1
    file.save()
    
    # 获取文件路径
    file_path = file.file.path
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise Http404("文件不存在")
    
    # 获取文件类型
    content_type, encoding = mimetypes.guess_type(file_path)
    if content_type is None:
        content_type = 'application/octet-stream'
    
    # 创建响应
    response = FileResponse(
        FileWrapper(open(file_path, 'rb')),
        content_type=content_type
    )
    
    # 设置Content-Disposition头，使浏览器下载文件而不是显示
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file.file.name)}"'
    
    return response

def file_preview(request, pk):
    """文件预览"""
    file = get_object_or_404(File, pk=pk)
    
    # 检查权限
    if not file.is_public and not request.user.is_authenticated:
        return redirect('login')
    
    if not file.is_public and request.user != file.uploaded_by and not request.user.is_staff:
        raise Http404("您没有权限预览此文件")
    
    # 获取文件路径
    file_path = file.file.path
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise Http404("文件不存在")
    
    # 获取文件类型
    content_type, encoding = mimetypes.guess_type(file_path)
    
    # 如果是图片、PDF或文本文件，则可以直接预览
    previewable_types = ['image/', 'application/pdf', 'text/']
    can_preview = any(content_type and content_type.startswith(t) for t in previewable_types)
    
    context = {
        'file': file,
        'can_preview': can_preview,
        'content_type': content_type
    }
    
    return render(request, 'file_manager/file_preview.html', context)

def serve_file(request, pk):
    """提供文件内容"""
    file = get_object_or_404(File, pk=pk)
    
    # 检查权限
    if not file.is_public and not request.user.is_authenticated:
        return redirect('login')
    
    if not file.is_public and request.user != file.uploaded_by and not request.user.is_staff:
        raise Http404("您没有权限访问此文件")
    
    # 获取文件路径
    file_path = file.file.path
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise Http404("文件不存在")
    
    # 获取文件类型
    content_type, encoding = mimetypes.guess_type(file_path)
    if content_type is None:
        content_type = 'application/octet-stream'
    
    # 创建响应
    response = FileResponse(
        FileWrapper(open(file_path, 'rb')),
        content_type=content_type
    )
    
    return response
