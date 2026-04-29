import pygame
import sys
import random
from entities import Jogador, Camera, SistemaVisual
from settings import *
from utils import load_scaled, draw_arrow_up, draw_key_hint

# ==========================================
# CONFIGURAÇÕES DA FASE 5 (ODS 6)
# ==========================================
LARGURA_MAPA = 4000
CHAO_Y = 620

CORES = {
    "idle": (255, 255, 255),
    "fundo": (0, 0, 0),
    "texto": (255, 255, 255),
    "chefe": (255, 255, 0),
    "instrucao": (200, 200, 200),
    "go": (255, 0, 0)
}

CENA_DESERTO = "deserto"
CENA_CASA = "casa"
CENA_DIALOGO = "dialogo"
CENA_GAMEOVER = "gameover"

# ==========================================
# GAME CLASS
# ==========================================
class Game:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED | pygame.RESIZABLE)
        pygame.display.set_caption("Fase 5 - ODS 6")
        self.clock = pygame.time.Clock()
        self.tela_jogo = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
        
        self.load_assets()
        self.reset()
        
        self.visual = SistemaVisual(LARGURA_TELA, ALTURA_TELA)
        self.mouse_pos = (LARGURA_TELA // 2, ALTURA_TELA // 2)

    def load_assets(self):
        # Backgrounds
        self.bg_mountains = load_scaled("assets/desert_mountains.png", ALTURA_TELA)
        self.bg_dunes = load_scaled("assets/desert_dunes.png", ALTURA_TELA)
        self.bg_ground = load_scaled("assets/desert_ground.png", ALTURA_TELA)
        self.img_chao = load_scaled("assets/chao_deserto.png", 160)
        self.w_chao = self.img_chao.get_width()

        # Objects & Entities
        self.img_coqueiro = load_scaled("assets/coqueiro.png", 200)
        self.img_casa1 = load_scaled("assets/casa1.png", 200)
        self.img_casa2 = load_scaled("assets/casa2.png", 280)
        self.img_aldeao1 = load_scaled("assets/aldeao1.png", 70)
        self.img_aldeao2 = load_scaled("assets/aldeao2.png", 70)
        self.img_chefe1 = load_scaled("assets/chefe1.png", 75)
        self.img_chefe2 = load_scaled("assets/chefe2.png", 75)
        self.img_chefe_dialogo = pygame.transform.flip(load_scaled("assets/chefe2.png", 450), True, False)
        
        # Floors
        self.img_chao_casa = load_scaled("assets/chao_casa1.png", 160)
        self.w_chao_casa = self.img_chao_casa.get_width()
        self.img_chao_chefe = load_scaled("assets/chao_chefe.png", 160)
        self.w_chao_chefe = self.img_chao_chefe.get_width()
        
        # Items & Misc
        self.img_alavanca = load_scaled("assets/alavanca.png", 50)
        self.img_hope = load_scaled("assets/hope.png", 300) 
        self.img_axe = load_scaled("assets/axe.png", 40)
        self.img_letter = load_scaled("assets/carta.png", 30)
        self.img_coco = load_scaled("assets/coco.png", 15)

        # Cacti variants
        self.variacoes_cacto = []
        for h in [350, 450, 550]:
            img = load_scaled("assets/cacto.png", h)
            img_blur = pygame.transform.smoothscale(img, (img.get_width() // 4, img.get_height() // 4))
            self.variacoes_cacto.append(pygame.transform.smoothscale(img_blur, (img.get_width(), img.get_height())))
        
        self.cactos_fg = [(100, 420, 0), (1200, 370, 1), (2200, 320, 2)]

        # Fonts
        self.fonts = {
            "ui": pygame.font.SysFont("Consolas", 20, bold=True),
            "dialogo": pygame.font.SysFont("Consolas", 16, bold=True),
            "instrucao": pygame.font.SysFont("Consolas", 12),
            "grande": pygame.font.SysFont("Consolas", 70, bold=True)
        }

    def reset(self):
        self.cena_atual = CENA_DESERTO
        self.largura_mapa_atual = LARGURA_MAPA
        self.pos_entrada_x = 0
        self.id_casa_atual = 0
        self.tipo_casa_proxima = None
        
        self.inventario = []
        self.machado_disponivel = True
        self.carta_disponivel = True
        self.lendo_carta = False
        self.coqueiros_cortados = 0
        self.vila_reunida = False
        self.pos_ultimo_coqueiro = 0
        
        # Puzzles & Boss
        self.puzzle_alavancas = [{"x": 2000 + i*120, "ativo": False, "id": i+1} for i in range(5)]
        self.puzzle_sequencia = []
        self.puzzle_correto = [4, 3, 5, 1, 2]
        self.puzzle_vencido = False
        
        self.boss_final_x = 3000
        self.boss_final_ativo = False
        self.boss_final_falando = False
        self.boss_final_concluido = False
        
        self.cocos_caindo = []
        self.iris_raio = LARGURA_TELA
        self.iris_ativa = False
        self.iris_velocidade = 800
        
        self.jogador = Jogador(CHAO_Y)
        self.camera = Camera(LARGURA_TELA, self.largura_mapa_atual)
        
        self.dialogo_char_idx = 0
        self.dialogo_timer = 0
        self.dialogo_vel = 0.05
        self.txt_chefe = "Pare de mexer onde não é chamada!"
        
        self.plataformas_chefe = [
            pygame.Rect(500, CHAO_Y - 100, 150, 20),
            pygame.Rect(750, CHAO_Y - 200, 150, 20),
            pygame.Rect(1000, CHAO_Y - 100, 150, 20),
            pygame.Rect(1250, CHAO_Y - 200, 150, 20),
            pygame.Rect(1550, CHAO_Y - 120, 250, 20) 
        ]

        self.objetos_cenario = [
            [self.img_coqueiro, 250, 0, "coqueiro", True, 0, 0, 0],
            [self.img_coqueiro, 700, 0, "coqueiro", True, 0, 0, 0],
            [self.img_coqueiro, 1100, 0, "coqueiro", True, 0, 0, 0],
            [self.img_coqueiro, 1500, 0, "coqueiro", True, 0, 0, 0],
            [self.img_coqueiro, 1900, 0, "coqueiro", True, 0, 0, 0],
            [self.img_casa1, 2300, 0, "casa1", True, 0, 0, 0],
            [self.img_aldeao1, 2380, 5, "aldeao", True, -80, 0, 0],
            [self.img_casa2, 2650, 15, "casa2", True, 0, 0, 0],
            [self.img_chefe1, 2810, 10, "chefe", True, 0, 0, 0],
            [self.img_casa1, 3100, 0, "casa1", True, 0, 0, 0],
            [self.img_aldeao2, 3180, 5, "aldeao", True, 80, 0, 0],
            [self.img_casa1, 3500, 0, "casa1", True, 0, 0, 0],
            [self.img_aldeao1, 3580, 5, "aldeao", True, 160, 0, 0]
        ]

    def handle_events(self):
        mostrar_prompt = False
        if self.cena_atual == CENA_DESERTO:
            for obj in self.objetos_cenario:
                img, cx, oy, tipo, ativo, offset, golpes, shake = obj
                if ativo and tipo in ("casa1", "casa2"):
                    porta_x = cx + img.get_width() // 2
                    if abs(self.jogador.rect.centerx - porta_x) < 40:
                        mostrar_prompt, self.tipo_casa_proxima = True, img
                        break

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif e.type == pygame.MOUSEWHEEL:
                self.visual.handle_event(e)
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_F11: pygame.display.toggle_fullscreen()
                elif e.key in (pygame.K_w, pygame.K_UP):
                    self.process_up_key(mostrar_prompt)
                elif e.key == pygame.K_e:
                    self.process_interaction_key()
                elif self.cena_atual == CENA_GAMEOVER:
                    self.reset()
        
        return mostrar_prompt

    def process_up_key(self, mostrar_prompt):
        if mostrar_prompt and self.cena_atual == CENA_DESERTO:
            porta_x = 0
            for obj in self.objetos_cenario:
                if obj[3] in ("casa1", "casa2") and abs(self.jogador.rect.centerx - (obj[1] + obj[0].get_width() // 2)) < 40:
                    porta_x = obj[1] + obj[0].get_width() // 2
                    break
            
            if self.tipo_casa_proxima == self.img_casa1:
                self.enter_house(porta_x)
            else:
                if self.vila_reunida:
                    self.enter_house(porta_x)
                else:
                    self.cena_atual, self.jogador.velX, self.dialogo_char_idx = CENA_DIALOGO, 0, 0
                    self.txt_chefe = "Pare de mexer onde não é chamada!"
                    self.lendo_carta = False
        elif self.cena_atual == CENA_DIALOGO:
            if self.dialogo_char_idx < len(self.txt_chefe):
                self.dialogo_char_idx = len(self.txt_chefe)
            else:
                self.advance_dialogue()
        else:
            self.jogador.jumpBuffer = 0.15

    def enter_house(self, porta_x):
        self.pos_entrada_x = self.jogador.pos_x
        self.cena_atual = CENA_CASA
        self.largura_mapa_atual = 800
        self.id_casa_atual = porta_x 
        self.jogador.pos_x = self.jogador.rect.x = 80
        self.jogador.velX = 0
        self.camera.largura_mapa, self.camera.x = self.largura_mapa_atual, 0

    def advance_dialogue(self):
        if self.lendo_carta:
            self.cena_atual = CENA_CASA
            self.lendo_carta = False
        elif self.boss_final_falando:
            self.cena_atual = CENA_CASA
            self.boss_final_concluido = True
            self.boss_final_falando = False
            self.iris_ativa = True 
        else:
            self.cena_atual = CENA_GAMEOVER

    def process_interaction_key(self):
        if self.cena_atual == CENA_CASA:
            # Check lever puzzle
            es_casa_chefe = (self.id_casa_atual == 2650 + self.img_casa2.get_width() // 2)
            if es_casa_chefe:
                for alav in self.puzzle_alavancas:
                    if abs(self.jogador.rect.centerx - alav["x"]) < 40 and not self.puzzle_vencido:
                        alav["ativo"] = not alav["ativo"]
                        if alav["id"] not in self.puzzle_sequencia:
                            self.puzzle_sequencia.append(alav["id"])
                            if len(self.puzzle_sequencia) == len(self.puzzle_correto):
                                if self.puzzle_sequencia == self.puzzle_correto:
                                    self.puzzle_vencido = True
                                else:
                                    self.puzzle_sequencia = []
                                    for a in self.puzzle_alavancas: a["ativo"] = False
                        break
        elif self.cena_atual == CENA_DESERTO:
            for obj in self.objetos_cenario:
                img, cx, oy, tipo, ativo, offset, golpes, shake = obj
                if ativo and tipo == "coqueiro":
                    dist = abs(self.jogador.rect.centerx - (cx + img.get_width() // 2))
                    if dist < 60:
                        if "machado" in self.inventario:
                            obj[4] = False 
                            self.coqueiros_cortados += 1
                            self.pos_ultimo_coqueiro = cx + img.get_width() // 2
                            if self.coqueiros_cortados == 5:
                                self.cena_atual = CENA_GAMEOVER
                            elif self.coqueiros_cortados >= 3:
                                self.vila_reunida = True
                        else:
                            obj[6] += 1
                            obj[7] = 0.3
                            if obj[6] >= 3:
                                self.cocos_caindo.append({
                                    "x": cx + img.get_width() // 2 - self.img_coco.get_width() // 2,
                                    "y": CHAO_Y - img.get_height() + 60,
                                    "velY": 0
                                })
                                obj[6] = 0
                        break

    def update(self, dt):
        self.mouse_pos = pygame.mouse.get_pos()
        
        if self.cena_atual in (CENA_DESERTO, CENA_CASA):
            plats = self.plataformas_chefe if (self.cena_atual == CENA_CASA and self.id_casa_atual == 2650 + self.img_casa2.get_width() // 2) else None
            chao_at = True
            if plats and 400 < self.jogador.pos_x < 1800: chao_at = False 
            
            if plats: 
                self.largura_mapa_atual = 3500
                self.camera.largura_mapa = self.largura_mapa_atual
            
            teclas = pygame.key.get_pressed()
            mov = (teclas[pygame.K_d] or teclas[pygame.K_RIGHT]) - (teclas[pygame.K_a] or teclas[pygame.K_LEFT])
            self.jogador.update(dt, teclas, mov, CHAO_Y, self.largura_mapa_atual, plats, chao_at)
            self.camera.update(dt, self.jogador, mov)
            
            # Falling coconuts update
            for coco in self.cocos_caindo[:]:
                coco["velY"] += 1600 * dt
                coco["y"] += coco["velY"] * dt
                rect_coco = pygame.Rect(coco["x"], coco["y"], self.img_coco.get_width(), self.img_coco.get_height())
                if rect_coco.colliderect(self.jogador.rect):
                    self.cena_atual = CENA_GAMEOVER
                    break
                if coco["y"] > CHAO_Y + 50:
                    self.cocos_caindo.remove(coco)

            if self.jogador.rect.y > ALTURA_TELA:
                self.cena_atual = CENA_GAMEOVER
            
            if self.puzzle_vencido and not self.boss_final_concluido:
                if self.boss_final_x > self.jogador.pos_x + 150:
                    self.boss_final_x -= 150 * dt
                elif not self.boss_final_falando:
                    self.boss_final_falando = True
                    self.cena_atual = CENA_DIALOGO
                    self.txt_chefe = "Você mexeu onde não devia, garota!"
                    self.dialogo_char_idx = 0
                self.lendo_carta = False
        
        elif self.cena_atual == CENA_DIALOGO:
            self.dialogo_timer += dt
            if self.dialogo_timer >= self.dialogo_vel and self.dialogo_char_idx < len(self.txt_chefe):
                self.dialogo_char_idx += 1
                self.dialogo_timer = 0
        
        if self.vila_reunida and self.cena_atual == CENA_DESERTO:
            for obj in self.objetos_cenario:
                if obj[3] in ("aldeao", "chefe"):
                    alvo = self.pos_ultimo_coqueiro + obj[5]
                    if abs(obj[1] - alvo) > 5:
                        obj[1] += 120 * dt * (1 if obj[1] < alvo else -1)
        
        for obj in self.objetos_cenario:
            if obj[7] > 0: obj[7] = max(0, obj[7] - dt)

        # House entry/item collection
        if self.cena_atual == CENA_CASA:
            if self.id_casa_atual == 2300 + self.img_casa1.get_width() // 2 and self.machado_disponivel:
                rect_axe = pygame.Rect(400, CHAO_Y - 40, 40, 40)
                if self.jogador.rect.colliderect(rect_axe):
                    self.inventario.append("machado")
                    self.machado_disponivel = False
            
            if self.id_casa_atual == 3100 + self.img_casa1.get_width() // 2 and self.carta_disponivel:
                rect_carta = pygame.Rect(400, CHAO_Y - 30, 40, 40)
                if self.jogador.rect.colliderect(rect_carta):
                    self.txt_chefe = "4 3 5 1 2"
                    self.dialogo_char_idx = 0
                    self.cena_atual = CENA_DIALOGO
                    self.lendo_carta = True
                    self.carta_disponivel = False

            if self.jogador.pos_x <= 0:
                self.exit_house()

    def exit_house(self):
        self.cena_atual, self.largura_mapa_atual = CENA_DESERTO, LARGURA_MAPA
        self.jogador.pos_x, self.jogador.rect.x = self.pos_entrada_x, int(self.pos_entrada_x)
        self.camera.largura_mapa = self.largura_mapa_atual
        self.camera.x = max(0, min(self.jogador.rect.centerx - self.camera.pos_tela, self.camera.largura_mapa - self.camera.largura_tela))

    def draw(self, mostrar_prompt):
        self.tela_jogo.fill(CORES["fundo"])
        em_casa = (self.cena_atual == CENA_CASA) or (self.cena_atual == CENA_DIALOGO and (self.boss_final_falando or self.lendo_carta))
        no_deserto = (self.cena_atual == CENA_DESERTO) or (self.cena_atual == CENA_DIALOGO and not self.boss_final_falando and not self.lendo_carta)

        if no_deserto:
            self.draw_desert()
        elif em_casa:
            self.draw_house()

        self.draw_player()
        
        if no_deserto:
            self.draw_foreground_cacti()

        # Zoom & Final UI
        self.visual.render(self.tela_jogo, self.tela, self.mouse_pos)

        if mostrar_prompt: self.render_prompt()
        if self.cena_atual == CENA_DIALOGO: self.render_dialogue()
        elif self.cena_atual == CENA_GAMEOVER: self.render_gameover()
        
        if self.cena_atual != CENA_GAMEOVER: self.render_inventory()
        if self.iris_ativa: self.render_iris()

        pygame.display.flip()

    def draw_desert(self):
        for img, spd in [(self.bg_mountains, 0.2), (self.bg_dunes, 0.5), (self.bg_ground, 0.8)]:
            w, shift = img.get_width(), ((self.camera.x - self.camera.offset_x) * spd) % img.get_width()
            for x in range(int(-shift), LARGURA_TELA, w): self.tela_jogo.blit(img, (x, 0))

        for i in range(0, self.largura_mapa_atual, self.w_chao):
            if -self.w_chao < i - (self.camera.x - self.camera.offset_x) < LARGURA_TELA:
                self.tela_jogo.blit(self.img_chao, (i - (self.camera.x - self.camera.offset_x), CHAO_Y - 60))

        for obj in self.objetos_cenario:
            img, cx, oy, tipo, ativo, offset, golpes, shake = obj
            if ativo and -img.get_width() < cx - (self.camera.x - self.camera.offset_x) < LARGURA_TELA:
                img_draw = img
                if tipo in ("aldeao", "chefe"):
                    alvo_olhar = self.pos_ultimo_coqueiro if self.vila_reunida else self.jogador.rect.centerx
                    flip = alvo_olhar < cx + img.get_width() // 2
                    img_draw = pygame.transform.flip(img, flip, False)
                
                dx = random.randint(-4, 4) if shake > 0 else 0
                self.tela_jogo.blit(img_draw, (cx - (self.camera.x - self.camera.offset_x) + dx, CHAO_Y - img_draw.get_height() + oy))
                if tipo in ("casa1", "casa2") and abs(self.jogador.rect.centerx - (cx + img.get_width() // 2)) < 40:
                    draw_arrow_up(self.tela_jogo, (cx + img.get_width() // 2) - (self.camera.x - self.camera.offset_x), CHAO_Y - 80)
                if tipo == "coqueiro" and abs(self.jogador.rect.centerx - (cx + img.get_width() // 2)) < 60:
                    draw_key_hint(self.tela_jogo, (cx + img.get_width() // 2) - (self.camera.x - self.camera.offset_x), CHAO_Y - img.get_height() - 20, "E")
        
        for coco in self.cocos_caindo:
            self.tela_jogo.blit(self.img_coco, (coco["x"] - (self.camera.x - self.camera.offset_x), coco["y"]))

    def draw_house(self):
        es_casa_chefe = (self.id_casa_atual == 2650 + self.img_casa2.get_width() // 2)
        img_chao_render = self.img_chao_chefe if es_casa_chefe else self.img_chao_casa
        w_chao_render = self.w_chao_chefe if es_casa_chefe else self.w_chao_casa

        for i in range(0, self.largura_mapa_atual, w_chao_render):
            desenhar_chao = False
            if not es_casa_chefe: desenhar_chao = True
            elif i < 400 or i > 1800: desenhar_chao = True
            if desenhar_chao: self.tela_jogo.blit(img_chao_render, (i - (self.camera.x - self.camera.offset_x), CHAO_Y - 60))
        
        if es_casa_chefe:
            for p in self.plataformas_chefe:
                for px in range(p.x, p.x + p.width, w_chao_render):
                    self.tela_jogo.blit(self.img_chao_chefe, (px - (self.camera.x - self.camera.offset_x), p.y), (0, 0, min(self.w_chao_chefe, p.x + p.width - px), p.height))
                pygame.draw.rect(self.tela_jogo, (200, 200, 200), (p.x - (self.camera.x - self.camera.offset_x), p.y, p.width, p.height), 2)
            
            for alav in self.puzzle_alavancas:
                img_alav = self.img_alavanca
                if alav["ativo"]: img_alav = pygame.transform.flip(self.img_alavanca, True, False)
                self.tela_jogo.blit(img_alav, (alav["x"] - (self.camera.x - self.camera.offset_x), CHAO_Y + 10 - img_alav.get_height()))
                if abs(self.jogador.rect.centerx - alav["x"]) < 40 and not self.puzzle_vencido:
                    draw_key_hint(self.tela_jogo, alav["x"] - (self.camera.x - self.camera.offset_x), CHAO_Y - 80, "E")

            if self.puzzle_vencido:
                img_f = pygame.transform.flip(self.img_chefe2, True, False)
                self.tela_jogo.blit(img_f, (self.boss_final_x - (self.camera.x - self.camera.offset_x), CHAO_Y + 10 - self.img_chefe2.get_height()))
        
        if self.id_casa_atual == 2300 + self.img_casa1.get_width() // 2 and self.machado_disponivel:
            self.tela_jogo.blit(self.img_axe, (400 - (self.camera.x - self.camera.offset_x), CHAO_Y - 40))
        if self.id_casa_atual == 3100 + self.img_casa1.get_width() // 2 and self.carta_disponivel:
            self.tela_jogo.blit(self.img_letter, (400 - (self.camera.x - self.camera.offset_x), CHAO_Y - 30))

    def draw_player(self):
        if self.jogador.current_animation:
            sprite = self.jogador.current_animation[self.jogador.frame_index]
            if self.jogador.direcao == "esquerda": sprite = pygame.transform.flip(sprite, True, False)
            offsetX = (sprite.get_width() - self.jogador.rect.width) // 2
            self.tela_jogo.blit(sprite, (self.jogador.rect.x - (self.camera.x - self.camera.offset_x) - offsetX, self.jogador.rect.y))
        else:
            pygame.draw.rect(self.tela_jogo, (255,255,255), (self.jogador.rect.x - (self.camera.x - self.camera.offset_x), self.jogador.rect.y, *self.jogador.rect.size))

    def draw_foreground_cacti(self):
        rect_j = pygame.Rect(self.jogador.rect.x - (self.camera.x - self.camera.offset_x), self.jogador.rect.y, *self.jogador.rect.size)
        for cx, cy, idx in self.cactos_fg:
            img_v = self.variacoes_cacto[idx]
            x = (cx - (self.camera.x - self.camera.offset_x) * 1.8) % 3200 - 600
            img_v.set_alpha(150 if pygame.Rect(x, cy, *img_v.get_size()).colliderect(rect_j) else 255)
            self.tela_jogo.blit(img_v, (x, cy))

    def render_prompt(self):
        txt = self.fonts["ui"].render("PRESSIONE 'W' OU '↑' PARA ENTRAR", False, CORES["texto"])
        smd = self.fonts["ui"].render("PRESSIONE 'W' OU '↑' PARA ENTRAR", False, CORES["fundo"])
        px, py = LARGURA_TELA // 2 - txt.get_width() // 2, ALTURA_TELA - 50
        self.tela.blit(smd, (px + 2, py + 2)); self.tela.blit(txt, (px, py))

    def render_dialogue(self):
        overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150)); self.tela.blit(overlay, (0, 0))
        if self.lendo_carta:
            pygame.draw.rect(self.tela, (30, 30, 30), (50, ALTURA_TELA - 150, LARGURA_TELA - 100, 100))
            pygame.draw.rect(self.tela, (200, 200, 200), (50, ALTURA_TELA - 150, LARGURA_TELA - 100, 100), 2)
            self.tela.blit(self.img_hope, (20, ALTURA_TELA - 380))
            self.tela.blit(self.fonts["ui"].render("CARTA:", False, (255, 255, 255)), (280, ALTURA_TELA - 140))
            self.tela.blit(self.fonts["dialogo"].render(self.txt_chefe[:self.dialogo_char_idx], False, (220, 220, 220)), (280, ALTURA_TELA - 100))
        else:
            self.tela.blit(self.img_chefe_dialogo, (LARGURA_TELA - self.img_chefe_dialogo.get_width() + 50, ALTURA_TELA - 350))
            pygame.draw.rect(self.tela, (0, 0, 0), (50, ALTURA_TELA - 150, LARGURA_TELA - 100, 100))
            pygame.draw.rect(self.tela, (255, 255, 255), (50, ALTURA_TELA - 150, LARGURA_TELA - 100, 100), 2)
            self.tela.blit(self.fonts["ui"].render("CHEFE:", False, (200, 0, 0)), (70, ALTURA_TELA - 140))
            self.tela.blit(self.fonts["dialogo"].render(self.txt_chefe[:self.dialogo_char_idx], False, (180, 180, 180)), (70, ALTURA_TELA - 100))
        if self.dialogo_char_idx >= len(self.txt_chefe):
            inst = self.fonts["instrucao"].render("Pressione qualquer tecla para continuar...", False, (100, 100, 100))
            self.tela.blit(inst, (LARGURA_TELA - inst.get_width() - 70, ALTURA_TELA - 70))

    def render_gameover(self):
        self.tela.fill(CORES["fundo"])
        txt_go = self.fonts["grande"].render("GAME OVER", False, CORES["go"])
        self.tela.blit(txt_go, (LARGURA_TELA // 2 - txt_go.get_width() // 2, ALTURA_TELA // 2 - 100))
        txt_r = self.fonts["ui"].render("Pressione qualquer tecla para reiniciar", False, CORES["texto"])
        self.tela.blit(txt_r, (LARGURA_TELA // 2 - txt_r.get_width() // 2, ALTURA_TELA // 2 + 50))

    def render_inventory(self):
        overlay_inv = pygame.Surface((60, 60), pygame.SRCALPHA)
        overlay_inv.fill((0, 0, 0, 120)) 
        self.tela.blit(overlay_inv, (20, 20))
        pygame.draw.rect(self.tela, (255, 255, 255, 180), (20, 20, 60, 60), 2) 
        if "machado" in self.inventario:
            ax, ay = 20 + (60 - self.img_axe.get_width()) // 2, 20 + (60 - self.img_axe.get_height()) // 2
            self.tela.blit(self.img_axe, (ax, ay))

    def render_iris(self):
        dt = self.clock.get_time() / 1000.0
        self.iris_raio = max(0, self.iris_raio - self.iris_velocidade * dt)
        px = self.jogador.rect.centerx - (self.camera.x - self.camera.offset_x)
        py = self.jogador.rect.centery
        s_iris = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        s_iris.fill((0, 0, 0, 255))
        pygame.draw.circle(s_iris, (0, 0, 0, 0), (int(px), int(py)), int(self.iris_raio))
        self.tela.blit(s_iris, (0, 0))
        if self.iris_raio <= 0:
            txt_fim = self.fonts["ui"].render("To Be Continued...", False, (255, 255, 255))
            self.tela.blit(txt_fim, (LARGURA_TELA // 2 - txt_fim.get_width() // 2, ALTURA_TELA // 2 - 20))

    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000.0
            mostrar_prompt = self.handle_events()
            self.update(dt)
            self.draw(mostrar_prompt)

if __name__ == "__main__":
    Game().run()