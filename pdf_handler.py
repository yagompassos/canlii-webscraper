import re
import PyPDF2
from curl_cffi import requests

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
            file_handler.write_lines([title])  
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
            with open(pdf_path, 'wb') as file:
                file.write(response.content)
            print(f"PDF baixado: {pdf_name}")
            return pdf_path
        except requests.exceptions.RequestException as e:
            print(f"Erro ao baixar o PDF {pdf_name}: {e}")
            return None