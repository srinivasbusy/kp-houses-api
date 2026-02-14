from flask import Flask, request, jsonify
import swisseph as swe

app = Flask(__name__)

# Set KP-compatible Lahiri
swe.set_sid_mode(swe.SIDM_USER, 84863, 0)


@app.route("/")
def home():
    return "KP Houses API Running"

@app.route("/houses")
def houses():
    try:
        jd = float(request.args.get("jd"))
        lat = float(request.args.get("lat"))
        lon = float(request.args.get("lon"))

        cusps, ascmc = swe.houses_ex(
            jd,
            lat,
            lon,
            b'P',              # Placidus
            swe.FLG_SIDEREAL   # Sidereal mode
        )

        return jsonify({
            "cusps": list(cusps[:12]),
            "asc": ascmc[0],
            "mc": ascmc[1]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
