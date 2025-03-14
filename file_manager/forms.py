from django import forms
from .models import File, FileCategory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div

class FileCategoryForm(forms.ModelForm):
    """文件分类表单"""
    class Meta:
        model = FileCategory
        fields = ['name', 'description']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', '保存', css_class='btn-primary'))
        self.helper.layout = Layout(
            'name',
            'description',
        )

class FileUploadForm(forms.ModelForm):
    """文件上传表单"""
    class Meta:
        model = File
        fields = ['title', 'description', 'file', 'category', 'is_public']
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.add_input(Submit('submit', '上传', css_class='btn-primary'))
        self.helper.layout = Layout(
            'title',
            'description',
            'file',
            'category',
            'is_public',
        )
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.uploaded_by = self.user
        if commit:
            instance.save()
        return instance

class FileSearchForm(forms.Form):
    """文件搜索表单"""
    query = forms.CharField(
        label='搜索',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '搜索文件名或描述'})
    )
    category = forms.ModelChoiceField(
        label='分类',
        queryset=FileCategory.objects.all(),
        required=False,
        empty_label="所有分类"
    )
    file_type = forms.ChoiceField(
        label='文件类型',
        choices=[('', '所有类型')],  # 将在视图中动态填充
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        file_types = kwargs.pop('file_types', [])
        super().__init__(*args, **kwargs)
        
        # 动态添加文件类型选项
        type_choices = [('', '所有类型')]
        for file_type in file_types:
            if file_type:  # 确保不是空字符串
                type_choices.append((file_type, file_type.upper()))
        self.fields['file_type'].choices = type_choices
        
        # 设置表单布局
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            Row(
                Column('query', css_class='form-group col-md-6 mb-0'),
                Column('category', css_class='form-group col-md-3 mb-0'),
                Column('file_type', css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
            ),
            Div(
                Submit('submit', '搜索', css_class='btn-primary'),
                css_class='form-group'
            )
        ) 