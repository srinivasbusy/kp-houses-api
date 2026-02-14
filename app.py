from flask import Flask, request, jsonify
import swisseph as swe
import os

app = Flask(__name__)

# Set Swiss ephemeris path
swe.set_ephe_path(".")

# KP Old ayanamsa = 23°34'23"
# Convert to arcseconds:
# 23° = 23 * 3600 = 82800
# 34' = 34 * 60 = 2040
# 23" = 23
# Total = 84863 arcseconds
KP_OLD_ARCSECONDS = 84863


@app.route("/")
def home():
    return "KP Houses API Running"


@app.route("/houses")
def houses():

    try:
        year = int(request.args.get("year"))
        month = int(request.args.get("month"))
        day = int(request.args.get("day"))

        hour = int(request.args.get("hour"))
        minute = int(request.args.get("minute"))

        lat = float(request.args.get("lat"))
        lon = float(request.args.get("lon"))

        tz = float(request.args.get("tz"))

    except:
        return jsonify({"error": "Invalid parameters"}), 400

    # -------------------------
    # 1️⃣ Convert Local Time → UTC
    # -------------------------
    decimal_hour = hour + (minute / 60.0)
    utc_hour = decimal_hour - tz

    # If UTC becomes negative or > 24, Swiss handles it internally
    jd = swe.julday(year, month, day, utc_hour)

    # -------------------------
    # 2️⃣ Compute Tropical Houses
    # -------------------------
    cusps, ascmc = swe.houses(jd, lat, lon, b'P')  # Placidus

    # -------------------------
    # 3️⃣ Get KP Old Ayanamsa
    # -------------------------
    swe.set_sid_mode(swe.SIDM_USER, KP_OLD_ARCSECONDS, 0)
    ayan = swe.get_ayanamsa(jd)

    # -------------------------
    # 4️⃣ Convert to Sidereal (KP style)
    # -------------------------
    sidereal_cusps = []
    for c in cusps:
        val = (c - ayan) % 360
        sidereal_cusps.append(val)

    asc = sidereal_cusps[0]
    mc = (ascmc[1] - ayan) % 360

    # -------------------------
    # 5️⃣ Return JSON
    # -------------------------
    return jsonify({
        "jd": jd,
        "ayanamsa": ayan,
        "asc": asc,
        "cusps": sidereal_cusps,
        "mc": mc
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
