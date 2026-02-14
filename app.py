from flask import Flask, request, jsonify
import swisseph as swe
import os

app = Flask(__name__)

swe.set_ephe_path(".")

# KP Old = 23°34'23"
KP_OLD_DEGREES = 23 + (34/60) + (23/3600)


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

    # Convert local time to UTC
    decimal_hour = hour + minute / 60.0
    utc_hour = decimal_hour - tz

    jd = swe.julday(year, month, day, utc_hour)

    # 1️⃣ Tropical houses
    cusps, ascmc = swe.houses(jd, lat, lon, b'P')

    # 2️⃣ Set KP Old ayanamsa properly
    swe.set_sid_mode(swe.SIDM_USER, KP_OLD_DEGREES, 0)
    ayan = swe.get_ayanamsa(jd)

    # 3️⃣ Subtract ayanamsa manually (KP method)
    sidereal_cusps = [(c - ayan) % 360 for c in cusps]

    asc = sidereal_cusps[0]
    mc = (ascmc[1] - ayan) % 360

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
