import re
import PyPDF2
from curl_cffi import requests
import time
import random

class DataCleaner:
    @staticmethod
    def clean_text(text):
        # Remove all non-letter characters and convert to lowercase
        return re.sub(r'[^a-zA-Z]', '', text).lower()
    

class FileHandler:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_lines(self):
        with open(self.file_path, 'r') as file:
            return [line.strip() for line in file]

    def write_lines(self, lines):
        with open(self.file_path, 'w') as file:
            for line in lines:
                file.write(line + '\n')
    

class PdfHandler:
    def __init__(self, session: requests.Session):
        self.session = session

    def is_duplicate(self, title: str, file_path: str):        
        file_handler = FileHandler(file_path)
        data_cleaner = DataCleaner()
        clean_title = data_cleaner.clean_text(title)
        existing_titles = file_handler.read_lines()
        if clean_title in [data_cleaner.clean_text(t) for t in existing_titles]:
            return True
        else:
            return False
        
    def extract_text_from_pdf(self, pdf_path: str):
        content = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file) 
            for page in reader.pages:
                content += page.extract_text()
        return content
    
    def download_pdf(self, item: dict, save_folder: str):
        print("timeout de 5 a 10 minutos...")
        #time.sleep(random.uniform(300, 600))      # espera entre 5 a 10 minutos para cada requisição de PDF (culpada por erro HTTP 429)
        print(f"Baixando PDF: {item.get('title')}")

        USER_AGENTS = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", # Chrome no Windows 11
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Firefox/120.0", # Firefox no macOS
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1", # Safari no iPhone (iOS)
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0", # Edge no Windows 11
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" # Chrome no Linux
        ]
        
        self.session.headers.update({"User-Agent": random.choice(USER_AGENTS)}) # atualiza user agent para evitar HTTP 429

        pdf_url = item.get('path') 
        title = item.get('title') 
        if not pdf_url or not title:
            print(f"Item inválido: {item}")
            return

        i = pdf_url.find('html')
        pdf_url = pdf_url[:i] + 'pdf'

        pdf_name = f"{title}.pdf"
        pdf_path = f"{save_folder}/{pdf_name}"

        entire_url = 'https://www.canlii.org' + pdf_url

        try:
            response = self.session.get(entire_url)
            response.raise_for_status()
            
            # Salva o PDF
            with open(pdf_path, 'wb') as file:
                file.write(response.content)
            print(f"PDF baixado: {pdf_name}")

            # Adiciona o título ao arquivo de registros (modo append)
            with open("pdfs_encontrados.txt", 'a', encoding='utf-8') as file:
                file.write(title + '\n')
                
            return pdf_path
        except requests.exceptions.RequestException as e:
            print(f"Erro ao baixar o PDF {pdf_name}: {e}")
            return None