from flask import Flask, render_template, request, jsonify
from predictor import predict_score

app = Flask(__name__)

# ----------------------------
# Data: All IPL Teams & Venues
# ----------------------------
TEAMS = [
    "Royal Challengers Bangalore",
    "Chennai Super Kings",
    "Delhi Capitals",
    "Gujarat Titans",
    "Kolkata Knight Riders",
    "Lucknow Super Giants",
    "Mumbai Indians",
    "Punjab Kings",
    "Rajasthan Royals",
    "Sunrisers Hyderabad",
    # Legacy teams
    "Deccan Chargers",
    "Delhi Daredevils",
    "Gujarat Lions",
    "Kings XI Punjab",
    "Kochi Tuskers Kerala",
    "Pune Warriors",
    "Rising Pune Supergiant",
    "Rising Pune Supergiants",
]

VENUES = [
    "Narendra Modi Stadium",
    "Wankhede Stadium",
    "M Chinnaswamy Stadium",
    "Eden Gardens",
    "MA Chidambaram Stadium",
    "Arun Jaitley Stadium",
    "Punjab Cricket Association IS Bindra Stadium",
    "Rajiv Gandhi International Stadium",
    "Sawai Mansingh Stadium",
    "Holkar Cricket Stadium",
    "Himachal Pradesh Cricket Association Stadium",
    "Maharashtra Cricket Association Stadium",
    "Saurashtra Cricket Association Stadium",
    "Dr DY Patil Sports Academy",
    "JSCA International Stadium Complex",
    "Brabourne Stadium",
    "Subrata Roy Sahara Stadium",
    "Vidarbha Cricket Association Stadium, Jamtha",
    "Green Park",
    "Dubai International Cricket Stadium",
    "Sharjah Cricket Stadium",
    "Sheikh Zayed Stadium",
    "New Wanderers Stadium",
    "Newlands",
    "SuperSport Park",
]


@app.route("/")
def home():
    return render_template("index.html", teams=TEAMS, venues=VENUES)


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        batting_team = data.get("batting_team", "").strip()
        bowling_team = data.get("bowling_team", "").strip()
        venue = data.get("venue", "").strip()
        overs = int(data.get("overs", 0))
        balls = int(data.get("balls", 0))
        current_score = int(data.get("current_score", 0))
        extras_run = int(data.get("extras_run", 0))
        wickets_lost = int(data.get("wickets_lost", 0))
        last_5_runs = int(data.get("last_5_runs", 0))
        last_5_wickets = int(data.get("last_5_wickets", 0))

        # ---------- Validation ----------
        errors = []

        if not batting_team:
            errors.append("Batting Team is required.")
        if not bowling_team:
            errors.append("Bowling Team is required.")
        if batting_team and bowling_team and batting_team == bowling_team:
            errors.append("Batting and bowling teams cannot be the same.")
        if overs == 20 and balls > 0:
            errors.append("Invalid overs: Cannot exceed 20.0 overs.")
        if overs < 6:
            errors.append("Model requires at least 6 overs to have been bowled.")
        if not (0 <= balls <= 5):
            errors.append("Balls must be between 0 and 5.")
        if current_score < 0:
            errors.append("Current score cannot be negative.")
        if not (0 <= wickets_lost <= 9):
            errors.append("Wickets lost must be between 0 and 9.")
        if not (0 <= last_5_wickets <= 5):
            errors.append("Last 5 overs wickets must be between 0 and 5.")
        if last_5_runs < 0:
            errors.append("Last 5 overs runs cannot be negative.")
        if extras_run < 0:
            errors.append("Extras cannot be negative.")

        if errors:
            return jsonify({"success": False, "errors": errors}), 400

        current_over = overs + (balls / 10)

        prediction, phase, wickets_left, balls_left, run_rate, venue_avg = predict_score(
            venue=venue,
            batting_team=batting_team,
            bowling_team=bowling_team,
            current_over=current_over,
            current_score=current_score,
            extras_run=extras_run,
            wickets_lost=wickets_lost,
            last_5_runs=last_5_runs,
            last_5_wickets=last_5_wickets,
        )

        # Score range ±7
        lower = max(0, prediction - 7)
        upper = prediction + 7

        # Match insight
        if prediction >= 200:
            insight = "Explosive Innings"
            insight_class = "explosive"
        elif prediction >= 175:
            insight = "Competitive Total"
            insight_class = "competitive"
        elif prediction >= 155:
            insight = "Par Score"
            insight_class = "par"
        else:
            insight = "Below Par"
            insight_class = "belowpar"

        return jsonify({
            "success": True,
            "prediction": prediction,
            "lower": lower,
            "upper": upper,
            "phase": phase,
            "wickets_left": wickets_left,
            "balls_left": balls_left,
            "run_rate": run_rate,
            "venue_avg": venue_avg,
            "insight": insight,
            "insight_class": insight_class,
        })

    except ValueError as ve:
        return jsonify({"success": False, "errors": [f"Invalid input: {str(ve)}"]}), 400
    except Exception as e:
        return jsonify({"success": False, "errors": ["❌ Prediction Failed. Please check inputs."]}), 500


if __name__ == "__main__":
    app.run(debug=True)