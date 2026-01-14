import subprocess
import sys
import os

# ==========================================
# 步驟 0: 自動安裝環境
# ==========================================
def install_dependencies():
    print("正在檢查與安裝必要套件...")
    try:
        # 在 Kaggle 安裝 bitsandbytes 需要一點時間
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "transformers", "accelerate", "bitsandbytes", "gradio", "huggingface_hub"
        ])
        print("環境安裝完成！")
    except Exception as e:
        print(f"安裝部分套件失敗 (若是 Kaggle 預裝環境通常可忽略): {e}")

install_dependencies()

# ==========================================
# 步驟 1: 載入模組
# ==========================================
import time
import csv
import torch
import gradio as gr
from datetime import datetime
from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer, 
    pipeline, 
    BitsAndBytesConfig
)
from huggingface_hub import login

# ==========================================
# 步驟 2: 模型與登入 (Kaggle Secrets 支援)
# ==========================================
# 如何在 Kaggle 設定 HF_TOKEN:
# 1. 在 Kaggle Notebook 頂部選單點擊 'Add-ons' -> 'Secrets'。
# 2. 點擊 'Add a new secret'。
# 3. Label 輸入 'HF_TOKEN'，Value 輸入您的 Hugging Face Access Token。
# 4. 勾選該 Secret 旁邊的 'Attached' 複選框以啟用它。
# 5. 確保 Notebook 右側面板的 'Internet' 選項已開啟 (On)。
try:
    from kaggle_secrets import UserSecretsClient
    user_secrets = UserSecretsClient()
    hf_token = user_secrets.get_secret("HF_TOKEN")
    if hf_token:
        login(token=hf_token)
        print("✅ Hugging Face 登入成功 (via Secrets)")
except Exception:
    print("ℹ️ 未設定 Kaggle Secret 'HF_TOKEN'，將以匿名模式下載模型。")

MODEL_ID = "fdtn-ai/Foundation-Sec-8B"
print(f"正在載入模型: {MODEL_ID} (這在 Kaggle 需要幾分鐘)...")

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16
)

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        quantization_config=bnb_config,
        device_map="auto",
        low_cpu_mem_usage=True
    )

    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        return_full_text=False 
    )
    print("🎉 模型載入成功！")

except Exception as e:
    print(f"❌ 模型載入失敗: {e}")
    print("請確認: 1. 右側 Internet 是否開啟?  2. 是否需要 HF_TOKEN?")
    raise e

# Log 設定 (Kaggle output path)
WORKING_DIR = "/kaggle/working" 
LOG_FILE = os.path.join(WORKING_DIR, "security_log.csv")

# ==========================================
# 步驟 3: 生成邏輯 (Completion Prompt)
# ==========================================
def generate_security_analysis(prompt, max_tokens, temperature, top_p):
    start_time = time.time()
    try:
        full_prompt = f"""[Security Analysis Report]
Topic: {prompt}
Date: {datetime.now().strftime('%Y-%m-%d')}
Analyst: Automated Security System
Analysis Details:
"""
        output = pipe(
            full_prompt, 
            max_new_tokens=max_tokens, 
            do_sample=True, 
            temperature=temperature,
            top_p=top_p,
            pad_token_id=tokenizer.eos_token_id,
            repetition_penalty=1.2 
        )
        
        response = output[0]['generated_text'].strip()
        if not response: response = "(無內容生成)"

        # 寫入 Log
        duration = time.time() - start_time
        # 確保目錄存在
        os.makedirs(WORKING_DIR, exist_ok=True)
        
        file_exists = os.path.isfile(LOG_FILE)
        with open(LOG_FILE, mode='a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "Prompt", "Response", "Duration", "Params"])
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                prompt, 
                response, 
                f"{duration:.2f}",
                f"T={temperature}"
            ])
        return response

    except Exception as e:
        return f"Error: {str(e)}"

# ==========================================
# 步驟 4: Gradio 介面
# ==========================================
custom_css = ".eta-stats { background: #f0f0f0 !important; }"

with gr.Blocks(title="Kaggle Security POC", theme=gr.themes.Soft(), css=custom_css) as demo:
    gr.Markdown("# 🛡️ Kaggle Security Model POC (T4 Optimized)")
    
    with gr.Row():
        with gr.Column(scale=1):
            input_box = gr.Textbox(label="Input", placeholder="Enter CVE or Topic...", lines=5)
            with gr.Accordion("Parameters", open=False):
                max_tokens = gr.Slider(64, 2048, 512, step=64, label="Max Tokens")
                temp = gr.Slider(0.1, 1.0, 0.4, step=0.1, label="Temperature")
                top_p = gr.Slider(0.1, 1.0, 0.9, step=0.05, label="Top-p")
            submit = gr.Button("Generate", variant="primary")
            
        with gr.Column(scale=1):
            output = gr.Textbox(label="Output", lines=20, interactive=False, show_copy_button=True)

    submit.click(generate_security_analysis, [input_box, max_tokens, temp, top_p], output)

# Kaggle 上必須設定 share=True
demo.launch(share=True, debug=True)