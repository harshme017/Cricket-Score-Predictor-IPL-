<div align="center">

# 🏏 CricketAI — IPL Score Predictor

### ML-Powered · Real-Time · Production-Grade

A full-stack machine learning web app that predicts IPL innings final scores in real time.
Built with Flask, Random Forest, and a dark SaaS-style UI with animated sidebars and fireworks.

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.3+-000000?style=for-the-badge&logo=flask&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.2+-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-CSS3-E34F26?style=for-the-badge&logo=html5&logoColor=white)

</div>

---

## 📸 Preview

| Feature | Screenshot |
|---|---|
| Dark SaaS Dashboard | Glassmorphism prediction form |
| Animated IPL sidebars | Year-labelled scrolling photo panels |
| Result card | Score range, stats, phase badge, match insight |
| 🎆 Fireworks | Canvas animation on every prediction |

---

## ✨ Features

- 🤖 **ML Score Prediction** — Random Forest model trained on 14 years of IPL ball-by-ball data
- 📊 **Score Range Output** — Predicts a ±7 run confidence band (`172 – 186`)
- 🏏 **Cricket Logic Layer** — Physics-based fallback for outlier inputs the model hasn't seen
- 🔢 **Live Analytics** — Run rate, balls left, wickets left, venue average, innings phase
- 🎯 **Match Insight** — Auto-classifies as Explosive / Competitive / Par / Below Par
- 🎆 **Fireworks Animation** — Full canvas rocket + particle burst on every prediction
- 🖼️ **Animated Sidebars** — Auto-scrolling IPL season photos (2008–2026) with year labels
- 🌑 **Dark SaaS UI** — Glassmorphism cards, red accent theme, Rajdhani + Inter fonts
- 🛡️ **Dual Validation** — Client-side (instant) + server-side (safe fallback)
- 📱 **Responsive** — Adapts from widescreen down to mobile

---

## 🧠 ML Model

| Property | Detail |
|---|---|
| Algorithm | Random Forest Regressor |
| Training Data | IPL Ball-by-Ball 2008–2022 (first innings only) |
| Min Overs Required | 6 overs (model trained from over 6 onwards) |
| Features | 16 engineered features |
| Preprocessing | OneHotEncoder via sklearn ColumnTransformer Pipeline |
| Target Variable | Final innings score |

### Engineered Features

| Feature | Description |
|---|---|
| `current_score` | Runs scored so far |
| `current_rr` | Current run rate (score ÷ overs elapsed) |
| `balls_left` | Balls remaining in innings |
| `wickets_left` | Wickets in hand (10 − wickets lost) |
| `last_5_runs` | Runs in last 5 overs (momentum) |
| `last_5_wickets` | Wickets in last 5 overs (pressure) |
| `extras_run` | Wides, no-balls, byes |
| `phase` | Powerplay / Middle Overs / Death Overs |
| `venue_avg` | Historical average score at that ground |
| `tail_end` | Flag: only 1 wicket remaining |
| `balls_per_wicket` | Resource pressure metric |
| `death_risk` | Flag: ≤2 wickets + ≥24 balls left |
| `Venue` | One-hot encoded stadium |
| `BattingTeam` | One-hot encoded batting team |
| `BowlingTeam` | One-hot encoded bowling team |

### Cricket Logic Layer

The model was trained on scores in the typical IPL range (80–220). For out-of-distribution inputs (e.g. 174 runs in 7 overs), a physics-based fallback is triggered:

```
effective_rr = 0.60 × min(current_rr, 12) + 0.40 × T20_average(8)
projected    = current_score + balls_left × (effective_rr ÷ 6)
```

This regression-to-mean formula correctly handles extreme scoring scenarios that the ML model has never seen in training.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- pip

### Installation

```bash
git clone https://github.com/harshme017/Cricket-Score-Predictor-IPL-.git
cd Cricket-Score-Predictor-IPL-
 
pip install -r requirements.txt
```

### Add Your IPL Images

Drop your celebration images into `static/images/` named by year:

```
static/images/
├── 2008.jpg
├── 2009.jpg
├── ...
└── 2026.jpg
```

These auto-load into the animated sidebars with year labels.

### Run

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## 📁 Project Structure

```
CRICKET-SCORE-PREDICTOR/
│
├── datasets/                          ← Training data (not included in repo)
│   ├── IPL_Ball_by_Ball_2008_2022.csv
│   └── IPL_Matches_2008_2022.csv
│
├── static/
│   ├── css/
│   │   └── style.css                 ← Full dark SaaS theme
│   ├── js/
│   │   └── script.js                 ← Slider, fetch API, fireworks engine
│   └── images/                       ← IPL season photos (2008–2026)
│
├── templates/
│   └── index.html                    ← Jinja2 dashboard template
│
├── app.py                            ← Flask server + JSON prediction API
├── predictor.py                      ← Model + cricket logic layer
├── train_model.py                    ← Full model training pipeline
├── cricket_model.pkl                 ← Trained Random Forest (35MB)
├── requirements.txt
└── README.md
```

---

## 🎯 Input Fields

| Field | Type | Description |
|---|---|---|
| Batting Team | Dropdown | IPL team currently batting (18 teams) |
| Bowling Team | Dropdown | IPL team currently bowling |
| Stadium / Venue | Dropdown | Match ground (25 venues) |
| Overs | Dropdown | Overs completed (6–20) |
| Balls | Dropdown | Extra balls this over (0–5) |
| Current Score | Number | Runs on the board |
| Wickets Lost | Dropdown | Wickets fallen (0–9) |
| Extras | Number | Wides, no-balls, byes |
| Runs (Last 5 Overs) | Number | Recent batting momentum |
| Wickets (Last 5 Overs) | Dropdown | Recent bowling pressure |

---

## ✅ Validation Rules

Both client-side (instant) and server-side (safe):

- Overs 20 + Balls > 0 → ❌ Invalid
- Balls must be 0–5 only (never 6)
- Minimum 6 overs required for reliable prediction
- Batting and bowling teams must be different
- All scores and run counts must be ≥ 0
- Wickets lost must be 0–9

---

## 🎆 Fireworks Animation

Every successful prediction triggers a canvas-based fireworks show:

- **Wave 1** — 4 rockets at 0ms
- **Wave 2** — 5 rockets at 700ms
- **Wave 3** — 4 rockets at 1500ms
- **Wave 4** — 3 finale rockets at 2300ms

Each rocket rises to a random height, then bursts into 80–140 spark/star particles in IPL-inspired colors (red, gold, blue, green, pink). Automatically clears after 4.5 seconds. Clicks pass through the canvas so the UI stays fully interactive.

---

## 🎨 UI Design System

| Element | Detail |
|---|---|
| Theme | Dark minimalist (`#080c14` base) |
| Accent | Red (`#ef4444`) — IPL energy |
| Cards | Glassmorphism (`rgba(8,12,20,0.72)` + `blur(24px)`) |
| Fonts | Rajdhani (display/scores) + Inter (body) |
| Background | Full-screen BCCI stadium photo (`brightness(0.28)`) |
| Sidebars | JS `requestAnimationFrame` scroll — left up, right down |
| Animations | Slide-in header, fade-up cards, spring result reveal |

---

## 🛠️ Retrain the Model

If you have the IPL datasets:

```bash
python train_model.py
```

Saves a new `cricket_model.pkl`. The training pipeline includes:
- First innings filtering
- Ball-by-ball cumulative score and wicket calculation
- Rolling 30-ball window for last-5-overs features
- Phase labelling (Powerplay / Middle / Death)
- Venue average computation
- Random Forest with `n_estimators=50`, `max_depth=20`

---

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.9+, Flask 2.3+ |
| ML | scikit-learn, pandas, numpy, joblib |
| Frontend | HTML5, CSS3, Vanilla JavaScript (ES6+) |
| Fonts | Google Fonts — Rajdhani, Inter, Space Grotesk |
| Design | Glassmorphism, CSS keyframe animations |
| Animation | Canvas API (`requestAnimationFrame`) |

---

## 👤 Author

**Harsh**
Built with Python, Flask and Machine Learning to demonstrate real-time IPL score prediction.

---

## 📄 License

MIT License — free to use, modify, and showcase.

---

<div align="center">
  <i>Star ⭐ this repo if you found it useful!</i>
</div>