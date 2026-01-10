# 智能联网助手 (深度历史感知)

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/AI-Ollama-000000?logo=ollama&logoColor=white)](https://ollama.com/)
[![Playwright](https://img.shields.io/badge/Web-Playwright-45ba4b?logo=playwright&logoColor=white)](https://playwright.dev/)
[![License](https://img.shields.io/badge/License-Proprietary-red)](LICENSE)

> **一个基于开源大语言模型的智能本地 AI Agent，具备免费自主联网搜索、混合记忆管理和上下文感知查询重写功能。**

## 📖 项目概述

**Smart Online Assistant** 是一个“隐私优先”的本地 AI Agent，由 **Ollama** (LLM) 和 **Playwright** 驱动。与普通聊天机器人不同，它打通了离线隐私与实时信息之间的壁垒。

它实现了一套 **RAG (检索增强生成)** 工作流：能在必要时自主浏览网页，根据对话历史重写搜索查询，并通过独特的 **混合记忆 (Raw/Zip)** 系统管理上下文，确保回答既实时又准确。

## ✨ 核心功能

*   **🌐 自主联网搜索**: 使用 Playwright 模拟人类浏览行为 (DuckDuckGo)，自动处理翻页和反爬虫机制，无需 API 费用即可获取实时数据。
*   **🧠 混合记忆架构**:
    *   **Raw 模式**: 保留完整的全文对话历史。
    *   **Zip 模式**: 自动总结过往交互内容，在保留关键事实的同时大幅节省上下文 Token。
*   **🔄 上下文感知意图分析**: Agent 会分析你的意图 (`analyze_intent`) 并利用近期历史重写搜索关键词，确保搜索结果与当前对话高度相关。
*   **⚡ 本地与隐私**: 完全由本地模型驱动 (如 `qwen3:30b-instruct`)。所有数据均保留在你的机器上。
*   **🛠️ 完全掌控**: 支持通过指令强制搜索 (`/s`)、强制离线 (`/n`) 或即时切换记忆模式。

## 🚀 快速开始

### 前置条件
1.  已安装 **Python 3.9+**。
2.  已安装并运行 **[Ollama](https://ollama.com/)**。

### 安装步骤

1.  **克隆仓库** (如果适用) 或下载源码。

2.  **安装 Python 依赖**:
    ```bash
    cd hybrid_agent_project
    pip install -r requirements.txt
    ```

3.  **安装 Playwright 浏览器**:
    ```bash
    playwright install chromium
    ```

4.  **准备模型**:
    拉取所需的模型 (请确保与 `config.py` 中的 `MODEL_NAME` 一致):
    ```bash
    ollama run qwen3:30b-instruct
    # 等待模型下载完成
    ```

### 运行助手

运行主脚本:
```bash
python main.py
```

或者作为模块运行:
```bash
python -m hybrid_agent_project.main
```

## 💡 使用指南

启动后，你可以自然地与 Agent 对话，或使用以下指令：

| 指令 | 说明 |
| :--- | :--- |
| `/s <文本>` | **强制搜索**: 基于历史 + `<文本>` 重写查询词并进行联网搜索。 |
| `/n <文本>` | **不搜索**: 强制 LLM 仅利用内部知识/记忆进行回答。 |
| `/raw` | 切换记忆至 **全文 (Full-text)** 模式。 |
| `/zip` | 切换记忆至 **总结 (Summarized)** 模式 (节省 Token)。 |
| `/clear` | 清除所有对话历史。 |
| `exit` / `q` | 退出程序。 |

### 📄 真实案例
> **请查看 [`real_chat.txt`](real_chat.txt) 获取完整的真实对话日志、搜索流程以及记忆压缩的实录。**

### 输出示例
```text
You [📉 compressed]: /s Bill Gates net worth
🔧 [manual force-search] Assistant rewrites query -> Bill Gates net worth 2026
>> 🌐 Performing web search and simulated pagination...
AI is thinking...
AI: ... (根据实时搜索结果回答)
```

## ⚙️ 配置说明

编辑 `config.py` 可自定义 Agent 的行为：

*   `MODEL_NAME`: 用于对话的 Ollama 模型 (默认: `qwen3:30b-instruct`)。
*   `SUMMARY_MODEL`: 用于压缩/总结记忆的模型。
*   `HIDE_WINDOW`: 设为 `False` 可实时观看浏览器爬取过程 (Headless 模式)。
*   `HISTORY_LIMIT`: 用于意图分析的历史轮数。
*   `MEMORY_FILE`: JSON 记忆文件的路径。

## 📂 项目结构

```text
hybrid_agent_project/
├── agent.py              # 核心逻辑：结合 LLM、记忆和搜索
├── search.py             # 网页爬取：集成 Playwright & DuckDuckGo
├── memory.py             # 记忆系统：JSON 处理 & 自动总结
├── config.py             # 设置：模型名、超时、搜索限制
├── main.py               # 入口点：CLI 交互循环
├── utils.py              # 辅助工具：文本处理
├── real_chat.txt         # 真实使用案例日志
└── requirements.txt      # 依赖列表
```

## ⚠️ License / Copyright

**Copyright (c) 2026 Feng Simo. All rights reserved.**

This code is for **demonstration purposes only**. You may not use, modify, distribute, or sublicense this code without explicit permission.