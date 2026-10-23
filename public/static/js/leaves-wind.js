/**
 * CLIMATEX - Dynamic Wind & Moving Leaves Simulation Engine
 * Powered by User-Uploaded Botanical Leaves & Sunrise Mountain Valley Ambiance.
 * Features:
 * - High-performance 2D Canvas rendering at 60 FPS
 * - Real user-uploaded leaf assets (Green Laurel, Golden Orange Maple, Crimson Red Maple)
 * - 3D tumble physics: multi-axis roll, pitch, rotation, and pendulum sway
 * - Atmospheric wind streamlines ("with air") gliding across screen
 * - Ambient golden sunlight / mountain mist motes
 * - Dynamic natural mountain wind gusts & breeze velocity oscillation
 * - Interactive cursor airflow disturbance (leaves kick up and scatter on mouse move)
 * - Interactive Breeze Control widget (Gentle / Moderate / Gusty / Pause)
 * - Retina DPR support & Page Visibility CPU throttling
 */

(function () {
    'use strict';

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initLeavesWindSimulation);
    } else {
        initLeavesWindSimulation();
    }

    function initLeavesWindSimulation() {
        const canvas = document.getElementById('leavesWindCanvas');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Preload User Uploaded Leaf Assets
        const LEAF_IMAGES = [
            { src: '/static/images/leaf-green.png', img: new Image(), loaded: false, w: 225, h: 131, baseAngle: -0.45 },
            { src: '/static/images/leaf-orange.png', img: new Image(), loaded: false, w: 420, h: 476, baseAngle: 0 },
            { src: '/static/images/leaf-red.png', img: new Image(), loaded: false, w: 357, h: 353, baseAngle: 0 }
        ];

        LEAF_IMAGES.forEach(item => {
            item.img.onload = () => { item.loaded = true; };
            item.img.src = item.src;
        });

        // Simulation Configuration
        const CONFIG = {
            leafCount: 38,
            airMoteCount: 26,
            windStreamCount: 6,
            windStrength: 1.0, // 0: Paused, 0.5: Gentle, 1.0: Moderate, 1.8: Mountain Gusts
            baseWindX: 1.8,
            baseWindY: 1.1,
            gravity: 0.95,
            mouseRadius: 140,
            mouseForce: 2.0,
            colors: [
                { main: '#E08A1E', under: '#F4C078', stem: '#8C4D0A' },
                { main: '#65A30D', under: '#BEF264', stem: '#365314' },
                { main: '#C0392B', under: '#F1948A', stem: '#641E16' }
            ]
        };

        let width = 0;
        let height = 0;
        let dpr = window.devicePixelRatio || 1;
        let animationFrameId = null;
        let isRunning = true;
        let time = 0;

        // Dynamic Wind Gust State
        let gustTime = 0;
        let currentGust = 0;
        let targetGust = 0;

        // Mouse Tracker for Airflow Wake
        const mouse = {
            x: -9999,
            y: -9999,
            vx: 0,
            vy: 0,
            lastX: -9999,
            lastY: -9999,
            isActive: false
        };

        // Window resize
        function resize() {
            width = window.innerWidth;
            height = window.innerHeight;
            dpr = Math.min(window.devicePixelRatio || 1, 2);

            canvas.width = Math.floor(width * dpr);
            canvas.height = Math.floor(height * dpr);
            canvas.style.width = width + 'px';
            canvas.style.height = height + 'px';

            ctx.scale(dpr, dpr);
        }

        window.addEventListener('resize', resize, { passive: true });
        resize();

        // Mouse / Touch Interaction for Wind Airflow
        window.addEventListener('mousemove', function (e) {
            const currentX = e.clientX;
            const currentY = e.clientY;
            if (mouse.lastX !== -9999) {
                mouse.vx = (currentX - mouse.lastX) * 0.35;
                mouse.vy = (currentY - mouse.lastY) * 0.35;
            }
            mouse.x = currentX;
            mouse.y = currentY;
            mouse.lastX = currentX;
            mouse.lastY = currentY;
            mouse.isActive = true;
        }, { passive: true });

        window.addEventListener('mouseleave', function () {
            mouse.isActive = false;
            mouse.x = -9999;
            mouse.y = -9999;
        });

        window.addEventListener('touchmove', function (e) {
            if (e.touches && e.touches.length > 0) {
                const touch = e.touches[0];
                mouse.x = touch.clientX;
                mouse.y = touch.clientY;
                mouse.isActive = true;
            }
        }, { passive: true });

        // Leaf Class
        class Leaf {
            constructor(spawnAnywhere = false) {
                this.init(spawnAnywhere);
            }

            init(spawnAnywhere = false) {
                this.imageIndex = Math.floor(Math.random() * LEAF_IMAGES.length);
                this.fallbackPalette = CONFIG.colors[this.imageIndex % CONFIG.colors.length];

                // Depth (0 = distant & smaller/slower, 1 = foreground & larger/faster)
                this.depth = 0.35 + Math.random() * 0.65;
                // Target leaf display size in pixels
                this.size = (30 + Math.random() * 26) * this.depth;

                // Position
                if (spawnAnywhere) {
                    this.x = Math.random() * (width + 300) - 150;
                    this.y = Math.random() * height;
                } else {
                    if (Math.random() < 0.65) {
                        this.x = Math.random() * (width + 200) - 100;
                        this.y = -50 - Math.random() * 60;
                    } else {
                        this.x = -60 - Math.random() * 80;
                        this.y = Math.random() * (height * 0.75);
                    }
                }

                // Velocities
                this.baseVx = (CONFIG.baseWindX * (0.8 + Math.random() * 0.6)) * this.depth;
                this.baseVy = (CONFIG.baseWindY * (0.7 + Math.random() * 0.5) + CONFIG.gravity * 0.8) * this.depth;
                this.vx = this.baseVx;
                this.vy = this.baseVy;

                // 3D Flutter Physics
                this.rotation = Math.random() * Math.PI * 2;
                this.rotationSpeed = (Math.random() - 0.5) * 0.045;

                this.roll = Math.random() * Math.PI * 2;
                this.rollSpeed = 0.025 + Math.random() * 0.045;

                this.pitch = Math.random() * Math.PI * 2;
                this.pitchSpeed = 0.02 + Math.random() * 0.035;

                // Pendulum Sway
                this.swayPhase = Math.random() * Math.PI * 2;
                this.swaySpeed = 0.022 + Math.random() * 0.03;
                this.swayAmp = 18 + Math.random() * 26;

                this.opacity = (0.82 + Math.random() * 0.18) * (0.7 + this.depth * 0.3);
            }

            update(gust, dt) {
                this.swayPhase += this.swaySpeed * (1 + gust * 0.5);
                const swayOffset = Math.sin(this.swayPhase) * (this.swayAmp * 0.04);

                const effectiveWind = CONFIG.windStrength;
                const windX = (this.baseVx + gust * 2.4 * this.depth) * effectiveWind;
                const windY = (this.baseVy + Math.abs(gust) * 0.45 * this.depth) * effectiveWind;

                this.vx = windX + swayOffset;
                this.vy = windY;

                // Interactive Mouse Air disturbance
                if (mouse.isActive) {
                    const dx = this.x - mouse.x;
                    const dy = this.y - mouse.y;
                    const distSq = dx * dx + dy * dy;
                    const r = CONFIG.mouseRadius;

                    if (distSq < r * r && distSq > 4) {
                        const dist = Math.sqrt(distSq);
                        const pushFactor = (1 - dist / r) * CONFIG.mouseForce * 4.2;
                        const angle = Math.atan2(dy, dx);

                        this.vx += Math.cos(angle) * pushFactor + mouse.vx * 0.18;
                        this.vy += Math.sin(angle) * pushFactor + mouse.vy * 0.18;
                        this.rollSpeed += 0.09 * (1 - dist / r);
                        this.rotationSpeed += 0.06 * (Math.random() - 0.5);
                    }
                }

                // Update position
                this.x += this.vx;
                this.y += this.vy;

                // Update 3D angles
                this.rotation += this.rotationSpeed * effectiveWind;
                this.roll += this.rollSpeed * (1 + gust * 0.6) * effectiveWind;
                this.pitch += this.pitchSpeed * effectiveWind;

                // Recycle if moved outside boundary
                if (this.y > height + 80 || this.x > width + 120 || this.x < -160) {
                    this.init(false);
                }
            }

            draw(ctx) {
                ctx.save();
                ctx.translate(this.x, this.y);

                // Apply 2D Rotation
                ctx.rotate(this.rotation);

                // Apply 3D perspective squashing (Roll and Pitch)
                const scaleX = Math.cos(this.roll);
                const scaleY = Math.cos(this.pitch * 0.5);

                ctx.scale(scaleX, Math.max(0.18, Math.abs(scaleY)));
                ctx.globalAlpha = Math.max(0.2, this.opacity);

                const leafData = LEAF_IMAGES[this.imageIndex];

                if (leafData && leafData.loaded) {
                    const aspect = leafData.w / leafData.h;
                    let drawW, drawH;
                    if (aspect >= 1) {
                        drawW = this.size * 1.35;
                        drawH = drawW / aspect;
                    } else {
                        drawH = this.size * 1.35;
                        drawW = drawH * aspect;
                    }

                    ctx.save();
                    if (leafData.baseAngle) {
                        ctx.rotate(leafData.baseAngle);
                    }
                    // Subtle underside brightness shift when flipped
                    if (scaleX < 0) {
                        ctx.filter = 'brightness(0.9) contrast(0.96)';
                    }
                    ctx.drawImage(leafData.img, -drawW / 2, -drawH / 2, drawW, drawH);
                    ctx.restore();
                } else {
                    // Fallback procedural rendering while images load
                    const s = this.size;
                    ctx.fillStyle = scaleX < 0 ? this.fallbackPalette.under : this.fallbackPalette.main;
                    ctx.beginPath();
                    ctx.ellipse(0, 0, s * 0.5, s * 0.9, 0, 0, Math.PI * 2);
                    ctx.fill();
                }

                ctx.restore();
            }
        }

        // Air Mote Class (Floating golden sunlight motes / mountain mist particles)
        class AirMote {
            constructor() {
                this.init(true);
            }

            init(anywhere = false) {
                this.x = anywhere ? Math.random() * width : Math.random() * (width + 100) - 50;
                this.y = anywhere ? Math.random() * height : -10;
                this.radius = 0.8 + Math.random() * 2.2;
                this.alpha = 0.2 + Math.random() * 0.5;
                this.speedX = 0.9 + Math.random() * 1.9;
                this.speedY = 0.4 + Math.random() * 1.0;
                this.pulseSpeed = 0.03 + Math.random() * 0.04;
                this.pulse = Math.random() * Math.PI * 2;
                this.color = Math.random() > 0.35 ? '251, 191, 36' : '56, 189, 248';
            }

            update(gust) {
                this.pulse += this.pulseSpeed;
                const effectiveWind = CONFIG.windStrength;
                this.x += (this.speedX + gust * 2.1) * effectiveWind;
                this.y += (this.speedY + Math.sin(this.pulse) * 0.5) * effectiveWind;

                if (this.x > width + 20 || this.y > height + 20) {
                    this.init(false);
                }
            }

            draw(ctx) {
                const currentAlpha = Math.max(0.05, this.alpha * (0.6 + 0.4 * Math.sin(this.pulse)));
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(${this.color}, ${currentAlpha})`;
                ctx.shadowColor = `rgba(${this.color}, 0.5)`;
                ctx.shadowBlur = 6;
                ctx.fill();
                ctx.shadowBlur = 0;
            }
        }

        // Wind Streamline Class ("With Air" visualization)
        class WindStream {
            constructor() {
                this.init(true);
            }

            init(anywhere = false) {
                this.y = Math.random() * height;
                this.x = anywhere ? (Math.random() * width - 400) : -500;
                this.length = 320 + Math.random() * 480;
                this.speed = 4.8 + Math.random() * 5.2;
                this.waveAmp = 18 + Math.random() * 26;
                this.phase = Math.random() * Math.PI * 2;
                this.width = 1.2 + Math.random() * 2.0;
                this.opacity = 0.12 + Math.random() * 0.22;
                this.hue = Math.random() > 0.4 ? '56, 189, 248' : '251, 191, 36';
            }

            update(gust) {
                const effectiveWind = CONFIG.windStrength;
                this.x += (this.speed + gust * 6.2) * effectiveWind;
                this.phase += 0.03 * effectiveWind;

                if (this.x - this.length > width + 100) {
                    this.init(false);
                }
            }

            draw(ctx) {
                if (CONFIG.windStrength <= 0) return;

                const startX = this.x;
                const endX = this.x + this.length;
                const midX = (startX + endX) / 2;

                const startY = this.y + Math.sin(this.phase) * this.waveAmp;
                const midY = this.y + Math.sin(this.phase + Math.PI * 0.5) * (this.waveAmp * 1.3);
                const endY = this.y + Math.sin(this.phase + Math.PI) * this.waveAmp;

                const grad = ctx.createLinearGradient(startX, startY, endX, endY);
                grad.addColorStop(0, `rgba(${this.hue}, 0)`);
                grad.addColorStop(0.3, `rgba(${this.hue}, ${this.opacity * 0.85})`);
                grad.addColorStop(0.7, `rgba(${this.hue}, ${this.opacity})`);
                grad.addColorStop(1, `rgba(${this.hue}, 0)`);

                ctx.save();
                ctx.beginPath();
                ctx.moveTo(startX, startY);
                ctx.quadraticCurveTo(midX, midY, endX, endY);
                ctx.strokeStyle = grad;
                ctx.lineWidth = this.width;
                ctx.lineCap = 'round';
                ctx.shadowColor = `rgba(${this.hue}, 0.4)`;
                ctx.shadowBlur = 8;
                ctx.stroke();
                ctx.shadowBlur = 0;
                ctx.restore();
            }
        }

        // Initialize Entities
        const leaves = [];
        for (let i = 0; i < CONFIG.leafCount; i++) {
            leaves.push(new Leaf(true));
        }

        const airMotes = [];
        for (let i = 0; i < CONFIG.airMoteCount; i++) {
            airMotes.push(new AirMote());
        }

        const windStreams = [];
        for (let i = 0; i < CONFIG.windStreamCount; i++) {
            windStreams.push(new WindStream());
        }

        // Main Animation Loop
        let lastTimestamp = performance.now();

        function render(timestamp) {
            if (!isRunning) return;

            const dt = Math.min((timestamp - lastTimestamp) / 1000, 0.1);
            lastTimestamp = timestamp;
            time += dt;

            // Mountain Gust Dynamics
            gustTime += dt;
            if (gustTime > 8) {
                targetGust = 1.2 + Math.random() * 1.5;
                if (gustTime > 11) {
                    targetGust = 0;
                    gustTime = Math.random() * 2;
                }
            } else {
                targetGust = Math.sin(time * 0.8) * 0.3;
            }

            currentGust += (targetGust - currentGust) * 0.05;

            // Clear screen
            ctx.clearRect(0, 0, width, height);

            // 1. Draw Visible Air Streamlines
            for (let i = 0; i < windStreams.length; i++) {
                windStreams[i].update(currentGust);
                windStreams[i].draw(ctx);
            }

            // 2. Draw Sunlight / Mist Air Motes
            for (let i = 0; i < airMotes.length; i++) {
                airMotes[i].update(currentGust);
                airMotes[i].draw(ctx);
            }

            // 3. Draw User-Uploaded Moving Leaves in Wind
            for (let i = 0; i < leaves.length; i++) {
                leaves[i].update(currentGust, dt);
                leaves[i].draw(ctx);
            }

            animationFrameId = requestAnimationFrame(render);
        }

        animationFrameId = requestAnimationFrame(render);

        // Pause animation when tab is inactive to preserve CPU / Battery
        document.addEventListener('visibilitychange', function () {
            if (document.hidden) {
                isRunning = false;
                if (animationFrameId) cancelAnimationFrame(animationFrameId);
            } else {
                isRunning = true;
                lastTimestamp = performance.now();
                animationFrameId = requestAnimationFrame(render);
            }
        });

        // Setup Interactive Breeze Controls UI
        setupBreezeController(CONFIG);
    }

    function setupBreezeController(config) {
        const toggleBtn = document.getElementById('breezeToggleBtn');
        const statusLabel = document.getElementById('breezeStatusText');
        const iconElem = document.getElementById('breezeIcon');

        if (!toggleBtn) return;

        const modes = [
            { name: 'Moderate Breeze', strength: 1.0, icon: 'bi-wind', color: '#38BDF8' },
            { name: 'Mountain Gusts', strength: 1.8, icon: 'bi-tornado', color: '#F59E0B' },
            { name: 'Gentle Air', strength: 0.5, icon: 'bi-cloud-sun', color: '#10B981' },
            { name: 'Paused', strength: 0.0, icon: 'bi-pause-circle', color: '#94A3B8' }
        ];

        let modeIndex = 0;

        toggleBtn.addEventListener('click', function (e) {
            e.preventDefault();
            modeIndex = (modeIndex + 1) % modes.length;
            const currentMode = modes[modeIndex];
            config.windStrength = currentMode.strength;

            if (statusLabel) {
                statusLabel.innerText = currentMode.name;
            }

            if (iconElem) {
                iconElem.className = `bi ${currentMode.icon}`;
                iconElem.style.color = currentMode.color;
            }
        });
    }

})();
