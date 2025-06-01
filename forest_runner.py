import pygame
import random
import sys
import os
import audio_manager  # Import our custom audio manager

# Initialize pygame
pygame.init()
pygame.font.init()

# Initialize audio manager
audio = audio_manager.initialize()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 300
GROUND_HEIGHT = 250
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
LIGHT_BLUE = (173, 216, 230)
FPS = 60

# Set all text to use white color
TEXT_COLOR = WHITE
TEXT_SHADOW_COLOR = DARK_GRAY

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Forest Runner")
clock = pygame.time.Clock()

# Load sounds
jump_sound = None

# Load fonts
try:
    title_font = pygame.font.Font(None, 60)  # Larger font for titles
    main_font = pygame.font.Font(None, 36)   # Main font for most text
    score_font = pygame.font.Font(None, 26)  # Smaller font for scores (reduced from 32)
except:
    # Fallback to system font if custom font loading fails
    title_font = pygame.font.SysFont('Arial', 60)
    main_font = pygame.font.SysFont('Arial', 36)
    score_font = pygame.font.SysFont('Arial', 26)  # Smaller font for scores (reduced from 32)

# Function to render text with border
def render_text_with_border(font, text, text_color, border_color):
    # Render the text in the main color
    text_surface = font.render(text, True, text_color)
    
    # Create a slightly larger surface for the border
    w, h = text_surface.get_size()
    border_surface = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
    
    # Render the border by drawing the text in border color at offset positions
    for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
        border_text = font.render(text, True, border_color)
        border_surface.blit(border_text, (1 + dx, 1 + dy))
    
    # Draw the main text on top
    border_surface.blit(text_surface, (1, 1))
    
    return border_surface

# Load background images with meaningful names
background_layers = {
    'sky': {'speed': 0.1, 'image': None},
    'cloud': {'speed': 0.3, 'image': None},
    'hills': {'speed': 0.5, 'image': None},
    'tree2': {'speed': 0.7, 'image': None},
    'tree1': {'speed': 0.9, 'image': None},
    'bush': {'speed': 1.1, 'image': None},
    'support': {'speed': 1.3, 'image': None},
    'ground': {'speed': 1.5, 'image': None}
}

# Load each background image
for layer_name in background_layers:
    try:
        img_path = os.path.join('backgrounds', f'{layer_name}.png')
        if os.path.exists(img_path):
            img = pygame.image.load(img_path).convert_alpha()
            # Scale the image to fit the screen height while maintaining aspect ratio
            aspect_ratio = img.get_width() / img.get_height()
            new_height = SCREEN_HEIGHT
            new_width = int(new_height * aspect_ratio)
            img = pygame.transform.scale(img, (new_width, new_height))
            background_layers[layer_name]['image'] = img
            print(f"Loaded {layer_name} background")
    except pygame.error as e:
        print(f"Could not load background image {layer_name}.png: {e}")

# Background class for parallax scrolling
class Background:
    def __init__(self, image, speed):
        self.image = image
        self.speed = speed
        self.width = image.get_width()
        # Start with three copies to ensure full coverage
        self.positions = [0, self.width, self.width * 2]
    
    def update(self):
        # Move all copies of the background
        for i in range(len(self.positions)):
            self.positions[i] -= self.speed
            
            # If an image is completely off screen to the left, move it to the right
            if self.positions[i] + self.width < 0:
                # Find the rightmost position
                rightmost = max(self.positions)
                # Place this image to the right of the rightmost one
                self.positions[i] = rightmost + self.width
    
    def draw(self, surface):
        # Draw all copies of the background
        for pos in self.positions:
            surface.blit(self.image, (pos, 0))
        
        # Draw an extra copy if needed to fill any gaps at the right edge
        rightmost = max(self.positions)
        if rightmost < SCREEN_WIDTH:
            surface.blit(self.image, (rightmost + self.width, 0))

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        # Load idle animation frames
        self.idle_frames = []
        for i in range(1, 11):  # Idle frames 1-10
            try:
                img_path = os.path.join('hero', f'Idle ({i}).png')
                if os.path.exists(img_path):
                    img = pygame.image.load(img_path).convert_alpha()
                    # Scale the image to a reasonable size
                    img = pygame.transform.scale(img, (75, 80))
                    self.idle_frames.append(img)
            except pygame.error as e:
                print(f"Could not load idle frame {i}: {e}")
        
        # Load run animation frames
        self.run_frames = []
        for i in range(1, 9):  # Run frames 1-8
            try:
                img_path = os.path.join('hero', f'Run ({i}).png')
                if os.path.exists(img_path):
                    img = pygame.image.load(img_path).convert_alpha()
                    # Scale the image with better proportions (increased width)
                    img = pygame.transform.scale(img, (75, 80))
                    self.run_frames.append(img)
            except pygame.error as e:
                print(f"Could not load run frame {i}: {e}")
        
        # Load jump animation frames
        self.jump_frames = []
        for i in range(1, 13):  # Jump frames 1-12
            try:
                img_path = os.path.join('hero', f'Jump ({i}).png')
                if os.path.exists(img_path):
                    img = pygame.image.load(img_path).convert_alpha()
                    # Scale the image with better proportions (increased width)
                    img = pygame.transform.scale(img, (75, 80))
                    self.jump_frames.append(img)
            except pygame.error as e:
                print(f"Could not load jump frame {i}: {e}")
        
        # Set initial image
        if self.idle_frames:
            self.image = self.idle_frames[0]
        elif self.run_frames:
            self.image = self.run_frames[0]
        else:
            # Fallback to rectangle if images couldn't be loaded
            self.image = pygame.Surface((40, 60))
            self.image.fill(BLACK)
        
        self.rect = self.image.get_rect()
        self.rect.bottom = GROUND_HEIGHT
        self.rect.left = 50
        
        # Animation variables
        self.current_frame = 0
        self.animation_speed = 0.15
        self.animation_timer = 0
        
        # Jump mechanics
        self.velocity = 0
        self.jump_power = -15
        self.gravity = 0.8
        self.is_jumping = False
    
    def update(self):
        # Apply gravity
        if self.is_jumping:
            self.velocity += self.gravity
            self.rect.y += self.velocity
            
            # Use jump animation
            self.animate_jump()
            
            # Check if landed
            if self.rect.bottom >= GROUND_HEIGHT:
                self.rect.bottom = GROUND_HEIGHT
                self.is_jumping = False
                self.velocity = 0
                self.current_frame = 0  # Reset animation frame
        else:
            # Use run animation when not jumping
            self.animate_run()
    
    def update_start_screen(self):
        # Use idle animation for the start screen
        self.animate_idle()
    
    def animate_idle(self):
        if not self.idle_frames:
            return
            
        # Update animation frame
        self.animation_timer += 1
        if self.animation_timer >= FPS * self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.idle_frames)
            
            # Store the old rect position
            old_bottom = self.rect.bottom
            old_left = self.rect.left
            
            # Update image
            self.image = self.idle_frames[self.current_frame]
            
            # Reset the rect with the new image and restore position
            self.rect = self.image.get_rect()
            self.rect.bottom = old_bottom
            self.rect.left = old_left
    
    def animate_run(self):
        if not self.run_frames:
            return
            
        # Update animation frame
        self.animation_timer += 1
        if self.animation_timer >= FPS * self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.run_frames)
            
            # Store the old rect position
            old_bottom = self.rect.bottom
            old_left = self.rect.left
            
            # Update image
            self.image = self.run_frames[self.current_frame]
            
            # Reset the rect with the new image and restore position
            self.rect = self.image.get_rect()
            self.rect.bottom = old_bottom
            self.rect.left = old_left
    
    def animate_jump(self):
        if not self.jump_frames:
            return
            
        # Calculate which jump frame to use based on vertical position/velocity
        # This makes the jump animation match the jump arc
        if self.velocity < 0:  # Going up
            # Map the upward part of the jump to the first half of frames
            progress = min(1.0, abs(self.velocity) / abs(self.jump_power))
            frame_index = int(progress * (len(self.jump_frames) // 2))
        else:  # Going down or at peak
            # Map the downward part to the second half of frames
            progress = min(1.0, self.velocity / (abs(self.jump_power) * 0.8))
            frame_index = (len(self.jump_frames) // 2) + int(progress * (len(self.jump_frames) // 2))
        
        # Ensure frame index is within bounds
        frame_index = max(0, min(frame_index, len(self.jump_frames) - 1))
        
        # Store the old rect position
        old_bottom = self.rect.bottom
        old_left = self.rect.left
        
        # Update image
        self.image = self.jump_frames[frame_index]
        
        # Reset the rect with the new image and restore position
        self.rect = self.image.get_rect()
        self.rect.bottom = old_bottom
        self.rect.left = old_left
    
    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.velocity = self.jump_power
            # Play jump sound using audio manager
            audio.play_sound('jump')

# Obstacle class (rocks)
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        # Choose a random rock image from the available options
        rock_options = ['Rock1.png', 'Rock2.png', 'Rock3.png', 'Rock4.png']
        chosen_rock = random.choice(rock_options)
        
        # Try to load the obstacle image
        try:
            self.image = pygame.image.load(f'obstacles/{chosen_rock}').convert_alpha()
            
            # Scale the image to an appropriate size based on which rock it is
            if chosen_rock == 'Rock1.png':
                self.image = pygame.transform.scale(self.image, (80, 70))
            elif chosen_rock == 'Rock2.png':
                self.image = pygame.transform.scale(self.image, (75, 65))
            elif chosen_rock == 'Rock3.png':
                self.image = pygame.transform.scale(self.image, (70, 60))
            else:  # Rock4.png
                self.image = pygame.transform.scale(self.image, (85, 75))
                
        except pygame.error:
            # Fallback to a rectangle if image loading fails
            print(f"Could not load obstacle image {chosen_rock}. Using fallback.")
            self.image = pygame.Surface((40, 60))
            self.image.fill(BLACK)
        
        self.rect = self.image.get_rect()
        self.rect.bottom = GROUND_HEIGHT
        self.rect.left = SCREEN_WIDTH
        self.speed = speed
        
        # Store which rock type this is for collision detection
        self.rock_type = chosen_rock
    
    def update(self):
        self.rect.x -= self.speed
        # Remove if off screen
        if self.rect.right < 0:
            self.kill()

# Game class
class Game:
    def __init__(self):
        self.player = Player()
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        
        self.speed = 5
        self.score = 0
        self.high_score = self.load_high_score()  # Load high score from previous sessions
        self.player_name = ""  # Player name will be entered at start
        self.high_score_name = self.load_high_score_name()  # Load name of high score holder
        self.game_over = False
        self.spawn_timer = 0
        self.game_started = False  # Flag to track if the game has started
        self.change_name = False   # Flag to indicate if player wants to change name
        self.input_active = True   # Flag for name input activity
        self.change_name = False   # Flag to indicate if player wants to change name
        
        # Create parallax backgrounds with different speeds
        self.backgrounds = []
        
        # Create backgrounds in the correct order (from back to front)
        layer_order = ['sky', 'cloud', 'hills', 'tree2', 'tree1', 'bush', 'support', 'ground']
        for layer_name in layer_order:
            if background_layers[layer_name]['image'] is not None:
                self.backgrounds.append(
                    Background(
                        background_layers[layer_name]['image'], 
                        background_layers[layer_name]['speed']
                    )
                )
    
    def name_change_screen(self):
        """Show screen for changing player name"""
        # This method is no longer used - we go directly to start screen instead
        pass
            
    def show_start_screen(self):
        # Start screen loop
        waiting = True
        name_entered = False
        input_box = pygame.Rect(SCREEN_WIDTH // 2 - 100, 150, 200, 40)
        color_inactive = pygame.Color('lightskyblue3')
        color_active = pygame.Color('dodgerblue2')
        color = color_inactive
        
        # Start playing background music
        audio.play_music()
        
        while waiting:
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if not name_entered:
                    # Handle name input events
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        # Toggle input_active if the user clicked on the input box
                        self.input_active = input_box.collidepoint(event.pos)
                        color = color_active if self.input_active else color_inactive
                    
                    if event.type == pygame.KEYDOWN:
                        if self.input_active:
                            if event.key == pygame.K_RETURN and self.player_name.strip():
                                # Confirm name when Enter is pressed and name is not empty
                                name_entered = True
                            elif event.key == pygame.K_BACKSPACE:
                                # Remove last character on backspace
                                self.player_name = self.player_name[:-1]
                            elif len(self.player_name) < 15:  # Limit name length
                                # Add character to name
                                if event.unicode.isalnum() or event.unicode.isspace():
                                    self.player_name += event.unicode
                else:
                    # After name is entered, wait for space to start game
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        waiting = False
                        self.game_started = True
            
            # Update the character's idle animation
            self.player.update_start_screen()
            
            # Draw the start screen
            screen.fill((50, 50, 80))  # Dark blue-gray background for better contrast with white text
            
            # Draw static backgrounds
            for bg in self.backgrounds:
                bg.draw(screen)
            
            # Draw ground line (only if ground image is not loaded)
            if background_layers['ground']['image'] is None:
                pygame.draw.line(screen, BLACK, (0, GROUND_HEIGHT), 
                                (SCREEN_WIDTH, GROUND_HEIGHT), 2)
            
            # Draw the character
            screen.blit(self.player.image, self.player.rect)
            
            # Draw welcome text with shadow effect and border
            welcome_text = render_text_with_border(title_font, "Welcome to Forest Runner!", TEXT_COLOR, BLACK)
            screen.blit(welcome_text, (SCREEN_WIDTH // 2 - welcome_text.get_width() // 2, 50))
            
            if not name_entered:
                # Draw name input prompt with border
                name_prompt = render_text_with_border(main_font, "Enter your name:", TEXT_COLOR, BLACK)
                screen.blit(name_prompt, (SCREEN_WIDTH // 2 - name_prompt.get_width() // 2, 120))
                
                # Draw input box
                pygame.draw.rect(screen, color, input_box, 2)
                
                # Render the current text with border
                txt_surface = render_text_with_border(main_font, self.player_name, TEXT_COLOR, BLACK)
                # Blit the text
                screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
                
                # Draw blinking cursor if input is active
                if self.input_active and pygame.time.get_ticks() % 1000 < 500:
                    cursor_x = input_box.x + 5 + txt_surface.get_width() - 2  # Adjust for border
                    pygame.draw.line(screen, TEXT_COLOR, 
                                    (cursor_x, input_box.y + 5),
                                    (cursor_x, input_box.y + 35), 2)
            else:
                # Draw instructions after name is entered with border
                instruction_text = render_text_with_border(main_font, f"Hello, {self.player_name}! Press SPACE to start", TEXT_COLOR, BLACK)
                screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, 150))
            
            # Draw high score on start screen with border
            if self.high_score is not None and self.high_score > 0:
                high_score = self.high_score // 10
                formatted_high_score = f"{high_score:04d}"
                high_score_text = render_text_with_border(score_font, f"High Score: {formatted_high_score} by {self.high_score_name}", TEXT_COLOR, BLACK)
                screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, 200))
            
            # Update display
            pygame.display.flip()
            clock.tick(FPS)
    
    def load_high_score(self):
        """Load high score from file if it exists"""
        try:
            with open('high_score.txt', 'r') as f:
                content = f.read().strip().split('|')
                if len(content) >= 1:
                    return int(content[0])
                else:
                    return 0
        except (FileNotFoundError, ValueError):
            return 0
    
    def save_high_score(self):
        """Save high score and player name to a single file"""
        # Only save if this is a new high score
        if self.high_score is None or self.score >= self.high_score:
            with open('high_score.txt', 'w') as f:
                f.write(f"{self.score}|{self.player_name}")
            # Update the high score name in memory
            self.high_score_name = self.player_name
    
    def load_high_score_name(self):
        """Load name of high score holder if it exists"""
        try:
            with open('high_score.txt', 'r') as f:
                content = f.read().strip().split('|')
                if len(content) >= 2:
                    return content[1]
                else:
                    return "Unknown"
        except FileNotFoundError:
            return "Unknown"
    
    def reset_game(self):
        """Reset the game state without changing player name"""
        # Keep the player name and high score
        player_name = self.player_name
        high_score = self.high_score
        high_score_name = self.high_score_name
        
        # Reset game objects
        self.player = Player()
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        
        # Reset game state
        self.speed = 5
        self.score = 0
        self.game_over = False
        self.spawn_timer = 0
        self.change_name = False
        
        # Restore player name and high score
        self.player_name = player_name
        self.high_score = high_score
        self.high_score_name = high_score_name
        
        # Create backgrounds in the correct order (from back to front)
        self.backgrounds = []
        layer_order = ['sky', 'cloud', 'hills', 'tree2', 'tree1', 'bush', 'support', 'ground']
        for layer_name in layer_order:
            if background_layers[layer_name]['image'] is not None:
                self.backgrounds.append(
                    Background(
                        background_layers[layer_name]['image'], 
                        background_layers[layer_name]['speed']
                    )
                )
        
        # Resume music
        audio.unpause_music()
    
    def run(self):
        # Show start screen first
        self.show_start_screen()
        
        # Main game loop
        running = True
        while running:
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.game_over:
                        self.player.jump()
                    if event.key == pygame.K_r and self.game_over:
                        # Reset game without going to start screen
                        self.reset_game()
                    if event.key == pygame.K_n and self.game_over:
                        # Return to start screen to change player name
                        self.__init__()  # Reset everything
                        self.show_start_screen()  # Show start screen for name input
                    # Audio controls
                    if event.key == pygame.K_m:
                        # Toggle music
                        audio.toggle_music()
                    if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        # Increase music volume
                        audio.set_music_volume(audio.music_volume + 0.1)
                    if event.key == pygame.K_MINUS:
                        # Decrease music volume
                        audio.set_music_volume(audio.music_volume - 0.1)
            
            if not self.game_over:
                # Update backgrounds
                for bg in self.backgrounds:
                    bg.update()
                
                # Update sprites
                self.all_sprites.update()
                
                # Spawn obstacles with randomized timing and spacing
                self.spawn_timer += 1
                spawn_interval = random.randint(80, 200)  # Wider range for more variability
                
                if self.spawn_timer > spawn_interval:
                    # Check if there's enough distance from the last obstacle
                    can_spawn = True
                    min_distance = 300 + (self.speed - 5) * 20  # Base minimum distance
                    
                    # Check all existing obstacles to ensure proper spacing
                    for obs in self.obstacles:
                        # Don't spawn if any obstacle is too close to the right edge
                        if obs.rect.x > SCREEN_WIDTH - min_distance:
                            can_spawn = False
                            break
                    
                    # Only spawn if there's enough space
                    if can_spawn:
                        self.spawn_obstacle()
                        self.spawn_timer = random.randint(0, 40)  # Randomize timer reset
                
                # Check collisions
                # Create a smaller hitbox for the player for more accurate collisions
                player_hitbox = pygame.Rect(
                    self.player.rect.x + self.player.rect.width * 0.3,  # Moved right edge in more
                    self.player.rect.y + self.player.rect.height * 0.2,
                    self.player.rect.width * 0.4,  # Made hitbox narrower (was 0.5)
                    self.player.rect.height * 0.7
                )
                
                # For debugging - uncomment to see hitboxes
                # pygame.draw.rect(screen, (255, 0, 0), player_hitbox, 2)
                
                for obstacle in self.obstacles:
                    # Create a custom hitbox for each obstacle type
                    if hasattr(obstacle, 'rock_type'):
                        if obstacle.rock_type == 'Rock1.png':
                            # Taller, narrower hitbox for Rock1 - adjusted to match visual shape
                            obstacle_hitbox = pygame.Rect(
                                obstacle.rect.x + obstacle.rect.width * 0.35,
                                obstacle.rect.y + obstacle.rect.height * 0.2,
                                obstacle.rect.width * 0.3,  # Narrower hitbox
                                obstacle.rect.height * 0.7
                            )
                        elif obstacle.rock_type == 'Rock2.png':
                            # Medium hitbox for Rock2 - adjusted to match visual shape
                            obstacle_hitbox = pygame.Rect(
                                obstacle.rect.x + obstacle.rect.width * 0.3,
                                obstacle.rect.y + obstacle.rect.height * 0.25,
                                obstacle.rect.width * 0.4,
                                obstacle.rect.height * 0.6
                            )
                        elif obstacle.rock_type == 'Rock3.png':
                            # Wider hitbox for Rock3 - adjusted to match visual shape
                            obstacle_hitbox = pygame.Rect(
                                obstacle.rect.x + obstacle.rect.width * 0.25,
                                obstacle.rect.y + obstacle.rect.height * 0.3,
                                obstacle.rect.width * 0.5,
                                obstacle.rect.height * 0.5
                            )
                        else:  # Rock4.png
                            # Largest hitbox for Rock4 - adjusted to match visual shape
                            obstacle_hitbox = pygame.Rect(
                                obstacle.rect.x + obstacle.rect.width * 0.2,
                                obstacle.rect.y + obstacle.rect.height * 0.25,
                                obstacle.rect.width * 0.6,
                                obstacle.rect.height * 0.6
                            )
                    else:
                        # Default hitbox if rock_type is not available
                        obstacle_hitbox = pygame.Rect(
                            obstacle.rect.x + obstacle.rect.width * 0.25,
                            obstacle.rect.y + obstacle.rect.height * 0.25,
                            obstacle.rect.width * 0.5,
                            obstacle.rect.height * 0.5
                        )
                    
                    # For debugging - uncomment to see hitboxes
                    # pygame.draw.rect(screen, (0, 255, 0), obstacle_hitbox, 2)
                    
                    # Use a more precise collision detection
                    if player_hitbox.colliderect(obstacle_hitbox):
                        # Calculate the actual overlap area
                        overlap_width = min(player_hitbox.right, obstacle_hitbox.right) - max(player_hitbox.left, obstacle_hitbox.left)
                        overlap_height = min(player_hitbox.bottom, obstacle_hitbox.bottom) - max(player_hitbox.top, obstacle_hitbox.top)
                        overlap_area = overlap_width * overlap_height
                        
                        # Only count as collision if overlap area is significant
                        if overlap_area > 50:  # Minimum overlap threshold
                            self.game_over = True
                            audio.pause_music()  # Pause background music
                            audio.play_sound('game_over')  # Play game over sound
                            break
                
                # Update score
                self.score += 1
                
                # Update high score if needed
                if self.high_score is None or self.score > self.high_score:
                    self.high_score = self.score
                    self.high_score_name = self.player_name  # Update high score holder name
                
                # Increase difficulty over time
                if self.score % 500 == 0:
                    self.speed += 0.5
            
            # Draw
            screen.fill((50, 50, 80))  # Dark blue-gray background for better contrast with white text
            
            # Draw backgrounds
            for bg in self.backgrounds:
                bg.draw(screen)
            
            # Draw ground line (only if ground image is not loaded)
            if background_layers['ground']['image'] is None:
                pygame.draw.line(screen, BLACK, (0, GROUND_HEIGHT), 
                                (SCREEN_WIDTH, GROUND_HEIGHT), 2)
            
            # Draw sprites
            self.all_sprites.draw(screen)
            
            # Draw score (divided by 10 to slow it down) with smaller font and border
            visible_score = self.score // 10
            
            # Format score as 4 digits (0000)
            formatted_score = f"{visible_score:04d}"
            
            # Create a score display with border
            score_text = render_text_with_border(score_font, f"Score: {formatted_score}", TEXT_COLOR, BLACK)
            screen.blit(score_text, (10, 10))
            
            # Draw high score with border (without player name during gameplay)
            high_score = self.high_score // 10
            formatted_high_score = f"{high_score:04d}"
            high_score_text = render_text_with_border(score_font, f"High Score: {formatted_high_score}", TEXT_COLOR, BLACK)
            screen.blit(high_score_text, (10, 40))  # Adjusted position due to smaller font
            
            # Draw player name with border
            name_text = render_text_with_border(score_font, f"Player: {self.player_name}", TEXT_COLOR, BLACK)
            screen.blit(name_text, (SCREEN_WIDTH - name_text.get_width() - 10, 10))
            
            # Check if death animation is complete
            
                
            
            # Show game over screen if needed
            if self.game_over:
                # Create a semi-transparent overlay
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))  # Black with 50% transparency
                screen.blit(overlay, (0, 0))
                
                # Game over text with border
                game_over_text = render_text_with_border(title_font, "Game Over!", TEXT_COLOR, BLACK)
                screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
                
                # Restart instruction with border
                restart_text = render_text_with_border(main_font, "Press R to restart", TEXT_COLOR, BLACK)
                screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
                
                # Change name instruction with border
                name_change_text = render_text_with_border(main_font, "Press N to change player", TEXT_COLOR, BLACK)
                screen.blit(name_change_text, (SCREEN_WIDTH // 2 - name_change_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
                
                # New high score notification with border
                if self.score == self.high_score and self.score > 0:
                    high_score_text = render_text_with_border(main_font, "NEW HIGH SCORE!", (255, 255, 0), BLACK)  # Yellow text with black border
                    screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 90))
                
                # Save high score when game is over
                self.save_high_score()
                
            # Check if death animation is complete
            
                
            
            # Update display
            pygame.display.flip()
            clock.tick(FPS)
    
    def spawn_obstacle(self):
        # Create a new obstacle
        obstacle = Obstacle(self.speed)
        self.obstacles.add(obstacle)
        self.all_sprites.add(obstacle)

# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()
