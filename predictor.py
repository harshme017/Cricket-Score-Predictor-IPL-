import joblib
import pandas as pd
import numpy as np
import os
import warnings

warnings.filterwarnings("ignore")

# ----------------------------
# Load Model
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "cricket_model.pkl")
model = joblib.load(model_path)

# ----------------------------
# Venue Average Scores
# ----------------------------
VENUE_AVG = {
    "Wankhede Stadium": 173,
    "M Chinnaswamy Stadium": 175,
    "Eden Gardens": 162,
    "MA Chidambaram Stadium": 158,
    "Narendra Modi Stadium": 168,
    "Sardar Patel Stadium, Motera": 168,
    "Arun Jaitley Stadium": 163,
    "Feroz Shah Kotla": 163,
    "Punjab Cricket Association IS Bindra Stadium": 164,
    "Rajiv Gandhi International Stadium": 165,
    "Sawai Mansingh Stadium": 161,
    "Holkar Cricket Stadium": 172,
    "Himachal Pradesh Cricket Association Stadium": 159,
    "Maharashtra Cricket Association Stadium": 165,
    "Saurashtra Cricket Association Stadium": 160,
    "Dr DY Patil Sports Academy": 169,
    "JSCA International Stadium Complex": 155,
    "Brabourne Stadium": 166,
    "Subrata Roy Sahara Stadium": 158,
    "Vidarbha Cricket Association Stadium, Jamtha": 157,
    "Green Park": 152,
    "Nehru Stadium": 153,
    "Shaheed Veer Narayan Singh International Stadium": 148,
    "Barabati Stadium": 154,
    "Dubai International Cricket Stadium": 156,
    "Sharjah Cricket Stadium": 153,
    "Sheikh Zayed Stadium": 155,
    "Zayed Cricket Stadium, Abu Dhabi": 154,
    "New Wanderers Stadium": 168,
    "Newlands": 160,
    "Kingsmead": 161,
    "SuperSport Park": 163,
    "St George's Park": 157,
    "OUTsurance Oval": 159,
    "De Beers Diamond Oval": 156,
    "Buffalo Park": 153,
    "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium": 158,
}
DEFAULT_VENUE_AVG = 162


# ----------------------------
# Cricket logic bounds
# ----------------------------
def _cricket_bounds(current_score, balls_left, wickets_left):
    """
    Return (floor, ceiling) for the final score using pure cricket logic.
    These are used to sanity-check / override the ML model when the input
    is an outlier the model has never seen in training data.

    floor   = current score + (balls_left * min_run_rate_per_ball)
    ceiling = current score + (balls_left * max_run_rate_per_ball)

    Min rate per ball  = 0.40 r/ball (~2.4 rpo)  — slowest possible crawl
    Max rate per ball  = 2.50 r/ball (~15 rpo)    — absolute maximum T20 hitting
    Expected rate      = 0.83 r/ball (~5 rpo)     — T20 average when wickets in hand
    """
    min_rpb = 0.40   # absolute floor per ball remaining
    max_rpb = 2.50   # absolute ceiling per ball remaining

    # Adjust max downward if wickets are running out
    if wickets_left <= 2:
        max_rpb = 1.2
    elif wickets_left <= 4:
        max_rpb = 2.0

    floor   = int(current_score + balls_left * min_rpb)
    ceiling = int(current_score + balls_left * max_rpb)
    return floor, ceiling


# ----------------------------
# Prediction Function
# ----------------------------
def predict_score(
    venue,
    batting_team,
    bowling_team,
    current_over,       # e.g. 7.1 means 7 overs 1 ball (training format)
    current_score,
    extras_run,
    wickets_lost,
    last_5_runs,
    last_5_wickets,
):
    # ── Derive ball counts ──────────────────────────────────────────
    whole_over  = int(current_over)
    ball_digit  = round((current_over - whole_over) * 10)  # 0-5

    balls_played    = whole_over * 6 + ball_digit
    balls_left      = max(0, 120 - balls_played)
    wickets_left    = 10 - wickets_lost

    # ── Run rate (consistent with training: score / current_over) ───
    # Training data used overs+ball/10 as denominator — keep the same.
    # Guard against division by zero at very start.
    actual_overs_elapsed = balls_played / 6.0   # true decimal overs
    current_rr = (current_score / actual_overs_elapsed) if actual_overs_elapsed > 0 else 0.0

    # ── Phase ───────────────────────────────────────────────────────
    if current_over <= 6:
        phase = "Powerplay"
    elif current_over <= 15:
        phase = "Middle Overs"
    else:
        phase = "Death Overs"

    # ── Advanced features ───────────────────────────────────────────
    tail_end        = 1 if wickets_left <= 1 else 0
    balls_per_wicket = balls_left / (wickets_left + 1)
    death_risk      = 1 if (wickets_left <= 2 and balls_left >= 24) else 0
    venue_avg       = VENUE_AVG.get(venue, DEFAULT_VENUE_AVG)

    sample = pd.DataFrame({
        "Venue":           [venue],
        "BattingTeam":     [batting_team],
        "BowlingTeam":     [bowling_team],
        "current_over":    [current_over],
        "current_score":   [current_score],
        "extras_run":      [extras_run],
        "wickets_left":    [wickets_left],
        "current_rr":      [current_rr],
        "balls_left":      [balls_left],
        "last_5_runs":     [last_5_runs],
        "last_5_wickets":  [last_5_wickets],
        "phase":           [phase],
        "venue_avg":       [venue_avg],
        "tail_end":        [tail_end],
        "balls_per_wicket":[balls_per_wicket],
        "death_risk":      [death_risk],
    })

    # ── ML prediction ───────────────────────────────────────────────
    ml_pred = int(model.predict(sample)[0])

    # ── Hard cricket-logic bounds ───────────────────────────────────
    floor, ceiling = _cricket_bounds(current_score, balls_left, wickets_left)

    # ── Detect out-of-distribution inputs ───────────────────────────
    # The model was trained on IPL data where the maximum score at any
    # point rarely exceeds 130 in the first 10 overs. When current_score
    # is already much higher than what the model has seen, its prediction
    # gets anchored to its training distribution (~160-210) and becomes
    # unreliable. We detect this by checking if the ML prediction implies
    # fewer additional runs than the physics floor demands.
    #
    # Key insight: if ml_pred < floor, OR if ml_pred - current_score
    # is less than the minimum physically possible additional runs
    # (floor - current_score), the model is wrong — bypass it.

    min_additional  = floor - current_score   # minimum more runs possible
    ml_additional   = ml_pred - current_score  # what model thinks will be added

    T20_AVG_RPO  = 8.0
    MAX_SUST_RPO = 12.0

    model_is_unreliable = (
        ml_additional < min_additional or    # model below physical floor
        ml_pred < floor or                   # same check on absolute value
        (current_rr > 14.0 and ml_additional < (balls_left * 1.0))  # RR outlier: model anchored to training distribution
    )

    if model_is_unreliable:
        # Physics-based projection with regression to T20 mean.
        # The higher the current RR, the more it regresses:
        #   RR 24 → effective ~11.2 rpo
        #   RR 18 → effective ~10.8 rpo
        #   RR 14 → effective ~10.4 rpo
        #   RR 10 → effective ~9.2 rpo (barely regresses — already near average)
        capped_rr    = min(current_rr, MAX_SUST_RPO)
        effective_rr = 0.60 * capped_rr + 0.40 * T20_AVG_RPO
        effective_rpb = effective_rr / 6.0
        projected    = current_score + int(balls_left * effective_rpb)
        prediction   = max(projected, floor)
    elif ml_pred > ceiling:
        prediction = ceiling
    else:
        prediction = max(ml_pred, floor)

    # ── Wicket-based upper limits ───────────────────────────────────
    # (applied AFTER the bounds check so we don't cap reasonable scores)
    if wickets_left == 1:
        prediction = min(prediction, current_score + 22)
    elif wickets_left == 2:
        prediction = min(prediction, current_score + 38)

    # Final absolute floor: cannot predict less than current score
    prediction = max(prediction, current_score)

    return prediction, phase, wickets_left, balls_left, round(current_rr, 2), venue_avg