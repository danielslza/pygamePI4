# utils.py - Funções auxiliares de carregamento e desenho

import pygame

def load_scaled(path, tgt_h):
    """Carrega uma imagem e a redimensiona mantendo a proporção."""
    img = pygame.image.load(path).convert_alpha()
    aspect_ratio = img.get_width() / img.get_height()
    return pygame.transform.scale(img, (int(tgt_h * aspect_ratio), tgt_h))

def draw_arrow_up(surf, x, y):
    """Desenha uma seta indicadora para cima."""
    points = [(x, y), (x-12, y+12), (x-6, y+12), (x-6, y+25), (x+6, y+25), (x+6, y+12), (x+12, y+12)]
    pygame.draw.polygon(surf, (255, 255, 255), points)
    pygame.draw.polygon(surf, (0, 0, 0), points, 2)

def draw_key_hint(surf, x, y, key_txt):
    """Desenha uma dica de tecla (ex: [E])."""
    f = pygame.font.SysFont("Consolas", 20, bold=True)
    txt = f.render(f"{key_txt}", False, (255, 255, 255))
    size = max(txt.get_width(), txt.get_height()) + 10
    bg_r = pygame.Rect(x - size//2, y + txt.get_height()//2 - size//2, size, size)
    
    # Criar fundo semitransparente
    s = pygame.Surface((bg_r.width, bg_r.height), pygame.SRCALPHA)
    s.fill((0, 0, 0, 150))
    
    surf.blit(s, (bg_r.x, bg_r.y))
    surf.blit(txt, (x - txt.get_width()//2, y))
