# Hope's Adventure - ODS 6 (Fase 5)

Uma aventura interativa em 2D desenvolvida com **Python** e **Pygame**, focada na temática de preservação e descoberta no deserto (inspirado na ODS 6 - Água Potável e Saneamento).

## 🎮 O Jogo
Acompanhe **Hope** em uma jornada por uma vila isolada no deserto. Explore casas, encontre itens perdidos e resolva enigmas lógicos para confrontar o chefe da vila e descobrir o que está escondido atrás de suas portas trancadas.

## ✨ Funcionalidades
- **Mecânicas de Exploração**: Coleta de itens (Machado, Cartas) e interação com o cenário.
- **Puzzles Lógicos**: Sistema de alavancas com sequências específicas e reset dinâmico.
- **Desafios de Plataforma**: Níveis internos com abismos e saltos de precisão.
- **Narrativa Interativa**: Sistema de diálogos com perfis de personagens e backgrounds dinâmicos.
- **Visual Retro**: Estética Pixel Art com sistema de zoom dinâmico e paralaxe no deserto.
- **Transições Cinematográficas**: Efeito de fechamento de íris ("Iris Out") para encerramento de cenas.

## ⌨️ Controles
| Ação | Tecla |
|------|-------|
| Movimentação | `A` / `D` ou `Setas` |
| Pular / Entrar em Casas | `W` / `Seta Cima` |
| Interagir (Cortar/Alavanca) | `E` |
| Tela Cheia | `F11` |
| Zoom | `Scroll do Mouse` |

## 🚀 Como Executar

1. **Pré-requisitos**:
   - Python 3.12 ou superior.
   - Biblioteca Pygame instalada.

2. **Instalação**:
   ```bash
   pip install pygame
   ```

3. **Execução**:
   ```bash
   python main.py
   ```

## 📁 Estrutura do Projeto
- `main.py`: Loop principal, gerenciamento de estados e renderização.
- `entities.py`: Lógica de física da protagonista (Hope) e comportamento da câmera elástica.
- `assets/`: Sprites, fundos e texturas do jogo.
- `COMO_JOGAR.txt`: Guia rápido para o usuário final.

---
Desenvolvido como parte do projeto **pygamePI4**.
*"A água é o segredo escondido no coração do deserto."*
