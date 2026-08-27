"""
app/routes.py — All Flask routes for the FiXiT application.

Routes follow REST-ish conventions:
  GET  /                                    → Dashboard
  GET  /assets                              → List all assets
  GET  /assets/<id>                         → Asset detail + history
  GET  /assets/add                          → Add asset form
  POST /assets/add                          → Process add asset form
  GET  /assets/<id>/maintenance/add         → Add maintenance record form
  POST /assets/<id>/maintenance/add         → Process add maintenance form
"""

from datetime import date, datetime
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
)
from app import db
from app.models import Asset, MaintenanceRecord, ASSET_CATEGORIES

main = Blueprint("main", __name__)


# ──────────────────────────────────────────────────────────
# Helper utilities
# ──────────────────────────────────────────────────────────

def _parse_date(date_str: str) -> date | None:
    """
    Convert a date string from an HTML date input (YYYY-MM-DD) to a Python
    date object. Returns None if the string is empty or invalid.
    """
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


# ──────────────────────────────────────────────────────────
# Route: Dashboard  GET /
# ──────────────────────────────────────────────────────────

@main.route("/")
def index():
    """
    Home / Dashboard.

    Fetches all assets from the database, then derives summary statistics
    in Python so the Jinja template stays logic-free.
    """
    all_assets = Asset.query.order_by(Asset.created_at.desc()).all()

    # Categorise assets by their computed status.
    overdue = [a for a in all_assets if a.maintenance_status == "Overdue"]
    due_soon = [a for a in all_assets if a.maintenance_status == "Due Soon"]
    up_to_date = [a for a in all_assets if a.maintenance_status == "Up to Date"]

    # Show the 5 most recently maintained assets on the dashboard.
    recently_maintained = (
        Asset.query
        .filter(Asset.last_maintenance_date.isnot(None))
        .order_by(Asset.last_maintenance_date.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "index.html",
        total_assets=len(all_assets),
        overdue=overdue,
        due_soon=due_soon,
        up_to_date=up_to_date,
        recently_maintained=recently_maintained,
    )


# ──────────────────────────────────────────────────────────
# Route: Assets list  GET /assets
# ──────────────────────────────────────────────────────────

@main.route("/assets")
def assets():
    """Display all registered assets sorted by name."""
    all_assets = Asset.query.order_by(Asset.name).all()
    return render_template("assets.html", assets=all_assets)


# ──────────────────────────────────────────────────────────
# Route: Asset detail  GET /assets/<id>
# ──────────────────────────────────────────────────────────

@main.route("/assets/<int:asset_id>")
def asset_detail(asset_id: int):
    """
    Show full details for one asset including its maintenance history.
    Returns 404 if the asset does not exist.
    """
    # get_or_404 automatically returns a 404 response for missing records.
    asset = db.get_or_404(Asset, asset_id)

    # Records are already ordered by date descending via the model relationship.
    return render_template("asset_detail.html", asset=asset)


# ──────────────────────────────────────────────────────────
# Route: Add asset  GET + POST /assets/add
# ──────────────────────────────────────────────────────────

@main.route("/assets/add", methods=["GET", "POST"])
def add_asset():
    """
    GET  — Display the blank Add Asset form.
    POST — Validate and save the new asset, then redirect to the assets list.
    """
    if request.method == "POST":
        # Pull form values.
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        purchase_date = _parse_date(request.form.get("purchase_date", ""))
        last_maintenance_date = _parse_date(
            request.form.get("last_maintenance_date", "")
        )
        notes = request.form.get("notes", "").strip()

        # Parse maintenance interval — must be a positive integer.
        try:
            interval = int(request.form.get("maintenance_interval_months", 0))
        except ValueError:
            interval = 0

        # ── Server-side validation ───────────────────────────
        errors = []

        if not name:
            errors.append("Asset name is required.")
        elif len(name) > 120:
            errors.append("Asset name must be 120 characters or fewer.")

        if not category or category not in ASSET_CATEGORIES:
            errors.append("Please select a valid category.")

        if interval < 1 or interval > 120:
            errors.append("Maintenance interval must be between 1 and 120 months.")

        if errors:
            for err in errors:
                flash(err, "danger")
            # Re-render the form with the previously entered values.
            return render_template(
                "add_asset.html",
                categories=ASSET_CATEGORIES,
                form_data=request.form,
            )

        # ── Persist to database ──────────────────────────────
        asset = Asset(
            name=name,
            category=category,
            purchase_date=purchase_date,
            last_maintenance_date=last_maintenance_date,
            maintenance_interval_months=interval,
            notes=notes or None,
        )
        db.session.add(asset)
        db.session.commit()

        flash(f'Asset "{asset.name}" added successfully!', "success")
        return redirect(url_for("main.assets"))

    # GET — render the empty form.
    return render_template(
        "add_asset.html",
        categories=ASSET_CATEGORIES,
        form_data={},
    )


# ──────────────────────────────────────────────────────────
# Route: Add maintenance record  GET + POST /assets/<id>/maintenance/add
# ──────────────────────────────────────────────────────────

@main.route("/assets/<int:asset_id>/maintenance/add", methods=["GET", "POST"])
def add_maintenance(asset_id: int):
    """
    GET  — Display the Add Maintenance Record form for the given asset.
    POST — Validate and save the record, then redirect to the asset detail page.
    """
    asset = db.get_or_404(Asset, asset_id)

    if request.method == "POST":
        maintenance_date = _parse_date(
            request.form.get("maintenance_date", "")
        )
        service_type = request.form.get("service_type", "").strip()
        service_provider = request.form.get("service_provider", "").strip()
        notes = request.form.get("notes", "").strip()

        # Cost is optional — allow blank entries.
        cost_str = request.form.get("cost", "").strip()
        try:
            cost = float(cost_str) if cost_str else None
        except ValueError:
            cost = None

        # ── Server-side validation ───────────────────────────
        errors = []

        if not maintenance_date:
            errors.append("Maintenance date is required.")
        elif maintenance_date > date.today():
            errors.append("Maintenance date cannot be in the future.")

        if not service_type:
            errors.append("Service type is required.")
        elif len(service_type) > 120:
            errors.append("Service type must be 120 characters or fewer.")

        if cost is not None and cost < 0:
            errors.append("Cost cannot be negative.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template(
                "add_maintenance.html",
                asset=asset,
                form_data=request.form,
            )

        # ── Persist record ───────────────────────────────────
        record = MaintenanceRecord(
            asset_id=asset.id,
            maintenance_date=maintenance_date,
            service_type=service_type,
            cost=cost,
            service_provider=service_provider or None,
            notes=notes or None,
        )
        db.session.add(record)

        # Update the asset's last_maintenance_date if this record is newer.
        if (
            asset.last_maintenance_date is None
            or maintenance_date > asset.last_maintenance_date
        ):
            asset.last_maintenance_date = maintenance_date

        db.session.commit()

        flash("Maintenance record added successfully!", "success")
        return redirect(url_for("main.asset_detail", asset_id=asset.id))

    # GET — render the empty form.
    return render_template(
        "add_maintenance.html",
        asset=asset,
        form_data={},
    )
