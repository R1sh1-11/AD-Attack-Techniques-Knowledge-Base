import gradio as gr
from generate import ask

def handle_query(question):
    if not question.strip():
        return "Please enter a question.", ""
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources

with gr.Blocks(title="AD Attack Knowledge Base") as demo:
    gr.Markdown("# AD Attack Techniques Knowledge Base")
    gr.Markdown("Ask questions about Active Directory attacks, detections, and mitigations.")
    inp = gr.Textbox(label="Your question", placeholder="e.g. How does Kerberoasting work?")
    btn = gr.Button("Ask")
    answer = gr.Textbox(label="Answer", lines=10)
    sources = gr.Textbox(label="Sources", lines=3)
    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

demo.launch()