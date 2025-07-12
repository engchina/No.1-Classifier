# 训练数据配置说明

## 训练数据格式

我们使用 **JSONL (JSON Lines)** 格式来存储训练数据，这是一种每行一个JSON对象的格式，非常适合存储大量结构化数据。

### 文件格式：`training_data.jsonl`

每行一个JSON对象，格式如下：
```json
{"text": "文本内容", "label": "标签"}
```

### 示例数据
```
{"text": "这个产品太棒了，完全超出预期！", "label": "好评"}
{"text": "服务非常糟糕，再也不会购买了", "label": "差评"}
{"text": "质量一般，价格有点高", "label": "中评"}
```

## 使用方法

### 1. 修改训练数据
直接编辑 `training_data.jsonl` 文件，每行添加一个新的训练样本。

### 2. 训练模型
启动应用后，调用训练API：

```bash
# 训练模型
curl -X POST http://localhost:5000/train

# 响应示例
{
    "message": "模型训练成功",
    "training_samples": 8,
    "labels": ["好评", "差评", "中评"]
}
```

### 3. 使用分类功能
训练完成后，可以使用分类功能：

```bash
# 分类文本
curl -X POST http://localhost:5000/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "这个产品很好"}'

# 响应示例
{
    "text": "这个产品很好",
    "prediction": "好评",
    "probabilities": {"中评": 0.123, "好评": 0.765, "差评": 0.112}
}
```

### 4. 重新训练
也可以使用自定义数据重新训练：

```bash
# 重新训练
curl -X POST http://localhost:5000/retrain \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["新样本1", "新样本2"],
    "labels": ["好评", "差评"]
  }'
```

## 文件结构
- `training_data.jsonl` - 训练数据文件
- `text_classifier_oracle.joblib` - 训练后的模型文件（自动生成）

## 注意事项
1. 训练数据需要至少每个标签有2个样本
2. 文本内容建议使用UTF-8编码
3. 标签可以是任意字符串，但建议保持一致性
4. 模型训练后会自动保存，下次启动时会自动加载