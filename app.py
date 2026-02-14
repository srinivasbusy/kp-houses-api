from flask import Flask, request, jsonify
import swisseph as swe
import os

app = Flask(__name__)

# Swiss ephemeris data path
swe.set_ephe_path(".")

# KP OLD Ayanamsa = 23°34'23"
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
        jd = float(request.args.get("jd"))
        lat = float(request.args.get("lat"))
        lon = float(request.args.get("lon"))
    except:
        return jsonify({"error": "Invalid parameters"}), 400

    # 🔥 IMPORTANT: Set sidereal mode BEFORE calculations
    swe.set_sid_mode(swe.SIDM_USER, KP_OLD_ARCSECONDS, 0)

    # 🔥 Use houses_ex with SIDEREAL flag
    cusps, ascmc = swe.houses_ex(
        jd,
        lat,
        lon,
        b'P',                # Placidus
        swe.FLG_SIDEREAL     # IMPORTANT
    )

    # Normalize values to 0–360
    cusps = [c % 360 for c in cusps]

    result = {
        "asc": cusps[0],
        "cusps": cusps,
        "mc": ascmc[1] % 360
    }

    return jsonify(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
