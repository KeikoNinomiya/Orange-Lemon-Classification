# オレンジ・レモン判別アプリ

アップロードした果物の画像が「オレンジ」か「レモン」かを、学習済みの CNN モデルで判定する Django 製の Web アプリです。

## 仕様

### 機能

- 画像ファイルを選択（またはドラッグ＆ドロップ）して送信すると、判定結果を「オレンジ」「レモン」で表示します。
- 判定結果に応じて画面の配色が変わります。
- 画像以外のファイルを送信した場合はフォームのバリデーションエラーを表示します。
- アップロードされた画像は `media/` ディレクトリに保存されます。

### 画面

| URL | 内容 |
| --- | --- |
| `/` | 画像アップロードと判定結果の表示 |
| `/admin/` | Django 管理画面 |

### 判定ロジック

1. アップロード画像を 100×100 にリサイズし、画素値を 0〜1 に正規化します。
2. 学習済みモデル `prediction/models/model_100.h5`（Conv2D ×3 + Dense の CNN）で推論します。
3. 2 クラスの softmax 出力のうち、インデックス 1（オレンジ）が 0.5 以上ならオレンジ、未満ならレモンと判定します。

### 技術スタック

- Python 3.11.2
- Django 4.2.1
- TensorFlow 2.21.0 / Keras 3（モデルが Keras 3 形式で保存されているため TensorFlow 2.16 以上が必要）
- Pillow, NumPy
- gunicorn（本番起動用）

### ディレクトリ構成

```
.
├── manage.py
├── requirements.txt
├── Procfile                    # gunicorn による起動設定（Heroku 等向け）
├── runtime.txt                 # Python バージョン指定
├── orangeorlemon/              # プロジェクト設定（settings, urls など）
├── prediction/
│   ├── views.py                # モデル読み込みと判定処理
│   ├── forms.py                # 画像アップロードフォーム
│   ├── urls.py
│   ├── templates/home.html     # 画面（HTML/CSS/JS）
│   └── models/model_100.h5     # 学習済みモデル
└── media/                      # アップロード画像の保存先（実行時に作成）
```

## 実行方法

### 1. 事前準備

Python 3.11 がインストールされていることを確認してください。

### 2. セットアップ

```bash
# 仮想環境の作成と有効化
python3.11 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

# 依存パッケージのインストール
pip install -r requirements.txt
```

### 3. 開発サーバーの起動

```bash
python manage.py runserver
```

ブラウザで <http://127.0.0.1:8000/> を開き、画像を選択して判定してください。

> 初回起動時は TensorFlow とモデルの読み込みに少し時間がかかります。

### 4. 本番相当での起動（任意）

```bash
gunicorn --workers=1 --worker-class=sync orangeorlemon.wsgi --timeout 300
```

## 注意事項

- `ALLOWED_HOSTS` には `127.0.0.1` と `.herokuapp.com` のみ設定されています。`localhost` や他のドメインで動かす場合は [orangeorlemon/settings.py](orangeorlemon/settings.py) を編集してください。
- `DEBUG = True` のままです。公開環境で運用する場合は `DEBUG` の無効化と `SECRET_KEY` の環境変数化を行ってください。
- `media/` と `db.sqlite3` は `.gitignore` により Git 管理対象外です。
