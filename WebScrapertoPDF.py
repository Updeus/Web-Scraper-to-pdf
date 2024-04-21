import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import random
import time
from tqdm import tqdm  # Progress bar library
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_chapter(chapter_url, headers, delay):
    time.sleep(delay)  # Implement the delay
    response = requests.get(chapter_url, headers=headers)
    response.raise_for_status()  # Check for HTTP errors
    return response.text

def process_chapter(chapter_html, styles, chapter_num):
    soup = BeautifulSoup(chapter_html, 'html.parser')

    # Extract titles and contents
    chapter_title = soup.find('span', class_='chapter-title').text.strip() if soup.find('span', class_='chapter-title') else f"Chapter {chapter_num}"
    content_div = soup.find('div', id='chapter-container')

    # Formatting styles
    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], fontSize=18, spaceAfter=6, alignment=1)
    chapter_style = ParagraphStyle('ChapterStyle', parent=styles['Title'], fontSize=16, spaceBefore=12, spaceAfter=12, alignment=1)
    story = [Paragraph(chapter_title, chapter_style)]

    # Process content
    if content_div:
        style = styles["BodyText"]
        style.leading = 12
        for para in content_div.find_all('p'):
            text = para.get_text(strip=True)
            p = Paragraph(text, style)
            story.append(p)
            story.append(Spacer(1, 12))
    return chapter_num, story

def scrape_to_pdf(base_url, start_chapter, num_chapters, output_filename):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0. Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    doc = SimpleDocTemplate(output_filename, pagesize=letter)
    styles = getSampleStyleSheet()
    chapter_contents = {}  # Dictionary to store chapter content by chapter number
    delays = [random.randint(1, 5) for _ in range(num_chapters)]
    start_time = time.time()  # Start timing the operation

    chapters_info = [(f"{base_url}/chapter-{i}", i, delays[i - start_chapter]) for i in range(start_chapter, start_chapter + num_chapters)]

    # Using ThreadPoolExecutor to manage threading
    with ThreadPoolExecutor(max_workers=6) as executor:
        future_to_info = {executor.submit(fetch_chapter, info[0], headers, info[2]): info for info in chapters_info}
        for future in tqdm(as_completed(future_to_info), total=len(chapters_info), desc="Downloading Chapters", unit="chapter"):
            info = future_to_info[future]
            try:
                html = future.result()
                chapter_num, chapter_elements = process_chapter(html, styles, info[1])
                chapter_contents[chapter_num] = chapter_elements  # Store chapters by number
            except Exception as exc:
                print(f"{info[0]} generated an exception: {exc}")

    # Append the collected stories to the document in the correct order
    ordered_chapters = []
    for chapter_num in sorted(chapter_contents.keys()):
        ordered_chapters.extend(chapter_contents[chapter_num])

    doc.build(ordered_chapters)  # Build the document once with the complete ordered story content

    total_time = time.time() - start_time  # Calculate the total operation time
    print(f"PDF created successfully: {output_filename}")
    print(f"Total operation time: {total_time:.2f} seconds.")

# Example usage
base_url = 'https://www.testsite/novel/novelTitle'
start_chapter = 1
num_chapters = 10
output_filename = 'story.pdf'
scrape_to_pdf(base_url, start_chapter, num_chapters, output_filename)
