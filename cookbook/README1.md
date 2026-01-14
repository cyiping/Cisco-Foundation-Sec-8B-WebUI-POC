# Cisco Foundation AI Cookbook (食譜)

歡迎來到 Cisco Foundation AI Cookbook！本儲存庫旨在協助您快速上手並有效利用 Cisco Foundation AI 團隊開發的各類模型。

本食譜涵蓋了眾多與網路安全相關的使用案例、部署選項，以及如微調 (finetuning) 等實用的模型適配方法。

如需了解本食譜的高層級概覽，請參閱我們的 [部落格介紹文章](https://www.linkedin.com/pulse/foundation-sec-8b-language-model-cybersecurity-introduction-cookbook-l9tsc)。

---

## 什麼是 Foundation AI？

Foundation AI 是 Cisco Security 內部的先鋒團隊，由人工智慧與網路安全領域的頂尖專家組成（這些專家隨 Robust Intelligence 被 Cisco 收購而加入）。我們的使命是挑戰 AI 與安全交匯點的極限。

我們開發尖端的開源模型與工具，旨在提升網路安全的未來。從保護當前的數位基礎設施，到預測未來的 AI 驅動挑戰，Foundation AI 正在塑造一個更安全、更智慧的未來。

- **[Foundation AI 官方網站](https://fdtn.ai/)**：我們持續發佈關於產品與研究的最新部落格。
- **[Hugging Face](https://huggingface.co/fdtn-ai)**：從此平台下載我們的模型。
- **[LinkedIn 專頁](https://www.linkedin.com/company/fdtn/)**：追蹤我們的最新動態。

**對預覽版模型感興趣嗎？請透過 [此表單](https://fdtn.ai/early-access) 申請早期存取！**

---

## 演示影片

[![](https://img.youtube.com/vi/ei5ND9bwmRo/0.jpg)](https://www.youtube.com/watch?v=ei5ND9bwmRo)

想在不寫程式的情況下在筆電上運行模型嗎？另一個演示影片展示了如何在 UI 上使用我們的模型。點擊 [這裡](https://github.com/cisco-foundation-ai/cookbook/tree/main/1_quickstarts) 觀看。

---

## 導覽本食譜

本食譜分為以下四大類別。請參閱各章節以獲取詳細指引：

### 1. [快速入門 (Quickstarts)](./1_quickstarts)
提供快速下載並使用模型進行入門主題的指南。
- **支援模型**：包含基礎模型 (Foundation-Sec-8B)、指令微調模型 (Instruct model) 以及預覽版的推理模型 (Reasoning model)。
- **硬體需求**：模型可以在單張 Nvidia A100 GPU 上運行。
- **LM Studio 支援**：想在不寫程式的情況下在筆電上運行模型嗎？[LM Studio](https://lmstudio.ai/) 是一個絕佳的工具。觀看我們的 [演示影片](https://www.youtube.com/watch?v=txIbkBX50MQ)。

### 2. [使用案例範例 (Examples)](./2_examples)
展示如何充分利用不同類型的模型來處理多種網路安全使用案例：

#### 基礎模型 (Base Model) 案例：
- **零樣本分類 (Zero-Shot Classification)**：利用困惑度評分 (Perplexity scoring) 進行分類。
- **日誌中的大海撈針 (Needle in the Logstack)**。

#### 指令微調模型 (Instruct Model) 案例：
- **YARA 模式生成 (YARA patterns)**
- **事件摘要 (Incident Summarization)**
- **MITRE 映射 (MITRE Mapping)**
- **建置環境安全 (Build Environment Security)**

#### 推理模型 (Reasoning Model) 案例：
- **端到端事件調查 (Incident Investigation e2e)**
- **OSINT 偵察與報告 (OSINT reporting)**
- **紅隊規劃 (Redteam Planning)**
- **漏洞利用生成 (Exploit Generation)**
- **根因分析 (Root Cause Analysis)**
- **警報優先級排序 (Alert Prioritization)**
- **配置評估 (Configuration Assessment)**

> **注意**：推理模型目前處於預覽模式，需透過 [此表單](https://fdtn.ai/early-access) 申請早期存取。

### 3. [模型採用與適配 (Adoptions)](./3_adoptions)
用於生產環境的模型使用筆記本與腳本。
- **[微調 (Finetuning)](./3_adoptions/finetuning)**：針對特定任務微調基礎模型的流程。
- **[量化模型 (Quantization)](./3_adoptions/quantization)**：用於輕量化推理的量化模型（如 GGUF 格式）。
- **[部署 (Deployments)](./3_adoptions/deployment)**：適用於多個平台（如 vLLM, TGI 等）的部署腳本範例。
- **[整合 (Integrations)](./3_adoptions/integrations)**：將 FoundationSec 模型整合至服務與工作流的腳本範例。

### 4. [文件與資源 (Documents)](./4_documents)
實用的文件與連結。
- **[常見問題 (FAQ)](./4_documents/FAQ.md)**：針對常見疑問的解答。
- **[參考資料 (Reference)](./4_documents/Reference.md)**：包含 Cisco 部落格、技術模型報告等資源連結。
- **[模型作為惡意軟體 (Models as Malware)](./4_documents/models_as_malware)**：探討 AI 模型安全性的相關研究。

---

## 貢獻指南

我們非常歡迎您的貢獻！如果您有任何問題、建議（包括缺失的使用案例）或發現任何問題，請開啟 Issue、發起討論或提交 Pull Request。
