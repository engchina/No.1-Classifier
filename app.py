from flask import Flask, request, jsonify
import numpy as np
from sklearn.linear_model import LogisticRegression
import joblib
import os
import json
import oci
from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import EmbedTextDetails
from dotenv import load_dotenv, find_dotenv

app = Flask(__name__)

# 加载环境变量
load_dotenv(find_dotenv())

# 配置 Oracle OCI
CONFIG_PROFILE = "DEFAULT"
config = oci.config.from_file('~/.oci/config', CONFIG_PROFILE)

# 初始化 OCI Generative AI 客户端
generative_ai_inference_client = GenerativeAiInferenceClient(
    config=config,
    service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
    retry_strategy=oci.retry.NoneRetryStrategy(),
    timeout=(10, 240)  # 连接超时10秒，读取超时240秒
)

# 模型配置
COMPARTMENT_ID = os.getenv("OCI_COMPARTMENT_ID")  # 从环境变量获取 Compartment ID

# 训练分类模型
def train_classifier(texts, labels):
    """使用 Oracle OCI Cohere 模型训练分类器"""
    try:
        # 获取嵌入向量
        embed_text_detail = EmbedTextDetails(
            compartment_id=COMPARTMENT_ID,
            inputs=texts,
            serving_mode=oci.generative_ai_inference.models.OnDemandServingMode(
                model_id="cohere.embed-v4.0"
            ),
            truncate="END"
        )
        
        embed_text_response = generative_ai_inference_client.embed_text(embed_text_detail)
        embeddings = np.array(embed_text_response.data.embeddings)
        
        # 训练逻辑回归分类器
        classifier = LogisticRegression(max_iter=1000)
        classifier.fit(embeddings, labels)
        return classifier
        
    except Exception as e:
        print(f"训练分类器时出错: {str(e)}")
        raise e

# 获取文本嵌入
def get_text_embedding(text):
    """使用 Oracle OCI Cohere 模型获取文本嵌入"""
    try:
        embed_text_detail = EmbedTextDetails(
            compartment_id=COMPARTMENT_ID,
            inputs=[text],
            serving_mode=oci.generative_ai_inference.models.OnDemandServingMode(
                model_id="cohere.embed-v4.0"
            ),
            truncate="END"
        )
        
        embed_text_response = generative_ai_inference_client.embed_text(embed_text_detail)
        embedding = np.array(embed_text_response.data.embeddings[0])
        return embedding
        
    except Exception as e:
        print(f"获取文本嵌入时出错: {str(e)}")
        raise e

# 模型路径
MODEL_PATH = "text_classifier_oracle.joblib"
TRAINING_DATA_PATH = "training_data.jsonl"

# 全局变量
classifier = None
is_trained = False

# 加载训练数据
def load_training_data(data_path):
    """从JSONL文件加载训练数据"""
    texts = []
    labels = []
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line.strip())
                    texts.append(data['text'])
                    labels.append(data['label'])
        return texts, labels
    except Exception as e:
        print(f"加载训练数据时出错: {str(e)}")
        raise e

# 初始化模型
def initialize_model():
    """初始化模型：如果存在预训练模型则加载，否则需要训练"""
    global classifier, is_trained
    if os.path.exists(MODEL_PATH):
        classifier = joblib.load(MODEL_PATH)
        is_trained = True
        print("已加载预训练模型")
    else:
        print("未找到预训练模型，需要先进行训练")
        is_trained = False

@app.route('/train', methods=['POST'])
def train_model():
    """训练模型API端点"""
    global classifier, is_trained
    
    try:
        # 加载训练数据
        if not os.path.exists(TRAINING_DATA_PATH):
            return jsonify({"error": f"训练数据文件 {TRAINING_DATA_PATH} 不存在"}), 400
        
        train_texts, train_labels = load_training_data(TRAINING_DATA_PATH)
        
        if not train_texts or not train_labels:
            return jsonify({"error": "训练数据为空"}), 400
        
        # 训练模型（无论是否已训练过，都重新训练）
        print("正在训练模型...")
        classifier = train_classifier(train_texts, train_labels)
        
        # 保存模型
        joblib.dump(classifier, MODEL_PATH)
        is_trained = True
        
        return jsonify({
            "message": "模型训练成功",
            "training_samples": len(train_texts),
            "labels": list(set(train_labels))
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/classify', methods=['POST'])
def classify_text():
    """文本分类API端点"""
    try:
        # 检查是否已训练
        if not is_trained:
            return jsonify({"error": "模型尚未训练，请先调用 /train 端点进行训练"}), 400
        
        # 获取请求数据
        data = request.json
        text = data.get('text')
        
        if not text:
            return jsonify({"error": "请求体中缺少 'text' 字段"}), 400
        
        # 获取文本嵌入
        embedding = get_text_embedding(text)
        
        # 使用分类模型预测
        prediction = classifier.predict([embedding])
        probabilities = classifier.predict_proba([embedding])
        
        # 构造响应
        return jsonify({
            "text": text,
            "prediction": prediction[0],
            "probabilities": dict(zip(classifier.classes_, probabilities[0].round(3).tolist()))
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        "status": "healthy",
        "model_trained": is_trained,
        "model_path_exists": os.path.exists(MODEL_PATH)
    })

if __name__ == '__main__':
    # 检查必要的环境变量
    if not COMPARTMENT_ID:
        print("错误: 请设置环境变量 OCI_COMPARTMENT_ID")
        exit(1)
    
    # 初始化模型
    initialize_model()
    
    print("Oracle OCI 文本分类 API 启动中...")
    print(f"Compartment ID: {COMPARTMENT_ID[:10]}...")
    
    app.run(host='0.0.0.0', port=5000, debug=True)