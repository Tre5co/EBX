#!/usr/bin/env python3
"""scripts/safe_write.py — atomic write helper for tracked HTML/TS files.

Why this exists
---------------
Pass 9 surfaced a Windows ↔ Linux mount truncation bug: writes initiated from
the Linux sandbox occasionally land on the Windows side as truncated copies
(see README §2.12). Symptom: `wc -c` on the sandbox reports ~36KB for files
that are well over 1200 lines on the host. The root cause looks like the
Win → 9p mount flushing partial buffers when a sandbox-side editor closes the
fd between writes.

Mitigation: every sandbox-side write is staged in a sibling tempfile in the
same directory, fsync'd to disk, then renamed over the target with
`os.replace` (which is atomic on POSIX and on Windows ≥ Vista). The host sees
either the old file or the complete new file — never a partial one — and
there's no window where the editor process is holding the target fd open
mid-write.

Usage from a script::

    from scripts.safe_write import safe_write_text
    safe_write_text("index.html", new_contents)

Usage from the CLI::

    cat new_index.html | python -m scripts.safe_write index.html        # stdin
    python -m scripts.safe_write index.html ./staged/index.html          # copy

A `--verify` flag re-reads the destination after the rename and compares
bytes, so callers can fail loudly if the mount truncated despite the atomic
swap. This pairs with the `EBX_TAIL_SENTINEL`/IIFE-close build-integrity
check called out in README §4.
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path


def safe_write_bytes(target: str | os.PathLike[str], data: bytes, *, verify: bool = True) -> Path:
    """Atomically write ``data`` to ``target``.

    Returns the resolved Path to the written file.
    Raises ``IOError`` if ``verify=True`` and the post-write read-back differs.
    """
    target_path = Path(target).resolve()
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # Stage in the same directory so os.replace is a same-filesystem rename.
    fd, tmp_path = tempfile.mkstemp(
        prefix=f".{target_path.name}.",
        suffix=".tmp",
        dir=str(target_path.parent),
    )
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            try:
                os.fsync(f.fileno())
            except OSError:
                # fsync isn't supported on every filesystem (e.g. some 9p mounts).
                # The os.replace below is still atomic; we just lose the durability
                # guarantee, which is acceptable for dev-time HTML edits.
                pass
        os.replace(tmp_path, target_path)
    except Exception:
        # Clean up the staging file on any error.
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

    if verify:
        readback = target_path.read_bytes()
        if readback != data:
            raise IOError(
                f"safe_write verification failed for {target_path}: "
                f"wrote {len(data)} bytes, read back {len(readback)} bytes"
            )
    return target_path


def safe_write_text(
    target: str | os.PathLike[str],
    text: str,
    *,
    encoding: str = "utf-8",
    newline: str = "\n",
    verify: bool = True,
) -> Path:
    """Atomically write ``text`` to ``target`` using ``encoding``.

    ``newline`` is applied to embedded ``\n`` chars before encoding so callers
    can pin LF endings explicitly on a Windows host.
    """
    if newline != "\n":
        text = text.replace("\n", newline)
    return safe_write_bytes(target, text.encode(encoding), verify=verify)


def _main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("target", help="Path to write to")
    p.add_argument(
        "source",
        nargs="?",
        help="Path to read from. Omit to read stdin.",
    )
    p.add_argument(
        "--no-verify",
        action="store_true",
        help="Skip the post-write read-back check.",
    )
    args = p.parse_args(argv)

    if args.source:
        data = Path(args.source).read_bytes()
    else:
        data = sys.stdin.buffer.read()

    out = safe_write_bytes(args.target, data, verify=not args.no_verify)
    print(f"wrote {len(data)} bytes -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
