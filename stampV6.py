import argparse
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from PIL import Image
from reportlab.lib.utils import ImageReader

def add_stamp_to_pdf(input_pdf_path, stamp_image_path, output_pdf_path, opacity=0.5):
    input_pdf = PdfReader(open(input_pdf_path, "rb"))
    output = PdfWriter()

    stamp = Image.open(stamp_image_path)
    stamp = stamp.convert("RGBA")

    # Create a new image with adjusted opacity
    stamp_with_opacity = Image.new("RGBA", stamp.size)
    for x in range(stamp.width):
        for y in range(stamp.height):
            r, g, b, a = stamp.getpixel((x, y))
            stamp_with_opacity.putpixel((x, y), (r, g, b, int(a * opacity) if opacity < 1.0 else a))

    for page_num in range(len(input_pdf.pages)):
        page = input_pdf.pages[page_num]

        page_mediabox = page['/MediaBox']
        page_width = float(page_mediabox[2])
        page_height = float(page_mediabox[3])

        stamp_width, stamp_height = stamp.size

        scale_x = page_width / stamp_width
        scale_y = page_height / stamp_height
        scale_factor = min(scale_x, scale_y)

        stamp_with_opacity_resized = stamp_with_opacity.resize((int(stamp_width * scale_factor), int(stamp_height * scale_factor)))

        stamped_page_buffer = BytesIO()
        c = canvas.Canvas(stamped_page_buffer, pagesize=(page_width, page_height))

        x_offset = (page_width - stamp_with_opacity_resized.width) / 2
        y_offset = (page_height - stamp_with_opacity_resized.height) / 2

        stamp_buffer = BytesIO()
        stamp_with_opacity_resized.save(stamp_buffer, format="PNG")
        stamp_buffer.seek(0)
        stamp_reader = ImageReader(stamp_buffer)

        c.drawImage(stamp_reader, x_offset, y_offset, width=stamp_with_opacity_resized.width, height=stamp_with_opacity_resized.height, mask='auto', preserveAspectRatio=True)

        c.save()

        stamped_page = PdfReader(BytesIO(stamped_page_buffer.getvalue())).pages[0]
        stamped_page.merge_page(page)
        output.add_page(stamped_page)

    with open(output_pdf_path, "wb") as output_pdf:
        output.write(output_pdf)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add stamp to a PDF")
    parser.add_argument("input_pdf_path", help="Path to the input PDF file")
    parser.add_argument("stamp_image_path", help="Path to the stamp image file")
    parser.add_argument("output_pdf_path", help="Path for the output PDF file")
    parser.add_argument("--opacity", type=float, default=0.5, help="Opacity of the stamp (default: 0.5)")
    
    args = parser.parse_args()
    
    add_stamp_to_pdf(args.input_pdf_path, args.stamp_image_path, args.output_pdf_path, args.opacity)
