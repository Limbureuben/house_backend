from xhtml2pdf import pisa
from django.template.loader import get_template
from io import BytesIO

def generate_booking_pdf(booking):
    template = get_template('pdf/booking_agreement.html')
    html = template.render({'booking': booking})

    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)

    if pisa_status.err:
        return None

    return result.getvalue()  # Returns PDF as bytes
