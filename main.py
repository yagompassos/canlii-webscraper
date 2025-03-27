import os
import random
import time
from curl_cffi import requests
from ai_pdf_analyzer import AIClient
from pdf_handler import PdfHandler
import json
from dotenv import load_dotenv

load_dotenv()

def new_session():
    session = requests.Session(impersonate="chrome") 
    return session

def search_api(session: requests.Session, query: str, page: int):
    time.sleep(random.uniform(3, 7))      # espera entre 3 a 7 segundos para cada requisição de PDF (culpada por erro HTTP 429)

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", # Chrome no Windows 11
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Firefox/120.0", # Firefox no macOS
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1", # Safari no iPhone (iOS)
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0", # Edge no Windows 11
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" # Chrome no Linux
    ]
    
    session.headers.update({"User-Agent": random.choice(USER_AGENTS)}) # atualiza user agent para evitar HTTP 429
    
    url = f"https://www.canlii.org/en/search/ajaxSearch.do?type=decision&text={query}&page={page}"
    resp = session.get(url)
    resp.raise_for_status()
    data = resp.json()
    
    # Extrai informações de paginação
    pages_info = json.loads(data.get("pages", "[]"))
    total_pages = len(pages_info) if pages_info else 1
    
    return {
        "results": data.get("results", []),
        "total_pages": total_pages,
        "current_page": page
    }

def load_queries(file_path="queries.txt"):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file if line.strip()]

def process_query(session, query, pdf_handler, ai_client):
    print(f"\n{'='*50}\nProcessando query: '{query}'\n{'='*50}")
    
    save_folder = "untouched_pdfs"
    destination_folder = query.replace(" ", "_") + "_pdfs"
    os.makedirs(destination_folder, exist_ok=True)

    # Primeira requisição para descobrir o total de páginas
    first_page = search_api(session, query, 1)
    total_pages = first_page["total_pages"]
    all_results = first_page["results"]

    print(f"Total de páginas encontradas: {total_pages}")

    # Processa as páginas restantes (começando da 2)
    for page in range(2, total_pages + 1):
        print(f"Processando página {page} de {total_pages}...")
        try:
            page_data = search_api(session, query, page)
            all_results.extend(page_data["results"])
            time.sleep(2)  # Delay para evitar rate limiting
        except Exception as e:
            print(f"Erro ao processar página {page}: {e}")
            continue

    print(f"Total de resultados para '{query}': {len(all_results)}")

    # Processa cada resultado
    for result in all_results:
        title = result.get('title')
        if not title:
            continue

        if not pdf_handler.is_duplicate(title, "pdfs_encontrados.txt"):
            print(f"\nProcessando documento: {title}")
            pdf_path = pdf_handler.download_pdf(result, save_folder)
            
            if not pdf_path:
                continue
                
            content = pdf_handler.extract_text_from_pdf(pdf_path)
            if not content:
                continue

            try:
                ai_response = ai_client.analyze_text(content, query)
                if ai_response.startswith("True"):  
                    print("deepseek confirmou relevância")
                    new_path = os.path.join(destination_folder, os.path.basename(pdf_path))
                    os.rename(pdf_path, new_path)
                    print(f"Arquivo movido para: {new_path}")
                else:
                    print("deepseek descartou como irrelevante")
                    os.remove(pdf_path)  # Remove PDFs irrelevantes
            except Exception as e:
                print(f"Erro na análise do AI: {e}")
        else:
            print(f"Documento duplicado, pulando: {title}")
            with open("duplicated_titles.txt", 'a', encoding='utf-8') as file:
                file.write(title + '\n')

def main():
    session = new_session()
    api_key = os.getenv("OPEN_ROUTER_API_KEY")
    
    if not api_key:
        raise ValueError("A variável OPEN_ROUTER_API_KEY não está definida no .env!")

    pdf_handler = PdfHandler(session)
    ai_client = AIClient(api_key)
    queries = load_queries()

    for query in queries:
        try:
            process_query(session, query, pdf_handler, ai_client)
            time.sleep(5)  # Delay entre queries diferentes
        except Exception as e:
            print(f"Erro ao processar query '{query}': {e}")
            continue

if __name__ == "__main__":
    main()