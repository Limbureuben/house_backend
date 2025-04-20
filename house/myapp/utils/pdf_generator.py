from xhtml2pdf import pisa
from django.template.loader import get_template
import os

def generate_booking_pdf(booking, filename):
    template = get_template('pdf/booking_agreement.html')
    html = template.render({'booking': booking})

    pdf_path = os.path.join('media/pdfs', filename)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    with open(pdf_path, 'wb+') as pdf_file:
        pisa.CreatePDF(html, dest=pdf_file)

    return pdf_path
