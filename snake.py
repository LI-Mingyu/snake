import pygame
import random
import time

# 初始化 Pygame
pygame.init()

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# 游戏窗口设置
WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("贪吃蛇")

# 游戏时钟
clock = pygame.time.Clock()

# 方向控制
class Direction:
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

# 贪吃蛇类
class Snake:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.body = [(WIDTH//2, HEIGHT//2)]
        self.direction = random.choice([Direction.RIGHT, Direction.LEFT, Direction.UP, Direction.DOWN])
        self.grow = False
    
    def move(self):
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = ((head_x + dx*CELL_SIZE) % WIDTH, (head_y + dy*CELL_SIZE) % HEIGHT)
        
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False
    
    def check_collision(self):
        return len(self.body) != len(set(self.body))
    
    def draw(self):
        for idx, (x, y) in enumerate(self.body):
            color = GREEN if idx == 0 else BLUE
            pygame.draw.rect(screen, color, (x, y, CELL_SIZE-1, CELL_SIZE-1))

# 食物类
class Food:
    def __init__(self):
        self.spawn()
    
    def spawn(self):
        while True:
            self.position = (random.randrange(0, WIDTH, CELL_SIZE), 
                            random.randrange(0, HEIGHT, CELL_SIZE))
            # 确保食物不会生成在蛇身上
            if self.position not in snake.body:
                break
    
    def draw(self):
        pygame.draw.rect(screen, RED, (self.position[0], self.position[1], CELL_SIZE-1, CELL_SIZE-1))

# 游戏主函数
def game_loop():
    global snake, food
    snake = Snake()
    food = Food()
    score = 0
    game_over = False

    while True:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_SPACE:
                        game_loop()
                        return
                else:
                    if event.key == pygame.K_UP and snake.direction != Direction.DOWN:
                        snake.direction = Direction.UP
                    elif event.key == pygame.K_DOWN and snake.direction != Direction.UP:
                        snake.direction = Direction.DOWN
                    elif event.key == pygame.K_LEFT and snake.direction != Direction.RIGHT:
                        snake.direction = Direction.LEFT
                    elif event.key == pygame.K_RIGHT and snake.direction != Direction.LEFT:
                        snake.direction = Direction.RIGHT

        if not game_over:
            snake.move()
            
            # 检查是否吃到食物
            if snake.body[0] == food.position:
                snake.grow = True
                score += 1
                food.spawn()
            
            # 碰撞检测
            if snake.check_collision():
                game_over = True

        # 绘制界面
        screen.fill(BLACK)
        snake.draw()
        food.draw()
        
        # 显示分数
        font = pygame.font.SysFont(None, 30)
        text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(text, (10, 10))
        
        # 游戏结束显示
        if game_over:
            font = pygame.font.SysFont(None, 50)
            text = font.render("Game Over! Press SPACE to restart", True, RED)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
        
        pygame.display.flip()
        clock.tick(10)

if __name__ == "__main__":
    game_loop()