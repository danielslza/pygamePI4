import pygame, sys
from entities import Jogador, Camera

LARGURA_MAPA, LARGURA_TELA, ALTURA_TELA, CHAO_Y = 4000, 800, 600, 520
CORES = {
    "idle": (255, 255, 255), "fundo": (0, 0, 0), "texto": (255, 255, 255),
    "chefe": (255, 255, 0), "instrucao": (200, 200, 200), "go": (255, 0, 0)
}

zoom_nivel = 1.0
zoom_max = 3.0
zoom_velocidade = 0.1
mouse_pos = (LARGURA_TELA // 2, ALTURA_TELA // 2)

def get_zoom_min_height():
    return 1.0

def load_scaled(path, tgt_h):
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, (int(img.get_width() * (tgt_h / img.get_height())), tgt_h))

def draw_arrow_up(surf, x, y):
    points = [(x, y), (x-12, y+12), (x-6, y+12), (x-6, y+25), (x+6, y+25), (x+6, y+12), (x+12, y+12)]
    pygame.draw.polygon(surf, (255, 255, 255), points)
    pygame.draw.polygon(surf, (0, 0, 0), points, 2)

def draw_key_hint(surf, x, y, key_txt):
    f = pygame.font.SysFont("Consolas", 20, bold=True)
    txt = f.render(f"[{key_txt}]", False, (255, 255, 255))
    bg_r = pygame.Rect(x - txt.get_width()//2 - 5, y - 5, txt.get_width() + 10, txt.get_height() + 10)
    s = pygame.Surface((bg_r.width, bg_r.height), pygame.SRCALPHA)
    s.fill((0, 0, 0, 150))
    surf.blit(s, (bg_r.x, bg_r.y))
    pygame.draw.rect(surf, (255, 255, 255), bg_r, 1)
    surf.blit(txt, (x - txt.get_width()//2, y))

def main():
    global zoom_nivel, mouse_pos
    pygame.init()
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED | pygame.RESIZABLE)
    pygame.display.set_caption("Fase 5 - ODS 6")
    clock = pygame.time.Clock()
    tela_jogo = pygame.Surface((LARGURA_TELA, ALTURA_TELA))

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
    img_chao_chefe = load_scaled("assets/chao_chefe.png", 160)
    w_chao_chefe = img_chao_chefe.get_width()
    img_alavanca = load_scaled("assets/alavanca.png", 50)
    img_chefe2 = load_scaled("assets/chefe2.png", 75) 
    img_hope = load_scaled("assets/hope.png", 300) 
    
    img_axe = load_scaled("assets/axe.png", 40)
    img_letter = load_scaled("assets/carta.png", 30)
    inventario = []
    machado_disponivel = True
    carta_disponivel = True
    lendo_carta = False
    coqueiros_cortados = 0
    vila_reunida = False
    pos_ultimo_coqueiro = 0
    puzzle_alavancas = [{"x": 2000 + i*120, "ativo": False, "id": i+1} for i in range(5)]
    puzzle_sequencia = []
    puzzle_correto = [4, 3, 5, 1, 2]
    puzzle_vencido = False
    boss_final_x = 3000
    boss_final_ativo = False
    boss_final_falando = False
    boss_final_concluido = False
    iris_raio = LARGURA_TELA
    iris_ativa = False
    iris_velocidade = 800
    plataformas_chefe = [
        pygame.Rect(500, CHAO_Y - 100, 150, 20),
        pygame.Rect(750, CHAO_Y - 200, 150, 20),
        pygame.Rect(1000, CHAO_Y - 100, 150, 20),
        pygame.Rect(1250, CHAO_Y - 200, 150, 20),
        pygame.Rect(1550, CHAO_Y - 120, 250, 20) 
    ]

    img_chefe_dialogo = pygame.transform.flip(load_scaled("assets/chefe2.png", 450), True, False)

    variacoes_cacto = []
    for h in [350, 450, 550]:
        img = load_scaled("assets/cacto.png", h)
        img_blur = pygame.transform.smoothscale(img, (img.get_width() // 4, img.get_height() // 4))
        variacoes_cacto.append(pygame.transform.smoothscale(img_blur, (img.get_width(), img.get_height())))
    
    cactos_fg = [(100, 300, 0), (1200, 250, 1), (2200, 200, 2)]

    CENA_DESERTO, CENA_CASA, CENA_DIALOGO, CENA_GAMEOVER = "deserto", "casa", "dialogo", "gameover"
    cena_atual = CENA_DESERTO
    largura_mapa_atual = LARGURA_MAPA
    pos_entrada_x = 0
    id_casa_atual = 0 
    tipo_casa_proxima = None
    
    objetos_cenario = [
        [img_coqueiro, 250, 0, "coqueiro", True, 0],
        [img_coqueiro, 700, 0, "coqueiro", True, 0],
        [img_coqueiro, 1100, 0, "coqueiro", True, 0],
        [img_coqueiro, 1500, 0, "coqueiro", True, 0],
        [img_coqueiro, 1900, 0, "coqueiro", True, 0],
        [img_casa1, 2300, 0, "casa1", True, 0],
        [img_aldeao1, 2380, 5, "aldeao", True, -80],
        [img_casa2, 2650, 15, "casa2", True, 0],
        [img_chefe1, 2810, 10, "chefe", True, 0],
        [img_casa1, 3100, 0, "casa1", True, 0],
        [img_aldeao2, 3180, 5, "aldeao", True, 80],
        [img_casa1, 3500, 0, "casa1", True, 0],
        [img_aldeao1, 3580, 5, "aldeao", True, 160]
    ]

    jogador = Jogador(CHAO_Y)
    camera = Camera(LARGURA_TELA, largura_mapa_atual)
    
    fonts = {
        "ui": pygame.font.SysFont("Consolas", 20, bold=True),
        "dialogo": pygame.font.SysFont("Consolas", 16, bold=True),
        "instrucao": pygame.font.SysFont("Consolas", 12),
        "grande": pygame.font.SysFont("Consolas", 70, bold=True)
    }

    txt_chefe = "Pare de mexer onde não é chamada!"
    dialogo_char_idx, dialogo_timer, dialogo_vel = 0, 0, 0.05

    while True:
        dt = clock.tick(60) / 1000.0
        mouse_pos = pygame.mouse.get_pos()
        mostrar_prompt = False

        if cena_atual == CENA_DESERTO:
            for obj in objetos_cenario:
                img, cx, oy, tipo, ativo, offset = obj
                if ativo and tipo in ("casa1", "casa2"):
                    porta_x = cx + img.get_width() // 2
                    if abs(jogador.rect.centerx - porta_x) < 40:
                        mostrar_prompt, tipo_casa_proxima = True, img
                        break

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
                            id_casa_atual = porta_x 
                            jogador.pos_x = jogador.rect.x = 80
                            jogador.velX = 0
                            camera.largura_mapa, camera.x = largura_mapa_atual, 0
                        else:
                            if vila_reunida:
                                pos_entrada_x, cena_atual, largura_mapa_atual = jogador.pos_x, CENA_CASA, 800
                                id_casa_atual = porta_x
                                jogador.pos_x = jogador.rect.x = 80
                                jogador.velX = 0
                                camera.largura_mapa, camera.x = largura_mapa_atual, 0
                            else:
                                cena_atual, jogador.velX, dialogo_char_idx = CENA_DIALOGO, 0, 0
                                txt_chefe = "Pare de mexer onde não é chamado!"
                                lendo_carta = False
                    elif cena_atual == CENA_DIALOGO:
                        if dialogo_char_idx < len(txt_chefe): dialogo_char_idx = len(txt_chefe)
                        else:
                            if lendo_carta:
                                cena_atual = CENA_CASA
                                lendo_carta = False
                            elif boss_final_falando:
                                cena_atual = CENA_CASA
                                boss_final_concluido = True
                                boss_final_falando = False
                                iris_ativa = True 
                            else:
                                cena_atual = CENA_GAMEOVER
                    else:
                        jogador.jumpBuffer = 0.15
                elif e.key == pygame.K_e and cena_atual == CENA_CASA and plats:
                    for alav in puzzle_alavancas:
                        if abs(jogador.rect.centerx - alav["x"]) < 40 and not puzzle_vencido:
                            alav["ativo"] = not alav["ativo"]
                            if alav["id"] not in puzzle_sequencia:
                                puzzle_sequencia.append(alav["id"])
                                if len(puzzle_sequencia) == len(puzzle_correto):
                                    if puzzle_sequencia == puzzle_correto:
                                        puzzle_vencido = True
                                    else:
                                        puzzle_sequencia = []
                                        for a in puzzle_alavancas: a["ativo"] = False
                            break
                elif e.key == pygame.K_e and cena_atual == CENA_DESERTO and "machado" in inventario:
                    for obj in objetos_cenario:
                        img, cx, oy, tipo, ativo, offset = obj
                        if ativo and tipo == "coqueiro":
                            dist = abs(jogador.rect.centerx - (cx + img.get_width() // 2))
                            if dist < 60:
                                obj[4] = False 
                                coqueiros_cortados += 1
                                pos_ultimo_coqueiro = cx + img.get_width() // 2
                                if coqueiros_cortados >= 3:
                                    vila_reunida = True
                                break
                elif cena_atual == CENA_GAMEOVER:
                    cena_atual, largura_mapa_atual = CENA_DESERTO, LARGURA_MAPA
                    pos_entrada_x = 0
                    jogador, camera = Jogador(CHAO_Y), Camera(LARGURA_TELA, LARGURA_MAPA)
                    inventario, machado_disponivel = [], True
                    carta_disponivel, lendo_carta = True, False
                    coqueiros_cortados, vila_reunida = 0, False
                    pos_ultimo_coqueiro = 0
                    puzzle_sequencia, puzzle_vencido = [], False
                    for alav in puzzle_alavancas: alav["ativo"] = False
                    boss_final_x, boss_final_ativo, boss_final_falando = 3000, False, False
                    for obj in objetos_cenario: obj[4] = True
                    objetos_cenario[6][1], objetos_cenario[10][1], objetos_cenario[12][1] = 2380, 3180, 3580
                    objetos_cenario[8][1] = 2810

        teclas = pygame.key.get_pressed()
        mov = (teclas[pygame.K_d] or teclas[pygame.K_RIGHT]) - (teclas[pygame.K_a] or teclas[pygame.K_LEFT])
        
        if cena_atual in (CENA_DESERTO, CENA_CASA):
            plats = plataformas_chefe if (cena_atual == CENA_CASA and id_casa_atual == 2650 + img_casa2.get_width() // 2) else None
            chao_at = True
            if plats and 400 < jogador.pos_x < 1800: chao_at = False 
            
            if plats: 
                largura_mapa_atual = 3500
                camera.largura_mapa = largura_mapa_atual
            
            jogador.update(dt, teclas, mov, CHAO_Y, largura_mapa_atual, plats, chao_at)
            camera.update(dt, jogador, mov)
            
            if jogador.rect.y > ALTURA_TELA:
                cena_atual = CENA_GAMEOVER
            
            if plats and jogador.pos_x > 1800 and not puzzle_vencido:
                pass
            
            if puzzle_vencido and not boss_final_concluido:
                if boss_final_x > jogador.pos_x + 150:
                    boss_final_x -= 150 * dt
                elif not boss_final_falando:
                    boss_final_falando = True
                    cena_atual = CENA_DIALOGO
                    txt_chefe = "Você mexeu onde não devia, garota!"
                    dialogo_char_idx = 0
                lendo_carta = False
        elif cena_atual == CENA_DIALOGO:
            dialogo_timer += dt
            if dialogo_timer >= dialogo_vel and dialogo_char_idx < len(txt_chefe):
                dialogo_char_idx += 1
                dialogo_timer = 0
        
        if vila_reunida and cena_atual == CENA_DESERTO:
            for obj in objetos_cenario:
                img, x, oy, tipo, ativo, offset = obj
                if tipo in ("aldeao", "chefe"):
                    alvo = pos_ultimo_coqueiro + offset
                    if abs(obj[1] - alvo) > 5:
                        obj[1] += 120 * dt * (1 if obj[1] < alvo else -1)
                
        if cena_atual == CENA_CASA:
            if id_casa_atual == 2300 + img_casa1.get_width() // 2 and machado_disponivel:
                rect_axe = pygame.Rect(400, CHAO_Y - 40, 40, 40)
                if jogador.rect.colliderect(rect_axe):
                    inventario.append("machado")
                    machado_disponivel = False
            
            if id_casa_atual == 3100 + img_casa1.get_width() // 2 and carta_disponivel:
                rect_carta = pygame.Rect(400, CHAO_Y - 30, 40, 40)
                if jogador.rect.colliderect(rect_carta):
                    txt_chefe = "4 3 5 1 2"
                    dialogo_char_idx = 0
                    cena_atual = CENA_DIALOGO
                    lendo_carta = True
                    carta_disponivel = False

        if cena_atual == CENA_CASA and jogador.pos_x <= 0:
            cena_atual, largura_mapa_atual = CENA_DESERTO, LARGURA_MAPA
            jogador.pos_x, jogador.rect.x = pos_entrada_x, int(pos_entrada_x)
            camera.largura_mapa = largura_mapa_atual
            camera.x = max(0, min(jogador.rect.centerx - camera.pos_tela, camera.largura_mapa - camera.largura_tela))

        tela_jogo.fill(CORES["fundo"])
        em_casa = (cena_atual == CENA_CASA) or (cena_atual == CENA_DIALOGO and (boss_final_falando or lendo_carta))
        no_deserto = (cena_atual == CENA_DESERTO) or (cena_atual == CENA_DIALOGO and not boss_final_falando and not lendo_carta)

        if no_deserto:
            for img, spd in [(bg_mountains, 0.2), (bg_dunes, 0.5), (bg_ground, 0.8)]:
                w, shift = img.get_width(), (camera.x * spd) % img.get_width()
                for x in range(int(-shift), LARGURA_TELA, w): tela_jogo.blit(img, (x, 0))

            for i in range(0, largura_mapa_atual, w_chao):
                if -w_chao < i - camera.x < LARGURA_TELA:
                    tela_jogo.blit(img_chao, (i - camera.x, CHAO_Y - 60))

            for obj in objetos_cenario:
                img, cx, oy, tipo, ativo, offset = obj
                if ativo and -img.get_width() < cx - camera.x < LARGURA_TELA:
                    img_draw = img
                    if tipo in ("aldeao", "chefe"):
                        alvo_olhar = pos_ultimo_coqueiro if vila_reunida else jogador.rect.centerx
                        flip = alvo_olhar < cx + img.get_width() // 2
                        img_draw = pygame.transform.flip(img, flip, False)
                    tela_jogo.blit(img_draw, (cx - camera.x, CHAO_Y - img_draw.get_height() + oy))
                    if tipo in ("casa1", "casa2") and abs(jogador.rect.centerx - (cx + img.get_width() // 2)) < 40:
                        draw_arrow_up(tela_jogo, (cx + img.get_width() // 2) - camera.x, CHAO_Y - 80)
                    
                    if tipo == "coqueiro" and "machado" in inventario:
                        if abs(jogador.rect.centerx - (cx + img.get_width() // 2)) < 60:
                            draw_key_hint(tela_jogo, (cx + img.get_width() // 2) - camera.x, CHAO_Y - img.get_height() - 20, "E")
        
        elif em_casa:
            es_casa_chefe = (id_casa_atual == 2650 + img_casa2.get_width() // 2)
            img_chao_render = img_chao_chefe if es_casa_chefe else img_chao_casa
            w_chao_render = w_chao_chefe if es_casa_chefe else w_chao_casa

            for i in range(0, largura_mapa_atual, w_chao_render):
                desenhar_chao = False
                if not es_casa_chefe: desenhar_chao = True
                elif i < 400 or i > 1800: desenhar_chao = True
                
                if desenhar_chao:
                    tela_jogo.blit(img_chao_render, (i - camera.x, CHAO_Y - 60))
            
            if es_casa_chefe:
                for p in plataformas_chefe:
                    for px in range(p.x, p.x + p.width, w_chao_chefe):
                        tela_jogo.blit(img_chao_chefe, (px - camera.x, p.y), (0, 0, min(w_chao_chefe, p.x + p.width - px), p.height))
                    pygame.draw.rect(tela_jogo, (200, 200, 200), (p.x - camera.x, p.y, p.width, p.height), 2)
                
                for alav in puzzle_alavancas:
                    img_alav = img_alavanca
                    if alav["ativo"]: img_alav = pygame.transform.flip(img_alavanca, True, False)
                    tela_jogo.blit(img_alav, (alav["x"] - camera.x, CHAO_Y + 10 - img_alav.get_height()))
                    if abs(jogador.rect.centerx - alav["x"]) < 40 and not puzzle_vencido:
                        draw_key_hint(tela_jogo, alav["x"] - camera.x, CHAO_Y - 80, "E")

                if puzzle_vencido:
                    img_f = pygame.transform.flip(img_chefe2, True, False)
                    tela_jogo.blit(img_f, (boss_final_x - camera.x, CHAO_Y + 10 - img_chefe2.get_height()))
            
            if id_casa_atual == 2300 + img_casa1.get_width() // 2 and machado_disponivel:
                tela_jogo.blit(img_axe, (400 - camera.x, CHAO_Y - 40))
            
            if id_casa_atual == 3100 + img_casa1.get_width() // 2 and carta_disponivel:
                tela_jogo.blit(img_letter, (400 - camera.x, CHAO_Y - 30))

        k = f"{jogador.estado}_{jogador.direcao[:3]}" if jogador.estado != "idle" else "idle"
        if jogador.estado == "fall" and jogador.velX == 0: k = "fall_reto"
        if jogador.current_animation:
            sprite = jogador.current_animation[jogador.frame_index]
            if jogador.direcao == "esquerda": sprite = pygame.transform.flip(sprite, True, False)
            tela_jogo.blit(sprite, (jogador.rect.x - camera.x, jogador.rect.y))
        else:
            pygame.draw.rect(tela_jogo, (255,255,255), (jogador.rect.x - camera.x, jogador.rect.y, *jogador.rect.size))

        if no_deserto:
            rect_j = pygame.Rect(jogador.rect.x - camera.x, jogador.rect.y, *jogador.rect.size)
            for cx, cy, idx in cactos_fg:
                img_v = variacoes_cacto[idx]
                x = (cx - camera.x * 1.8) % 3200 - 600
                img_v.set_alpha(150 if pygame.Rect(x, cy, *img_v.get_size()).colliderect(rect_j) else 255)
                tela_jogo.blit(img_v, (x, cy))

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

        if mostrar_prompt:
            txt = fonts["ui"].render("PRESSIONE 'W' OU '↑' PARA ENTRAR", False, CORES["texto"])
            smd = fonts["ui"].render("PRESSIONE 'W' OU '↑' PARA ENTRAR", False, CORES["fundo"])
            px, py = LARGURA_TELA // 2 - txt.get_width() // 2, ALTURA_TELA - 50
            tela.blit(smd, (px + 2, py + 2)); tela.blit(txt, (px, py))

        if cena_atual == CENA_DIALOGO:
            overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150)); tela.blit(overlay, (0, 0))
            
            if lendo_carta:
                pygame.draw.rect(tela, (30, 30, 30), (50, ALTURA_TELA - 150, LARGURA_TELA - 100, 100))
                pygame.draw.rect(tela, (200, 200, 200), (50, ALTURA_TELA - 150, LARGURA_TELA - 100, 100), 2)
                tela.blit(img_hope, (20, ALTURA_TELA - 380))
                tela.blit(fonts["ui"].render("CARTA:", False, (255, 255, 255)), (280, ALTURA_TELA - 140))
                tela.blit(fonts["dialogo"].render(txt_chefe[:dialogo_char_idx], False, (220, 220, 220)), (280, ALTURA_TELA - 100))
            else:
                tela.blit(img_chefe_dialogo, (LARGURA_TELA - img_chefe_dialogo.get_width() + 50, ALTURA_TELA - 350))
                pygame.draw.rect(tela, (0, 0, 0), (50, ALTURA_TELA - 150, LARGURA_TELA - 100, 100))
                pygame.draw.rect(tela, (255, 255, 255), (50, ALTURA_TELA - 150, LARGURA_TELA - 100, 100), 2)
                tela.blit(fonts["ui"].render("CHEFE:", False, (200, 0, 0)), (70, ALTURA_TELA - 140))
                tela.blit(fonts["dialogo"].render(txt_chefe[:dialogo_char_idx], False, (180, 180, 180)), (70, ALTURA_TELA - 100))
            if dialogo_char_idx >= len(txt_chefe):
                inst = fonts["instrucao"].render("Pressione qualquer tecla para continuar...", False, (100, 100, 100))
                tela.blit(inst, (LARGURA_TELA - inst.get_width() - 70, ALTURA_TELA - 70))

        elif cena_atual == CENA_GAMEOVER:
            tela.fill(CORES["fundo"])
            txt_go = fonts["grande"].render("GAME OVER", False, CORES["go"])
            tela.blit(txt_go, (LARGURA_TELA // 2 - txt_go.get_width() // 2, ALTURA_TELA // 2 - 100))
            txt_r = fonts["ui"].render("Pressione qualquer tecla para reiniciar", False, CORES["texto"])
            tela.blit(txt_r, (LARGURA_TELA // 2 - txt_r.get_width() // 2, ALTURA_TELA // 2 + 50))

        if cena_atual != CENA_GAMEOVER:
            inv_rect = pygame.Rect(20, 20, 60, 60)
            overlay_inv = pygame.Surface((60, 60), pygame.SRCALPHA)
            overlay_inv.fill((0, 0, 0, 120)) 
            tela.blit(overlay_inv, (20, 20))
            pygame.draw.rect(tela, (255, 255, 255, 180), inv_rect, 2) 
            
            if "machado" in inventario:
                ax, ay = 20 + (60 - img_axe.get_width()) // 2, 20 + (60 - img_axe.get_height()) // 2
                tela.blit(img_axe, (ax, ay))

        if iris_ativa:
            iris_raio = max(0, iris_raio - iris_velocidade * dt)
            px = jogador.rect.centerx - camera.x
            py = jogador.rect.centery
            s_iris = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
            s_iris.fill((0, 0, 0, 255))
            pygame.draw.circle(s_iris, (0, 0, 0, 0), (int(px), int(py)), int(iris_raio))
            tela.blit(s_iris, (0, 0))
            
            if iris_raio <= 0:
                txt_fim = fonts["ui"].render("To Be Continued...", False, (255, 255, 255))
                tela.blit(txt_fim, (LARGURA_TELA // 2 - txt_fim.get_width() // 2, ALTURA_TELA // 2 - 20))

        pygame.display.flip()

if __name__ == "__main__":
    main()