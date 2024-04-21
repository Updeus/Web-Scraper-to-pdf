import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import time
import random
from tqdm import tqdm  # Progress bar library

def scrape_to_pdf(base_url, start_chapter, num_chapters, output_filename):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    doc = SimpleDocTemplate(output_filename, pagesize=letter)
    Story = []
    styles = getSampleStyleSheet()

    # Generate random delays for each chapter
    delays = [random.randint(1, 5) for _ in range(num_chapters)]
    total_delay = sum(delays)  # Total time for delays

    # Start progress bar
    with tqdm(total=num_chapters) as pbar:
        for i, delay in zip(range(start_chapter, start_chapter + num_chapters), delays):
            chapter_url = f"{base_url}/chapter-{i}"
            try:
                response = requests.get(chapter_url, headers=headers)
                response.raise_for_status()  # Check for HTTP errors
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract titles
                novel_title = soup.find('a', class_='booktitle').text.strip() if soup.find('a', class_='booktitle') else "Unknown Novel"
                chapter_title = soup.find('div', class_='chapter-title').text.strip() if soup.find('div', class_='chapter-title') else f"Chapter {i}"

                # Formatting styles
                title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], fontSize=18, spaceAfter=6, alignment=1)
                chapter_style = ParagraphStyle('ChapterStyle', parent=styles['Title'], fontSize=16, spaceBefore=12, spaceAfter=12, alignment=1)

                # Append titles to document
                if i == start_chapter:  # Only add the novel title for the first chapter
                    Story.append(Paragraph(novel_title, title_style))
                Story.append(Paragraph(chapter_title, chapter_style))

                # Extract and format content
                content_div = soup.find('div', id='chapter-container')
                if content_div:
                    style = styles["BodyText"]
                    style.leading = 12
                    for para in content_div.find_all('p'):
                        text = para.get_text(strip=True)
                        p = Paragraph(text, style)
                        Story.append(p)
                        Story.append(Spacer(1, 3))

                # Update progress and simulate delay
                pbar.update(1)
                pbar.set_description(f"Processing Chapter {i - start_chapter + 1}")
                time.sleep(delay)  # Wait for the randomly determined time
            except requests.HTTPError as e:
                print(f"Failed to download {chapter_url}: {e}")

    # Build the PDF with all chapters
    doc.build(Story)
    print(f"PDF created successfully: {output_filename}")
    print(f"Total operation time approximated to {total_delay} seconds.")

# Example usage
base_url = 'https://www.testurl'
start_chapter = 1
num_chapters = 10
output_filename = 'story.pdf'
scrape_to_pdf(base_url, start_chapter, num_chapters, output_filename)
