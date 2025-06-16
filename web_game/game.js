// Game constants
const CANVAS_WIDTH = 800;
const CANVAS_HEIGHT = 600;
const BASKET_WIDTH = 100;
const BASKET_HEIGHT = 50;
const OBJECT_RADIUS = 20;
const INITIAL_LIVES = 3;
let GAME_DURATION = 60; // seconds - now variable

// Game variables
let canvas, ctx;
let gameState = "menu"; // menu, playing, paused, gameOver
let score = 0;
let lives = INITIAL_LIVES;
let highScore = 0;
let gameStartTime;
let lastSpawnTime;
let fallingObjects = [];
let basketX;
let basketY;
let difficulty = "Easy";
let difficultySettings = {
    Easy: { initialSpawnRate: 1.5, initialSpeedRange: [100, 200] },
    Medium: { initialSpawnRate: 1.0, initialSpeedRange: [150, 250] },
    Hard: { initialSpawnRate: 0.7, initialSpeedRange: [200, 300] }
};
let currentSpawnRate;
let currentSpeedRange;
let difficultyIncreaseFactor = 1.0;
let applesCaught = 0;
let rocksAvoided = 0;
let selectedMusic = "music1";
let customMusicLoaded = false;

// DOM elements
let mainMenu, pauseMenu, gameOverScreen;
let highScoreDisplay, finalScoreDisplay, endHighScoreDisplay;
let applesCaughtDisplay, rocksAvoidedDisplay, difficultyLevelDisplay;

// Audio elements
let catchSound, missSound, badCatchSound, bombSound, gameOverSound;
let backgroundMusic1, backgroundMusic2, backgroundMusic3, customMusicPlayer;
let currentMusic;

// Initialize the game
window.onload = function() {
    // Get canvas and context
    canvas = document.getElementById("game-canvas");
    ctx = canvas.getContext("2d");
    
    // Get DOM elements
    mainMenu = document.getElementById("main-menu");
    pauseMenu = document.getElementById("pause-menu");
    gameOverScreen = document.getElementById("game-over");
    
    highScoreDisplay = document.getElementById("high-score-value");
    finalScoreDisplay = document.getElementById("final-score");
    endHighScoreDisplay = document.getElementById("end-high-score");
    applesCaughtDisplay = document.getElementById("apples-caught");
    rocksAvoidedDisplay = document.getElementById("rocks-avoided");
    difficultyLevelDisplay = document.getElementById("difficulty-level");
    
    // Get audio elements
    catchSound = document.getElementById("catch-sound");
    missSound = document.getElementById("miss-sound");
    badCatchSound = document.getElementById("bad-catch-sound");
    bombSound = document.getElementById("bomb-sound");
    gameOverSound = document.getElementById("game-over-sound");
    backgroundMusic1 = document.getElementById("background-music1");
    backgroundMusic2 = document.getElementById("background-music2");
    backgroundMusic3 = document.getElementById("background-music3");
    customMusicPlayer = document.getElementById("custom-music-player");
    
    // Set initial values
    basketX = CANVAS_WIDTH / 2;
    basketY = CANVAS_HEIGHT - 50;
    
    // Load high score from local storage
    loadHighScore();
    
    // Set up event listeners
    setupEventListeners();
    
    // Update duration display
    document.querySelector('.slider-value').textContent = `${GAME_DURATION} seconds`;
    
    // Start the game loop
    requestAnimationFrame(gameLoop);
};

// Load high score from local storage
function loadHighScore() {
    const savedHighScore = localStorage.getItem("catchGameHighScore");
    if (savedHighScore) {
        highScore = parseInt(savedHighScore);
    } else {
        highScore = 0;
    }
    // Always update the high score display
    highScoreDisplay.textContent = highScore;
}

// Save high score to local storage
function saveHighScore() {
    if (score > highScore) {
        highScore = score;
        localStorage.setItem("catchGameHighScore", highScore);
        // Update all high score displays
        highScoreDisplay.textContent = highScore;
        endHighScoreDisplay.textContent = highScore;
    }
}

// Set up event listeners
function setupEventListeners() {
    // Mouse movement for basket control
    canvas.addEventListener("mousemove", function(event) {
        const rect = canvas.getBoundingClientRect();
        basketX = event.clientX - rect.left;
    });
    
    // Keyboard controls
    document.addEventListener("keydown", function(event) {
        if (event.key === "p" || event.key === "P") {
            if (gameState === "playing") {
                pauseGame();
            }
        } else if (event.key === "r" || event.key === "R") {
            if (gameState === "paused") {
                resumeGame();
            }
        }
    });
    
    // Button click handlers
    document.getElementById("start-button").addEventListener("click", startGame);
    document.getElementById("resume-button").addEventListener("click", resumeGame);
    document.getElementById("quit-button").addEventListener("click", quitToMenu);
    document.getElementById("play-again-button").addEventListener("click", startGame);
    document.getElementById("menu-button").addEventListener("click", quitToMenu);
    
    // Difficulty buttons
    document.getElementById("easy-button").addEventListener("click", function() {
        setDifficulty("Easy");
    });
    document.getElementById("medium-button").addEventListener("click", function() {
        setDifficulty("Medium");
    });
    document.getElementById("hard-button").addEventListener("click", function() {
        setDifficulty("Hard");
    });
    
    // Duration slider
    document.getElementById("duration-slider").addEventListener("input", function() {
        GAME_DURATION = parseInt(this.value);
        document.querySelector('.slider-value').textContent = `${GAME_DURATION} seconds`;
    });
    
    // Music buttons
    document.getElementById("music1-button").addEventListener("click", function() {
        setMusic("music1");
    });
    document.getElementById("music2-button").addEventListener("click", function() {
        setMusic("music2");
    });
    document.getElementById("music3-button").addEventListener("click", function() {
        setMusic("music3");
    });
    document.getElementById("no-music-button").addEventListener("click", function() {
        setMusic("none");
    });
    
    // Custom music upload
    document.getElementById("custom-music-input").addEventListener("change", function(event) {
        const file = event.target.files[0];
        if (file) {
            const url = URL.createObjectURL(file);
            customMusicPlayer.src = url;
            customMusicLoaded = true;
            setMusic("custom");
        }
    });
}

// Set difficulty
function setDifficulty(newDifficulty) {
    difficulty = newDifficulty;
    
    // Update UI
    document.querySelectorAll(".difficulty-button").forEach(button => {
        button.classList.remove("selected");
    });
    document.getElementById(`${difficulty.toLowerCase()}-button`).classList.add("selected");
}

// Set music
function setMusic(musicType) {
    selectedMusic = musicType;
    
    // Update UI
    document.querySelectorAll(".music-button").forEach(button => {
        button.classList.remove("selected");
    });
    
    if (musicType !== "custom") {
        document.getElementById(`${musicType}-button`).classList.add("selected");
    }
    
    // Stop all music
    backgroundMusic1.pause();
    backgroundMusic2.pause();
    backgroundMusic3.pause();
    customMusicPlayer.pause();
    
    // Play selected music
    if (musicType === "music1") {
        currentMusic = backgroundMusic1;
    } else if (musicType === "music2") {
        currentMusic = backgroundMusic2;
    } else if (musicType === "music3") {
        currentMusic = backgroundMusic3;
    } else if (musicType === "custom" && customMusicLoaded) {
        currentMusic = customMusicPlayer;
    } else {
        currentMusic = null;
    }
    
    if (currentMusic && gameState === "playing") {
        currentMusic.currentTime = 0;
        currentMusic.play();
    }
}

// Start the game
function startGame() {
    // Reset game variables
    score = 0;
    lives = INITIAL_LIVES;
    fallingObjects = [];
    gameStartTime = Date.now();
    lastSpawnTime = Date.now();
    applesCaught = 0;
    rocksAvoided = 0;
    difficultyIncreaseFactor = 1.0;
    
    // Set initial difficulty settings
    currentSpawnRate = difficultySettings[difficulty].initialSpawnRate;
    currentSpeedRange = [...difficultySettings[difficulty].initialSpeedRange];
    
    // Hide menus, show game
    mainMenu.style.display = "none";
    pauseMenu.style.display = "none";
    gameOverScreen.style.display = "none";
    
    // Start music
    if (currentMusic) {
        currentMusic.currentTime = 0;
        currentMusic.play();
    }
    
    // Set game state
    gameState = "playing";
}

// Pause the game
function pauseGame() {
    if (gameState === "playing") {
        gameState = "paused";
        pauseMenu.style.display = "flex";
        
        // Pause music
        if (currentMusic) {
            currentMusic.pause();
        }
    }
}

// Resume the game
function resumeGame() {
    if (gameState === "paused") {
        gameState = "playing";
        pauseMenu.style.display = "none";
        
        // Resume music
        if (currentMusic) {
            currentMusic.play();
        }
    }
}

// Quit to main menu
function quitToMenu() {
    gameState = "menu";
    mainMenu.style.display = "flex";
    pauseMenu.style.display = "none";
    gameOverScreen.style.display = "none";
    
    // Stop music
    if (currentMusic) {
        currentMusic.pause();
    }
}

// End the game
function endGame() {
    gameState = "gameOver";
    
    // Update high score
    saveHighScore();
    
    // Update game over screen
    finalScoreDisplay.textContent = score;
    endHighScoreDisplay.textContent = highScore;
    applesCaughtDisplay.textContent = applesCaught;
    rocksAvoidedDisplay.textContent = rocksAvoided;
    difficultyLevelDisplay.textContent = `${difficulty} (${GAME_DURATION}s)`;
    
    // Show game over screen
    gameOverScreen.style.display = "flex";
    
    // Play game over sound
    gameOverSound.play();
    
    // Stop music
    if (currentMusic) {
        currentMusic.pause();
    }
}

// Spawn a new falling object
function spawnObject() {
    const x = Math.random() * (CANVAS_WIDTH - 2 * OBJECT_RADIUS) + OBJECT_RADIUS;
    const y = -OBJECT_RADIUS;
    
    // Determine object type (0 = apple, 1 = rock, 2 = bomb)
    let objectType;
    const rand = Math.random();
    if (rand < 0.7) {
        objectType = 0; // 70% chance for apple
    } else if (rand < 0.9) {
        objectType = 1; // 20% chance for rock
    } else {
        objectType = 2; // 10% chance for bomb
    }
    
    // Calculate speed based on current speed range and difficulty increase factor
    const minSpeed = currentSpeedRange[0] * difficultyIncreaseFactor;
    const maxSpeed = currentSpeedRange[1] * difficultyIncreaseFactor;
    const speed = minSpeed + Math.random() * (maxSpeed - minSpeed);
    
    fallingObjects.push({
        x: x,
        y: y,
        speed: speed,
        type: objectType
    });
}

// Update game state
function update(deltaTime) {
    // Check if game time is up
    const currentTime = Date.now();
    const elapsedTime = (currentTime - gameStartTime) / 1000; // in seconds
    
    if (elapsedTime >= GAME_DURATION) {
        endGame();
        return;
    }
    
    // Increase difficulty over time
    difficultyIncreaseFactor = 1.0 + (elapsedTime / GAME_DURATION);
    
    // Spawn new objects
    if (currentTime - lastSpawnTime > currentSpawnRate * 1000 / difficultyIncreaseFactor) {
        spawnObject();
        lastSpawnTime = currentTime;
    }
    
    // Update falling objects
    for (let i = fallingObjects.length - 1; i >= 0; i--) {
        const obj = fallingObjects[i];
        
        // Move object
        obj.y += obj.speed * deltaTime;
        
        // Check if object is caught
        if (obj.y + OBJECT_RADIUS >= basketY - BASKET_HEIGHT/2 &&
            obj.y - OBJECT_RADIUS <= basketY + BASKET_HEIGHT/2 &&
            obj.x >= basketX - BASKET_WIDTH/2 &&
            obj.x <= basketX + BASKET_WIDTH/2) {
            
            // Handle different object types
            if (obj.type === 0) { // Apple
                score += 10;
                applesCaught++;
                catchSound.currentTime = 0;
                catchSound.play();
            } else if (obj.type === 1) { // Rock
                score -= 5;
                badCatchSound.currentTime = 0;
                badCatchSound.play();
            } else if (obj.type === 2) { // Bomb
                lives--;
                bombSound.currentTime = 0;
                bombSound.play();
                
                if (lives <= 0) {
                    endGame();
                    return;
                }
            }
            
            // Remove the caught object
            fallingObjects.splice(i, 1);
        }
        // Check if object is missed
        else if (obj.y - OBJECT_RADIUS > CANVAS_HEIGHT) {
            if (obj.type === 0) { // Only count missed apples
                missSound.currentTime = 0;
                missSound.play();
            } else if (obj.type === 1) {
                rocksAvoided++;
            }
            
            // Remove the missed object
            fallingObjects.splice(i, 1);
        }
    }
}

// Draw game elements
function draw() {
    // Clear canvas
    ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    // Draw sky background
    ctx.fillStyle = "#87CEEB"; // Sky blue
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    // Create gradient for better sky effect
    const skyGradient = ctx.createLinearGradient(0, 0, 0, CANVAS_HEIGHT);
    skyGradient.addColorStop(0, "#1e88e5");
    skyGradient.addColorStop(1, "#64b5f6");
    ctx.fillStyle = skyGradient;
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    // Draw clouds
    drawClouds();
    
    // Draw ground
    const groundGradient = ctx.createLinearGradient(0, CANVAS_HEIGHT - 20, 0, CANVAS_HEIGHT);
    groundGradient.addColorStop(0, "#66bb6a");
    groundGradient.addColorStop(1, "#388e3c");
    ctx.fillStyle = groundGradient;
    ctx.fillRect(0, CANVAS_HEIGHT - 20, CANVAS_WIDTH, 20);
    
    // Draw falling objects
    for (const obj of fallingObjects) {
        if (obj.type === 0) { // Apple
            drawApple(obj.x, obj.y);
        } else if (obj.type === 1) { // Rock
            drawRock(obj.x, obj.y);
        } else if (obj.type === 2) { // Bomb
            drawBomb(obj.x, obj.y);
        }
    }
    
    // Draw basket
    drawBasket();
    
    // Draw UI
    drawUI();
}

// Draw clouds
function drawClouds() {
    ctx.fillStyle = "rgba(255, 255, 255, 0.8)";
    
    // Draw 5 clouds at fixed positions
    const cloudPositions = [
        {x: 100, y: 80},
        {x: 300, y: 60},
        {x: 500, y: 100},
        {x: 700, y: 70},
        {x: 200, y: 150}
    ];
    
    for (const pos of cloudPositions) {
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, 30, 0, Math.PI * 2);
        ctx.arc(pos.x + 25, pos.y - 10, 25, 0, Math.PI * 2);
        ctx.arc(pos.x + 50, pos.y, 30, 0, Math.PI * 2);
        ctx.arc(pos.x + 25, pos.y + 10, 25, 0, Math.PI * 2);
        ctx.fill();
    }
}

// Draw apple
function drawApple(x, y) {
    // Draw apple body
    ctx.fillStyle = "#FF0000"; // Red
    ctx.beginPath();
    ctx.arc(x, y, OBJECT_RADIUS, 0, Math.PI * 2);
    ctx.fill();
    
    // Draw stem
    ctx.fillStyle = "#8B4513"; // Brown
    ctx.fillRect(x - 2, y - 25, 4, 10);
    
    // Draw leaf
    ctx.fillStyle = "#008000"; // Green
    ctx.beginPath();
    ctx.ellipse(x + 5, y - 22, 5, 3, 0, 0, Math.PI * 2);
    ctx.fill();
}

// Draw rock
function drawRock(x, y) {
    // Draw rock body
    ctx.fillStyle = "#808080"; // Gray
    ctx.beginPath();
    ctx.arc(x, y, OBJECT_RADIUS, 0, Math.PI * 2);
    ctx.fill();
    
    // Draw rock details
    ctx.fillStyle = "#606060"; // Darker gray
    ctx.beginPath();
    ctx.arc(x - 8, y - 5, 5, 0, Math.PI * 2);
    ctx.arc(x + 5, y - 8, 4, 0, Math.PI * 2);
    ctx.arc(x + 7, y + 5, 6, 0, Math.PI * 2);
    ctx.fill();
}

// Draw bomb
function drawBomb(x, y) {
    // Draw bomb body
    ctx.fillStyle = "#000000"; // Black
    ctx.beginPath();
    ctx.arc(x, y, OBJECT_RADIUS, 0, Math.PI * 2);
    ctx.fill();
    
    // Draw fuse
    ctx.strokeStyle = "#8B4513"; // Brown
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(x, y - OBJECT_RADIUS);
    ctx.quadraticCurveTo(x + 10, y - 30, x + 5, y - 35);
    ctx.stroke();
    
    // Draw spark
    ctx.fillStyle = "#FFFF00"; // Yellow
    ctx.beginPath();
    ctx.arc(x + 5, y - 35, 4, 0, Math.PI * 2);
    ctx.fill();
    
    // Draw highlight
    ctx.fillStyle = "rgba(255, 255, 255, 0.3)";
    ctx.beginPath();
    ctx.arc(x - 7, y - 7, 8, 0, Math.PI * 2);
    ctx.fill();
}

// Draw basket
function drawBasket() {
    // Create basket rect
    const basketRect = {
        left: basketX - BASKET_WIDTH/2,
        top: basketY - BASKET_HEIGHT/2,
        width: BASKET_WIDTH,
        height: BASKET_HEIGHT
    };
    
    // Draw basket body (brown)
    const basketGradient = ctx.createLinearGradient(
        basketRect.left, basketRect.top, 
        basketRect.left, basketRect.top + basketRect.height
    );
    basketGradient.addColorStop(0, "#8B4513");
    basketGradient.addColorStop(1, "#A0522D");
    ctx.fillStyle = basketGradient;
    
    // Draw rounded rectangle for basket
    ctx.beginPath();
    ctx.moveTo(basketRect.left + 10, basketRect.top);
    ctx.lineTo(basketRect.left + basketRect.width - 10, basketRect.top);
    ctx.quadraticCurveTo(basketRect.left + basketRect.width, basketRect.top, 
                        basketRect.left + basketRect.width, basketRect.top + 10);
    ctx.lineTo(basketRect.left + basketRect.width, basketRect.top + basketRect.height - 10);
    ctx.quadraticCurveTo(basketRect.left + basketRect.width, basketRect.top + basketRect.height,
                        basketRect.left + basketRect.width - 10, basketRect.top + basketRect.height);
    ctx.lineTo(basketRect.left + 10, basketRect.top + basketRect.height);
    ctx.quadraticCurveTo(basketRect.left, basketRect.top + basketRect.height,
                        basketRect.left, basketRect.top + basketRect.height - 10);
    ctx.lineTo(basketRect.left, basketRect.top + 10);
    ctx.quadraticCurveTo(basketRect.left, basketRect.top,
                        basketRect.left + 10, basketRect.top);
    ctx.fill();
    
    // Draw basket rim
    ctx.fillStyle = "#A0522D"; // Sienna
    ctx.beginPath();
    ctx.rect(basketX - BASKET_WIDTH/2, basketY - BASKET_HEIGHT/2, BASKET_WIDTH, 10);
    ctx.fill();
    
    // Add texture to basket
    for (let i = 0; i < 5; i++) {
        ctx.strokeStyle = "rgba(101, 67, 33, 0.5)";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(basketX - BASKET_WIDTH/2, basketY - BASKET_HEIGHT/2 + 15 + i * 8);
        ctx.lineTo(basketX + BASKET_WIDTH/2, basketY - BASKET_HEIGHT/2 + 15 + i * 8);
        ctx.stroke();
    }
    
    // Draw basket handle
    ctx.strokeStyle = "#A0522D"; // Sienna
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.arc(basketX, basketY - BASKET_HEIGHT/2, BASKET_WIDTH/3, Math.PI, 0);
    ctx.stroke();
}

// Draw UI
function drawUI() {
    // Draw score
    ctx.fillStyle = "white";
    ctx.font = "24px Arial";
    ctx.textAlign = "left";
    ctx.textBaseline = "top";
    ctx.fillText(`Score: ${score}`, 20, 20);
    
    // Draw timer
    const elapsedTime = (Date.now() - gameStartTime) / 1000; // in seconds
    const remainingTime = Math.max(0, GAME_DURATION - elapsedTime);
    ctx.textAlign = "center";
    ctx.fillText(`Time: ${Math.ceil(remainingTime)}s`, CANVAS_WIDTH / 2, 20);
    
    // Draw lives
    ctx.textAlign = "right";
    ctx.fillText(`Lives: ${lives}`, CANVAS_WIDTH - 20, 20);
    
    // Draw hearts for lives
    for (let i = 0; i < lives; i++) {
        drawHeart(CANVAS_WIDTH - 100 + i * 30, 60);
    }
    
    // Draw difficulty level and factor
    ctx.textAlign = "left";
    ctx.font = "16px Arial";
    ctx.fillText(`Difficulty: ${difficulty} (x${difficultyIncreaseFactor.toFixed(1)})`, 20, 60);
}

// Draw heart
function drawHeart(x, y) {
    ctx.fillStyle = "#FF0000"; // Red
    ctx.beginPath();
    ctx.moveTo(x, y + 5);
    ctx.bezierCurveTo(x, y, x - 10, y, x - 10, y + 10);
    ctx.bezierCurveTo(x - 10, y + 15, x, y + 20, x, y + 25);
    ctx.bezierCurveTo(x, y + 20, x + 10, y + 15, x + 10, y + 10);
    ctx.bezierCurveTo(x + 10, y, x, y, x, y + 5);
    ctx.fill();
}

// Game loop
let lastTime = 0;
function gameLoop(timestamp) {
    // Calculate delta time
    const deltaTime = (timestamp - lastTime) / 1000; // in seconds
    lastTime = timestamp;
    
    // Update and draw based on game state
    if (gameState === "playing") {
        update(deltaTime);
        draw();
    }
    
    // Continue the game loop
    requestAnimationFrame(gameLoop);
}
