from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

from flask import Flask, flash, redirect, render_template, request, send_file, url_for


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = Path(os.getenv("DEBIT_TRACKER_DB", BASE_DIR / "debit_tracker_demo.sqlite3"))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "portfolio-demo-key")


RESERVE_RULES: dict[str, list[dict[str, str]]] = {
    "WRIA 48 - Twisp River Single Domestic and Stockwater Reserve": [
        {"rule": "Only Indoor Domestic", "quantity": "30"},
        {"rule": "Only Outdoor Domestic", "quantity": "650"},
        {"rule": "Indoor + Outdoor Domestic", "quantity": "680"},
        {"rule": "Indoor + Outdoor + Stockwater", "quantity": "710"},
        {"rule": "No Debit", "quantity": "0"},
    ],
    "WRIA 48 - Chewuch River Single Domestic and Stockwater Reserve": [
        {"rule": "Only Indoor Domestic", "quantity": "30"},
        {"rule": "Only Outdoor Domestic", "quantity": "650"},
        {"rule": "Indoor + Outdoor Domestic", "quantity": "680"},
        {"rule": "Indoor + Outdoor + Stockwater", "quantity": "710"},
        {"rule": "No Debit", "quantity": "0"},
    ],
    "WRIA 48 - Middle Methow Single Domestic and Stockwater Reserve": [
        {"rule": "Only Indoor Domestic", "quantity": "30"},
        {"rule": "Only Outdoor Domestic", "quantity": "650"},
        {"rule": "Indoor + Outdoor Domestic", "quantity": "680"},
        {"rule": "Indoor + Outdoor + Stockwater", "quantity": "710"},
        {"rule": "No Debit", "quantity": "0"},
    ],
    "WRIA 48 - Lower Methow Single Domestic and Stockwater Reserve": [
        {"rule": "Only Indoor Domestic", "quantity": "30"},
        {"rule": "Only Outdoor Domestic", "quantity": "650"},
        {"rule": "Indoor + Outdoor Domestic", "quantity": "680"},
        {"rule": "Indoor + Outdoor + Stockwater", "quantity": "710"},
        {"rule": "No Debit", "quantity": "0"},
    ],
    "Bonaparte-Johnson (Middle Okanogan) - 90.94 Future Consumptive Use Offsets": [
        {"rule": "Only Indoor Domestic", "quantity": "15"},
        {"rule": "Only Outdoor Domestic", "quantity": "299"},
        {"rule": "Indoor + Outdoor", "quantity": "314"},
        {"rule": "No Debit", "quantity": "0"},
    ],
    "Similkameen - 90.94 Future Consumptive Use Offsets": [
        {"rule": "Only Indoor Domestic", "quantity": "15"},
        {"rule": "Only Outdoor Domestic", "quantity": "299"},
        {"rule": "Indoor + Outdoor", "quantity": "314"},
        {"rule": "No Debit", "quantity": "0"},
    ],
    "WRIA 49 Overall 2018-2038 Future Consumptive Use Offsets (90.94)": [
        {"rule": "Indoor + Outdoor Domestic", "quantity": "314"},
        {"rule": "No Debit", "quantity": "0"},
    ],
    "Loup Loup-Swamp (Lower Okanogan) - 90.94 Future Consumptive Use Offsets": [
        {"rule": "Only Indoor Domestic", "quantity": "15"},
        {"rule": "Only Outdoor Domestic", "quantity": "299"},
        {"rule": "Indoor + Outdoor", "quantity": "314"},
        {"rule": "No Debit", "quantity": "0"},
    ],
    "WRIA 48 - Methow Headwaters Single Domestic and Stockwater Reserve": [
        {"rule": "Only Indoor Domestic", "quantity": "30"},
        {"rule": "Only Outdoor Domestic", "quantity": "650"},
        {"rule": "Indoor + Outdoor Domestic", "quantity": "680"},
        {"rule": "Indoor + Outdoor + Stockwater", "quantity": "710"},
        {"rule": "No Debit", "quantity": "0"},
    ],
    "Antoine-Whitestone (Upper Okanogan) - 90.94 Future Consumptive Use Offsets": [
        {"rule": "Only Indoor Domestic", "quantity": "15"},
        {"rule": "Only Outdoor Domestic", "quantity": "299"},
        {"rule": "Indoor + Outdoor", "quantity": "314"},
        {"rule": "No Debit", "quantity": "0"},
    ],
    "Salmon Creek - 90.94 Future Consumptive Use Offsets": [
        {"rule": "Only Indoor Domestic", "quantity": "15"},
        {"rule": "Only Outdoor Domestic", "quantity": "299"},
        {"rule": "Indoor + Outdoor", "quantity": "314"},
        {"rule": "No Debit", "quantity": "0"},
    ],
    "WRIA 48 - Upper Methow Single Domestic and Stockwater Reserve": [
        {"rule": "Only Indoor Domestic", "quantity": "30"},
        {"rule": "Only Outdoor Domestic", "quantity": "650"},
        {"rule": "Indoor + Outdoor Domestic", "quantity": "680"},
        {"rule": "Indoor + Outdoor + Stockwater", "quantity": "710"},
        {"rule": "No Debit", "quantity": "0"},
    ],
}

BASINS = {
    "WRIA 48 - Twisp River Single Domestic and Stockwater Reserve": "Twisp River",
    "WRIA 48 - Chewuch River Single Domestic and Stockwater Reserve": "Chewuch River",
    "WRIA 48 - Middle Methow Single Domestic and Stockwater Reserve": "Middle Methow",
    "WRIA 48 - Lower Methow Single Domestic and Stockwater Reserve": "Lower Methow",
    "WRIA 48 - Methow Headwaters Single Domestic and Stockwater Reserve": "Methow Headwaters",
    "WRIA 48 - Upper Methow Single Domestic and Stockwater Reserve": "Upper Methow",
    "Bonaparte-Johnson (Middle Okanogan) - 90.94 Future Consumptive Use Offsets": "Middle Okanogan",
    "Similkameen - 90.94 Future Consumptive Use Offsets": "Similkameen",
    "WRIA 49 Overall 2018-2038 Future Consumptive Use Offsets (90.94)": "WRIA 49",
    "Loup Loup-Swamp (Lower Okanogan) - 90.94 Future Consumptive Use Offsets": "Lower Okanogan",
    "Antoine-Whitestone (Upper Okanogan) - 90.94 Future Consumptive Use Offsets": "Upper Okanogan",
    "Salmon Creek - 90.94 Future Consumptive Use Offsets": "Salmon Creek",
}

FIELDS = [
    "parcel_number", "reserve", "rule", "quantity", "basin", "debit_type",
    "water_source", "irrigation", "connection_number", "building_type",
    "permit_number", "permit_date", "permit_type", "septic", "number_of_wells",
    "well_id", "well_type", "irrigation_district", "cofo_date", "notes",
]


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS debits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parcel_number TEXT NOT NULL,
                reserve TEXT NOT NULL,
                rule TEXT,
                quantity REAL NOT NULL DEFAULT 0,
                basin TEXT,
                debit_type TEXT DEFAULT 'Exempt',
                water_source TEXT,
                irrigation TEXT,
                connection_number INTEGER,
                building_type TEXT,
                permit_number TEXT,
                permit_date TEXT,
                permit_type TEXT,
                septic TEXT,
                number_of_wells INTEGER,
                well_id TEXT,
                well_type TEXT,
                irrigation_district TEXT,
                cofo_date TEXT,
                notes TEXT
            )
            """
        )
        count = conn.execute("SELECT COUNT(*) FROM debits").fetchone()[0]
        if count == 0:
            seed_demo_data(conn)


def seed_demo_data(conn: sqlite3.Connection) -> None:
    sample_rows = [
        ("3322140011", "WRIA 48 - Twisp River Single Domestic and Stockwater Reserve", "Indoor + Outdoor Domestic", 680, "Twisp River", "Exempt", "Private well", "No", 1, "Single Family Residential", "BP-2025-101", "2025-04-11", "SFR - Single Family Residential", "Yes", 1, "WELL-1032", "Domestic", "", "2025-05-01", "Demo record based on county planning workflow."),
        ("3421050042", "Bonaparte-Johnson (Middle Okanogan) - 90.94 Future Consumptive Use Offsets", "Only Indoor Domestic", 15, "Middle Okanogan", "Exempt", "Private well", "No", 1, "Single Family Residential", "BP-2025-118", "2025-05-20", "SFR - Single Family Residential", "Yes", 1, "WELL-2044", "Domestic", "", "2025-06-02", "Small indoor domestic debit."),
        ("3024190099", "WRIA 48 - Lower Methow Single Domestic and Stockwater Reserve", "Indoor + Outdoor + Stockwater", 710, "Lower Methow", "Exempt", "Private well", "Yes", 1, "Single Family Residential", "BP-2025-126", "2025-06-13", "SFR - Single Family Residential", "Yes", 1, "WELL-3309", "Domestic/stock", "", "2025-07-01", "Includes stockwater use."),
    ]
    conn.executemany(
        """
        INSERT INTO debits (
            parcel_number, reserve, rule, quantity, basin, debit_type, water_source,
            irrigation, connection_number, building_type, permit_number, permit_date,
            permit_type, septic, number_of_wells, well_id, well_type,
            irrigation_district, cofo_date, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        sample_rows,
    )


def row_from_form() -> dict[str, Any]:
    data = {field: request.form.get(field, "").strip() for field in FIELDS}
    data["quantity"] = float(data["quantity"] or 0)
    data["connection_number"] = int(data["connection_number"] or 0)
    data["number_of_wells"] = int(data["number_of_wells"] or 0)
    data["debit_type"] = data["debit_type"] or "Exempt"
    return data


@app.before_request
def ensure_database() -> None:
    init_db()


@app.route("/")
def index():
    search_query = request.args.get("search", "").strip()
    params: list[Any] = []
    where = ""
    if search_query:
        where = "WHERE parcel_number LIKE ? OR reserve LIKE ? OR basin LIKE ?"
        pattern = f"%{search_query}%"
        params = [pattern, pattern, pattern]

    with get_db() as conn:
        records = conn.execute(
            f"""
            SELECT id, parcel_number, quantity, reserve, rule, basin
            FROM debits
            {where}
            ORDER BY id DESC
            """,
            params,
        ).fetchall()

    return render_template("index.html", records=records, search_query=search_query)


@app.route("/new")
def new():
    return render_template("form.html", row=None, reserve_rules=RESERVE_RULES, basins=BASINS)


@app.route("/edit/<int:record_id>")
def edit(record_id: int):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM debits WHERE id = ?", (record_id,)).fetchone()
    if row is None:
        flash("Record not found.", "warning")
        return redirect(url_for("index"))
    return render_template("form.html", row=row, reserve_rules=RESERVE_RULES, basins=BASINS)


@app.route("/submit", methods=["POST"])
def submit():
    data = row_from_form()
    placeholders = ", ".join("?" for _ in FIELDS)
    columns = ", ".join(FIELDS)
    with get_db() as conn:
        conn.execute(
            f"INSERT INTO debits ({columns}) VALUES ({placeholders})",
            [data[field] for field in FIELDS],
        )
    flash("Debit record added.", "success")
    return redirect(url_for("index"))


@app.route("/update/<int:record_id>", methods=["POST"])
def update(record_id: int):
    data = row_from_form()
    assignments = ", ".join(f"{field} = ?" for field in FIELDS)
    with get_db() as conn:
        conn.execute(
            f"UPDATE debits SET {assignments} WHERE id = ?",
            [data[field] for field in FIELDS] + [record_id],
        )
    flash("Debit record updated.", "success")
    return redirect(url_for("index"))


@app.route("/delete/<int:record_id>", methods=["POST"])
def delete(record_id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM debits WHERE id = ?", (record_id,))
    flash("Debit record deleted.", "success")
    return redirect(url_for("index"))


@app.route("/report")
def report():
    from report import build_capacity_report

    output_path = BASE_DIR / "reports" / "Consumptive_Use_Offset_Report_Demo.pdf"
    with get_db() as conn:
        rows = conn.execute(
            "SELECT reserve, SUM(quantity) AS used_gpd FROM debits GROUP BY reserve ORDER BY reserve"
        ).fetchall()
    build_capacity_report(rows, output_path)
    return send_file(output_path, as_attachment=True)


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)
