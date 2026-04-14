# 开发指南

本文档为开发者提供本地开发、测试和贡献代码的完整指引。

## 开发环境搭建

### 前置要求

- Python 3.9+
- pip
- （可选）Docker & Docker Compose
- （可选）Poppler（pdf2image 依赖，PDF 处理时需要）

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/lr0326/liver-function-report-analyzer.git
cd liver-function-report-analyzer

# 2. 创建并激活虚拟环境（推荐）
python -m venv .venv
source .venv/bin/activate          # Linux/macOS
# .venv\Scripts\activate            # Windows

# 3. 安装依赖
cd backend
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env，至少填写 OPENAI_API_KEY

# 5. 启动开发服务器
python main.py
```

服务默认在 `http://localhost:5000` 运行，可通过 `FLASK_ENV=development` 启用热重载。

## 项目结构说明

```
backend/
├── app/
│   ├── main.py            # Flask 应用工厂 (create_app)
│   ├── config.py          # 配置类 (Development / Production / Testing)
│   ├── routes/
│   │   └── reports.py     # API 路由：/api/reports/*
│   └── services/
│       ├── ocr_service.py      # OCR 与文本解析
│       ├── medical_kb.py       # 医学知识库与指标评估
│       ├── ai_analyzer.py      # AI 分析（OpenAI / 本地 LLM）
│       └── report_processor.py # 端到端流程编排
├── main.py        # 应用启动入口（gunicorn 兼容）
├── requirements.txt
├── .env.example
└── Dockerfile
tests/
├── conftest.py            # pytest fixtures
├── test_medical_kb.py     # 医学知识库单元测试
├── test_ocr_service.py    # OCR 文本解析单元测试
├── test_ai_analyzer.py    # AI 分析引擎单元测试
├── test_report_processor.py  # 报告处理流程单元测试
└── test_api.py            # Flask API 集成测试
```

## 运行测试

```bash
# 从项目根目录运行
pytest tests/ -v

# 运行单个测试文件
pytest tests/test_medical_kb.py -v

# 带覆盖率报告
pytest tests/ --cov=backend/app --cov-report=term-missing
```

## 代码规范

- **Python 版本**：3.9+，类型注解全覆盖
- **格式化工具**：建议使用 `ruff format` 或 `black`
- **Linting**：建议使用 `ruff check` 或 `flake8`
- **注释语言**：代码注释和 docstring 使用英文

## 添加新的肝功能指标

在 `backend/app/services/medical_kb.py` 的 `_INDICATORS` 字典中添加一个新的 `IndicatorInfo` 对象：

```python
"NEWINDICATOR": IndicatorInfo(
    code="NEWINDICATOR",
    chinese_name="中文名",
    english_name="English Name",
    reference_ranges=[
        ReferenceRange(low=X, high=Y, unit="U/L"),
    ],
    clinical_significance="临床意义说明",
    high_description="升高时的意义",
    low_description="降低时的意义",
    related_conditions=["相关疾病1", "相关疾病2"],
),
```

同时在 `backend/app/services/ocr_service.py` 的 `INDICATOR_ALIASES` 中添加对应的识别别名。

## 配置 AI 分析

### 使用 OpenAI

在 `.env` 中配置：
```env
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-4
```

### 使用本地 LLM（Ollama）

1. 安装并启动 [Ollama](https://ollama.ai)
2. 拉取模型：`ollama pull llama3`
3. 在 `.env` 中配置：
```env
USE_LOCAL_LLM=True
LOCAL_LLM_URL=http://localhost:11434
LOCAL_LLM_MODEL=llama3
```

### 无 LLM 模式

不配置任何 API key 时，系统自动使用基于规则的分析引擎，仍可提供基础的异常标记和健康建议。

## Docker 构建

```bash
# 构建镜像
docker build -t liver-analyzer-backend ./backend

# 单独运行容器
docker run -p 5000:5000 --env-file ./backend/.env liver-analyzer-backend

# 使用 docker-compose
docker-compose up --build
```

## 贡献流程

1. Fork 本仓库并创建特性分支
2. 编写代码并添加对应单元测试
3. 确认所有测试通过：`pytest tests/ -v`
4. 提交 Pull Request，描述变更内容
