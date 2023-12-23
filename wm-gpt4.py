from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfWriter, PdfReader
import numpy as np
from PIL import Image
from pdf2image import convert_from_path
import gradio as gr
import os

def add_watermark_to_pdf(input_pdf, 
                         output_pdf, 
                         watermark_text, 
                         watermark_size, 
                         watermark_opacity,
                         angle=-30):
    """
    Add four watermarks to the center axes of each page in a PDF file.

    Parameters:
    input_pdf (str): The path to the input PDF file.
    output_pdf (str): The path to the output PDF file with watermarks added.
    watermark_text (str): The text content of the watermark.
    watermark_size (int): The font size of the watermark, range 8 to 24.
    watermark_opacity (float): The opacity of the watermark, range 0 to 1 (0% to 100%).

    Returns:
    None
    """

    # Read the original PDF to determine the page size
    original_pdf = PdfReader(input_pdf)
    first_page = original_pdf.pages[0]
    page_width = first_page.mediabox[2]
    page_height = first_page.mediabox[3]

    # Create a PDF for the watermark
    c = canvas.Canvas("watermark.pdf", pagesize=(page_width, page_height))
    c.setFont("Times-Roman", watermark_size)
    c.setFillAlpha(watermark_opacity)
    
    # Calculate positions for watermarks on the center axes
    x_positions = [page_width / 4, page_width / 4 * 3]
    y_positions = [page_height / 4, page_height / 4 * 2, page_height / 4 * 3]
    
    for x in x_positions:
        for y in y_positions:
            c.saveState()
            c.translate(x, y)
            c.rotate(angle)
            c.drawCentredString(0, 0, watermark_text)
            c.restoreState()
    
    c.save()

    # Create a PdfWriter object for the output PDF
    pdf_writer = PdfWriter()

    # Add watermark to each page
    watermark_pdf = PdfReader("watermark.pdf")
    watermark_page = watermark_pdf.pages[0]

    for page in original_pdf.pages:
        page.merge_page(watermark_page)
        pdf_writer.add_page(page)


    
    # Write the output PDF file
    with open(output_pdf, 'wb') as output_file:
        pdf_writer.write(output_file)

def preview_watermarked_pdf_page(#page_number=0
                                ):
    """
    Convert the specified page of a PDF file to a numpy array or PIL image for preview.

    Parameters:
    output_pdf (str): The path to the watermarked PDF file.
    page_number (int): The page number to preview (starting from 0 for the first page).

    Returns:
    image (PIL.Image.Image): The PIL image of the specified page.
    """
    # Convert the specified page of the PDF to an image
    page_number=0
    images = convert_from_path("output.pdf", first_page=page_number + 1, last_page=page_number + 1)
    
    # Since we are converting only one page, we'll get only one image in the list
    image = images[0]
    
    return image

# Example usage:
# add_watermark_to_pdf(r'input.pdf', 'output.pdf', 'CONFIDENTIAL', 30, 0.4)

with gr.Blocks() as demo:
    file_choose = gr.File(label="选择PDF文件",
                          file_count="single",
                          file_types=["pdf"])
    watermark_text = gr.Textbox(label="水印文字", value="CONFIDENTIAL")
    watermark_size = gr.Slider(label="水印文字大小", minimum=1, maximum=100, value=30)
    watermark_opacity = gr.Slider(label="水印文字透明度", minimum=0.1, maximum=1, value=0.4)
    angle = gr.Slider(label="水印文字旋转角度", minimum=-180,maximum=180, value=-30)
    output_pdf = gr.Textbox(label="输出文件名称", value="output.pdf")
    pdf_preview = gr.Image(label="PDF预览",
                           type="pil")
    gen = gr.Button(value="生成水印", variant="primary")

    gen.click(add_watermark_to_pdf,
            inputs=[file_choose,output_pdf,watermark_text,watermark_size,watermark_opacity,]
            ).then(preview_watermarked_pdf_page,
                    outputs=pdf_preview)

demo.queue().launch(inbrowser=True,debug=True,show_api=False)

'''
下面是非 Gradio 测试


image = preview_watermarked_pdf_page('output.pdf', 0)

# To display the image using PIL
image.show()

# To convert the image to a numpy array and display using matplotlib (if needed)
import matplotlib.pyplot as plt

image_np = np.array(image)
plt.imshow(image_np)
plt.axis('off')  # Hide the axis
plt.show()
'''