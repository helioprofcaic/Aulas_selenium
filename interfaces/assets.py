import os
from PIL import Image, ImageTk # Requer: pip install Pillow

# Cache para evitar que o Garbage Collector do Python apague as imagens
_cache_icones = {}

def get_icon(nome, tamanho=(32, 32)):
    """
    Carrega um ícone da pasta 'recursos', redimensiona e retorna um objeto PhotoImage.
    
    Args:
        nome (str): Nome lógico do ícone ('app', 'scraper', 'planejamento', etc.)
        tamanho (tuple): Tamanho desejado (largura, altura). Padrão 32x32.
    """
    global _cache_icones
    
    # Mapeamento dos nomes lógicos para os arquivos gerados
    mapa_arquivos = {
        'app': 'icone_app.png',
        'scraper': 'icone_scraper.png',
        'planejamento': 'icone_planejamento.png',
        'preenchimento': 'icone_preenchimento.png',
        'registro': 'icone_registro.png',
        'config': 'icone_config.png'
    }
    
    filename = mapa_arquivos.get(nome, f"{nome}.png")
    chave_cache = (filename, tamanho)
    
    if chave_cache in _cache_icones:
        return _cache_icones[chave_cache]

    # Define o caminho da pasta recursos (assumindo estrutura: projeto/interfaces/assets.py)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho_img = os.path.join(base_dir, 'recursos', filename)
    
    if not os.path.exists(caminho_img):
        print(f"⚠️ Ícone não encontrado: {caminho_img}")
        return None
        
    try:
        pil_img = Image.open(caminho_img)
        pil_img = pil_img.resize(tamanho, Image.Resampling.LANCZOS)
        tk_img = ImageTk.PhotoImage(pil_img)
        _cache_icones[chave_cache] = tk_img
        return tk_img
    except Exception as e:
        print(f"❌ Erro ao carregar ícone {filename}: {e}")
        return None