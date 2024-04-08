from flask import Flask, render_template, request
import fitz
import tempfile
import base64

app = Flask(__name__)

extracted_text = ""  # Variable to store the extracted text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_pdf_to_html():
    global extracted_text  # Reference to the global variable

    uploaded_file = request.files['file']
    print("Uploaded file name:", uploaded_file.filename)  # Debugging statement
    if uploaded_file.filename != '':
        pdf_file = uploaded_file.read()
        extracted_text, extracted_images = extract_text_and_images_from_pdf(pdf_file)
        return render_template('result.html', pdf_text=extracted_text, pdf_images=extracted_images)
    return "No file selected"

def extract_text_and_images_from_pdf(pdf_file):
    extracted_text = ''
    extracted_images = []

    with tempfile.NamedTemporaryFile(delete=False) as temp_pdf:
        temp_pdf.write(pdf_file)
        temp_pdf_path = temp_pdf.name

    pdf_document = fitz.open(temp_pdf_path)

    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        extracted_text += page.get_text() + "\n\n"

        images = page.get_images(full=True)
        for img_info in images:
            try:
                if isinstance(img_info, dict):
                    image_ref = list(img_info.keys())[0]
                else:
                    image_ref = img_info[0]
                image_bytes = pdf_document.extract_image(image_ref)["image"]
                encoded_image = base64.b64encode(image_bytes).decode('utf-8')
                extracted_images.append(encoded_image)
                # Add base64 encoded image string to the extracted text
                extracted_text += f"Base64 Encoded Image: {encoded_image}\n\n"
            except Exception as e:
                print("Error extracting image:", e)

    return extracted_text, extracted_images

if __name__ == '__main__':
    app.run(debug=True)