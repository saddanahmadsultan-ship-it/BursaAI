from __future__ import annotations

import hashlib
import json
import os
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

from Research.candidate import utc_now_iso
from Research.result import ResearchResult


class ResultStoreError(RuntimeError):
    pass


class ResearchResultStore:
    """
    Persistent store untuk keputusan research.

    Struktur:
    ResearchResults/
      manifest.json
      results/
      by_experiment/
    """

    def __init__(self, base_dir: str | Path = "ResearchResults") -> None:
        self.base_dir = Path(base_dir)
        self.results_dir = self.base_dir / "results"
        self.by_experiment_dir = self.base_dir / "by_experiment"

        for path in (
            self.base_dir,
            self.results_dir,
            self.by_experiment_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)

        self.manifest_path = self.base_dir / "manifest.json"
        self._lock = threading.RLock()

        if not self.manifest_path.exists():
            self._write_manifest(
                {
                    "schema_version": 1,
                    "updated_at": utc_now_iso(),
                    "results": {},
                }
            )

    def _result_path(self, result_id: str) -> Path:
        return self.results_dir / f"{result_id}.json"

    def _experiment_index_path(self, experiment_id: str) -> Path:
        return self.by_experiment_dir / f"{experiment_id}.json"

    @staticmethod
    def _sha256(payload: bytes) -> str:
        return hashlib.sha256(payload).hexdigest()

    def _read_manifest(self) -> Dict[str, Any]:
        try:
            return json.loads(
                self.manifest_path.read_text(encoding="utf-8")
            )
        except Exception as exc:
            raise ResultStoreError(
                f"Manifest result store rosak: {exc}"
            ) from exc

    def _write_manifest(self, data: Dict[str, Any]) -> None:
        data["updated_at"] = utc_now_iso()
        tmp = self.manifest_path.with_suffix(
            f".{threading.get_ident()}.json.tmp"
        )

        payload = json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )

        with open(tmp, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(tmp, self.manifest_path)

    def save(
        self,
        result: ResearchResult,
        *,
        overwrite: bool = False,
    ) -> Path:
        if not isinstance(result, ResearchResult):
            raise TypeError("result mesti ResearchResult.")

        with self._lock:
            path = self._result_path(result.result_id)

            if path.exists() and not overwrite:
                raise ResultStoreError(
                    f"Result sudah wujud: {result.result_id}"
                )

            data = result.to_dict()
            payload = json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            ).encode("utf-8")

            tmp = path.with_suffix(
                f".{threading.get_ident()}.json.tmp"
            )

            with open(tmp, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())

            os.replace(tmp, path)

            checksum = self._sha256(payload)

            manifest = self._read_manifest()
            manifest["results"][result.result_id] = {
                "result_id": result.result_id,
                "experiment_id": result.experiment_id,
                "candidate_id": result.candidate_id,
                "candidate_hash": result.candidate_hash,
                "successful": result.successful,
                "final_score": result.metrics.final_score,
                "created_at": result.created_at,
                "checksum": checksum,
                "file": f"results/{result.result_id}.json",
            }

            self._write_manifest(manifest)
            self._update_experiment_index(result)

            return path

    def load(
        self,
        result_id: str,
        *,
        verify_checksum: bool = True,
    ) -> ResearchResult:
        path = self._result_path(result_id)

        if not path.exists():
            raise FileNotFoundError(
                f"Research result tidak ditemui: {result_id}"
            )

        payload = path.read_bytes()

        if verify_checksum:
            manifest = self._read_manifest()
            entry = manifest.get("results", {}).get(result_id)

            if not entry:
                raise ResultStoreError(
                    "Result tiada dalam manifest."
                )

            actual = self._sha256(payload)
            expected = entry.get("checksum")

            if actual != expected:
                raise ResultStoreError(
                    "Checksum research result tidak sepadan."
                )

        data = json.loads(payload.decode("utf-8"))

        return ResearchResult.from_dict(data)

    def list(
        self,
        experiment_id: Optional[str] = None,
        successful: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        with self._lock:
            manifest = self._read_manifest()
            items = list(
                manifest.get("results", {}).values()
            )

        if experiment_id is not None:
            items = [
                item
                for item in items
                if item.get("experiment_id") == experiment_id
            ]

        if successful is not None:
            items = [
                item
                for item in items
                if bool(item.get("successful")) is successful
            ]

        return sorted(
            items,
            key=lambda item: item.get("created_at", ""),
            reverse=True,
        )

    def best_result(
        self,
        experiment_id: str,
    ) -> Optional[ResearchResult]:
        items = self.list(
            experiment_id=experiment_id,
            successful=True,
        )

        if not items:
            return None

        best_entry = max(
            items,
            key=lambda item: float(
                item.get("final_score", 0.0)
            ),
        )

        return self.load(best_entry["result_id"])

    def delete(self, result_id: str) -> bool:
        path = self._result_path(result_id)
        existed = path.exists()

        if path.exists():
            path.unlink()

        manifest = self._read_manifest()
        entry = manifest.get("results", {}).pop(
            result_id,
            None,
        )

        self._write_manifest(manifest)

        if entry:
            self._remove_from_experiment_index(
                entry["experiment_id"],
                result_id,
            )

        return existed

    def _update_experiment_index(
        self,
        result: ResearchResult,
    ) -> None:
        path = self._experiment_index_path(
            result.experiment_id
        )

        if path.exists():
            data = json.loads(
                path.read_text(encoding="utf-8")
            )
        else:
            data = {
                "experiment_id": result.experiment_id,
                "updated_at": utc_now_iso(),
                "result_ids": [],
            }

        if result.result_id not in data["result_ids"]:
            data["result_ids"].append(result.result_id)

        data["updated_at"] = utc_now_iso()

        path.write_text(
            json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

    def _remove_from_experiment_index(
        self,
        experiment_id: str,
        result_id: str,
    ) -> None:
        path = self._experiment_index_path(
            experiment_id
        )

        if not path.exists():
            return

        data = json.loads(
            path.read_text(encoding="utf-8")
        )

        data["result_ids"] = [
            item
            for item in data.get("result_ids", [])
            if item != result_id
        ]

        data["updated_at"] = utc_now_iso()

        path.write_text(
            json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
