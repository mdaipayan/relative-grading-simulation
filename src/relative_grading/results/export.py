"""Export module for multi-tab publication Excel workbooks and archival CSVs."""

from pathlib import Path
from typing import Dict
import pandas as pd


def export_results_to_excel(
    summaries: Dict[str, pd.DataFrame],
    output_excel_path: str,
) -> None:
    """Export summary tables into a clean, formatted multi-tab Excel workbook.

    Parameters
    ----------
    summaries : Dict[str, pd.DataFrame]
        Map of sheet name -> dataframe.
    output_excel_path : str
        Target Excel filepath.
    """
    path = Path(output_excel_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(str(path), engine="openpyxl") as writer:
        for sheet_name, df in summaries.items():
            # Clean sheet name to max 31 chars per Excel spec
            clean_name = sheet_name[:31]
            df.to_excel(writer, sheet_name=clean_name, index=False)
