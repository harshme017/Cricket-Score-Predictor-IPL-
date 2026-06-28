/* =============================================
   CricketAI – script.js
   ============================================= */

"use strict";

// ── Image Slider Setup ───────────────────────
(function initSliders() {
  const leftTrack  = document.getElementById("leftTrack");
  const rightTrack = document.getElementById("rightTrack");
  if (!leftTrack || !rightTrack) return;

  // IPL seasons 2008–2026
  const IPL_YEARS = [
    2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,
    2018,2019,2020,2021,2022,2023,2024,2025,2026
  ];

  function createSlide(year) {
    const wrap = document.createElement("div");
    wrap.className = "slide-item";

    const img = document.createElement("img");
    img.src = `/static/images/${year}.jpg`;
    img.alt = `IPL ${year}`;
    img.onerror = function () { wrap.style.display = "none"; };

    const label = document.createElement("div");
    label.className = "slide-year";
    label.textContent = year;

    wrap.appendChild(img);
    wrap.appendChild(label);
    return wrap;
  }

  function buildTrack(track, years) {
    // Triple the set — guarantees seamless loop for any screen height
    [...years, ...years, ...years].forEach(y => track.appendChild(createSlide(y)));
  }

  buildTrack(leftTrack,  IPL_YEARS);
  buildTrack(rightTrack, [...IPL_YEARS].reverse());

  // ── rAF scroll loop ──────────────────────────
  // Speed: pixels per second. 55 = medium pace.
  const SPEED_LEFT  = 55;
  const SPEED_RIGHT = 48;

  let leftY  = 0;
  let rightY = 0;
  let lastTime = null;

  function getHalfHeight(track) {
    // The track contains 3 copies; half-height = 1 copy height
    return track.scrollHeight / 3;
  }

  function tick(ts) {
    if (!lastTime) lastTime = ts;
    const dt = (ts - lastTime) / 1000; // seconds since last frame
    lastTime = ts;

    // Left: scrolls upward
    leftY += SPEED_LEFT * dt;
    const leftHalf = getHalfHeight(leftTrack);
    if (leftY >= leftHalf) leftY -= leftHalf;   // seamless reset
    leftTrack.style.transform = `translateY(-${leftY}px)`;

    // Right: scrolls downward (starts at -half, moves toward 0)
    rightY += SPEED_RIGHT * dt;
    const rightHalf = getHalfHeight(rightTrack);
    if (rightY >= rightHalf) rightY -= rightHalf;
    // Invert direction: down = negative offset shrinking
    rightTrack.style.transform = `translateY(${rightY - rightHalf}px)`;

    requestAnimationFrame(tick);
  }

  // Small delay so images start loading before animation begins
  setTimeout(() => requestAnimationFrame(tick), 100);
})();


// ── Prediction Handler ───────────────────────
async function handlePredict() {
  const btn      = document.getElementById("predictBtn");
  const btnText  = btn.querySelector(".btn-text");
  const btnLoader = btn.querySelector("#btnLoader");
  const errorBox = document.getElementById("errorContainer");
  const resultCard = document.getElementById("resultCard");

  // ── Gather values ──
  const batting_team   = document.getElementById("batting_team").value.trim();
  const bowling_team   = document.getElementById("bowling_team").value.trim();
  const venue          = document.getElementById("venue").value.trim();
  const overs          = parseInt(document.getElementById("overs").value);
  const balls          = parseInt(document.getElementById("balls").value);
  const current_score  = parseInt(document.getElementById("current_score").value) || 0;
  const wickets_lost   = parseInt(document.getElementById("wickets_lost").value);
  const extras_run     = parseInt(document.getElementById("extras_run").value) || 0;
  const last_5_runs    = parseInt(document.getElementById("last_5_runs").value) || 0;
  const last_5_wickets = parseInt(document.getElementById("last_5_wickets").value);

  // ── Client-side validation ──
  const clientErrors = [];

  if (!batting_team)  clientErrors.push("Please select a batting team.");
  if (!bowling_team)  clientErrors.push("Please select a bowling team.");
  if (batting_team && bowling_team && batting_team === bowling_team)
    clientErrors.push("Batting and bowling teams cannot be the same.");
  if (overs === 20 && balls > 0)
    clientErrors.push("Invalid: 20 overs already completed — balls must be 0.");
  if (overs < 6)
    clientErrors.push("At least 6 overs must have been bowled to predict.");
  if (document.getElementById("current_score").value === "")
    clientErrors.push("Please enter the current score.");
  if (current_score < 0)
    clientErrors.push("Current score cannot be negative.");

  if (clientErrors.length) {
    showErrors(clientErrors, errorBox);
    resultCard.style.display = "none";
    return;
  }

  // ── Loading state ──
  errorBox.style.display = "none";
  btn.disabled = true;
  btnText.style.display = "none";
  btnLoader.style.display = "inline-flex";
  btnLoader.style.alignItems = "center";

  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        batting_team, bowling_team, venue,
        overs, balls, current_score,
        wickets_lost, extras_run,
        last_5_runs, last_5_wickets,
      }),
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
      showErrors(data.errors || ["Something went wrong. Please try again."], errorBox);
      resultCard.style.display = "none";
      return;
    }

    // ── Render result ──
    renderResult(data, batting_team, bowling_team);

  } catch (err) {
    showErrors(["Network error — is the Flask server running?"], errorBox);
    resultCard.style.display = "none";
  } finally {
    btn.disabled = false;
    btnText.style.display = "inline";
    btnLoader.style.display = "none";
  }
}


// ── Render prediction result ─────────────────
function renderResult(data, batting, bowling) {
  const resultCard = document.getElementById("resultCard");

  // Teams
  document.getElementById("resBatting").textContent = batting;
  document.getElementById("resBowling").textContent = bowling;

  // Phase badge
  const phaseBadge = document.getElementById("resPhaseBadge");
  phaseBadge.textContent = data.phase;
  phaseBadge.className = "res-phase-badge";
  const phaseMap = {
    "Powerplay":    "phase-powerplay",
    "Middle Overs": "phase-middle",
    "Death Overs":  "phase-death",
  };
  phaseBadge.classList.add(phaseMap[data.phase] || "phase-middle");

  // Score range
  document.getElementById("resLow").textContent  = data.lower;
  document.getElementById("resHigh").textContent = data.upper;
  document.getElementById("resBest").textContent = data.prediction;

  // Stats
  document.getElementById("resRR").textContent = data.run_rate;
  document.getElementById("resWL").textContent = data.wickets_left;
  document.getElementById("resBL").textContent = data.balls_left;
  document.getElementById("resVA").textContent = data.venue_avg;

  // Insight
  const insightBanner = document.getElementById("insightBanner");
  const insightText   = document.getElementById("insightText");
  const insightEmoji  = document.getElementById("insightEmoji");

  const insightMap = {
    explosive:   { emoji: "🔥", label: "Explosive Innings Expected" },
    competitive: { emoji: "💪", label: "Competitive Total Expected" },
    par:         { emoji: "⚡", label: "Par Score Expected" },
    belowpar:    { emoji: "📉", label: "Below Par Score — Tough Finish Ahead" },
  };
  const info = insightMap[data.insight_class] || insightMap.par;
  insightEmoji.textContent = info.emoji;
  insightText.textContent  = info.label;
  insightBanner.className  = `insight-banner ${data.insight_class}`;

  // Show with animation
  resultCard.style.display = "block";
  resultCard.style.animation = "none";
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      resultCard.style.animation = "";
      resultCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
    });
  });

  // 🎆 Fire the crackers!
  launchFireworks();
}


// ── Error renderer ───────────────────────────
function showErrors(errors, container) {
  container.innerHTML = "";
  errors.forEach((msg) => {
    const div = document.createElement("div");
    div.className = "error-item";
    div.textContent = msg;
    container.appendChild(div);
  });
  container.style.display = "block";
  container.scrollIntoView({ behavior: "smooth", block: "nearest" });
}


// ══════════════════════════════════════════════
// 🎆 FIRECRACKER / FIREWORKS ENGINE
// ══════════════════════════════════════════════
(function () {
  // Create a full-screen canvas overlay
  let canvas, ctx, particles = [], animId = null, killTimer = null;

  function init() {
    if (canvas) return; // already created
    canvas = document.createElement("canvas");
    canvas.id = "fireworksCanvas";
    Object.assign(canvas.style, {
      position:      "fixed",
      top:           "0",
      left:          "0",
      width:         "100%",
      height:        "100%",
      pointerEvents: "none",   // clicks pass through
      zIndex:        "9999",
    });
    document.body.appendChild(canvas);
    resize();
    window.addEventListener("resize", resize);
  }

  function resize() {
    if (!canvas) return;
    canvas.width  = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  // ── Particle class ──────────────────────────
  class Particle {
    constructor(x, y, color, type) {
      this.x  = x;
      this.y  = y;
      this.color = color;
      this.type  = type; // 'spark' | 'trail' | 'star'

      const angle  = Math.random() * Math.PI * 2;
      const speed  = type === "star"
        ? 1 + Math.random() * 3
        : 2 + Math.random() * 6;

      this.vx = Math.cos(angle) * speed;
      this.vy = Math.sin(angle) * speed - (type === "star" ? 1 : 0);
      this.gravity  = type === "trail" ? 0.05 : 0.12;
      this.alpha    = 1;
      this.decay    = type === "star"
        ? 0.008 + Math.random() * 0.006
        : 0.018 + Math.random() * 0.012;
      this.size     = type === "star"
        ? 2.5 + Math.random() * 2
        : 1.5 + Math.random() * 2.5;
      this.twinkle  = type === "star";
      this.twinklePhase = Math.random() * Math.PI * 2;
    }

    update() {
      this.x  += this.vx;
      this.y  += this.vy;
      this.vy += this.gravity;
      this.vx *= 0.98;
      this.alpha -= this.decay;
      if (this.twinkle) this.twinklePhase += 0.15;
    }

    draw(ctx) {
      const alpha = this.twinkle
        ? this.alpha * (0.6 + 0.4 * Math.sin(this.twinklePhase))
        : this.alpha;
      ctx.save();
      ctx.globalAlpha = Math.max(0, alpha);
      ctx.fillStyle   = this.color;
      ctx.shadowColor = this.color;
      ctx.shadowBlur  = this.type === "star" ? 6 : 4;
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }

    isDead() { return this.alpha <= 0; }
  }

  // ── Rocket (rises then bursts) ──────────────
  class Rocket {
    constructor() {
      this.x      = canvas.width * (0.15 + Math.random() * 0.70);
      this.y      = canvas.height;
      this.vy     = -(8 + Math.random() * 7);
      this.vx     = (Math.random() - 0.5) * 2.5;
      this.targetY = canvas.height * (0.10 + Math.random() * 0.45);
      this.trail  = [];
      this.burst  = false;

      // IPL-inspired colors: red, gold, white, orange, blue, green
      const palettes = [
        ["#ff4444","#ff8800","#ffdd00"],
        ["#ff2222","#ffffff","#ff6666"],
        ["#ffaa00","#ff6600","#ffff00"],
        ["#00cfff","#ffffff","#0066ff"],
        ["#ff44aa","#ff88cc","#ffddee"],
        ["#44ff88","#00cc44","#ffffff"],
      ];
      this.palette = palettes[Math.floor(Math.random() * palettes.length)];
    }

    update() {
      if (this.burst) return true; // done

      // Leave trail
      this.trail.push({ x: this.x, y: this.y, alpha: 0.6 });
      if (this.trail.length > 12) this.trail.shift();

      this.x += this.vx;
      this.y += this.vy;
      this.vy += 0.18; // slight gravity on ascent

      if (this.y <= this.targetY || this.vy >= 0) {
        this.explode();
        return true;
      }
      return false;
    }

    explode() {
      this.burst = true;
      const x = this.x, y = this.y;
      const count = 80 + Math.floor(Math.random() * 60);

      for (let i = 0; i < count; i++) {
        const color = this.palette[Math.floor(Math.random() * this.palette.length)];
        const type  = Math.random() < 0.2 ? "star" : "spark";
        particles.push(new Particle(x, y, color, type));
      }
      // Add a few trailing streamers
      for (let i = 0; i < 20; i++) {
        const color = this.palette[0];
        particles.push(new Particle(x, y, color, "trail"));
      }
    }

    drawTrail(ctx) {
      this.trail.forEach((t, i) => {
        ctx.save();
        ctx.globalAlpha = t.alpha * (i / this.trail.length);
        ctx.fillStyle   = "#ffaa44";
        ctx.shadowColor = "#ffaa44";
        ctx.shadowBlur  = 6;
        ctx.beginPath();
        ctx.arc(t.x, t.y, 2, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      });
    }
  }

  // ── Main loop ───────────────────────────────
  let rockets = [];

  function loop() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Update & draw rockets
    rockets = rockets.filter(r => {
      r.drawTrail(ctx);
      return !r.update();
    });

    // Update & draw particles
    particles = particles.filter(p => {
      p.update();
      p.draw(ctx);
      return !p.isDead();
    });

    if (rockets.length > 0 || particles.length > 0) {
      animId = requestAnimationFrame(loop);
    } else {
      stopFireworks();
    }
  }

  function stopFireworks() {
    if (animId) { cancelAnimationFrame(animId); animId = null; }
    if (canvas)  { ctx.clearRect(0, 0, canvas.width, canvas.height); }
  }

  // ── Public launcher ─────────────────────────
  window.launchFireworks = function () {
    init();
    ctx = canvas.getContext("2d");

    // Clear any previous run
    if (animId) cancelAnimationFrame(animId);
    if (killTimer) clearTimeout(killTimer);
    particles = [];
    rockets   = [];

    // Launch waves: immediate burst, then 3 more waves
    const launchWave = (count) => {
      for (let i = 0; i < count; i++) {
        setTimeout(() => rockets.push(new Rocket()), i * 120);
      }
    };

    launchWave(4);                              // instant — 4 rockets
    setTimeout(() => launchWave(5), 700);       // 0.7s  — 5 rockets
    setTimeout(() => launchWave(4), 1500);      // 1.5s  — 4 rockets
    setTimeout(() => launchWave(3), 2300);      // 2.3s  — 3 rockets (finale)

    // Start render loop
    animId = requestAnimationFrame(loop);

    // Auto-stop after 4.5s regardless
    killTimer = setTimeout(stopFireworks, 4500);
  };
})();