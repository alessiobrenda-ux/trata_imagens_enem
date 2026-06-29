"""
Propósito: Cortar a imagem horizontalmente com tripla validação e um recuo
          de 3 pixels para cima (dando mais 2px de respiro branco no topo).
Versão: Margem expandida no topo (y - 3)
"""

from PIL import Image
import os
import warnings

# Silencia o aviso de imagem muito longa no terminal
warnings.simplefilter('ignore', Image.DecompressionBombWarning)

def encontrar_linhas_de_corte_por_varredura(imagem, tolerancia=35):
    largura, altura = imagem.size
    pixels = imagem.load()
    
    pontos_de_corte = []
    
    # Amostra horizontal no meio da página onde a barra com certeza passa
    inicio_x = max(50, (largura // 2) - 150)
    fim_x = min(largura - 50, (largura // 2) + 150)
    
    y = 3  # Começa em 3 para permitir o recuo de -3 pixels com segurança
    while y < altura - 28:
        # 1. CHECAGEM DO TOPO: Verifica se a linha superior é realmente uma linha preta contínua
        topo_eh_preto = True
        for x_teste in range(largura // 2 - 20, largura // 2 + 20, 2):
            p_topo = pixels[x_teste, y][:3]
            if not (p_topo[0] < 65 and p_topo[1] < 65 and p_topo[2] < 65):
                topo_eh_preto = False
                break
                
        if topo_eh_preto:
            # 2. CHECAGEM DA BASE: A barra tem cerca de 24-25px, então a linha preta de baixo deve estar por ali
            y_base = y + 23
            p_base = pixels[largura // 2, y_base][:3]
            
            # Se a base também for escura, passamos para a validação do miolo cinza
            if p_base[0] < 70 and p_base[1] < 70 and p_base[2] < 70:
                
                # 3. CHECAGEM DO MIOLO: Verifica o padrão de tiras cinzas intercaladas
                y_miolo = y + 12
                pixels_cinzas_na_linha = 0
                
                for x in range(inicio_x, fim_x, 2):
                    p = pixels[x, y_miolo][:3]
                    # Tom aproximado do cinza das barrinhas (190)
                    if abs(p[0] - 190) < tolerancia and abs(p[1] - 190) < tolerancia and abs(p[2] - 190) < tolerancia:
                        pixels_cinzas_na_linha += 1
                
                # Se passou no topo preto, na base preta e tem o miolo cinza texturizado, é a barra!
                if pixels_cinzas_na_linha > 20:
                    # MODIFICAÇÃO: Recua 3 pixels para dar a folga branca extra que você pediu
                    ponto_exato = y - 3
                    pontos_de_corte.append(ponto_exato)
                    print(f"-> Barra confirmada! Linha de corte com folga extra definida em y = {ponto_exato}")
                    
                    # Salta a estrutura da barra inteira para continuar procurando as próximas
                    y += 55
                    continue
                    
        y += 1
        
    return pontos_de_corte

def executar_fatiamento_estrito(caminho_imagem, pasta_saida):
    if not os.path.exists(caminho_imagem):
        caminho_imagem = "colunas_concatenadas_verticalmente.jpg" if caminho_imagem.endswith(".png") else "colunas_concatenadas_verticalmente.png"
        if not os.path.exists(caminho_imagem):
            print("Erro: Imagem original não encontrada.")
            return

    imagem = Image.open(caminho_imagem).convert("RGB")
    largura, altura = imagem.size
    print(f"Iniciando varredura estrita na imagem de {largura}x{altura} px...")
    
    linhas_de_barra = encontrar_linhas_de_corte_por_varredura(imagem)
    
    if not linhas_de_barra:
        print("Erro: Nenhum padrão real de barra passou na tripla validação.")
        return
        
    print(f"\nTotal de barras reais encontradas: {len(linhas_de_barra)}")
    print("Fatiando nos locais exatos com folga branca...")
    os.makedirs(pasta_saida, exist_ok=True)
    
    inicio_bloco = 0
    for indice, fim_bloco in enumerate(linhas_de_barra):
        area_corte = (0, inicio_bloco, largura, fim_bloco)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"bloco_{indice+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} (De y={inicio_bloco} até y={fim_bloco})")
        
        inicio_bloco = fim_bloco

    if inicio_bloco < altura:
        area_corte = (0, inicio_bloco, largura, altura)
        secao = imagem.crop(area_corte)
        nome_arquivo = f"bloco_{len(linhas_de_barra)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo bloco final: {caminho_completo}")

if __name__ == "__main__":
    executar_fatiamento_estrito("colunas_concatenadas_verticalmente.png", "questoes_recortadas_horizontal")
    print("\nProcesso concluído! Agora com a margem superior perfeita.")