from flask import Flask, request, jsonify
from flask_cors import CORS
import swisseph as swe
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend calls

# Set ephemeris path (Railway container local dir)
swe.set_ephe_path(".")

# Use Lahiri (KP-compatible baseline)
swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)


@app.route("/")
def home():
    return "KP Houses API Running"


@app.route("/houses")
def houses():
    try:
        jd = float(request.args.get("jd"))
        lat = float(request.args.get("lat"))
        lon = float(request.args.get("lon"))

        # 🔹 Calculate Houses (Placidus, Sidereal)
        cusps, ascmc = swe.houses_ex(
            jd,
            lat,
            lon,
            b'P',
            swe.FLG_SIDEREAL
        )

        # 🔹 Calculate Planets
        planet_ids = {
            "Sun": swe.SUN,
            "Moon": swe.MOON,
            "Mars": swe.MARS,
            "Mercury": swe.MERCURY,
            "Jupiter": swe.JUPITER,
            "Venus": swe.VENUS,
            "Saturn": swe.SATURN,
            "Rahu": swe.MEAN_NODE  # KP uses Mean Node
        }

        planets = {}
        retrograde = {}

        for name, pid in planet_ids.items():
            lon_data, speed_data = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)
            longitude = lon_data[0] % 360
            speed = lon_data[3]

            planets[name] = longitude
            retrograde[name] = speed < 0

        # Ketu opposite Rahu
        planets["Ketu"] = (planets["Rahu"] + 180) % 360
        retrograde["Ketu"] = retrograde["Rahu"]

        return jsonify({
            "jd": jd,
            "ayanamsa": swe.get_ayanamsa(jd),
            "asc": cusps[0] % 360,
            "mc": ascmc[1] % 360,
            "cusps": [c % 360 for c in cusps[:12]],
            "planets": planets,
            "retrograde": retrograde
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
