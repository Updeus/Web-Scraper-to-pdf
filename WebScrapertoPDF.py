import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def scrape_to_pdf(url, output_filename):
    # Send HTTP request to the URL
    response = requests.get(url)
    response.raise_for_status()  

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    content_div = soup.find('div', id='chapter-container')
    if content_div is None:
        print("No content found with the specified ID.")
        return

    # Extract text from the div
    text_content = content_div.get_text(separator='\n', strip=True)
    
    # Create a PDF file with the extracted text
    c = canvas.Canvas(output_filename, pagesize=letter)
    text = c.beginText(40, 750)
    text.setFont("Helvetica", 12)
    text.setLeading(14)
    
    # Split the content into lines and add to the PDF
    for line in text_content.split('\n'):
        text.textLine(line)
    
    c.drawText(text)
    c.save()
    print(f"PDF created successfully: {output_filename}")


# Example usage
url = 'enterurlhere.com'
output_filename = 'chapter_output.pdf'
scrape_to_pdf(url, output_filename)