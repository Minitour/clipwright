#!/usr/bin/env python3
"""Compile a cast.yaml brief into a typed cast.ts file for Remotion, and
(optionally) emit a starter Character.tsx wrapper with the skill's default
circular avatar treatment baked in.

Reads a YAML mapping of character_id -> spec, validates each spec against
the known prop enums (data/prop_enums.json), and writes a TypeScript module
that exports a `cast` const typed as Record<CharacterId, CharacterSpec>.

Usage:
    # cast.ts only
    uv run --project <workspace-root> python skills/characters/scripts/scaffold_cast.py \\
        path/to/cast.yaml -o path/to/cast.ts

    # cast.ts plus a starter Character.tsx wrapper (won't overwrite if it exists)
    uv run --project <workspace-root> python skills/characters/scripts/scaffold_cast.py \\
        path/to/cast.yaml -o path/to/cast.ts --component path/to/Character.tsx

    # ...or force-overwrite an existing wrapper
    uv run --project <workspace-root> python skills/characters/scripts/scaffold_cast.py \\
        path/to/cast.yaml -o path/to/cast.ts --component path/to/Character.tsx --force

Exits non-zero with a clear error if validation fails.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

SKILL_ROOT = Path(__file__).resolve().parent.parent
PROP_ENUMS_PATH = SKILL_ROOT / "data" / "prop_enums.json"

HEX_COLOR_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


class ValidationError(Exception):
    """Raised when a cast.yaml entry fails validation."""


def load_prop_enums() -> dict[str, Any]:
    with PROP_ENUMS_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_color(value: Any, *, location: str) -> None:
    if isinstance(value, str):
        if not HEX_COLOR_RE.match(value):
            raise ValidationError(
                f"{location}: expected hex color (e.g. '#0F172A'), got {value!r}"
            )
        return
    if isinstance(value, dict) and "gradient" in value:
        gradient = value["gradient"]
        if not isinstance(gradient, dict):
            raise ValidationError(f"{location}.gradient: expected an object")
        for key in ("degree", "from", "to"):
            if key not in gradient:
                raise ValidationError(f"{location}.gradient: missing key {key!r}")
        if not isinstance(gradient["degree"], (int, float)):
            raise ValidationError(
                f"{location}.gradient.degree: expected number, got {gradient['degree']!r}"
            )
        validate_color(gradient["from"], location=f"{location}.gradient.from")
        validate_color(gradient["to"], location=f"{location}.gradient.to")
        return
    raise ValidationError(
        f"{location}: expected hex color string or {{gradient: {{degree, from, to}}}}, got {value!r}"
    )


def validate_spec(
    character_id: str, spec: dict[str, Any], prop_enums: dict[str, Any]
) -> None:
    if not isinstance(spec, dict):
        raise ValidationError(f"{character_id}: expected an object, got {type(spec).__name__}")

    library = spec.get("library")
    library_keys = sorted(k for k in prop_enums if not k.startswith("_"))
    if library not in library_keys:
        raise ValidationError(
            f"{character_id}.library: expected one of {library_keys}, got {library!r}"
        )

    library_enums = prop_enums[library]
    enum_keys = {k for k in library_enums if not k.startswith("_")}
    color_keys = set(library_enums.get("_color_props", []))
    passthrough_keys = set(library_enums.get("_passthrough_props", []))
    known_keys = enum_keys | color_keys | passthrough_keys | {"library"}

    for key, value in spec.items():
        location = f"{character_id}.{key}"

        if key == "library":
            continue
        if key in color_keys:
            validate_color(value, location=location)
            continue
        if key in passthrough_keys:
            continue
        if key in enum_keys:
            valid_values = library_enums[key]
            if value not in valid_values:
                hint = _typo_hint(value, valid_values)
                raise ValidationError(
                    f"{location}: {value!r} is not a known {library} {key} value.{hint}"
                )
            continue

        raise ValidationError(
            f"{location}: unknown prop for library {library!r}. "
            f"Known props: {sorted(known_keys - {'library'})}."
        )


def _typo_hint(value: Any, valid_values: list[str]) -> str:
    if not isinstance(value, str):
        return ""
    lower = value.lower()
    near = [v for v in valid_values if v.lower() == lower or v.lower().startswith(lower[:4])]
    if near:
        return f" Did you mean one of {near[:5]}?"
    return ""


def ts_literal(value: Any) -> str:
    """Render a Python value as a TypeScript literal expression."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace("'", "\\'")
        return f"'{escaped}'"
    if isinstance(value, list):
        return "[" + ", ".join(ts_literal(v) for v in value) + "]"
    if isinstance(value, dict):
        # Gradient sugar:
        #   YAML:  {gradient: {degree, from, to}}
        #   TS:    {degree, firstColor: from, secondColor: to}
        # The library's GradientType is a plain object literal type (not a class) using
        # `firstColor`/`secondColor` field names — we expose `from`/`to` in YAML for clarity.
        if set(value.keys()) == {"gradient"}:
            g = value["gradient"]
            parts = []
            if "type" in g:
                parts.append(f"type: {ts_literal(g['type'])}")
            parts.append(f"degree: {ts_literal(g['degree'])}")
            parts.append(f"firstColor: {ts_literal(g['from'])}")
            parts.append(f"secondColor: {ts_literal(g['to'])}")
            return "{ " + ", ".join(parts) + " }"
        entries = ", ".join(f"{_ts_key(k)}: {ts_literal(v)}" for k, v in value.items())
        return "{ " + entries + " }"
    raise ValidationError(f"Cannot render {type(value).__name__} as TypeScript literal: {value!r}")


_IDENT_RE = re.compile(r"^[A-Za-z_$][A-Za-z0-9_$]*$")


def _ts_key(key: str) -> str:
    if _IDENT_RE.match(key):
        return key
    escaped = key.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


def generate_ts(cast: dict[str, dict[str, Any]]) -> str:
    # react-peeps is the only supported library; validate_spec rejects anything else.
    lines: list[str] = []
    lines.append("// AUTO-GENERATED by skills/characters/scripts/scaffold_cast.py")
    lines.append("// Source: cast.yaml — edit the YAML, re-run the scaffolder.")
    lines.append("")
    # All names are imported as type-only — they're enum unions, not runtime values.
    # GradientType is NOT re-exported from the react-peeps package root, so we inline
    # an equivalent local type definition below rather than reaching into the deep path.
    lines.append(
        "import { type HairType, type FaceType, type AccessoryType, "
        "type FacialHairType, type BustPoseType, type StandingPoseType, "
        "type SittingPoseType } from 'react-peeps';"
    )
    lines.append("")
    # Mirrors react-peeps' internal GradientType (lib/peeps/types.d.ts); not re-exported.
    lines.append("type GradientType = {")
    lines.append("  type?: 'RadialGradient' | 'LinearGradient';")
    lines.append("  degree?: number;")
    lines.append("  firstColor: string;")
    lines.append("  secondColor: string;")
    lines.append("};")
    lines.append("")

    lines.append("export type CharacterSpec = {")
    lines.append("  library: 'react-peeps';")
    lines.append("  hair?: HairType;")
    lines.append("  face?: FaceType;")
    lines.append("  body?: BustPoseType | StandingPoseType | SittingPoseType;")
    lines.append("  accessory?: AccessoryType;")
    lines.append("  facialHair?: FacialHairType;")
    lines.append("  strokeColor?: string | GradientType;")
    lines.append("  backgroundColor?: string | GradientType;")
    lines.append("};")
    lines.append("")

    ids = list(cast.keys())
    id_union = " | ".join(f"'{i}'" for i in ids) if ids else "never"
    lines.append(f"export type CharacterId = {id_union};")
    lines.append("")

    lines.append("export const cast = {")
    for character_id, spec in cast.items():
        lines.append(f"  {_ts_key(character_id)}: {ts_literal(spec)},")
    lines.append("} as const satisfies Record<CharacterId, CharacterSpec>;")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Character.tsx wrapper — the canonical "house style" for cast members.
#
# Constants are intentionally inlined (not imported from a brand module) so
# the wrapper stands on its own and is trivially overridable per project by
# editing the top of the file. Defaults match [characters.peeps_style] in
# config.toml — keep these in sync when you change the config.
#
# Rendered via plain str.replace using @@NAME@@ sentinel placeholders so the
# TypeScript braces ({...}) and template literals (${...}) pass through
# verbatim. The sentinel form cannot appear naturally in TS code.
# ---------------------------------------------------------------------------
CHARACTER_TSX_TEMPLATE = '''\
import React from "react";
import Peep from "react-peeps";
import { cast, type CharacterId, type CharacterSpec } from "../cast";

type FaceOverride = NonNullable<CharacterSpec["face"]>;

// House style for react-peeps characters (from [characters.peeps_style] in
// the workspace config.toml). Override here to retheme the whole cast in one
// place — every <Character> across every scene picks up the change.
const CIRCLE_BG          = "@@CIRCLE_BG@@";
const CHARACTER_STROKE   = "@@CHARACTER_STROKE@@";
const CHARACTER_FILL     = "@@CHARACTER_FILL@@";
const BORDER_COLOR       = "@@BORDER_COLOR@@";
const BORDER_RATIO       = @@BORDER_RATIO@@;
const DROP_SHADOW        = "@@DROP_SHADOW@@";

type Props = {
  id: CharacterId;
  /** Diameter in pixels. The wrapper is square; the SVG fills it. */
  size?: number;
  style?: React.CSSProperties;
  /** Per-frame face override (Pattern 5 from skills/characters/rules/animation.md). */
  face?: FaceOverride;
};

// Renders a cast member by id, enclosed in a circular wrapper with the
// shared house-style colors + thin border + soft drop shadow. Per-character
// bg/stroke from cast.yaml are intentionally ignored so the cast reads as
// one set rather than independent illustrations.
export const Character: React.FC<Props> = ({ id, size = 380, style, face }) => {
  const spec = cast[id];
  if (spec.library !== "react-peeps") {
    // The characters skill currently supports react-peeps only.
    return null;
  }
  const { library: _library, backgroundColor: _bg, strokeColor: _stroke, ...peepProps } = spec;

  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: "50%",
        overflow: "hidden",
        background: CIRCLE_BG,
        border: `${Math.max(3, Math.round(size * BORDER_RATIO))}px solid ${BORDER_COLOR}`,
        boxShadow: DROP_SHADOW,
        position: "relative",
        ...style,
      }}
    >
      {/* SVG container is taller than wide so the bust fills the circle's
          width without aspect-ratio squashing; surplus height clips below. */}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: size * 0.06,
          width: "100%",
          height: size * 1.4,
        }}
      >
        <Peep
          {...peepProps}
          strokeColor={CHARACTER_STROKE}
          backgroundColor={CHARACTER_FILL}
          face={face ?? peepProps.face}
          style={{ width: "100%", height: "100%", display: "block" }}
        />
      </div>
    </div>
  );
};
'''


# Defaults baked into the wrapper template when --component is used. These
# mirror [characters.peeps_style] in config.toml; the template is rendered
# with these substitutions so each generated wrapper is self-contained.
PEEPS_STYLE_DEFAULTS = {
    "CIRCLE_BG": "#818CF8",
    "CHARACTER_STROKE": "#000000",
    "CHARACTER_FILL": "#FFFFFF",
    "BORDER_COLOR": "#FFFFFF",
    "BORDER_RATIO": "0.012",
    "DROP_SHADOW": "0 14px 32px rgba(0, 0, 0, 0.45), 0 0 24px rgba(129, 140, 248, 0.18)",
}


def render_character_wrapper() -> str:
    out = CHARACTER_TSX_TEMPLATE
    for key, value in PEEPS_STYLE_DEFAULTS.items():
        out = out.replace(f"@@{key}@@", value)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("cast_yaml", type=Path, help="Path to cast.yaml")
    parser.add_argument(
        "-o", "--output", type=Path, required=True, help="Path to write cast.ts"
    )
    parser.add_argument(
        "--component",
        type=Path,
        default=None,
        help=(
            "Optional path to write a starter Character.tsx wrapper with the skill's"
            " default circular avatar treatment. Refuses to overwrite an existing file"
            " unless --force is also passed."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="With --component, overwrite an existing wrapper file.",
    )
    args = parser.parse_args(argv)

    if not args.cast_yaml.is_file():
        print(f"error: cast file not found: {args.cast_yaml}", file=sys.stderr)
        return 2

    with args.cast_yaml.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    if raw is None:
        print(f"error: {args.cast_yaml} is empty", file=sys.stderr)
        return 2
    if not isinstance(raw, dict):
        print(
            f"error: {args.cast_yaml} must be a mapping of character_id -> spec at the top level",
            file=sys.stderr,
        )
        return 2

    prop_enums = load_prop_enums()
    try:
        for character_id, spec in raw.items():
            validate_spec(character_id, spec, prop_enums)
    except ValidationError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    ts_output = generate_ts(raw)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(ts_output, encoding="utf-8")
    print(f"wrote {args.output} ({len(raw)} character(s))")

    if args.component is not None:
        if args.component.exists() and not args.force:
            print(
                f"skipped {args.component}: file exists (use --force to overwrite)",
                file=sys.stderr,
            )
        else:
            args.component.parent.mkdir(parents=True, exist_ok=True)
            args.component.write_text(render_character_wrapper(), encoding="utf-8")
            print(f"wrote {args.component} (starter wrapper)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
