# ==========================================
# 步驟 1: 安裝環境 (重啟 GPU 後必做)
# ==========================================
import subprocess
import sys

def install_env():
    print("正在準備環境，請稍候...")
    packages = ["sqlalchemy>=1.4", "transformers", "accelerate", "bitsandbytes", "gradio"]
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
from transformers import pipeline

# ==========================================
# 步驟 3: 模型初始化
# ==========================================
print("正在載入 Foundation-Sec-8B 模型...")

pipe = pipeline(
    "text-generation", 
    model="fdtn-ai/Foundation-Sec-8B",
    model_kwargs={
        "torch_dtype": torch.float16,
        "load_in_4bit": True,      
        "device_map": "auto"       
    }
)

WORKING_DIR = "/kaggle/working"
LOG_FILE = os.path.join(WORKING_DIR, "security_log.csv")

# ==========================================
# 步驟 4: 定義生成邏輯
# ==========================================
def generate_security_analysis(prompt, max_tokens, temperature, top_p):
    start_time = time.time()
    try:
        output = pipe(
            prompt, 
            max_new_tokens=max_tokens, 
            do_sample=True, 
            temperature=temperature,
            top_p=top_p
        )
        full_text = output[0]['generated_text']
        response = full_text[len(prompt):].strip() if full_text.startswith(prompt) else full_text
        
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
# 步驟 5: 建立介面 (參數與說明一對一組合)
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
/* 讓建議值的字體稍微縮小並帶點灰，更像註解 */
.hint-text { font-size: 0.85em; color: #555; margin-bottom: 2px; }
"""

with gr.Blocks(title="Cisco Security Model POC", theme=gr.themes.Default(), css=custom_css) as demo:
    gr.Markdown("# 🛡️ Cisco Security Model POC", elem_classes="title_center")
    
    with gr.Row():
        # 左側：輸入與參數設定
        with gr.Column(scale=1):
            input_box = gr.Textbox(
                label="Security Prompt (提問)", 
                placeholder="例如：請分析此 CVE 的補救建議...",
                lines=8
            )
            
            # 使用 Accordion 並在內部將說明與滑桿群組
            with gr.Accordion("⚙️ 模型參數設定 (含建議值)", open=True):
                
                # Group 1: Max New Tokens
                gr.Markdown("**Max New Tokens: 控制回覆長度**", elem_classes="hint-text")
                gr.Markdown("*建議：短分析設 512，完整報告設 2048*", elem_classes="hint-text")
                max_tokens_slider = gr.Slider(minimum=128, maximum=4096, value=2048, step=128, label=None)
                
                gr.HTML("<hr style='margin: 10px 0;'>") # 分隔線
                
                # Group 2: Temperature
                gr.Markdown("**Temperature: 控制隨機性 (越低越精準)**", elem_classes="hint-text")
                gr.Markdown("*建議：資安技術分析設 0.1 - 0.4*", elem_classes="hint-text")
                temp_slider = gr.Slider(minimum=0.1, maximum=1.0, value=0.4, step=0.1, label=None)
                
                gr.HTML("<hr style='margin: 10px 0;'>") # 分隔線
                
                # Group 3: Top-p
                gr.Markdown("**Top-p: 控制詞彙選擇範圍**", elem_classes="hint-text")
                gr.Markdown("*建議：保持在 0.9*", elem_classes="hint-text")
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