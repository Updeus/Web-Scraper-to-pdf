import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import random
import time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

# Define the absolute path to the font, make sure to download a ttf font that has support for Asian languages
font_path = os.path.join('C:\\Users\\jarod\\Desktop\\Projects\\Web Scraper to pdf', 'DroidSansFallback.ttf')

# Register the font using the absolute path
pdfmetrics.registerFont(TTFont('DroidSansFallback', font_path))

def fetch_chapter(chapter_url, headers, delay, retry=0):
    time.sleep(delay)  # Implement the delay
    try:
        response = requests.get(chapter_url, headers=headers)
        response.raise_for_status()  # Check for HTTP errors
        return response.text
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429 and retry < 5:  # Check if it's a 'Too Many Requests' error
            wait = 2 ** retry  # Exponential backoff
            print(f"Rate limit exceeded. Retrying in {wait} seconds...")
            time.sleep(wait)
            return fetch_chapter(chapter_url, headers, delay, retry+1)  # Retry with increased backoff
        else:
            raise

def process_chapter(chapter_html, styles, chapter_num):
    soup = BeautifulSoup(chapter_html, 'html.parser')
    chapter_title = soup.find('span', class_='chapter-title').text.strip() if soup.find('span', class_='chapter-title') else f"Chapter {chapter_num}"
    content_div = soup.find('div', id='chapter-container')
    novel_title = soup.find('a', class_='booktitle').text.strip() if soup.find('a', class_='booktitle') else "Unknown Novel"

    # Using registered font
    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], fontName='DroidSansFallback', fontSize=18, spaceAfter=6, alignment=1)
    chapter_style = ParagraphStyle('ChapterStyle', parent=styles['Title'], fontName='DroidSansFallback', fontSize=16, spaceBefore=12, spaceAfter=12, alignment=1)
    story = [Paragraph(novel_title, title_style) if chapter_num == 1 else Paragraph(chapter_title, chapter_style)]

    if content_div:
        style = styles["BodyText"]
        style.fontName = 'DroidSansFallback'  # Apply the CJK-compatible font to the body text
        style.leading = 12
        for para in content_div.find_all('p'):
            text = para.get_text(strip=True)
            p = Paragraph(text, style)
            story.append(p)
            story.append(Spacer(1, 3))

    return chapter_num, story, novel_title if chapter_num == 1 else None

def scrape_to_pdf(base_url, start_chapter, num_chapters):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    styles = getSampleStyleSheet()
    chapter_contents = {}  # Dictionary to store chapter content by chapter number
    failed_chapters = []   # List to store failed chapter fetch attempts
    delays = [random.randint(1, 3) for _ in range(num_chapters)]
    start_time = time.time()  # Start timing the operation
    novel_title = "Unknown Novel"

    chapters_info = [(f"{base_url}/chapter-{i}", i, delays[i - start_chapter]) for i in range(start_chapter, start_chapter + num_chapters)]

    # Using ThreadPoolExecutor to manage threading
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_info = {executor.submit(fetch_chapter, info[0], headers, info[2]): info for info in chapters_info}
        for future in tqdm(as_completed(future_to_info), total=len(chapters_info), desc="Downloading Chapters", unit="chapter"):
            info = future_to_info[future]
            try:
                html = future.result()
                chapter_num, chapter_elements, fetched_novel_title = process_chapter(html, styles, info[1])
                if fetched_novel_title:
                    novel_title = fetched_novel_title  # Set novel title from the first chapter
                chapter_contents[chapter_num] = chapter_elements  # Store chapters by number
            except Exception as exc:
                print(f"{info[0]} generated an exception: {exc}")
                failed_chapters.append(info)  # Add to failed chapters for retry

    # Retry failed chapters
    if failed_chapters:
        print("Retrying failed chapters...")
        with ThreadPoolExecutor(max_workers=1) as executor: #set workers to lowest number possible as failsafe
            retry_future_to_info = {executor.submit(fetch_chapter, info[0], headers, 10): info for info in failed_chapters}  # Increased delay for retry
            for future in tqdm(as_completed(retry_future_to_info), total=len(retry_future_to_info), desc="Retrying Chapters", unit="chapter"):
                info = retry_future_to_info[future]
                try:
                    html = future.result()
                    chapter_num, chapter_elements, _ = process_chapter(html, styles, info[1])
                    chapter_contents[chapter_num] = chapter_elements  # Store retried chapters
                except Exception as exc:
                    print(f"Retry failed for {info[0]} with exception: {exc}")
                    
    # Build the PDF with all chapters
    output_filename = f"{novel_title}.pdf"  # Use novel title for the PDF filename
    doc = SimpleDocTemplate(output_filename, pagesize=letter)
    ordered_chapters = []
    for chapter_num in sorted(chapter_contents.keys()):
        ordered_chapters.extend(chapter_contents[chapter_num])

    doc.build(ordered_chapters)  # Build the document once with the complete ordered story content

    total_time = time.time() - start_time  # Calculate the total operation time
    print(f"PDF created successfully: {output_filename}")
    print(f"Total operation time: {total_time:.2f} seconds.")

# Example usage
base_url = 'https://www.lightnovelpub.com/novel/reverend-insanity-172'
start_chapter = 2250
num_chapters = 74
scrape_to_pdf(base_url, start_chapter, num_chapters)