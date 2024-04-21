import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

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

    # Create a PDF file with the extracted text
    doc = SimpleDocTemplate(output_filename, pagesize=letter)
    Story = []
    styles = getSampleStyleSheet()
    style = styles["BodyText"]

    # Iterate through each paragraph and add it to the PDF
    for para in content_div.find_all('p'):
        text = para.get_text(strip=True)
        p = Paragraph(text, style)
        Story.append(p)
        Story.append(Spacer(1, 12))  # Adds space after each paragraph

    doc.build(Story)
    print(f"PDF created successfully: {output_filename}")

# Example usage
url = 'test.com'
output_filename = 'chapter_output.pdf'
scrape_to_pdf(url, output_filename)
