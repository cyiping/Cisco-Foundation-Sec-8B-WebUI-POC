# ==========================================
# 步驟 1: 安裝環境 (修正版)
# ==========================================
import subprocess
import sys

def install_env():
    print("正在準備環境，請稍候...")
    # 關鍵修正：移除 'torch'，使用 Kaggle 內建版本避免版本衝突
    packages = ["transformers", "accelerate", "bitsandbytes", "gradio"]
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q"] + packages)
    print("環境安裝完成！")

install_env()

# ==========================================
# 步驟 2: 載入模組
# ==========================================
import os
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

# ==========================================
# 步驟 3: 模型初始化 (針對 T4 優化)
# ==========================================
MODEL_ID = "fdtn-ai/Foundation-Sec-8B"
print(f"正在載入模型: {MODEL_ID} ...")

# 設定 4-bit 量化 (關鍵：讓 16GB VRAM 的 T4 跑得動且不爆顯存)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16
)

try:
    # 1. 載入 Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    # 修正 Llama 架構常見的 padding 問題
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # 2. 載入模型
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        quantization_config=bnb_config,
        device_map="auto",
        low_cpu_mem_usage=True
    )

    # 3. 建立 Pipeline
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        return_full_text=False # 只回傳生成的內容
    )
    print("模型載入成功！")

except Exception as e:
    print(f"模型載入失敗: {e}")
    # 若是私有模型需要 login，請取消註解下行
    # from huggingface_hub import login; login()
    raise e

WORKING_DIR = "/kaggle/working"
LOG_FILE = os.path.join(WORKING_DIR, "security_log.csv")

# ==========================================
# 步驟 4: 定義生成邏輯 (已加入 Penalty)
# ==========================================
def generate_security_analysis(prompt, max_tokens, temperature, top_p):
    start_time = time.time()
    try:
        # 4.1 加入 System Prompt 強化角色設定
        system_prompt = "You are a senior cyber security Engineer. Analyze the vulnerability concisely."
        full_prompt = f"{system_prompt}\n\nTask: {prompt}\n\nAnswer:"

        # 4.2 執行生成 (加入 repetition_penalty)
        output = pipe(
            full_prompt, 
            max_new_tokens=max_tokens, 
            do_sample=True, 
            temperature=temperature,
            top_p=top_p,
            pad_token_id=tokenizer.eos_token_id,
            # ---------------------------------------------------
            # ★ 關鍵修改：加入重複懲罰，數值建議 1.1 ~ 1.2
            # ---------------------------------------------------
            repetition_penalty=1.15 
        )
        
        response = output[0]['generated_text'].strip()
        
        # 4.3 記錄 Log
        duration = time.time() - start_time
        file_exists = os.path.isfile(LOG_FILE)
        with open(LOG_FILE, mode='a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "Prompt", "Response", "Duration"])
            writer.writerow([datetime.now(), prompt, response, f"{duration:.2f}"])
            
        return response
    except Exception as e:
        return f"發生錯誤: {str(e)}"

# ==========================================
# 步驟 5: 建立介面
# ==========================================

custom_css = """
.eta-stats {
    font-size: 30px !important;      
    line-height: 2.5 !important;     
    font-weight: bold !important;
    background: #FFF9C4 !important;  
    border: 4px solid #FBC02D !important;
    border-radius: 15px !important;
    padding: 10px 30px !important;
}
.generating {
    transform: scale(2.2) !important; 
    margin-right: 25px !important;
}
.title_center { text-align: center; }
.hint-text { font-size: 0.85em; color: #555; margin-bottom: 2px; }
"""

with gr.Blocks(title="Cisco Security Model POC", theme=gr.themes.Default(), css=custom_css) as demo:
    gr.Markdown("# 🛡️ Cisco Security Model POC (Anti-Loop Fix)", elem_classes="title_center")
    
    with gr.Row():
        # 左側：輸入與參數設定
        with gr.Column(scale=1):
            input_box = gr.Textbox(
                label="Security Prompt (提問)", 
                placeholder="例如：analysis CVE-2022-21540...",
                lines=8
            )
            
            with gr.Accordion("⚙️ 模型參數設定 (含建議值)", open=True):
                
                # Group 1: Max New Tokens
                gr.Markdown("**Max New Tokens**", elem_classes="hint-text")
                max_tokens_slider = gr.Slider(minimum=128, maximum=4096, value=1024, step=128, label=None)
                
                gr.HTML("<hr style='margin: 10px 0;'>")
                
                # Group 2: Temperature
                gr.Markdown("**Temperature**", elem_classes="hint-text")
                temp_slider = gr.Slider(minimum=0.1, maximum=1.0, value=0.1, step=0.1, label=None)
                
                gr.HTML("<hr style='margin: 10px 0;'>")
                
                # Group 3: Top-p
                gr.Markdown("**Top-p**", elem_classes="hint-text")
                top_p_slider = gr.Slider(minimum=0.1, maximum=1.0, value=0.9, step=0.05, label=None)

            with gr.Row():
                clear_btn = gr.Button("Clear (清除)")
                submit_btn = gr.Button("Submit (提交分析)", variant="primary")
            
        # 右側：輸出
        with gr.Column(scale=1):
            output_display = gr.Textbox(
                label="Generation Result (分析結果)", 
                placeholder="等待模型生成...",
                lines=25,
                interactive=False,
                show_copy_button=True
            )
            flag_btn = gr.Button("Flag (紀錄/標記問題)")

    # 綁定功能
    submit_btn.click(
        fn=generate_security_analysis, 
        inputs=[input_box, max_tokens_slider, temp_slider, top_p_slider], 
        outputs=output_display
    )
    clear_btn.click(fn=lambda: ["", ""], outputs=[input_box, output_display])

# 啟動服務
demo.launch(share=True, debug=True)