import pygame, sys
from entities import Jogador, Camera

# --- CONFIGURAÇÕES ---
LARGURA_MAPA, LARGURA_TELA, ALTURA_TELA, CHAO_Y = 4000, 800, 600, 520
CORES = {
    "idle": (255, 255, 255), "fundo": (0, 0, 0), "texto": (255, 255, 255),
    "chefe": (255, 255, 0), "instrucao": (200, 200, 200), "go": (255, 0, 0)
}

# Variáveis globais para zoom
zoom_nivel = 1.0
zoom_max = 3.0
zoom_velocidade = 0.1
mouse_pos = (LARGURA_TELA // 2, ALTURA_TELA // 2)

# --- UTILITÁRIOS ---
def get_zoom_min_height():
    return 1.0

def load_scaled(path, tgt_h):
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, (int(img.get_width() * (tgt_h / img.get_height())), tgt_h))

def draw_arrow_up(surf, x, y):
    points = [(x, y), (x-12, y+12), (x-6, y+12), (x-6, y+25), (x+6, y+25), (x+6, y+12), (x+12, y+12)]
    pygame.draw.polygon(surf, (255, 255, 255), points)
    pygame.draw.polygon(surf, (0, 0, 0), points, 2)

def main():
    global zoom_nivel, mouse_pos
    pygame.init()
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED | pygame.RESIZABLE)
    pygame.display.set_caption("Fase 5 - ODS 6")
    clock = pygame.time.Clock()
    tela_jogo = pygame.Surface((LARGURA_TELA, ALTURA_TELA))

    # --- ASSETS ---
    bg_mountains = load_scaled("assets/desert_mountains.png", ALTURA_TELA)
    bg_dunes = load_scaled("assets/desert_dunes.png", ALTURA_TELA)
    bg_ground = load_scaled("assets/desert_ground.png", ALTURA_TELA)
    img_chao = load_scaled("assets/chao_deserto.png", 160)
    w_chao = img_chao.get_width()

    img_coqueiro = load_scaled("assets/coqueiro.png", 200)
    img_casa1 = load_scaled("assets/casa1.png", 200)
    img_casa2 = load_scaled("assets/casa2.png", 280)
    img_aldeao1 = load_scaled("assets/aldeao1.png", 70)
    img_aldeao2 = load_scaled("assets/aldeao2.png", 70)
    img_chefe1 = load_scaled("assets/chefe1.png", 75)
    img_chao_casa = load_scaled("assets/chao_casa1.png", 160)
    w_chao_casa = img_chao_casa.get_width()

    # Asset do Chefe (Diálogo)
    img_chefe_dialogo = pygame.transform.flip(load_scaled("assets/chefe2.png", 450), True, False)

    # Cactos Foreground
    variacoes_cacto = []
    for h in [350, 450, 550]:
        img = load_scaled("assets/cacto.png", h)
        img_blur = pygame.transform.smoothscale(img, (img.get_width() // 4, img.get_height() // 4))
        variacoes_cacto.append(pygame.transform.smoothscale(img_blur, (img.get_width(), img.get_height())))
    
    cactos_fg = [(100, 300, 0), (1200, 250, 1), (2200, 200, 2)]

    # --- ESTADO DO JOGO ---
    CENA_DESERTO, CENA_CASA, CENA_DIALOGO, CENA_GAMEOVER = "deserto", "casa", "dialogo", "gameover"
    cena_atual = CENA_DESERTO
    largura_mapa_atual = LARGURA_MAPA
    pos_entrada_x = 0
    tipo_casa_proxima = None
    
    objetos_cenario = [(img_coqueiro, cx, 0) for cx in [250, 700, 1100, 1500, 1900]] + \
                      [(img_casa1, 2300, 0), (img_aldeao1, 2380, 5), (img_casa2, 2650, 15), (img_chefe1, 2810, 10),
                       (img_casa1, 3100, 0), (img_aldeao2, 3180, 5), (img_casa1, 3500, 0), (img_aldeao1, 3580, 5)]

    jogador = Jogador(CHAO_Y)
    camera = Camera(LARGURA_TELA, largura_mapa_atual)
    
    fonts = {
        "ui": pygame.font.SysFont("Consolas", 20, bold=True),
        "dialogo": pygame.font.SysFont("Consolas", 16, bold=True),
        "instrucao": pygame.font.SysFont("Consolas", 12),
        "grande": pygame.font.SysFont("Consolas", 70, bold=True)
    }

    txt_chefe = "Pare de mexer onde não é chamado!"
    dialogo_char_idx, dialogo_timer, dialogo_vel = 0, 0, 0.05

    # --- LOOP PRINCIPAL ---
    while True:
        dt = clock.tick(60) / 1000.0
        mouse_pos = pygame.mouse.get_pos()
        mostrar_prompt = False

        # Detecta proximidade no deserto
        if cena_atual == CENA_DESERTO:
            for img, cx, oy in objetos_cenario:
                if img in (img_casa1, img_casa2):
                    porta_x = cx + img.get_width() // 2
                    if abs(jogador.rect.centerx - porta_x) < 40:
                        mostrar_prompt, tipo_casa_proxima = True, img
                        break

        # Eventos
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif e.type == pygame.MOUSEWHEEL:
                zoom_nivel = max(1.0, min(zoom_max, zoom_nivel + (zoom_velocidade if e.y > 0 else -zoom_velocidade)))
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_F11: pygame.display.toggle_fullscreen()
                elif e.key in (pygame.K_w, pygame.K_UP):
                    if mostrar_prompt and cena_atual == CENA_DESERTO:
                        if tipo_casa_proxima == img_casa1:
                            pos_entrada_x, cena_atual, largura_mapa_atual = jogador.pos_x, CENA_CASA, 800
                            jogador.pos_x = jogador.rect.x = 80
                            jogador.velX = 0
                            camera.largura_mapa, camera.x = largura_mapa_atual, 0
                        else:
                            cena_atual, jogador.velX, dialogo_char_idx = CENA_DIALOGO, 0, 0
                    elif cena_atual == CENA_DIALOGO:
                        if dialogo_char_idx < len(txt_chefe): dialogo_char_idx = len(txt_chefe)
                        else: cena_atual = CENA_GAMEOVER
                    else:
                        jogador.jumpBuffer = 0.15
                elif e.key == pygame.K_r and cena_atual == CENA_GAMEOVER:
                    cena_atual, largura_mapa_atual = CENA_DESERTO, LARGURA_MAPA
                    jogador, camera = Jogador(CHAO_Y), Camera(LARGURA_TELA, LARGURA_MAPA)

        # Update
        teclas = pygame.key.get_pressed()
        mov = (teclas[pygame.K_d] or teclas[pygame.K_RIGHT]) - (teclas[pygame.K_a] or teclas[pygame.K_LEFT])
        
        if cena_atual in (CENA_DESERTO, CENA_CASA):
            jogador.update(dt, teclas, mov, CHAO_Y, largura_mapa_atual)
            camera.update(dt, jogador, mov)
        elif cena_atual == CENA_DIALOGO:
            dialogo_timer += dt
            if dialogo_timer >= dialogo_vel and dialogo_char_idx < len(txt_chefe):
                dialogo_char_idx += 1
                dialogo_timer = 0

        # Saída da casa
        if cena_atual == CENA_CASA and jogador.pos_x <= 0:
            cena_atual, largura_mapa_atual = CENA_DESERTO, LARGURA_MAPA
            jogador.pos_x, jogador.rect.x = pos_entrada_x, int(pos_entrada_x)
            camera.largura_mapa = largura_mapa_atual
            camera.x = max(0, min(jogador.rect.centerx - camera.pos_tela, camera.largura_mapa - camera.largura_tela))

        # Renderização do Mundo
        tela_jogo.fill(CORES["fundo"])
        if cena_atual in (CENA_DESERTO, CENA_DIALOGO):
            # Parallax Background
            for img, spd in [(bg_mountains, 0.2), (bg_dunes, 0.5), (bg_ground, 0.8)]:
                w, shift = img.get_width(), (camera.x * spd) % img.get_width()
                for x in range(int(-shift), LARGURA_TELA, w): tela_jogo.blit(img, (x, 0))

            # Ground
            for i in range(0, largura_mapa_atual, w_chao):
                if -w_chao < i - camera.x < LARGURA_TELA:
                    tela_jogo.blit(img_chao, (i - camera.x, CHAO_Y - 60))

            # Scenario Objects
            for img, cx, oy in objetos_cenario:
                if -img.get_width() < cx - camera.x < LARGURA_TELA:
                    img_draw = img
                    if img in (img_aldeao1, img_aldeao2, img_chefe1):
                        flip = jogador.rect.centerx < cx + img.get_width() // 2
                        img_draw = pygame.transform.flip(img, flip, False)
                    tela_jogo.blit(img_draw, (cx - camera.x, CHAO_Y - img_draw.get_height() + oy))
                    if img in (img_casa1, img_casa2) and abs(jogador.rect.centerx - (cx + img.get_width() // 2)) < 40:
                        draw_arrow_up(tela_jogo, (cx + img.get_width() // 2) - camera.x, CHAO_Y - 80)
        
        elif cena_atual == CENA_CASA:
            for i in range(0, largura_mapa_atual, w_chao_casa):
                tela_jogo.blit(img_chao_casa, (i - camera.x, CHAO_Y - 60))

        # Jogador
        k = f"{jogador.estado}_{jogador.direcao[:3]}" if jogador.estado != "idle" else "idle"
        if jogador.estado == "fall" and jogador.velX == 0: k = "fall_reto"
        if jogador.current_animation:
            sprite = jogador.current_animation[jogador.frame_index]
            if jogador.direcao == "esquerda": sprite = pygame.transform.flip(sprite, True, False)
            tela_jogo.blit(sprite, (jogador.rect.x - camera.x, jogador.rect.y))
        else:
            pygame.draw.rect(tela_jogo, (255,255,255), (jogador.rect.x - camera.x, jogador.rect.y, *jogador.rect.size))

        # Foreground Cacti
        if cena_atual in (CENA_DESERTO, CENA_DIALOGO):
            rect_j = pygame.Rect(jogador.rect.x - camera.x, jogador.rect.y, *jogador.rect.size)
            for cx, cy, idx in cactos_fg:
                img_v = variacoes_cacto[idx]
                x = (cx - camera.x * 1.8) % 3200 - 600
                img_v.set_alpha(150 if pygame.Rect(x, cy, *img_v.get_size()).colliderect(rect_j) else 255)
                tela_jogo.blit(img_v, (x, cy))

        # Render Final com Zoom
        if zoom_nivel != 1.0:
            nw, nh = int(LARGURA_TELA * zoom_nivel), int(ALTURA_TELA * zoom_nivel)
            tela_zoom = pygame.transform.smoothscale(tela_jogo, (nw, nh))
            px, py = mouse_pos[0] / LARGURA_TELA, mouse_pos[1] / ALTURA_TELA
            ox = max(-nw + LARGURA_TELA, min(0, int(mouse_pos[0] - nw * px)))
            oy = max(-nh + ALTURA_TELA, min(0, int(mouse_pos[1] - nh * py)))
            tela.fill(CORES["fundo"])
            tela.blit(tela_zoom, (ox, oy))
        else:
            tela.blit(tela_jogo, (0, 0))

        # UI Overlays
        if mostrar_prompt:
            txt = fonts["ui"].render("PRESSIONE 'W' OU '↑' PARA ENTRAR", False, CORES["texto"])
            smd = fonts["ui"].render("PRESSIONE 'W' OU '↑' PARA ENTRAR", False, CORES["fundo"])
            px, py = LARGURA_TELA // 2 - txt.get_width() // 2, ALTURA_TELA - 50
            tela.blit(smd, (px + 2, py + 2)); tela.blit(txt, (px, py))

        if cena_atual == CENA_DIALOGO:
            overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150)); tela.blit(overlay, (0, 0))
            tela.blit(img_chefe_dialogo, (LARGURA_TELA - img_chefe_dialogo.get_width() + 50, ALTURA_TELA - 350))
            # Caixa de Diálogo (Fundo preto, borda cinza)
            pygame.draw.rect(tela, (0, 0, 0), (50, ALTURA_TELA - 150, LARGURA_TELA - 100, 100))
            pygame.draw.rect(tela, (100, 100, 100), (50, ALTURA_TELA - 150, LARGURA_TELA - 100, 100), 2)
            
            # Nome em vermelho, texto em cinza
            tela.blit(fonts["ui"].render("CHEFE:", False, (200, 0, 0)), (70, ALTURA_TELA - 140))
            tela.blit(fonts["dialogo"].render(txt_chefe[:dialogo_char_idx], False, (180, 180, 180)), (70, ALTURA_TELA - 100))
            if dialogo_char_idx >= len(txt_chefe):
                inst = fonts["instrucao"].render("Pressione qualquer tecla para continuar...", False, (100, 100, 100))
                tela.blit(inst, (LARGURA_TELA - inst.get_width() - 70, ALTURA_TELA - 70))

        elif cena_atual == CENA_GAMEOVER:
            tela.fill(CORES["fundo"])
            txt_go = fonts["grande"].render("GAME OVER", False, CORES["go"])
            tela.blit(txt_go, (LARGURA_TELA // 2 - txt_go.get_width() // 2, ALTURA_TELA // 2 - 100))
            txt_r = fonts["ui"].render("Pressione 'R' para reiniciar", False, CORES["texto"])
            tela.blit(txt_r, (LARGURA_TELA // 2 - txt_r.get_width() // 2, ALTURA_TELA // 2 + 50))

        pygame.display.flip()

if __name__ == "__main__":
    main()