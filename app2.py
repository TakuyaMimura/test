#python -m venv venv
#venv\Scripts\activate
#pip install pygame

import pygame
import random

# --- 設定 ---
CELL_SIZE = 30 #1マスのサイズ（ピクセル）
COLS = 10 #横のマス数
ROWS = 20 #縦のマス数
WIDTH = CELL_SIZE * COLS #画面の幅
HEIGHT = CELL_SIZE * ROWS #画面の高さ
FPS = 20 #ゲームのフレームレート

# テトリミノの形（7種類）
# 各形は 2次元リストで表現され、1 がブロックを示す
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 0, 0], [1, 1, 1]],  # L
    [[0, 0, 1], [1, 1, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]],  # Z
]
# テトリミノに対応する色のリスト
COLORS = [(0,255,255),(255,255,0),(128,0,128),(255,165,0),(0,0,255),(0,255,0),(255,0,0)]

#テトリミノを時計回りに90度回転させる
def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]

#衝突判定：テトリミノが盤面外や既存ブロックと衝突していないかをチェック
def check_collision(board, shape, offset):
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                if x + off_x < 0 or x + off_x >= COLS or y + off_y >= ROWS:
                    return True
                if y + off_y >= 0 and board[y + off_y][x + off_x]:
                    return True
    return False

#一列そろった行を削除し、上から空行を挿入する
def remove_row(board):
    new_board = [row for row in board if not all(cell != 0 for cell in row)]
    lines_cleared = ROWS - len(new_board)
    for _ in range(lines_cleared):
        new_board.insert(0, [0 for _ in range(COLS)])
    return new_board, lines_cleared

#ゲーム画面の描画処理
def draw_board(screen, board, shape, offset, color, score, ren_count, next_shape, next_color):
    screen.fill((0,0,0))
    # 盤面
    for y in range(ROWS):
        for x in range(COLS):
            if board[y][x]:
                pygame.draw.rect(screen, COLORS[board[y][x]-1], (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))
    # テトリミノ
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell and y+off_y >= 0:
                pygame.draw.rect(screen, color, ((x+off_x)*CELL_SIZE, (y+off_y)*CELL_SIZE, CELL_SIZE, CELL_SIZE))
    # --- Next表示 ---
    font = pygame.font.SysFont(None, 30)
    next_label = font.render("Next:", True, (255, 255, 255))
    screen.blit(next_label, (WIDTH - 90, 10))

    for y, row in enumerate(next_shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, next_color,
                    (WIDTH - 90 + x * CELL_SIZE // 2, 80 + y * CELL_SIZE // 2, CELL_SIZE // 2, CELL_SIZE // 2))

     # スコア表示
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    # REN表示（1以上のときのみ）
    if ren_count >= 0:
        ren_text = font.render(f"REN: {ren_count}", True, (255, 200, 0))
        screen.blit(ren_text, (10, 40))

    pygame.display.flip()

def game_over_screen(screen):
    """ゲームオーバー画面を表示し、再挑戦または終了を選択させる"""
    font = pygame.font.SysFont(None, 60)
    small_font = pygame.font.SysFont(None, 40)

    game_over_text = font.render("Game Over", True, (255, 0, 0))
    retry_text = small_font.render("Retry", True, (255, 255, 255))
    quit_text = small_font.render("Quit", True, (255, 255, 255))

    # ボタンの位置とサイズ
    retry_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2, 200, 50)
    quit_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 70, 200, 50)

    while True:
        screen.fill((0, 0, 0))
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 100))

        pygame.draw.rect(screen, (0, 128, 0), retry_rect)
        pygame.draw.rect(screen, (128, 0, 0), quit_rect)

        screen.blit(retry_text, (retry_rect.centerx - retry_text.get_width()//2,
                                 retry_rect.centery - retry_text.get_height()//2))
        screen.blit(quit_text, (quit_rect.centerx - quit_text.get_width()//2,
                                quit_rect.centery - quit_text.get_height()//2))

        pygame.display.flip()

        # ユーザー入力処理
        mouse_pos = pygame.mouse.get_pos() #カーソル変更関数の定義
         # ボタンの上にカーソルがあるかでカーソル変更
        if retry_rect.collidepoint(mouse_pos) or quit_rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if retry_rect.collidepoint(event.pos):
                    return True  # 再挑戦
                elif quit_rect.collidepoint(event.pos):
                    pygame.quit()
                    return False  # 終了

def process_line_clear(board, score, ren_count, level):
    """
    ライン消去に伴うスコア加算とREN更新処理
    戻り値: board, score, ren_count, lines_cleared
    """
    board, lines = remove_row(board)

    if lines > 0:
        ren_count += 1

        # スコア加算（公式に近い）
        if lines == 1:
            score += 100 * level
        elif lines == 2:
            score += 300 * level
        elif lines == 3:
            score += 500 * level
        elif lines == 4:
            score += 800 * level

        # RENボーナス（段階加算）
        if ren_count <= 2:
            score += 50 * ren_count
        elif ren_count <= 5:
            score += 100 * ren_count
        else:
            score += 150 * ren_count
    else:
        ren_count = -1  # RENリセット

    return board, score, ren_count, lines


def main():
    pygame.init() # pygameの初期化
    screen = pygame.display.set_mode((WIDTH, HEIGHT)) # ウィンドウ生成
    pygame.display.set_caption("Tetris") # ウィンドウのタイトル
    clock = pygame.time.Clock()  # フレームレート制御用タイマー
    # ゲームボード（空の状態）
    board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    # 現在のテトリミノ生成
    current = random.randint(0, len(SHAPES)-1)
    shape = SHAPES[current]
    color = COLORS[current]
    offset = [COLS//2 - len(shape[0])//2, -2]# 初期位置（画面外から登場）
    # 次のテトリミノ
    next_index = random.randint(0, len(SHAPES) - 1)
    next_shape = SHAPES[next_index]
    next_color = COLORS[next_index]

    pygame.key.set_repeat(500, 50) #長押し対応

    fall_time = 0 # テトリミノの落下時間カウント
    game_over = False
    score = 0        # スコア初期化
    ren_count = -1   # REN初期化（-1は未発生状態）
    level = 1        # レベル（今は固定。上昇ロジックは後で追加可）

    while not game_over:
        clock.tick(FPS) # 毎フレーム一定間隔で処理
        fall_time += 1
         # イベント処理（キーボード、ウィンドウの×ボタンなど）
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return # ゲーム終了
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    new_offset = [offset[0]-1, offset[1]]
                    if not check_collision(board, shape, new_offset):
                        offset = new_offset
                elif event.key == pygame.K_RIGHT:
                    new_offset = [offset[0]+1, offset[1]]
                    if not check_collision(board, shape, new_offset):
                        offset = new_offset
                elif event.key == pygame.K_DOWN:
                    new_offset = [offset[0], offset[1]+1]
                    if not check_collision(board, shape, new_offset):
                        offset = new_offset
                elif event.key == pygame.K_UP:
                    new_shape = rotate(shape)
                    if not check_collision(board, new_shape, offset):
                        shape = new_shape
                elif event.key == pygame.K_SPACE:
                    # テトリミノを最下部まで移動
                    while not check_collision(board, shape, [offset[0], offset[1]+1]):
                        offset[1] += 1
                    # ハードドロップ後に固定
                    for y, row in enumerate(shape):
                        for x, cell in enumerate(row):
                            if cell:
                                global_y = y + offset[1]
                                if global_y < 0:
                                   game_over = True
                                else:
                                    board[global_y][x + offset[0]] = COLORS.index(color) + 1

                    # ライン消去・スコア・RENの統一処理
                    board, score, ren_count, lines = process_line_clear(board, score, ren_count, level)

                    # 新しいテトリミノを生成
                    shape = next_shape
                    color = next_color
                    offset = [COLS//2 - len(shape[0])//2, -2]
                    next_index = random.randint(0, len(SHAPES)-1)
                    next_shape = SHAPES[next_index]
                    next_color = COLORS[next_index]

        # 一定時間ごとにテトリミノを1マス落とす（自然落下処理）
        if fall_time >= FPS//2:
            fall_time = 0
            new_offset = [offset[0], offset[1]+1]
            if not check_collision(board, shape, new_offset):
                offset = new_offset
            else:
                # テトリミノを盤面に固定
                # game_over = False   一旦 false にしておく
                for y, row in enumerate(shape):
                    for x, cell in enumerate(row):
                        if cell:
                            global_y = y + offset[1]
                            if global_y < 0:
                                game_over = True  # 画面外にブロックが残る → ゲームオーバー
                            else:
                                board[global_y][x + offset[0]] = COLORS.index(color) + 1
                #スコアやRENの処理
                board, score, ren_count, lines = process_line_clear(board, score, ren_count, level)

                # 新しいテトリミノ
                shape = next_shape
                color = next_color
                offset = [COLS//2 - len(shape[0])//2, -2]
                next_index = random.randint(0, len(SHAPES)-1)
                next_shape = SHAPES[next_index]
                next_color = COLORS[next_index]

        draw_board(screen, board, shape, offset, color, score, ren_count, next_shape, next_color) # 毎フレーム画面を更新
    
    # ゲームオーバー時の画面と選択処理
    retry = game_over_screen(screen)
    if retry:
        main()  # 再帰的にゲーム再スタート
    else:
        pygame.quit() # pygameを終了

if __name__ == "__main__":
    main()