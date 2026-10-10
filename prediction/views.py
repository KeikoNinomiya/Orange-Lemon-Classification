import os
import numpy as np
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing import image

from .forms import ImageUploadForm

MODEL_PATH = os.path.join(
    settings.BASE_DIR, "prediction", "models", "model_100.h5"
)


def build_model():
    model = models.Sequential(
        [
            layers.Input(shape=(100, 100, 3)),
            layers.Conv2D(32, (3, 3), activation="relu"),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(64, (3, 3), activation="relu"),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(128, (3, 3), activation="relu"),
            layers.MaxPooling2D((2, 2)),
            layers.Flatten(),
            layers.Dense(128, activation="relu"),
            layers.Dense(1, activation="sigmoid"),
        ]
    )
    return model


try:
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
except Exception:
    model = build_model()
    model.load_weights(MODEL_PATH, by_name=True, skip_mismatch=True)


def predict(request):
    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            img_file = request.FILES["image"]

            # 1. 画像ファイルを media フォルダに保存
            fs = FileSystemStorage()
            filename = fs.save(img_file.name, img_file)
            img_url = fs.url(filename)
            uploaded_img_path = fs.path(filename)  # 保存先ファイルの絶対パスを取得

            # 2. 保存したファイルパスを使って画像読み込みと前処理 (100x100)
            img = image.load_img(uploaded_img_path, target_size=(100, 100))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = img_array / 255.0

            # 3. 推論の実行
            predictions = model.predict(img_array)

            # 判定ロジックの反転（0.5以上をオレンジにする）
            if predictions[0][0] >= 0.5:
                prediction_result = "オレンジ"
            else:
                prediction_result = "レモン"
                
            return render(
                request,
                "home.html",
                {
                    "form": form,
                    "prediction": prediction_result,
                    "img_url": img_url,
                },
            )
    else:
        form = ImageUploadForm()

    return render(request, "home.html", {"form": form})