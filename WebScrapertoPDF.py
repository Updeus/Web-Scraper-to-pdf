import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def scrape_to_pdf(url, output_filename):
  
    response = requests.get(url)
    response.raise_for_status()  

   
    soup = BeautifulSoup(response.text, 'html.parser')

    content_div = soup.find('div', id='chapter-container')
    if content_div is None:
        print("No content found with the specified ID.")
        return

    
    text_content = content_div.get_text(separator='\n', strip=True)
    
    
    c = canvas.Canvas(output_filename, pagesize=letter)
    text = c.beginText(40, 750)
    text.setFont("Helvetica", 12)
    text.setLeading(14)
    
    
    for line in text_content.split('\n'):
        text.textLine(line)
    
    c.drawText(text)
    c.save()
    print(f"PDF created successfully: {output_filename}")