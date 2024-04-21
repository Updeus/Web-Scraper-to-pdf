import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import time
from tqdm import tqdm  # Progress bar library

def scrape_to_pdf(base_url, start_chapter, num_chapters, output_filename):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    doc = SimpleDocTemplate(output_filename, pagesize=letter)
    Story = []
    styles = getSampleStyleSheet()

    for i in tqdm(range(start_chapter, start_chapter + num_chapters)):
        chapter_url = f"{base_url}/chapter-{i}"
        response = requests.get(chapter_url, headers=headers)
        try:
            response.raise_for_status()  # Raise an exception for HTTP errors
            soup = BeautifulSoup(response.text, 'html.parser')

            # Title extraction and formatting
            novel_title = soup.find('a', class_='booktitle').text.strip() if soup.find('a', class_='booktitle') else "Unknown Novel"
            chapter_title = soup.find('div', class_='chapter-title').text.strip() if soup.find('div', class_='chapter-title') else f"Chapter {i}"

            title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], fontSize=18, spaceAfter=6, alignment=1)
            chapter_style = ParagraphStyle('ChapterStyle', parent=styles['Title'], fontSize=16, spaceBefore=12, spaceAfter=12, alignment=1)

            if i == start_chapter:  # Only add the novel title for the first chapter
                Story.append(Paragraph(novel_title, title_style))
            Story.append(Paragraph(chapter_title, chapter_style))

            # Content extraction and formatting
            content_div = soup.find('div', id='chapter-container')
            if content_div:
                style = styles["BodyText"]
                style.leading = 12
                for para in content_div.find_all('p'):
                    text = para.get_text(strip=True)
                    p = Paragraph(text, style)
                    Story.append(p)
                    Story.append(Spacer(1, 3))

            time.sleep(1)  # Delay to prevent being flagged as a bot
        except requests.HTTPError as e:
            print(f"Failed to download {chapter_url}: {e}")

    doc.build(Story)
    print(f"PDF created successfully: {output_filename}")

# Example usage
base_url = 'https://www.testsite'
start_chapter = 1
num_chapters = 5
output_filename = 'story.pdf'
scrape_to_pdf(base_url, start_chapter, num_chapters, output_filename)
