from django import forms
from .models import UserProfile
from django.contrib.auth.models import Group, User
from pathlib import Path
import nbformat
from .models import GroupAssignment


def validate_assignment_upload(upload, extensions):
    if upload.size > 10 * 1024 * 1024:
        raise forms.ValidationError("檔案不能超過 10 MB。")
    if Path(upload.name).suffix.lower() not in extensions:
        raise forms.ValidationError("不支援此檔案格式，可使用：" + "、".join(sorted(extensions)))
    if Path(upload.name).suffix.lower() == ".ipynb":
        try:
            notebook = nbformat.reads(upload.read().decode("utf-8-sig"), as_version=4)
            nbformat.validate(notebook)
        except Exception as exc:
            raise forms.ValidationError("Notebook 格式錯誤，請上傳有效的 .ipynb 檔。") from exc
        finally:
            upload.seek(0)
    return upload


class GroupAssignmentForm(forms.ModelForm):
    class Meta:
        model = GroupAssignment
        fields = ["title", "description", "prompt_file", "reference_file"]
        labels = {"title": "作業名稱", "description": "題目說明", "prompt_file": "題目附件（選填）",
                  "reference_file": "教師參考答案（.ipynb）"}
        help_texts = {"reference_file": "上傳含 pybryt.Value 等檢查點的 Notebook；後台會執行參考程式並自動產生此作業的 .pkl。"}
        widgets = {"description": forms.Textarea(attrs={"rows": 5}),
                   "reference_file": forms.FileInput(attrs={"accept": ".ipynb"})}

    def clean_prompt_file(self):
        upload = self.cleaned_data.get("prompt_file")
        return validate_assignment_upload(upload, {".md", ".txt", ".pdf", ".ipynb"}) if upload else upload

    def clean_reference_file(self):
        return validate_assignment_upload(self.cleaned_data["reference_file"], {".ipynb"})

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("description") and not cleaned.get("prompt_file"):
            self.add_error("description", "請填寫題目說明或上傳題目附件。")
        return cleaned


class AssignmentSubmissionForm(forms.Form):
    student = forms.ModelChoiceField(queryset=User.objects.none(), label="學生")
    notebook = forms.FileField(label="學生作業（.ipynb）")

    def __init__(self, *args, group, teacher, **kwargs):
        super().__init__(*args, **kwargs)
        if teacher:
            self.fields["student"].queryset = group.user_set.order_by("username")
        else:
            del self.fields["student"]

    def clean_notebook(self):
        return validate_assignment_upload(self.cleaned_data["notebook"], {".ipynb"})


class TeacherGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name"]
        labels = {"name": "群組名稱"}

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if name.casefold() == "teachers":
            raise forms.ValidationError("此名稱保留給教師權限群組，請使用其他名稱。")
        if Group.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("此群組名稱已存在。")
        return name


class TeacherGroupMembersForm(forms.Form):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(), label="使用者",
        widget=forms.CheckboxSelectMultiple,
        error_messages={"required": "請至少選擇一位使用者。"},
    )

    def __init__(self, *args, group, removing=False, **kwargs):
        super().__init__(*args, **kwargs)
        users = User.objects.order_by("username")
        self.fields["users"].queryset = (
            users.filter(groups=group) if removing
            else users.exclude(groups=group)
        )

class AvatarUploadForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["avatar"]
