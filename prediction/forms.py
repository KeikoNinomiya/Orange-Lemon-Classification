from django import forms


class ImageUploadForm(forms.Form):
    image = forms.ImageField() # ← 画像選択ボタンを作成
