import pathlib

import pandas as pd

from tricount_extractor.models.registry import Registry


class RegistrySaver:
    def save(self, registry: Registry, folder: str) -> str:
        path = self.get_path(registry, folder)
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            for sheet_name, df in registry.to_dataframe().items():
                df.to_excel(writer, sheet_name=sheet_name, index=True)
        return str(path)

    def get_path(self, registry: Registry, folder: str) -> pathlib.Path:
        return pathlib.Path(folder) / f"{self._safe_filename(registry)}.xlsx"

    @staticmethod
    def _safe_filename(registry: Registry) -> str:
        safe_title = (
            "".join(c if c.isalnum() or c in " -_" else "_" for c in registry.title)
            .strip()
            .replace(" ", "_")
            .lower()
        )
        return f"{safe_title}_{registry.id}"
