# Oracle OCI Cohere テキスト分類 API

Oracle OCI Generative AI の Cohere モデルを使用したテキスト分類 API です。この API は Flask フレームワークを採用し、Oracle OCI の埋め込みサービスを通じてテキストベクトルを生成し、分類モデルを学習させてテキスト分類機能を実現します。

## 主な機能

- Oracle OCI Cohere 埋め込みモデル (`cohere.embed-v4.0`) の利用
- 中国語テキスト分類のサポート
- RESTful API インターフェース
- モデルの永続化ストレージ
- ヘルスチェックエンドポイント
- モデルの再学習機能

## 動作環境

- Python 3.11+
- Oracle OCI アカウントと Compartment ID
- OCI CLI の設定完了

## インストール手順

### 1. 依存関係のインストール

```bash
conda create -n no.1-classifier python=3.11 -y
conda activate no.1-classifier
pip install -r requirements.txt
# pip list --format=freeze > requirements.txt
```

### 2. Oracle OCI の設定

#### 2.1 OCI CLI のインストールと設定

```bash
# OCI CLI のインストール
pip install oci-cli

# OCI CLI の設定
oci setup config
```

#### 2.2 環境変数の設定

環境変数テンプレートをコピー：

```bash
cp .env.example .env
```

`.env` ファイルを編集して、設定を入力：

```bash
# Oracle OCI 設定
OCI_COMPARTMENT_ID=ocid1.compartment.oc1..xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. アプリケーションの起動

```bash
python app.py
```

アプリケーションは `http://localhost:5000` で起動します。

## API 使用方法

### 1. テキスト分類

**エンドポイント**: `POST /classify`

**リクエスト例**:
```bash
curl -X POST http://localhost:5000/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "この製品はコスパが良くて、とても満足しています"}'
```

**レスポンス例**:
```json
{
  "text": "この製品はコスパが良くて、とても満足しています",
  "prediction": "好評",
  "probabilities": {
    "中評": 0.12,
    "悪評": 0.05,
    "好評": 0.83
  }
}
```

### 2. ヘルスチェック

**エンドポイント**: `GET /health`

**リクエスト例**:
```bash
curl http://localhost:5000/health
```

**レスポンス例**:
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### 3. モデルの再学習

**エンドポイント**: `POST /retrain`

**リクエスト例**:
```bash
curl -X POST http://localhost:5000/retrain \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["新しいテキスト1", "新しいテキスト2", "新しいテキスト3"],
    "labels": ["好評", "悪評", "中評"]
  }'
```

**レスポンス例**:
```json
{
  "message": "モデルの再学習が完了しました"
}
```

## プロジェクト構造

```
.
├── app.py                 # メインアプリケーションファイル
├── requirements.txt       # 依存関係リスト
├── .env.example          # 環境変数テンプレート
├── .env                  # 環境変数ファイル（作成が必要）
├── text_classifier_oracle.joblib  # 学習済みモデルファイル（自動生成）
└── README.md             # プロジェクト説明ドキュメント
```

## 設定説明

### Oracle OCI 設定

OCI CLI 設定ファイル (`~/.oci/config`) に以下の内容が含まれていることを確認：

```ini
[DEFAULT]
user=ocid1.user.oc1..xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
fingerprint=xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx
tenancy=ocid1.tenancy.oc1..xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
region=us-chicago-1
key_file=~/.oci/oci_api_key.pem
```

### Compartment ID の取得

1. [Oracle Cloud Console](https://cloud.oracle.com/) にログイン
2. 「アイデンティティとセキュリティ」>「コンパートメント」に移動
3. コンパートメントを選択し、OCID をコピー

## トラブルシューティング

### よくある問題

1. **OCI 認証エラー**
   - `~/.oci/config` ファイルの設定が正しいか確認
   - API キーファイルが存在し、正しい権限があるか確認
   - Compartment ID が正しいか確認

2. **モデル学習エラー**
   - ネットワーク接続を確認
   - OCI サービスが利用可能か確認
   - Compartment が Generative AI へのアクセス権限を持っているか確認

3. **ポート競合**
   - 5000番ポートが使用中の場合、`app.py` のポート番号を変更

### デバッグモード

デバッグモードでアプリケーションを起動：

```bash
python app.py
```

詳細なログ出力を確認して、問題を特定できます。

## 本番環境へのデプロイ

### Gunicorn の使用

```bash
pip install gunicorn
gunicorn wsgi:app -b 0.0.0.0:5000 -w 4
```

### Docker デプロイ

`Dockerfile` を作成：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

ビルドと実行：

```bash
docker build -t oracle-cohere-classifier .
docker run -p 5000:5000 --env-file .env oracle-cohere-classifier
```

## ライセンス

MIT License