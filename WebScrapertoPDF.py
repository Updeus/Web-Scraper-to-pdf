import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def scrape_to_pdf(url, output_filename):
  
    response = requests.get(url)
    response.raise_for_status()  

   
    soup = BeautifulSoup(response.text, 'html.parser')

