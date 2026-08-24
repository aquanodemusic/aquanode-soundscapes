#!/usr/bin/env python3
"""
Find duplicate / near-duplicate Vital presets between TWO folders
(folder1 and folder2) by comparing synth settings, ignoring metadata
and ignoring embedded audio (the 'sample' field and wavetable audio_file blobs).

Only cross-folder matches are considered (a file in folder1 can only match
a file in folder2, never another file within the same folder), and each
file can be part of at most one pair. Matched pairs are copied into
folder3 (created if needed) with a dup_00x_ prefix; unmatched files are
left untouched in their original folders.

Usage:
    python3 find_dupes_cross.py /path/to/folder1 /path/to/folder2 /path/to/folder3
    python3 find_dupes_cross.py folder1 folder2 folder3 --threshold 0.97 --out report.csv
"""
import json
import os
import sys
import glob
import argparse
import hashlib
from itertools import combinations

# Fields to ignore entirely - metadata, not sound-defining
IGNORE_TOP_LEVEL = {"author", "comments", "preset_name", "preset_style", "macro1", "macro2", "macro3", "macro4"}

# Keys inside "settings" that hold raw audio / are not meaningful "settings" to compare
IGNORE_SETTINGS_KEYS = {"sample"}  # the loaded audio sample itself

FLOAT_ROUND = 4  # tolerance for float comparisons


def strip_wavetable_audio(wavetables):
    """Keep wavetable structure/settings but drop the raw audio_file blobs,
    since those represent imported audio data rather than a 'setting'."""
    if not isinstance(wavetables, list):
        return wavetables
    cleaned = []
    for wt in wavetables:
        if not isinstance(wt, dict):
            cleaned.append(wt)
            continue
        wt2 = dict(wt)
        groups = wt2.get("groups")
        if isinstance(groups, list):
            new_groups = []
            for g in groups:
                if not isinstance(g, dict):
                    new_groups.append(g)
                    continue
                g2 = dict(g)
                comps = g2.get("components")
                if isinstance(comps, list):
                    new_comps = []
                    for c in comps:
                        if isinstance(c, dict):
                            c2 = {k: v for k, v in c.items() if k != "audio_file"}
                            new_comps.append(c2)
                        else:
                            new_comps.append(c)
                    g2["components"] = new_comps
                new_groups.append(g2)
            wt2["groups"] = new_groups
        cleaned.append(wt2)
    return cleaned


def normalize(value):
    """Recursively normalize a value for stable, tolerant comparison."""
    if isinstance(value, float):
        return round(value, FLOAT_ROUND)
    if isinstance(value, dict):
        return {k: normalize(v) for k, v in sorted(value.items())}
    if isinstance(value, list):
        return [normalize(v) for v in value]
    return value


def load_comparable_settings(path):
    """Return (settings_dict, wavetable_audio_hash, sample_present) for a preset file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    settings = data.get("settings", {})
    if not isinstance(settings, dict):
        settings = {}

    settings = {k: v for k, v in settings.items() if k not in IGNORE_SETTINGS_KEYS}

    # Wavetables: strip raw audio blobs but keep the rest (oscillator shape settings etc.)
    if "wavetables" in settings:
        settings["wavetables"] = strip_wavetable_audio(settings["wavetables"])

    settings = normalize(settings)

    sample_present = "sample" in (data.get("settings", {}) or {}) and bool(data["settings"]["sample"])

    return settings, sample_present


def flatten(d, prefix=""):
    """Flatten nested dict/list into {path: value} for per-key diffing."""
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            out.update(flatten(v, f"{prefix}.{k}" if prefix else k))
    elif isinstance(d, list):
        for i, v in enumerate(d):
            out.update(flatten(v, f"{prefix}[{i}]"))
    else:
        out[prefix] = d
    return out


def settings_hash(flat):
    """Stable hash of the flattened, normalized settings."""
    m = hashlib.sha256()
    for k in sorted(flat.keys()):
        m.update(k.encode("utf-8"))
        m.update(b"=")
        m.update(str(flat[k]).encode("utf-8"))
        m.update(b";")
    return m.hexdigest()


def similarity(flat_a, flat_b):
    """Fraction of shared keys whose values match, penalized for keys only on one side."""
    keys = set(flat_a.keys()) | set(flat_b.keys())
    if not keys:
        return 1.0
    matches = 0
    for k in keys:
        if flat_a.get(k, object()) == flat_b.get(k, object()):
            matches += 1
    return matches / len(keys)


def pair_up(remaining_a, remaining_b, flats, threshold):
    """Greedily pair files 1-to-1 by highest similarity, ONLY across the two
    given sets (one file from remaining_a with one file from remaining_b).
    No pairing within the same set. Returns (pairs, pair_scores) where pairs
    is a list of (a, b) tuples with a from remaining_a, b from remaining_b."""
    scored = []
    for a in remaining_a:
        for b in remaining_b:
            sim = similarity(flats[a], flats[b])
            if sim >= threshold:
                scored.append((sim, a, b))
    # Highest similarity first, so the strongest matches claim their partner first
    scored.sort(reverse=True)

    used = set()
    pairs = []
    pair_scores = {}
    for sim, a, b in scored:
        if a in used or b in used:
            continue
        used.add(a)
        used.add(b)
        pairs.append((a, b))
        pair_scores[(a, b)] = sim
    return pairs, pair_scores


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder1", help="First folder containing .vital preset files")
    ap.add_argument("folder2", help="Second folder containing .vital preset files")
    ap.add_argument("folder3", help="Destination folder for matched duplicate pairs (created if missing)")
    ap.add_argument("--threshold", type=float, default=0.97,
                     help="Similarity threshold (0-1) to consider two presets near-duplicates (default 0.97)")
    ap.add_argument("--out", default="dupe_report.csv", help="Output CSV report path")
    ap.add_argument("--pattern", default="*.vital", help="Glob pattern for preset files")
    ap.add_argument("--move", action="store_true",
                     help="Copy matched duplicate pairs into folder3, each prefixed with dup_001_, dup_002_, ... "
                          "(both files of a pair get the same prefix). Originals are left in place.")
    args = ap.parse_args()

    files1 = sorted(glob.glob(os.path.join(args.folder1, "**", args.pattern), recursive=True))
    files2 = sorted(glob.glob(os.path.join(args.folder2, "**", args.pattern), recursive=True))
    if not files1:
        print(f"No files matching {args.pattern} found in {args.folder1}")
        sys.exit(1)
    if not files2:
        print(f"No files matching {args.pattern} found in {args.folder2}")
        sys.exit(1)

    print(f"Found {len(files1)} files in folder1 and {len(files2)} files in folder2. Loading and normalizing...")

    flats = {}
    hashes = {}
    errors = []
    for path in files1 + files2:
        try:
            settings, _sample_present = load_comparable_settings(path)
            flat = flatten(settings)
            flats[path] = flat
            hashes[path] = settings_hash(flat)
        except Exception as e:
            errors.append((path, str(e)))

    if errors:
        print(f"\n{len(errors)} files failed to parse:")
        for p, e in errors[:20]:
            print(f"  {os.path.basename(p)}: {e}")

    paths1 = [p for p in files1 if p in flats]
    paths2 = [p for p in files2 if p in flats]
    print(f"Loaded {len(paths1)} files from folder1 and {len(paths2)} files from folder2 successfully.")

    # --- Step 1: exact duplicates via hash (folder1 <-> folder2 only) ---
    from collections import defaultdict
    by_hash1 = defaultdict(list)
    for p in paths1:
        by_hash1[hashes[p]].append(p)
    by_hash2 = defaultdict(list)
    for p in paths2:
        by_hash2[hashes[p]].append(p)

    # Every duplicate relationship is capped at exactly 2 files (one from
    # folder1, one from folder2). If multiple files on either side share a
    # hash, pair them off 1-to-1 in order - leftovers stay unmatched.
    exact_groups = []
    exact_used1 = set()
    exact_used2 = set()
    for h, group1 in by_hash1.items():
        group2 = by_hash2.get(h, [])
        for a, b in zip(group1, group2):
            exact_groups.append([a, b])
            exact_used1.add(a)
            exact_used2.add(b)

    print(f"\nExact-match pairs (identical settings, ignoring name/author/sample): {len(exact_groups)}")
    for g in exact_groups:
        print(f"  " + ", ".join(os.path.basename(x) for x in g))

    # --- Step 2: near-duplicates among the remaining (non-exact) files, cross-folder only ---
    remaining1 = [p for p in paths1 if p not in exact_used1]
    remaining2 = [p for p in paths2 if p not in exact_used2]
    print(f"\nComparing {len(remaining1)} x {len(remaining2)} remaining files for near-duplicates "
          f"(threshold={args.threshold})...")

    near_pairs, pair_scores = pair_up(remaining1, remaining2, flats, args.threshold)
    near_groups = [list(pair) for pair in near_pairs]

    print(f"Near-duplicate pairs (>= {args.threshold*100:.0f}% similar settings): {len(near_groups)}")
    for g in near_groups:
        sim = pair_scores[tuple(g)]
        print(f"  ({sim:.4f}) " + ", ".join(os.path.basename(x) for x in g))

    # --- Write CSV report ---
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("group_type,group_id,similarity,file\n")
        gid = 0
        for g in exact_groups:
            gid += 1
            for p in g:
                f.write(f"exact,{gid},1.0000,{p}\n")
        for g in near_groups:
            gid += 1
            # report min pairwise similarity within the group for reference
            sims = [pair_scores[(a, b)] for a, b in combinations(g, 2) if (a, b) in pair_scores]
            min_sim = min(sims) if sims else args.threshold
            for p in g:
                f.write(f"near,{gid},{min_sim:.4f},{p}\n")

    total_files = len(paths1) + len(paths2)
    matched_files = sum(len(g) for g in exact_groups) + sum(len(g) for g in near_groups)
    print(f"\nSummary:")
    print(f"  Total files:            {total_files} ({len(paths1)} in folder1, {len(paths2)} in folder2)")
    print(f"  Exact-duplicate groups: {len(exact_groups)} (covering {sum(len(g) for g in exact_groups)} files)")
    print(f"  Near-duplicate groups:  {len(near_groups)} (covering {sum(len(g) for g in near_groups)} files)")
    print(f"  Files with no duplicate found: {total_files - matched_files}")
    print(f"\nFull report written to: {args.out}")

    # --- Step 3 (optional): copy matched duplicate pairs into folder3 with a dup_XXX_ prefix ---
    all_groups = exact_groups + near_groups
    if args.move:
        if not all_groups:
            print("\nNo duplicate pairs found - nothing to copy.")
            return

        os.makedirs(args.folder3, exist_ok=True)

        print(f"\nMoving {sum(len(g) for g in all_groups)} files "
              f"across {len(all_groups)} duplicate pairs into {args.folder3} ...")

        import shutil
        move_log_path = os.path.join(args.folder3, "move_log.csv")
        with open(move_log_path, "w", encoding="utf-8") as log:
            log.write("dup_tag,group_type,similarity,original_path,new_path\n")
            gid = 0
            for is_exact, group_list in ((True, exact_groups), (False, near_groups)):
                for g in group_list:
                    gid += 1
                    tag = f"dup_{gid:03d}"

                    if is_exact:
                        sim_label = "1.0000"
                    else:
                        sim_label = f"{pair_scores.get(tuple(g), args.threshold):.4f}"

                    for p in g:
                        fname = os.path.basename(p)
                        new_name = f"{tag}_{fname}"
                        dest = os.path.join(args.folder3, new_name)
                        # avoid collisions (e.g. same filename in both folders)
                        if os.path.exists(dest):
                            base, ext = os.path.splitext(new_name)
                            i = 1
                            while os.path.exists(dest):
                                dest = os.path.join(args.folder3, f"{base}__{i}{ext}")
                                i += 1
                        try:
                            shutil.move(p, dest)
                            log.write(f"{tag},{'exact' if is_exact else 'near'},{sim_label},{p},{dest}\n")
                        except Exception as e:
                            print(f"  Failed to move {p}: {e}")

        print(f"Move log written to: {move_log_path}")
        print("Files with no duplicate were left untouched in folder1/folder2.")


if __name__ == "__main__":
    main()
