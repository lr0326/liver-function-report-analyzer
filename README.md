# 肝功能检查报告自动解读系统

AI-powered liver function test report analyzer with OCR and medical knowledge base.

## 功能特性

- **文件上传**：支持 PDF 和图片（JPG、PNG）格式的肝功能报告上传
- **OCR 识别**：使用 PaddleOCR 进行高精度中英文文字识别，自动提取肝功能指标
- **医学知识库**：内置 11 项肝功能指标的完整参考数据，含正常范围、临床意义、性别/年龄差异
- **AI 分析**：集成 OpenAI GPT 或本地 LLM（Ollama）进行专业医学解读
- **风险评分**：自动计算 0-100 风险评分并给出就医建议
- **REST API**：提供完整的 Flask API 端点，方便前端集成

## 支持的肝功能指标

| 代码 | 中文名 | 英文名 | 正常范围（成人）|
|------|--------|--------|----------------|
| ALT | 谷丙转氨酶 | Alanine Aminotransferase | 7–56 U/L |
| AST | 谷草转氨酶 | Aspartate Aminotransferase | 10–40 U/L |
| ALP | 碱性磷酸酶 | Alkaline Phosphatase | 30–120 U/L |
| GGT | γ-谷氨酰转移酶 | Gamma-Glutamyl Transferase | 9–48 U/L |
| TBIL | 总胆红素 | Total Bilirubin | 3.4–20.5 μmol/L |
| DBIL | 直接胆红素 | Direct Bilirubin | 0–6.8 μmol/L |
| IBIL | 间接胆红素 | Indirect Bilirubin | 1.7–13.7 μmol/L |
| ALB | 白蛋白 | Albumin | 35–55 g/L |
| GLB | 球蛋白 | Globulin | 20–35 g/L |
| TP | 总蛋白 | Total Protein | 60–83 g/L |
| A/G | 白/球蛋白比 | Albumin/Globulin Ratio | 1.2–2.5 |

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/lr0326/liver-function-report-analyzer.git
cd liver-function-report-analyzer
```

### 2. 配置环境变量

```bash
cd backend
cp .env.example .env
# 编辑 .env，填写 OPENAI_API_KEY 等配置
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 启动服务

```bash
python main.py
```

服务默认运行在 `http://localhost:5000`。

## API 端点

### 健康检查

```
GET /api/health
```

**响应示例：**
```json
{"status": "healthy", "message": "Liver Function Report Analyzer API is running"}
```

---

### 上传并分析报告

```
POST /api/reports/upload
Content-Type: multipart/form-data
```

**参数：**
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | ✅ | PDF / JPG / PNG 格式报告 |
| gender | string | ❌ | `male` / `female` / `all`（默认 `all`）|
| age_group | string | ❌ | `adult` / `child` / `elderly`（默认 `adult`）|

**示例：**
```bash
curl -X POST http://localhost:5000/api/reports/upload \
  -F "file=@report.pdf" \
  -F "gender=male"
```

---

### 直接分析文本

```
POST /api/reports/text
Content-Type: application/json
```

**请求体：**
```json
{
  "text": "ALT 120 U/L 7-56\nAST 85 U/L 10-40",
  "gender": "male",
  "age_group": "adult"
}
```

---

### 查询已有分析结果

```
GET /api/reports/analysis/{report_id}
```

---

### 响应示例（分析报告）

```json
{
  "report_id": "550e8400-e29b-41d4-a716-446655440000",
  "risk_score": 35,
  "risk_label": "中等风险",
  "abnormal_count": 2,
  "extracted_indicators": {
    "ALT": {"value": 120, "unit": "U/L", "severity": "moderate", "is_abnormal": true}
  },
  "summary": "本次肝功能检查发现 2 项指标异常…",
  "health_recommendations": ["尽量避免饮酒", "清淡饮食", "建议就医复诊"],
  "follow_up_plan": "建议 1-2 周内就医复诊",
  "urgency_level": "soon",
  "disclaimer": "本分析仅供参考，不能替代专业医生诊断。"
}
```

## Docker 部署

```bash
# 构建并启动
docker-compose up --build

# 后台运行
docker-compose up -d
```

## 技术栈

- **后端框架**：Flask 3.x
- **OCR**：PaddleOCR（支持中英文混合识别）
- **AI 分析**：OpenAI GPT-4 / 本地 Ollama LLM
- **PDF 处理**：pdf2image + PyPDF2
- **容器化**：Docker + Docker Compose
- **测试**：pytest + pytest-flask

## 项目结构

```
liver-function-report-analyzer/
├── backend/
│   ├── app/
│   │   ├── main.py                  # Flask 应用工厂
│   │   ├── config.py                # 配置管理
│   │   ├── routes/
│   │   │   └── reports.py           # API 端点
│   │   └── services/
│   │       ├── ocr_service.py       # OCR 识别服务
│   │       ├── medical_kb.py        # 医学知识库
│   │       ├── ai_analyzer.py       # AI 分析引擎
│   │       └── report_processor.py  # 报告处理流程
│   ├── main.py                      # 启动脚本
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── tests/                           # 单元测试 & 集成测试
├── docker-compose.yml
└── README.md
```

## 免责声明

本系统生成的分析报告**仅供参考**，不能替代执业医师的专业诊断和治疗建议。
如有健康疑虑，请及时就医。
