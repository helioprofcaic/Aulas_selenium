import os
import sys

def slice_image(image_path, output_dir, rows=2, cols=3):
    """
    Corta uma imagem de grade (sprite sheet) em ícones individuais.
    Requer: pip install Pillow
    """
    try:
        from PIL import Image
    except ImportError:
        print("❌ Erro: A biblioteca Pillow (PIL) é necessária.")
        print("   Instale rodando: pip install Pillow")
        return

    if not os.path.exists(image_path):
        print(f"❌ Arquivo não encontrado: {image_path}")
        return

    os.makedirs(output_dir, exist_ok=True)
    
    print(f"--- Processando: {image_path} ---")
    img = Image.open(image_path)
    w, h = img.size
    
    # Calcula o tamanho de cada célula
    icon_w = w // cols
    icon_h = h // rows
    
    names = ["icone_app", "icone_scraper", "icone_planejamento", "icone_preenchimento", "icone_registro", "icone_config"]
    
    count = 0
    for r in range(rows):
        for c in range(cols):
            if count >= len(names): break
            
            left = c * icon_w
            top = r * icon_h
            right = left + icon_w
            bottom = top + icon_h
            
            crop = img.crop((left, top, right, bottom))
            output_filename = f"{names[count]}.png"
            save_path = os.path.join(output_dir, output_filename)
            crop.save(save_path)
            print(f"  ✅ Salvo: {output_filename}")
            count += 1
    
    print(f"\nÍcones extraídos para a pasta: {output_dir}")

if __name__ == "__main__":
    # Uso: python tools/cortar_icones.py caminho/para/sua_imagem_grade.png
    if len(sys.argv) < 2:
        print("Uso: python tools/cortar_icones.py <caminho_da_imagem_grade.png>")
    else:
        # Define a pasta de saída como 'recursos' na raiz do projeto
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output = os.path.join(root, 'recursos')
        slice_image(sys.argv[1], output)


# **Como usar o script:**
# 1. Instale a biblioteca de imagem: `pip install Pillow`
# 2. Salve a imagem que o Gemini gerou (ex: `grade.png`) na pasta do projeto.
# 3. Rode no terminal:
#   ```bash
#   python tools/cortar_icones.py grade.png
# ```