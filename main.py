import pygame, sys
from entities import Jogador, Camera

LARGURA_MAPA, LARGURA_TELA, ALTURA_TELA, CHAO_Y = 6000, 800, 600, 520
CORES = {
    "idle": (255, 255, 255), "run_dir": (204, 204, 204), "run_esq": (127, 127, 127),
    "jump_dir": (178, 178, 178), "jump_esq": (102, 102, 102), "fall_dir": (153, 153, 153),
    "fall_esq": (76, 76, 76), "fall_reto": (114, 114, 114), "fundo": (0, 0, 0)
}

def load_scaled(path, tgt_h):
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, (int(img.get_width() * (tgt_h / img.get_height())), tgt_h))

def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED | pygame.RESIZABLE)
    pygame.display.set_caption("Love2D to Pygame - Otimizado")
    clock = pygame.time.Clock()

    bg_mountains = load_scaled("desert_mountains.png", ALTURA_TELA)
    bg_dunes = load_scaled("desert_dunes.png", ALTURA_TELA)
    bg_ground = load_scaled("desert_ground.png", ALTURA_TELA)
    
    img_chao = load_scaled("chao_deserto.png", 160)
    w_chao = max(1, img_chao.get_width())

    img_coqueiro = load_scaled("coqueiro.png", 200)
    img_casa1 = load_scaled("casa1.png", 250)
    img_casa2 = load_scaled("casa2.png", 300)

    objetos_cenario = [
        (img_coqueiro, cx, 0) for cx in [250, 660, 900, 1300, 1750, 2200, 2650, 3100, 3500, 3850]
    ] + [
        (img_casa1, 4300, 25), (img_casa2, 4600, 5), (img_casa1, 5000, 25), (img_casa1, 5400, 25)
    ]

    jogador = Jogador(CHAO_Y)
    camera = Camera(LARGURA_TELA, LARGURA_MAPA)

    while True:
        dt = clock.tick(60) / 1000.0

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_F11: pygame.display.toggle_fullscreen()
                elif e.key in (pygame.K_w, pygame.K_UP): jogador.jumpBuffer = 0.15

        teclas = pygame.key.get_pressed()
        mov = (teclas[pygame.K_d] or teclas[pygame.K_RIGHT]) - (teclas[pygame.K_a] or teclas[pygame.K_LEFT])
        
        jogador.update(dt, teclas, mov, CHAO_Y, LARGURA_MAPA)
        camera.update(dt, jogador, mov)

        tela.fill(CORES["fundo"])

        for img, spd in [(bg_mountains, 0.2), (bg_dunes, 0.5), (bg_ground, 0.8)]:
            w, shift = img.get_width(), (camera.x * spd) % img.get_width()
            x = -shift
            while x < LARGURA_TELA:
                tela.blit(img, (x, 0))
                x += w

        for i in range(0, LARGURA_MAPA, w_chao):
            if -w_chao < i - camera.x < LARGURA_TELA:
                tela.blit(img_chao, (i - camera.x, CHAO_Y - 60))

        for img, cx, oy in objetos_cenario:
            if -img.get_width() < cx - camera.x < LARGURA_TELA:
                tela.blit(img, (cx - camera.x, CHAO_Y - img.get_height() + oy))

        k = f"{jogador.estado}_{jogador.direcao[:3]}" if jogador.estado != "idle" else "idle"
        if jogador.estado == "fall" and jogador.velX == 0: k = "fall_reto"
        pygame.draw.rect(tela, CORES.get(k, CORES["idle"]), (jogador.rect.x - camera.x, jogador.rect.y, *jogador.rect.size))

        pygame.display.flip()

if __name__ == "__main__":
    main()