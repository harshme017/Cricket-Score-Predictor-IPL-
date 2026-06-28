# 🏏 CricketAI — IPL Score Predictor

> A production-grade machine learning web app that predicts IPL innings final scores in real time, built with Flask + Random Forest and a modern dark SaaS UI.

---

## ✨ Features

- **ML-Powered Predictions** — Random Forest model trained on ball-by-ball IPL data (2008–2022)
- **Real-Time Score Estimation** — Predicts final score range with ±7 run confidence band
- **Advanced Analytics** — Run rate, phase detection (Powerplay / Middle / Death), balls left, wicket pressure
- **Match Insights** — Auto-classifies innings as Explosive / Competitive / Par / Below Par
- **Modern Dark UI** — Glassmorphism cards, animated sidebars, smooth transitions
- **Full Input Validation** — Server-side + client-side with clear error messages
- **Responsive Design** — Works on desktop and mobile

---

## 🖥️ UI Preview

| Feature | Detail |
|---|---|
| Theme | Dark minimalist SaaS dashboard |
| Side Panels | Animated vertical IPL image sliders |
| Cards | Glassmorphism with blur + border |
| Font | Space Grotesk (headings) + Inter (body) |
| Accent | Amber / gold cricket palette |

---

## 🧠 ML Model

| Property | Value |
|---|---|
| Algorithm | Random Forest Regressor |
| Training Data | IPL Ball-by-Ball 2008–2022 |
| Features | 16 (current score, run rate, wickets, phase, venue, teams, etc.) |
| Preprocessing | OneHotEncoder via ColumnTransformer Pipeline |
| Target | Final innings score |

**Key engineered features:**
- `current_rr` — current run rate
- `balls_left` — balls remaining in innings
- `wickets_left` — wickets in hand
- `last_5_runs` / `last_5_wickets` — recent 5-over momentum
- `phase` — Powerplay / Middle Overs / Death Overs
- `tail_end` — tail-end situation flag
- `balls_per_wicket` — resource pressure metric
- `death_risk` — high-pressure end-game indicator
- `venue_avg` — ground average score

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
git clone https://github.com/yourusername/cricket-score-predictor.git
cd cricket-score-predictor

pip install -r requirements.txt
```

### Add Images (Optional)
Drop IPL celebration images into `static/images/` named `1.jpg`, `2.jpg`, … `12.jpg` for the animated side panels.

### Run

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## 📁 Project Structure

```
CRICKET-SCORE-PREDICTOR/
├── datasets/
│   ├── IPL_Ball_by_Ball_2008_2022.csv
│   └── IPL_Matches_2008_2022.csv
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   └── images/            ← Drop your IPL images here
│
├── templates/
│   └── index.html
│
├── app.py                 ← Flask server + API routes
├── predictor.py           ← Model loading + prediction logic
├── train_model.py         ← Model training script
├── cricket_model.pkl      ← Trained Random Forest model
├── requirements.txt
└── README.md
```

---

## 🎯 Input Fields

| Field | Description |
|---|---|
| Batting Team | IPL team currently batting |
| Bowling Team | IPL team currently bowling |
| Venue | Match stadium |
| Current Over | Overs completed (0–20) + balls (0–5) |
| Current Score | Runs scored so far |
| Wickets Lost | Wickets fallen |
| Extras | Wides, no-balls, byes, leg-byes |
| Runs (Last 5 Overs) | Recent scoring momentum |
| Wickets (Last 5 Overs) | Recent wicket-taking pressure |

---

## ⚠️ Validation Rules

- Overs cannot exceed 20.0 (20 overs + 0 balls)
- Balls must be 0–5 (not 6)
- Minimum 6 overs required for prediction accuracy
- Batting and bowling teams must be different
- All scores and run counts must be ≥ 0

---

## 🛠️ Retrain the Model

If you have the IPL datasets, retrain from scratch:

```bash
python train_model.py
```

This saves a new `cricket_model.pkl`.

---

## 📦 Tech Stack

| Layer | Tech |
|---|---|
| Backend | Python, Flask |
| ML | scikit-learn, pandas, numpy, joblib |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Fonts | Google Fonts (Space Grotesk, Inter) |
| Design | Glassmorphism, CSS animations |

---

## 📄 License

MIT License — feel free to use, modify, and showcase.

---

*Built for the love of cricket and machine learning* 🏏
