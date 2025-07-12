# Oracle OCI Cohere 文本分类 API

这是一个使用 Oracle OCI Generative AI 的 Cohere 模型实现的文本分类 API。该 API 使用 Flask 框架，通过 Oracle OCI 的嵌入服务生成文本向量，并训练分类模型来实现文本分类功能。

## 功能特性

- 使用 Oracle OCI Cohere 嵌入模型 (`cohere.embed-v4.0`)
- 支持中文文本分类
- RESTful API 接口
- 模型持久化存储
- 健康检查端点
- 模型重训练功能

## 环境要求

- Python 3.11+
- Oracle OCI 账户和 Compartment ID
- OCI CLI 配置完成

## 安装步骤

### 1. 安装依赖

```bash
conda create -n no.1-classifier python=3.11 -y
conda activate no.1-classifier
pip install -r requirements.txt
# pip list --format=freeze > requirements.txt
```

### 2. 配置 Oracle OCI

#### 2.1 安装并配置 OCI CLI

```bash
# 安装 OCI CLI
pip install oci-cli

# 配置 OCI CLI
oci setup config
```

#### 2.2 配置环境变量

复制环境变量模板：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的配置：

```bash
# Oracle OCI 配置
OCI_COMPARTMENT_ID=ocid1.compartment.oc1..xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. 运行应用

```bash
python app.py
```

应用将在 `http://localhost:5000` 启动

## API 使用说明

### 1. 文本分类

**端点**: `POST /classify`

**请求示例**:
```bash
curl -X POST http://localhost:5000/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "这个产品物超所值，非常满意"}'
```

**响应示例**:
```json
{
  "text": "这个产品物超所值，非常满意",
  "prediction": "好评",
  "probabilities": {
    "中评": 0.12,
    "差评": 0.05,
    "好评": 0.83
  }
}
```

### 2. 健康检查

**端点**: `GET /health`

**请求示例**:
```bash
curl http://localhost:5000/health
```

**响应示例**:
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### 3. 重新训练模型

**端点**: `POST /retrain`

**请求示例**:
```bash
curl -X POST http://localhost:5000/retrain \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["新文本1", "新文本2", "新文本3"],
    "labels": ["好评", "差评", "中评"]
  }'
```

**响应示例**:
```json
{
  "message": "模型重新训练成功"
}
```

## 项目结构

```
.
├── app.py                 # 主应用文件
├── requirements.txt       # 依赖列表
├── .env.example          # 环境变量模板
├── .env                  # 环境变量文件（需要创建）
├── text_classifier_oracle.joblib  # 训练好的模型文件（自动生成）
└── README.md             # 项目说明文档
```

## 配置说明

### Oracle OCI 配置

确保你的 OCI CLI 配置文件 (`~/.oci/config`) 包含以下内容：

```ini
[DEFAULT]
user=ocid1.user.oc1..xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
fingerprint=xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx
tenancy=ocid1.tenancy.oc1..xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
region=us-chicago-1
key_file=~/.oci/oci_api_key.pem
```

### 获取 Compartment ID

1. 登录 [Oracle Cloud Console](https://cloud.oracle.com/)
2. 导航到 "身份与安全" > "区间"
3. 选择你的区间，复制 OCID

## 故障排除

### 常见问题

1. **OCI 认证失败**
   - 检查 `~/.oci/config` 文件配置是否正确
   - 确保 API 密钥文件存在且有正确权限
   - 验证 Compartment ID 是否正确

2. **模型训练失败**
   - 检查网络连接
   - 验证 OCI 服务是否可用
   - 检查 Compartment 是否有访问 Generative AI 的权限

3. **端口占用**
   - 如果 5000 端口被占用，修改 `app.py` 中的端口号

### 调试模式

以调试模式运行应用：

```bash
python app.py
```

查看详细日志输出，便于排查问题。

## 生产部署

### 使用 Gunicorn

```bash
pip install gunicorn
gunicorn wsgi:app -b 0.0.0.0:5000 -w 4
```

### Docker 部署

创建 `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

构建并运行：

```bash
docker build -t oracle-cohere-classifier .
docker run -p 5000:5000 --env-file .env oracle-cohere-classifier
```

## 许可证

MIT License