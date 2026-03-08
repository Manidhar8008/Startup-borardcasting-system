"""
JAN App UI

Defines the Gradio interface for the application.
"""
import gradio as gr
from core.jan_engine import run_pipeline

def create_ui() -> gr.Blocks:
    """
    Creates and configures the Gradio web interface.
    
    Returns:
        A gr.Blocks application instance.
    """
    with gr.Blocks(title="JAN MVP") as app:
        gr.Markdown("# JAN AI Social Media Agent")
        
        with gr.Row():
            idea_input = gr.Textbox(
                label="Content Idea", 
                placeholder="Enter your idea here..."
            )
        
        generate_btn = gr.Button("Generate", variant="primary")
        output_display = gr.Textbox(label="Pipeline Output", interactive=False)
        
        generate_btn.click(
            fn=run_pipeline,
            inputs=[idea_input],
            outputs=[output_display]
        )
        
    return app
