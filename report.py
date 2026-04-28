from __future__ import annotations

from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

CAPACITY_CFS = {
    "WRIA 48 - Twisp River Single Domestic and Stockwater Reserve": 2.0,
    "WRIA 48 - Chewuch River Single Domestic and Stockwater Reserve": 2.0,
    "WRIA 48 - Middle Methow Single Domestic and Stockwater Reserve": 2.0,
    "WRIA 48 - Lower Methow Single Domestic and Stockwater Reserve": 2.0,
    "Bonaparte-Johnson (Middle Okanogan) - 90.94 Future Consumptive Use Offsets": 0.116,
    "Similkameen - 90.94 Future Consumptive Use Offsets": 0.014,
    "WRIA 49 Overall 2018-2038 Future Consumptive Use Offsets (90.94)": 0.281,
    "Loup Loup-Swamp (Lower Okanogan) - 90.94 Future Consumptive Use Offsets": 0.0515,
    "WRIA 48 - Methow Headwaters Single Domestic and Stockwater Reserve": 2.0,
    "Antoine-Whitestone (Upper Okanogan) - 90.94 Future Consumptive Use Offsets": 0.058,
    "Salmon Creek - 90.94 Future Consumptive Use Offsets": 0.016,
    "WRIA 48 - Upper Methow Single Domestic and Stockwater Reserve": 2.0,
}

GPD_TO_CFS = 1.54723e-7


def build_capacity_report(rows: Iterable, output_path: str | Path) -> Path:
    """Create a multi-page PDF capacity report from grouped debit rows."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with PdfPages(output_path) as pdf:
        for row in rows:
            reserve = str(row["reserve"]).strip()
            used_gpd = float(row["used_gpd"] or 0)
            capacity_cfs = CAPACITY_CFS.get(reserve)
            if capacity_cfs is None or capacity_cfs <= 0:
                continue

            used_cfs = used_gpd * GPD_TO_CFS
            chart_used_cfs = min(capacity_cfs, used_cfs)
            remaining_cfs = max(0.0, capacity_cfs - used_cfs)
            used_percent = (chart_used_cfs / capacity_cfs) * 100
            remaining_percent = 100 - used_percent

            fig = plt.figure(figsize=(10, 4))
            grid = fig.add_gridspec(1, 2, width_ratios=[1, 2.4])
            chart_axis = fig.add_subplot(grid[0, 0])
            text_axis = fig.add_subplot(grid[0, 1])

            values = [chart_used_cfs, remaining_cfs]
            wedges, _ = chart_axis.pie(
                values,
                labels=None,
                startangle=90,
                counterclock=False,
                wedgeprops={"edgecolor": "white", "linewidth": 1.5},
            )
            chart_axis.legend(wedges, ["Used", "Capacity Reserve"], loc="lower left", bbox_to_anchor=(-0.2, -0.15))
            chart_axis.axis("equal")

            for wedge, value in zip(wedges, values):
                if value <= 0:
                    continue
                angle = (wedge.theta2 - wedge.theta1) / 2 + wedge.theta1
                x = 0.6 * np.cos(np.deg2rad(angle))
                y = 0.6 * np.sin(np.deg2rad(angle))
                chart_axis.text(x, y, f"{(value / capacity_cfs) * 100:.1f}%", ha="center", va="center", fontweight="bold")

            text_axis.set_axis_off()
            fig.suptitle(reserve, fontsize=12, y=0.98)
            lines = [
                ("Total Capacity:", f"{capacity_cfs:.3f} CFS"),
                ("Used/Debited:", f"{used_cfs:.3f} CFS ({used_percent:.2f}%)"),
                ("Remaining:", f"{remaining_cfs:.3f} CFS ({remaining_percent:.2f}%)"),
            ]
            for index, (label, value) in enumerate(lines):
                y = 0.78 - (index * 0.20)
                text_axis.text(0.05, y, label, fontsize=11, fontweight="bold")
                text_axis.text(0.42, y, value, fontsize=11)

            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

    return output_path
