"""
app/models.py — SQLAlchemy database models.

Two tables:
  - Asset            : a household item/appliance owned by the user
  - MaintenanceRecord: a single service/repair event for one asset

Relationship: Asset 1 ──── N MaintenanceRecord
"""

from datetime import date, timedelta
from app import db


# ──────────────────────────────────────────────────────────
# Asset categories available in the Add Asset form dropdown
# ──────────────────────────────────────────────────────────
ASSET_CATEGORIES = [
    "Air Conditioner",
    "Washing Machine",
    "Refrigerator",
    "Water Purifier",
    "Car / Bike",
    "Inverter",
    "Laptop",
    "Other",
]


class Asset(db.Model):
    """
    Represents a household asset or appliance.

    The maintenance_status property is computed in Python from the stored
    dates and interval — not in Jinja templates or as raw SQL.
    """

    __tablename__ = "assets"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    purchase_date = db.Column(db.Date, nullable=True)
    last_maintenance_date = db.Column(db.Date, nullable=True)

    # How often the asset needs servicing (in months).
    maintenance_interval_months = db.Column(db.Integer, nullable=False, default=6)

    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.Date, nullable=False, default=date.today)

    # One-to-many relationship: one asset → many maintenance records.
    # cascade="all, delete-orphan" ensures records are deleted with their asset.
    maintenance_records = db.relationship(
        "MaintenanceRecord",
        backref="asset",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="MaintenanceRecord.maintenance_date.desc()",
    )

    # ── Computed properties ──────────────────────────────────

    @property
    def next_maintenance_date(self) -> date | None:
        """
        Calculate the date when the next service is due.
        Returns None if last_maintenance_date has not been recorded yet.
        """
        if not self.last_maintenance_date:
            return None
        # Approximate a month as 30 days to avoid calendar-month arithmetic issues.
        days = self.maintenance_interval_months * 30
        return self.last_maintenance_date + timedelta(days=days)

    @property
    def maintenance_status(self) -> str:
        """
        Determine maintenance status based on how close the next service date is.

        Rules:
          - No last_maintenance_date recorded  → 'Overdue'
          - Next service date < today          → 'Overdue'
          - Next service date within 30 days   → 'Due Soon'
          - Otherwise                          → 'Up to Date'
        """
        next_date = self.next_maintenance_date

        if not next_date:
            return "Overdue"

        today = date.today()
        days_remaining = (next_date - today).days

        if days_remaining < 0:
            return "Overdue"
        elif days_remaining <= 30:
            return "Due Soon"
        else:
            return "Up to Date"

    @property
    def status_badge_class(self) -> str:
        """
        Return the Bootstrap badge colour class matching the maintenance status.
        Keeps template logic minimal — templates just call asset.status_badge_class.
        """
        return {
            "Overdue": "bg-danger",
            "Due Soon": "bg-warning text-dark",
            "Up to Date": "bg-success",
        }.get(self.maintenance_status, "bg-secondary")

    def __repr__(self) -> str:
        return f"<Asset {self.id}: {self.name}>"


class MaintenanceRecord(db.Model):
    """
    A single maintenance/service event for an asset.
    """

    __tablename__ = "maintenance_records"

    id = db.Column(db.Integer, primary_key=True)

    # Foreign key linking back to the Asset table.
    asset_id = db.Column(
        db.Integer, db.ForeignKey("assets.id"), nullable=False
    )

    maintenance_date = db.Column(db.Date, nullable=False)
    service_type = db.Column(db.String(120), nullable=False)
    cost = db.Column(db.Numeric(10, 2), nullable=True)       # stored as decimal
    service_provider = db.Column(db.String(120), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.Date, nullable=False, default=date.today)

    def __repr__(self) -> str:
        return f"<MaintenanceRecord {self.id} for Asset {self.asset_id}>"
