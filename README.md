# Web Scraper CanLII

Este projeto realiza scraping de PDFs jurídicos, extrai seu conteúdo e os analisa usando IA.

## Configuração e Instalação
1. Clone o repositório:
   ```sh
   git clone https://github.com/yagompassos/canlii-webscraper
   cd canlii-webscraper
   ```

2. Crie e ative um ambiente virtual:
   ```sh
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Instale as dependências:
   ```sh
   pip install -r requirements.txt
   ```

4. Crie e copie uma chave de api na Open Router através do link: https://openrouter.ai/settings/keys

5. Configure o arquivo `.env` baseado no `.env.example`:
   ```sh
   cp .env.example .env
   ```
   Edite `.env` e adicione sua chave de API:
   ```env
   OPEN_ROUTER_API_KEY=suachaveaqui
   ```

## Como Usar
Execute o script principal:
```sh
python main.py
```

