from flask import Flask, request, jsonify
import swisseph as swe
import os

app = Flask(__name__)

swe.set_ephe_path(".")


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

    # Convert to UTC
    decimal_hour = hour + minute / 60.0
    utc_hour = decimal_hour - tz

    jd = swe.julday(year, month, day, utc_hour)

    # KP ayanamsa
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)

    # 🔥 EQUAL HOUSE SYSTEM
    cusps, ascmc = swe.houses_ex(
        jd,
        lat,
        lon,
        b'E',
        swe.FLG_SIDEREAL
    )

    cusps = [c % 360 for c in cusps]

    return jsonify({
        "jd": jd,
        "ayanamsa": swe.get_ayanamsa(jd),
        "asc": cusps[0],
        "cusps": cusps,
        "mc": ascmc[1] % 360
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
