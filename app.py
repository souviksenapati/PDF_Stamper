from flask import Flask, render_template, request, send_file
import os
from stampV6 import add_stamp_to_pdf  # Import the function from your existing script

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_pdf = request.files['input_pdf']
        stamp_image = request.files['stamp_image']
        opacity = request.form['opacity']

        input_pdf_path = 'input.pdf'
        stamp_image_path = 'stamp.png'
        output_pdf_path = 'output.pdf'

        input_pdf.save(input_pdf_path)
        stamp_image.save(stamp_image_path)

        add_stamp_to_pdf(input_pdf_path, stamp_image_path, output_pdf_path, float(opacity))

        return send_file(output_pdf_path, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
