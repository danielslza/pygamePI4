import pygame

class Jogador:
    def __init__(self, CHAO_Y):
        self.rect = pygame.Rect(100, CHAO_Y - 80, 40, 80)
        self.velX = self.velY = self.jumpBuffer = 0
        self.velocidadeMax, self.aceleracao, self.desaceleracao = 400, 1000, 1400
        self.forcaPulo, self.gravidade, self.gravidadeQueda = -820, 1600, 2000
        self.noChao, self.direcao, self.estado = True, "direita", "idle"

    def update(self, dt, teclas, mov, CHAO_Y, LARGURA_MAPA):
        self.jumpBuffer = max(0, self.jumpBuffer - dt)

        if mov:
            self.direcao = "direita" if mov > 0 else "esquerda"
            acel = self.desaceleracao if mov * self.velX < 0 else self.aceleracao
            self.velX = max(-self.velocidadeMax, min(self.velocidadeMax, self.velX + mov * acel * dt))
        else:
            self.velX = max(0, abs(self.velX) - self.desaceleracao * dt) * (1 if self.velX > 0 else -1)

        self.rect.x = max(0, min(LARGURA_MAPA - self.rect.width, self.rect.x + self.velX * dt))
        if self.rect.x in (0, LARGURA_MAPA - self.rect.width): self.velX = 0

        self.velY += (self.gravidade if self.velY < 0 else self.gravidadeQueda) * dt
        self.rect.y += self.velY * dt

        if self.rect.bottom >= CHAO_Y:
            self.rect.bottom, self.velY, self.noChao = CHAO_Y, 0, True
        else:
            self.noChao = False

        if self.jumpBuffer > 0 and self.noChao:
            self.velY, self.noChao, self.jumpBuffer = self.forcaPulo, False, 0
        elif not (teclas[pygame.K_w] or teclas[pygame.K_UP]) and self.velY < 0:
            self.velY *= 0.7

        self.estado = "jump" if self.velY < 0 else "fall" if not self.noChao else "run" if self.velX else "idle"

class Camera:
    def __init__(self, largura_tela, largura_mapa):
        self.x = 0.0
        self.largura_tela, self.largura_mapa = largura_tela, largura_mapa
        self.pos_tela = largura_tela / 2

    def update(self, dt, jogador, mov):
        alvo_pos = self.largura_tela * (0.4 if mov > 0 else 0.6 if mov < 0 else 0.45 if jogador.direcao == "direita" else 0.55)
        self.pos_tela += (alvo_pos - self.pos_tela) * 2.0 * dt
        alvoCamera = jogador.rect.centerx - self.pos_tela
        
        vel = min(0.5 + abs(alvoCamera - self.x) / 80.0 * 4.5, 8.0)
        self.x = max(0, min(self.x + (alvoCamera - self.x) * vel * dt, self.largura_mapa - self.largura_tela))