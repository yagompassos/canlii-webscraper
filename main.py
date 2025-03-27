import os
from curl_cffi import requests
from ai_pdf_analyzer import AIClient
from pdf_handler import PdfHandler
from dotenv import load_dotenv

load_dotenv()

def new_session():
    session = requests.Session(impersonate="chrome") 
    return session

def search_api(session: requests.Session, query: str, page: int):
    url = f"https://www.canlii.org/en/search/ajaxSearch.do?type=decision&text={query}&page={page}"
    resp = session.get(url)
    resp.raise_for_status()  
    return resp.json().get("results", [])

def main():
    session = new_session()
    save_folder = "untouched_pdfs"
    query = "Sexual Exploitation"
    page = 1
    api_key = os.getenv("OPEN_ROUTER_API_KEY")
    if not api_key:
        raise ValueError("A variável OPEN_ROUTER_API_KEY não está definida no .env!")

    pdf_handler = PdfHandler(session)
    ai_client = AIClient(api_key)

    results = search_api(session, query, page)

    pdf_path = pdf_handler.download_pdf(results[1], save_folder)
 
    for result in results:
        title = result.get('title')
        if title:
            if not pdf_handler.is_duplicate(title, "pdfs_encontrados.txt"):
                print(f"Documento não duplicado, prosseguindo...")
                pdf_path = pdf_handler.download_pdf(session, result, save_folder)
                if pdf_path:
                    content = pdf_handler.extract_text_from_pdf(pdf_path)
                    if content:
                        ai_response = ai_client.analyze_text(content, query)
                        if ai_response.startswith("True"):  
                            print("deepseek disse que é verdade:" + ai_response)
                            destination_folder = query.replace(" ", "_") + "_pdfs"	
                            os.makedirs(destination_folder, exist_ok=True)
                            new_path = os.path.join(destination_folder, os.path.basename(pdf_path))
                            os.rename(pdf_path, new_path)
                            print(f"PDF moved to {new_path}")
                        elif ai_response.startswith("False"):
                            print("deepseek disse que é falso:" + ai_response)
                        else:
                            print("deepseek não respondeu corretamente: " + ai_response)
            else :
                print(f"Duplicado, pulando documento...")
        else: 
            print('Title not found in result')
                


if __name__ == "__main__":
    main()