import pygame
import random
import math
import time
from pygame.locals import *

# 初始化 Pygame
pygame.init()

# 春节主题配置
SPRING_FESTIVAL = {
    "colors": {
        "bg": (200, 8, 20),        # 中国红背景
        "snake_head": (255, 215, 0), # 金色蛇头
        "snake_body": (255, 165, 0), # 橙色蛇身
        "food": (255, 255, 102),     # 元宝黄
        "special_food": (220, 20, 60) # 鞭炮红
    },
    "special_food_duration": 15,   # 特殊食物持续时间(秒)
    "firework_particles": 50       # 烟花粒子数
}

# 游戏窗口设置
WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("新春贪吃蛇")

# 游戏时钟
clock = pygame.time.Clock()

# 解决中文乱码问题（macOS适配）
try:
    font = pygame.font.Font("/System/Library/Fonts/STHeiti Medium.ttc", 30)
except:
    try:
        font = pygame.font.SysFont("simhei", 30)
    except:
        font = pygame.font.Font(None, 30)

# 生成音效
def generate_beep_sound(freq=440, duration=0.1):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = pygame.sndarray.make_sound(
        pygame.sndarray.array(
            pygame.mixer.Sound(
                buffer=bytes([int(127 * math.sin(2 * math.pi * freq * t / sample_rate) + 127)
                for t in range(n_samples)])
            )
        )
    )
    return buf

# 初始化音效
try:
    firework_sound = pygame.mixer.Sound("firework.wav")
    drum_sound = pygame.mixer.Sound("drum.wav")
except:
    firework_sound = generate_beep_sound(880, 0.3)  # 高频爆竹声
    drum_sound = generate_beep_sound(220, 0.2)      # 低频鼓声

# 方向控制
class Direction:
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

# 春节特效类
class SpringEffects:
    @staticmethod
    def create_firework(pos):
        particles = []
        for _ in range(SPRING_FESTIVAL["firework_particles"]):
            angle = random.uniform(0, 2*math.pi)
            speed = random.uniform(1, 5)
            lifetime = random.randint(20, 40)
            particles.append({
                "pos": list(pos),
                "velocity": [speed*math.cos(angle), speed*math.sin(angle)],
                "lifetime": lifetime
            })
        return particles

# 贪吃蛇类（修复问题1：普通食物触发粒子特效）
class Snake:
    def __init__(self):
        self.reset()
        self.fireworks = []
    
    def reset(self):
        self.body = [(WIDTH//2, HEIGHT//2)]
        self.direction = random.choice([Direction.RIGHT, Direction.LEFT, Direction.UP, Direction.DOWN])
        self.grow = False
    
    def move(self):
        # 移除此处可能触发粒子特效的代码
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
        # 绘制烟花
        for firework in self.fireworks[:]:
            alpha = min(255, firework["lifetime"]*12)
            color = (random.randint(200,255), random.randint(100,200), 0)
            pygame.draw.circle(screen, color, 
                             (int(firework["pos"][0]), int(firework["pos"][1])), 3)
            firework["pos"][0] += firework["velocity"][0]
            firework["pos"][1] += firework["velocity"][1]
            firework["lifetime"] -= 1
            if firework["lifetime"] <= 0:
                self.fireworks.remove(firework)
        
        # 绘制蛇身
        for idx, (x, y) in enumerate(self.body):
            color = SPRING_FESTIVAL["colors"]["snake_head"] if idx == 0 \
                   else SPRING_FESTIVAL["colors"]["snake_body"]
            if idx > 0:
                pygame.draw.line(screen, (255,240,0), 
                               (x+3, y+3), (x+CELL_SIZE-3, y+CELL_SIZE-3), 2)
            pygame.draw.rect(screen, color, (x, y, CELL_SIZE-1, CELL_SIZE-1))

# 食物类（修复问题2：确保音效触发）
class Food:
    def __init__(self):
        self.is_special = False
        self.special_timer = 0
        self.spawn()
    
    def spawn(self):
        self.is_special = random.random() < 0.4
        while True:
            self.position = (random.randrange(0, WIDTH, CELL_SIZE), 
                            random.randrange(0, HEIGHT, CELL_SIZE))
            if self.position not in snake.body:
                break
        self.special_timer = time.time()
    
    def draw(self):
        color = SPRING_FESTIVAL["colors"]["special_food"] if self.is_special \
               else SPRING_FESTIVAL["colors"]["food"]
        if self.is_special:
            # 绘制鞭炮
            pygame.draw.rect(screen, color, (self.position[0]+8, self.position[1], 4, 20))
            pygame.draw.circle(screen, (40,40,40), 
                             (self.position[0]+10, self.position[1]+22), 3)
        else:
            # 绘制元宝
            pygame.draw.polygon(screen, color, [
                (self.position[0]+5, self.position[1]+10),
                (self.position[0]+15, self.position[1]+10),
                (self.position[0]+18, self.position[1]+15),
                (self.position[0]+2, self.position[1]+15),
                (self.position[0]+5, self.position[1]+10)
            ])

# 游戏主函数（关键修复）
def game_loop():
    global snake, food
    snake = Snake()
    food = Food()
    score = 0
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
            if event.type == KEYDOWN:
                if game_over:
                    if event.key == K_SPACE:
                        game_loop()
                        return
                else:
                    if event.key == K_UP and snake.direction != Direction.DOWN:
                        snake.direction = Direction.UP
                    elif event.key == K_DOWN and snake.direction != Direction.UP:
                        snake.direction = Direction.DOWN
                    elif event.key == K_LEFT and snake.direction != Direction.RIGHT:
                        snake.direction = Direction.LEFT
                    elif event.key == K_RIGHT and snake.direction != Direction.LEFT:
                        snake.direction = Direction.RIGHT

        if not game_over:
            snake.move()
            
            # 食物检测（关键修改点）
            if snake.body[0] == food.position:
                snake.grow = True
                score += 5 if food.is_special else 1
                
                # 问题修复1：仅特殊食物触发粒子特效
                if food.is_special:
                    snake.fireworks.extend(SpringEffects.create_firework(food.position))
                    firework_sound.play()
                
                # 问题修复2：每次吃到食物都播放鼓声
                drum_sound.play()
                
                food.spawn()
            
            # 特殊食物超时
            if food.is_special and time.time()-food.special_timer > SPRING_FESTIVAL["special_food_duration"]:
                food.spawn()
            
            # 碰撞检测
            if snake.check_collision():
                game_over = True
                firework_sound.play()

        # 绘制界面
        screen.fill(SPRING_FESTIVAL["colors"]["bg"])
        
        # 绘制灯笼
        for x in range(50, WIDTH, 150):
            pygame.draw.circle(screen, (255,240,0), (x, 30), 15)
            pygame.draw.rect(screen, (180,0,0), (x-15, 15, 30, 20))
            pygame.draw.line(screen, (200,200,0), (x,15), (x,5), 3)
        
        snake.draw()
        food.draw()
        
        # 显示分数
        text = font.render(f"福气: {score}", True, (255,255,0))
        screen.blit(text, (10, 10))
        
        # 游戏结束显示
        if game_over:
            text1 = font.render("蛇年快乐！", True, (255,255,0))
            text2 = font.render("按空格键辞旧迎新", True, (255,255,0))
            screen.blit(text1, (WIDTH//2-80, HEIGHT//2-30))
            screen.blit(text2, (WIDTH//2-140, HEIGHT//2+10))
        
        pygame.display.flip()
        clock.tick(10)

if __name__ == "__main__":
    game_loop()