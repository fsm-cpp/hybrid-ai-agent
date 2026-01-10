# 智能联网助手 (深度历史感知)

这是一个基于 Ollama 和 Playwright 的智能AI本地大模型助手，具备联网搜索和混合记忆功能。它能够理解对话上下文，重构搜索关键词，并根据实时搜索结果和历史对话进行回答。

## 项目结构

```
hybrid_agent_project/
├── config.py             # 全局配置和常量，例如模型名称、上下文窗口、搜索结果数量等。
├── utils.py              # 通用辅助函数，如限制历史消息数量。
├── memory.py             # 记忆管理模块，处理对话历史的加载、保存和压缩。
├── search.py             # 网络搜索功能模块，使用Playwright进行网页搜索和内容提取。
├── agent.py              # 核心AI代理模块，整合记忆管理、搜索和LLM交互逻辑。
├── main.py               # 程序入口，负责初始化和运行AI助手。
├── requirements.txt      # 项目依赖列表。
├── README.md             # 项目说明文件。
└── hybrid_memory.json # 记忆文件，存储对话历史，程序运行时自动创建或更新。
```

## 功能特点

*   **混合记忆模式**: 支持"原文模式"（`raw`）和"压缩模式"（`zip`），在压缩模式下，AI会自动提炼回答摘要以节省上下文。
*   **深度历史感知**: `analyze_intent` 函数结合受限的对话历史来重构搜索关键词，使搜索更精准。
*   **智能联网搜索**: 使用 DuckDuckGo 进行搜索，并通过 Playwright 模拟浏览器操作，包括翻页和内容抓取。
*   **指令控制**:
    *   `/s <内容>`: 强制联网搜索，AI会根据历史和 `<内容>` 重新生成搜索词。
    *   `/n <内容>`: 强制不联网搜索，仅根据已知知识和记忆回答 `<内容>`。
    *   `/raw`: 切换记忆模式到原文模式。
    *   `/zip`: 切换记忆模式到压缩模式。
    *   `/clear`: 清空所有历史记忆。
    *   `exit`, `quit`, `退出`, `q`: 退出程序。
*   **自定义配置**: 所有的关键参数都可在 `config.py` 文件中进行调整。

## 环境准备

1.  **Python 环境**: 确保你的系统安装了 Python 3.9+。

2.  **Ollama**:
    *   安装 Ollama 服务：访问 [ollama.com](https://ollama.com/) 下载并安装。
    *   拉取所需的模型（例如 `qwen3:30b-instruct`）。在终端运行：
        ```bash
        ollama run qwen3:30b-instruct
        # 等待模型下载完成
        ```
        请确保 `config.py` 中 `MODEL_NAME` 和 `SUMMARY_MODEL` 设置的模型已拉取。

3.  **安装项目依赖**:
    ```bash
    cd hybrid_agent_project
    pip install -r requirements.txt
    ```

4.  **安装 Playwright 浏览器**:
    ```bash
    playwright install chromium
    ```

## 运行项目

在 `hybrid_agent_project` 目录下，运行 `main.py` 文件：

```bash
python main.py
```

或者作为模块运行：

```bash
python -m hybrid_agent_project.main
```

## 使用说明

启动程序后，你将看到如下提示：

```
=== 智能联网助手 V7.0 (深度历史感知) ===
指令: /s <内容> 强搜(AI改写词) | /n <内容> 禁搜 | /raw 原文 | /zip 压缩 | /clear 清空记忆
--------------------------------------------------

你 [📉压缩]:
```

你可以输入你的问题或使用指令来与AI互动。

**示例对话：**

```
你 [📉压缩]: 最近有什么关于AI模型的新进展？
AI 正在思考...
AI: ... (AI会联网搜索并给出回答)

你 [📉压缩]: /s 比尔盖茨的净资产是多少？
🔧 [手动强搜] AI 基于背景重构关键词 -> 比尔盖茨 净资产
>> 🌐 正在联网检索并模拟翻页: 比尔盖茨 净资产
... (搜索过程)
AI 正在思考...
AI: ... (AI会根据搜索结果回答)

你 [📉压缩]: /raw
>> 模式已切换到: raw
你 [📝原文]: 他最近有什么新的慈善项目吗？
AI 正在思考...
AI: ... (AI会根据历史对话和可能的新搜索回答，这里的"他"会识别为比尔盖茨)

你 [📝原文]: /clear
记忆已清空！
你 [📝原文]:
```
**真实对话：**
```
见real_chat.txt
```


## 配置修改

你可以修改 `config.py` 中的参数来调整助手的行为：

*   `MODEL_NAME`, `SUMMARY_MODEL`: 更改使用的Ollama模型。
*   `HEADLESS`, `HIDE_WINDOW`: 控制Playwright浏览器是否显示。
*   `CONTEXT_WINDOW`: 设置Ollama模型的上下文窗口大小。
*   `MAX_SEARCH_RESULTS`, `MAX_PAGES_TO_SCAN`: 调整搜索行为。
*   `HISTORY_LIMIT`: 调整AI在分析意图时考虑的历史对话轮数。
*   `MEMORY_FILE`: 修改记忆文件的名称。

## 注意事项

*   网络搜索的成功率取决于网络状况和目标网站的反爬机制。
*   Ollama模型的性能和回答质量取决于所选模型的尺寸和能力。
*   如果需要完全隐藏浏览器：`HIDE_WINDOW = True`。
*   如果想要看到浏览器：`HIDE_WINDOW = False`。


## ⚠️ License / Copyright (版权声明)

**Copyright (c) 2026 Feng Simo. All rights reserved.**

This code is for demonstration purposes only. You may not use, modify, distribute, or sublicense this code.

(本项目仅供展示，保留所有权利。严禁使用、修改、分发或再次许可本项目代码。)
