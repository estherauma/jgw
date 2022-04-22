from typing import Dict

from pytz import country_names

FilterList = Dict[str, list[str]]


class BaseAnalytics:
    def __init__(self) -> None:
        self.export_csv_name = "export.csv"

    def get_dataframe(self):
        return self.df

    def total_items(self):
        return len(self.df)

    def get_columns(self):
        return list(self.df.columns)

    def export_csv(self):
        self.df.to_csv(self.export_csv_name)

    def filter_by_destination(self, destination: list[str], df=None):
        _df = df if df is not None else self.get_dataframe()
        destination = [country_names.get(i).lower() for i in destination.split(",")]
        _routes = _df["route"].astype("str").str.lower()
        mask = _routes.str.endswith(tuple(destination))
        return _df.loc[mask]

    def filter_data(self, filters: FilterList = None):
        filter_map = {"destination": self.filter_by_destination}
        _df = None or self.df.copy()
        if bool(filters):
            for field, value in filters.items():
                filter = filter_map.get(field)
                if filter is not None:
                    _df = filter(value, _df)
        return _df

    def get_count(self, field: str, df=None):
        _df = df.copy() if df is not None else self.df.copy()
        return _df[field].value_counts().to_dict()
