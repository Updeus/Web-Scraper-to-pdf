import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
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

    # Find the title of the novel and chapter title
    novel_title = soup.find('a', class_='booktitle').text.strip() if soup.find('a', class_='booktitle') else "Unknown Novel"
    chapter_title = soup.find('span', class_='chapter-title').text.strip() if soup.find('span', class_='chapter-title') else "Unknown Chapter"

    # Find the content division
    content_div = soup.find('div', id='chapter-container')
    if content_div is None:
        print("No content found with the specified ID.")
        return

    # Create a PDF file with the extracted text
    doc = SimpleDocTemplate(output_filename, pagesize=letter)
    Story = []
    styles = getSampleStyleSheet()
    
    # Title styles
    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], fontSize=18, spaceAfter=6, alignment=1)  # Centered
    chapter_style = ParagraphStyle('ChapterStyle', parent=styles['Title'], fontSize=16, spaceBefore=12, spaceAfter=12, alignment=1)  # Centered

    # Add novel title and chapter title to the document
    Story.append(Paragraph(novel_title, title_style))
    Story.append(Paragraph(chapter_title, chapter_style))

    # Normal text style
    style = styles["BodyText"]
    style.leading = 12  # Adjusts the line spacing within paragraphs

    # Iterate through each paragraph and add it to the PDF
    for para in content_div.find_all('p'):
        text = para.get_text(strip=True)
        p = Paragraph(text, style)
        Story.append(p)
        Story.append(Spacer(1, 3))  # Adjusts space between paragraphs

    doc.build(Story)
    print(f"PDF created successfully: {output_filename}")

# Example usage
url = 'test.com'
output_filename = 'chapter_output.pdf'
scrape_to_pdf(url, output_filename)
