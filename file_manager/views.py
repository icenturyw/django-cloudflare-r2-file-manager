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
        # 获取当前文件对象
        file_obj = self.get_object()
        
        # 检查是否上传了新文件
        if 'file' in form.changed_data:
            # 删除旧文件
            try:
                file_obj.file.delete(save=False)
            except Exception as e:
                messages.warning(self.request, f'删除旧文件时出错: {str(e)}')
        
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
    
    def form_valid(self, form):
        file_obj = self.get_object()
        
        # 从存储中删除文件
        try:
            # 获取存储的文件
            file_obj.file.delete(save=False)
        except Exception as e:
            messages.error(self.request, f'删除文件时出错: {str(e)}')
        
        messages.success(self.request, '文件已删除！')
        return super().form_valid(form)

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
    
    def form_valid(self, form):
        category = self.get_object()
        
        # 获取该分类下的所有文件
        files = category.files.all()
        
        # 删除每个文件的存储
        for file_obj in files:
            try:
                # 从存储中删除文件
                file_obj.file.delete(save=False)
            except Exception as e:
                messages.error(self.request, f'删除文件时出错: {str(e)}')
        
        messages.success(self.request, '分类已删除！')
        return super().form_valid(form)

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
    
    # 获取文件类型
    content_type, encoding = mimetypes.guess_type(file.file.name)
    
    # 判断是否可以预览
    can_preview = False
    if content_type:
        if content_type.startswith('image/') or content_type == 'application/pdf' or content_type.startswith('text/'):
            can_preview = True
    
    # 获取文件URL
    file_url = file.file.url
    
    context = {
        'file': file,
        'can_preview': can_preview,
        'content_type': content_type,
        'file_url': file_url
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
    
    # 对于云存储，重定向到文件URL
    return redirect(file.file.url)
