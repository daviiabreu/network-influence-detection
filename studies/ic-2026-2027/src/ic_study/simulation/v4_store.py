"""Private append-only records and immutable numerical checkpoints outside Git."""

from __future__ import annotations

import hashlib
import json
import os
import time
from collections.abc import Iterator
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from pathlib import Path

import numpy as np

from ic_study.models.anchored_panel import Floats

DEFAULT_SEALED = Path.home() / ".local/state/research-workbench/sealed-v4-gate"


class SealedStore:
    def __init__(self, root: Path) -> None:
        resolved = root.resolve()
        if root.is_symlink() or any(
            (p / ".git").exists() for p in (resolved, *resolved.parents)
        ):
            raise ValueError("Sealed data must be outside every checkout")
        if resolved.is_relative_to(DEFAULT_SEALED.resolve()):
            DEFAULT_SEALED.mkdir(mode=0o700, parents=True, exist_ok=True)
            if DEFAULT_SEALED.stat().st_mode & 0o077:
                raise ValueError("Sealed root must have mode 0700")
        resolved.mkdir(mode=0o700, parents=True, exist_ok=True)
        if resolved.stat().st_mode & 0o077:
            raise ValueError("Sealed directory must have mode 0700")
        self.root = resolved

    def _path(self, key: str, suffix: str) -> Path:
        if not key or any(
            c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
            for c in key
        ):
            raise ValueError("Invalid checkpoint identifier")
        path = self.root / (key + suffix)
        if path.is_symlink():
            raise ValueError("Symlink inside sealed store")
        return path

    def log(self, action: str, key: str) -> None:
        self.append(
            "access",
            {
                "action": action,
                "key": key,
                "time_ns": time.time_ns(),
                "pid": os.getpid(),
            },
        )

    def _mutable(self) -> None:
        if (self.root / "seal.json").exists():
            raise ValueError("Scientific output is already sealed")

    def append(self, stream: str, record: dict[str, object]) -> None:
        if stream != "access":
            self._mutable()
        data = (json.dumps(record, sort_keys=True, allow_nan=False) + "\n").encode()
        descriptor = os.open(
            self._path(stream, ".jsonl"),
            os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW,
            0o600,
        )
        with os.fdopen(descriptor, "ab") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())

    def put_array(self, key: str, values: Floats) -> None:
        path = self._path(key, ".npy")
        if path.exists():
            raise FileExistsError("Immutable checkpoint exists")
        self._mutable()
        temporary = self._path(key + f".{os.getpid()}.partial", ".npy")
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                np.save(handle, values, allow_pickle=False)
                handle.flush()
                os.fsync(handle.fileno())
            os.link(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)
        self.log("write-array", key)

    def _verify(self, path: Path) -> None:
        seal = self.root / "seal.json"
        if seal.exists():
            record = json.loads(seal.read_bytes())
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            if record["files"].get(path.name) != actual:
                raise ValueError("Sealed content digest mismatch")

    def get_array(self, key: str) -> Floats | None:
        path = self._path(key, ".npy")
        if not path.exists():
            return None
        self.log("read-array", key)
        self._verify(path)
        with path.open("rb") as handle:
            return np.asarray(np.load(handle, allow_pickle=False), dtype=np.float64)

    def put_json(self, key: str, record: dict[str, object]) -> None:
        self._mutable()
        data = (
            json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + "\n"
        ).encode()
        path = self._path(key, ".json")
        temporary = self._path(key + f".{os.getpid()}.partial", ".json")
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            os.link(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)
        self.log("write-json", key)

    def get_json(self, key: str) -> dict[str, object] | None:
        path = self._path(key, ".json")
        if not path.exists():
            return None
        self.log("read-json", key)
        self._verify(path)
        value: dict[str, object] = json.loads(path.read_bytes())
        return value

    def seal(self) -> None:
        files = {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(self.root.iterdir())
            if p.is_file() and p.name not in {"access.jsonl", "seal.json", "lock"}
        }
        digest = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()
        self.put_json("seal", {"sha256": digest, "files": files})

    @contextmanager
    def capture_output(self) -> Iterator[None]:
        self._mutable()
        descriptor = os.open(
            self._path("worker-output", ".log"),
            os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW,
            0o600,
        )
        with (
            os.fdopen(descriptor, "a") as handle,
            redirect_stdout(handle),
            redirect_stderr(handle),
        ):
            yield
