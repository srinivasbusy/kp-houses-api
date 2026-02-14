from flask import Flask, request, jsonify
import swisseph as swe
import os

app = Flask(__name__)

# Set Swiss Ephemeris path
swe.set_ephe_path(".")

# KP Old Ayanamsa = 23°34'23"
# Convert to arcseconds
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
        lon = -float(request.args.get("lon"))


        tz = float(request.args.get("tz"))  # timezone like 5.5 for IST

    except:
        return jsonify({"error": "Invalid parameters"}), 400

    # Convert local time to UTC
    decimal_hour = hour + (minute / 60.0)
    utc_hour = decimal_hour - tz

    # Calculate Julian Day (UTC)
    jd = swe.julday(year, month, day, utc_hour)

    # Set KP Old ayanamsa
    swe.set_sid_mode(swe.SIDM_USER, KP_OLD_ARCSECONDS, 0)

    # Calculate houses (Placidus + Sidereal)
    cusps, ascmc = swe.houses_ex(
        jd,
        lat,
        lon,
        b'P',                # Placidus
        swe.FLG_SIDEREAL     # Important
    )

    cusps = [c % 360 for c in cusps]

    result = {
        "jd": jd,
        "asc": cusps[0],
        "cusps": cusps,
        "mc": ascmc[1] % 360
    }

    return jsonify(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
