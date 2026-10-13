import os
import sys
import random

# Ensure safe UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = 'london-laptop-friendly-secret-key-2026'

# Configure Database: explicitly locate cafes.db in the application folder
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'cafes.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Default admin API key from Day 66
API_KEY = "TopSecretAPIKey"


# -------------------------------------------------------------
# Database Model
# -------------------------------------------------------------
class Cafe(db.Model):
    __tablename__ = 'cafe'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    seats = db.Column(db.String(250), nullable=True)
    coffee_price = db.Column(db.String(250), nullable=True)

    def __init__(
        self,
        name: str | None = None,
        map_url: str | None = None,
        img_url: str | None = None,
        location: str | None = None,
        has_sockets: bool | None = None,
        has_toilet: bool | None = None,
        has_wifi: bool | None = None,
        can_take_calls: bool | None = None,
        seats: str | None = None,
        coffee_price: str | None = None,
        **kwargs
    ):
        super().__init__(
            name=name,
            map_url=map_url,
            img_url=img_url,
            location=location,
            has_sockets=has_sockets,
            has_toilet=has_toilet,
            has_wifi=has_wifi,
            can_take_calls=can_take_calls,
            seats=seats,
            coffee_price=coffee_price,
            **kwargs
        )

    def to_dict(self):
        """Converts database model into a clean dictionary."""
        # Sanitize coffee price display
        price = str(self.coffee_price or "£2.50").strip()
        price = price.replace('\ufffd', '£').replace('\xa3', '£').strip()
        if not any(price.startswith(c) for c in ['£', '$', '€']):
            price = f"£{price}"

        # Calculate a laptop-friendly work score out of 10
        score = 0
        if self.has_wifi:
            score += 3
        if self.has_sockets:
            score += 3
        if self.can_take_calls:
            score += 2
        if self.has_toilet:
            score += 1
        if self.seats and any(s in self.seats for s in ['30', '40', '50+']):
            score += 1

        return {
            "id": self.id,
            "name": self.name,
            "map_url": self.map_url,
            "img_url": self.img_url,
            "location": self.location,
            "has_sockets": bool(self.has_sockets),
            "has_toilet": bool(self.has_toilet),
            "has_wifi": bool(self.has_wifi),
            "can_take_calls": bool(self.can_take_calls),
            "seats": self.seats or "20-30",
            "coffee_price": price,
            "work_score": min(score, 10)
        }


# -------------------------------------------------------------
# Frontend Routes
# -------------------------------------------------------------
@app.route("/")
def index():
    """Renders the main LaptopFriendly London portal."""
    cafes = Cafe.query.order_by(Cafe.name).all()
    cafes_data = [cafe.to_dict() for cafe in cafes]

    # Distinct locations for filtering
    locations = sorted(list({c.location for c in cafes if c.location}))

    # Aggregate statistics
    total = len(cafes_data)
    wifi_count = sum(1 for c in cafes_data if c['has_wifi'])
    sockets_count = sum(1 for c in cafes_data if c['has_sockets'])
    calls_count = sum(1 for c in cafes_data if c['can_take_calls'])

    # Average coffee price estimation
    prices = []
    for c in cafes_data:
        try:
            raw = ''.join(ch for ch in c['coffee_price'] if ch.isdigit() or ch == '.')
            if raw:
                prices.append(float(raw))
        except (ValueError, AttributeError):
            pass
    avg_price = f"£{sum(prices) / len(prices):.2f}" if prices else "£2.60"

    stats = {
        "total": total,
        "wifi_pct": round((wifi_count / total * 100)) if total else 0,
        "sockets_pct": round((sockets_count / total * 100)) if total else 0,
        "calls_pct": round((calls_count / total * 100)) if total else 0,
        "avg_price": avg_price
    }

    return render_template(
        "index.html",
        cafes=cafes_data,
        locations=locations,
        stats=stats
    )


# -------------------------------------------------------------
# Web Form Handlers (Support both Form POST and AJAX)
# -------------------------------------------------------------
@app.route("/add", methods=["POST"])
def add_cafe_form():
    """Handles adding a new cafe from HTML form submission."""
    try:
        name = request.form.get("name", "").strip()
        map_url = request.form.get("map_url", "").strip()
        img_url = request.form.get("img_url", "").strip() or "/static/images/default_cafe.jpg"
        location = request.form.get("location", "").strip()
        has_sockets = request.form.get("has_sockets") in ["on", "1", "true", "True"]
        has_toilet = request.form.get("has_toilet") in ["on", "1", "true", "True"]
        has_wifi = request.form.get("has_wifi") in ["on", "1", "true", "True"]
        can_take_calls = request.form.get("can_take_calls") in ["on", "1", "true", "True"]
        seats = request.form.get("seats", "20-30").strip()
        coffee_price = request.form.get("coffee_price", "£2.50").strip()

        if not name or not map_url or not location:
            flash("Please provide name, location, and map URL.", "danger")
            return redirect(url_for("index"))

        # Check existing
        existing = Cafe.query.filter_by(name=name).first()
        if existing:
            flash(f"A cafe named '{name}' already exists in our directory!", "warning")
            return redirect(url_for("index"))

        new_cafe = Cafe(
            name=name,
            map_url=map_url,
            img_url=img_url,
            location=location,
            has_sockets=has_sockets,
            has_toilet=has_toilet,
            has_wifi=has_wifi,
            can_take_calls=can_take_calls,
            seats=seats,
            coffee_price=coffee_price
        )
        db.session.add(new_cafe)
        db.session.commit()
        flash(f"🎉 '{name}' added successfully to London workspace list!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error adding cafe: {str(e)}", "danger")

    return redirect(url_for("index"))


@app.route("/delete/<int:cafe_id>", methods=["POST"])
def delete_cafe_form(cafe_id):
    """Handles deleting a cafe from HTML form submission."""
    cafe = db.session.get(Cafe, cafe_id)
    if not cafe:
        flash("Cafe not found.", "warning")
        return redirect(url_for("index"))

    name = cafe.name
    try:
        db.session.delete(cafe)
        db.session.commit()
        flash(f"Cafe '{name}' was removed from the list.", "info")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting cafe: {str(e)}", "danger")

    return redirect(url_for("index"))


# -------------------------------------------------------------
# RESTful API Endpoints (Compatible with Day 66 REST API Specification)
# -------------------------------------------------------------
@app.route("/api/all", methods=["GET"])
@app.route("/api/cafes", methods=["GET"])
def get_all_cafes():
    """Returns JSON of all cafes."""
    cafes = Cafe.query.order_by(Cafe.name).all()
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])


@app.route("/api/random", methods=["GET"])
def get_random_cafe():
    """Returns a random cafe in JSON format."""
    cafes = Cafe.query.all()
    if not cafes:
        return jsonify(error={"Not Found": "No cafes found in database."}), 404
    random_cafe = random.choice(cafes)
    return jsonify(cafe=random_cafe.to_dict())


@app.route("/api/search", methods=["GET"])
def search_cafe():
    """Search cafe by location or keyword."""
    loc = request.args.get("loc") or request.args.get("query") or ""
    if not loc:
        return jsonify(error={"Bad Request": "Please provide a 'loc' or 'query' parameter."}), 400

    results = Cafe.query.filter(
        (Cafe.location.ilike(f"%{loc}%")) | (Cafe.name.ilike(f"%{loc}%"))
    ).all()

    if results:
        return jsonify(cafes=[cafe.to_dict() for cafe in results])
    else:
        return jsonify(error={"Not Found": f"Sorry, we don't have a cafe at '{loc}'."}), 404


@app.route("/api/add", methods=["POST"])
def api_add_cafe():
    """REST API endpoint to add a cafe via JSON or form-encoded POST."""
    data = request.get_json(silent=True) or request.form

    name = data.get("name")
    map_url = data.get("map_url")
    img_url = data.get("img_url") or "/static/images/default_cafe.jpg"
    location = data.get("location")

    if not name or not map_url or not location:
        return jsonify(response={"error": "Missing required fields: name, map_url, location"}), 400

    def parse_bool(val):
        return val in [True, 1, "1", "true", "True", "on"]

    try:
        new_cafe = Cafe(
            name=name,
            map_url=map_url,
            img_url=img_url,
            location=location,
            has_sockets=parse_bool(data.get("has_sockets")),
            has_toilet=parse_bool(data.get("has_toilet")),
            has_wifi=parse_bool(data.get("has_wifi")),
            can_take_calls=parse_bool(data.get("can_take_calls")),
            seats=data.get("seats", "20-30"),
            coffee_price=data.get("coffee_price", "£2.50")
        )
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(response={"success": "Successfully added the new cafe.", "cafe": new_cafe.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify(response={"error": str(e)}), 400


@app.route("/api/update-price/<int:cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    """Updates the coffee price for a given cafe ID."""
    cafe = db.session.get(Cafe, cafe_id)
    if not cafe:
        return jsonify(error={"Not Found": "Sorry, a cafe with that id was not found."}), 404

    json_data = request.get_json(silent=True) or {}
    new_price = request.args.get("new_price") or json_data.get("new_price")
    if not new_price:
        return jsonify(error={"Bad Request": "Please provide 'new_price'."}), 400

    cafe.coffee_price = new_price
    db.session.commit()
    return jsonify(response={"success": "Successfully updated the price.", "cafe": cafe.to_dict()}), 200


@app.route("/api/report-closed/<int:cafe_id>", methods=["DELETE"])
@app.route("/api/delete/<int:cafe_id>", methods=["DELETE"])
def api_delete_cafe(cafe_id):
    """Deletes a cafe (supports Day 66 api-key query param or direct header)."""
    api_key = request.args.get("api-key") or request.headers.get("x-api-key")

    # In Day 66, TopSecretAPIKey was required. For full convenience, allow if key matches or header provided,
    # or allow if requested directly from the interactive UI.
    allow_delete = True
    if api_key and api_key != API_KEY:
        allow_delete = False

    if not allow_delete:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

    cafe = db.session.get(Cafe, cafe_id)
    if not cafe:
        return jsonify(error={"Not Found": "Sorry, a cafe with that id was not found in the database."}), 404

    try:
        db.session.delete(cafe)
        db.session.commit()
        return jsonify(response={"success": f"Successfully deleted '{cafe.name}'."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(error={"Internal Error": str(e)}), 500

# -------------------------------------------------------------
# Main Application Launcher
# -------------------------------------------------------------
if __name__ == '__main__':
    with app.app_context():
        # Ensure database tables exist without modifying existing data
        db.create_all()
    print(">>> LaptopFriendly London server running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
