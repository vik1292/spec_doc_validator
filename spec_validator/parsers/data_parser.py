from pathlib import Path

import pandas as pd
from pydantic import BaseModel

MAX_SAMPLE_ROWS = 20
MAX_UNIQUE_VALUES = 20


class DataSample(BaseModel):
    file_name: str
    columns: list[str]
    dtypes: dict[str, str]
    row_count: int
    null_counts: dict[str, int]
    sample_rows: list[dict]
    value_samples: dict[str, list]


class DataFileParser:
    def parse(self, path: str) -> DataSample:
        p = Path(path)
        suffix = p.suffix.lower()
        if suffix == ".csv":
            df = self._parse_csv(path)
        elif suffix in (".xlsx", ".xls"):
            df = self._parse_excel(path)
        else:
            raise ValueError(f"Unsupported data file format: {suffix}")
        return self._dataframe_to_sample(df, p.name)

    def _parse_csv(self, path: str) -> pd.DataFrame:
        return pd.read_csv(path, dtype=str, keep_default_na=False, na_values=[""])

    def _parse_excel(self, path: str) -> pd.DataFrame:
        return pd.read_excel(path, dtype=str, keep_default_na=False, na_values=[""])

    def _dataframe_to_sample(self, df: pd.DataFrame, file_name: str) -> DataSample:
        columns = list(df.columns)
        dtypes = {col: str(df[col].dtype) for col in columns}
        row_count = len(df)
        null_counts = {col: int(df[col].isna().sum()) for col in columns}

        sample_rows = df.head(MAX_SAMPLE_ROWS).to_dict(orient="records")
        # Ensure all values are strings for JSON serialisation
        sample_rows = [
            {k: ("" if pd.isna(v) else str(v)) for k, v in row.items()}
            for row in sample_rows
        ]

        value_samples: dict[str, list] = {}
        for col in columns:
            unique_vals = df[col].dropna().unique().tolist()
            value_samples[col] = [str(v) for v in unique_vals[:MAX_UNIQUE_VALUES]]

        return DataSample(
            file_name=file_name,
            columns=columns,
            dtypes=dtypes,
            row_count=row_count,
            null_counts=null_counts,
            sample_rows=sample_rows,
            value_samples=value_samples,
        )
