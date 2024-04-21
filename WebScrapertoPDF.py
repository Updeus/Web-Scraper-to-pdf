import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def scrape_to_pdf(url, output_filename):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    # Send HTTP request to the URL with custom headers
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors if the response isn't successful

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    # Ensure to enter the name of the div that contains the content you want to scrape
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
url = 'test.com'
output_filename = 'chapter_output.pdf'
scrape_to_pdf(url, output_filename)
