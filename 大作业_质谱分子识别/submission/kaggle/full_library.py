"""B2: read the entire official training library in bounded batches."""

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq


COMPETITION = "enveda-CASMI26-molecule-id-mass-spectra"
META = ["precursor_mz", "adduct", "ionization_mode", "inchikey14", "normalized_smiles"]
PEAKS = ["ms2_mzs", "ms2_normalized_intensities"]


def vector(mzs, intensities, bin_width=1.0, power=0.5):
    result = np.zeros(int(np.ceil(1500.0 / bin_width)), dtype=np.float32)
    for mz, intensity in zip(mzs, intensities):
        if np.isfinite(mz) and np.isfinite(intensity) and 0 <= mz < 1500 and intensity > 0:
            result[int(mz / bin_width)] += intensity ** power
    length = np.linalg.norm(result)
    return result / length if length else result


def valid_rows(frame):
    return frame.dropna(subset=["inchikey14", "normalized_smiles"]).reset_index(drop=True)


def group_positions(frame):
    return frame.groupby(["adduct", "ionization_mode"], sort=False).indices


def predict_full(reference_path, queries, bin_width=1.0, power=0.5, ppm=20.0,
                 batch_size=4096):
    """Same mass filtering and max merging as B0, using all valid training rows.

    Pass 1 determines whether each query has strict candidates anywhere in the
    library. Pass 2 scores its selected candidates in batches. Keeping only the
    best 25 structures per molecule is exact for maximum-score merging.
    """
    if bin_width <= 0 or power <= 0 or ppm < 0 or batch_size < 1:
        raise ValueError("Invalid bin width, power, ppm or batch size")
    queries = queries.reset_index(drop=True)
    if queries.empty or queries.molecule_id.isna().any():
        raise ValueError("Queries must have molecule IDs")
    reader = pq.ParquetFile(reference_path)
    query_groups = group_positions(queries)
    masses = queries.precursor_mz.to_numpy(dtype=float)
    tolerance = np.maximum(np.abs(masses), 1e-12) * ppm / 1e6
    lower, upper = masses - tolerance, masses + tolerance
    strict = np.zeros(len(queries), dtype=np.int64)
    compatible = np.zeros(len(queries), dtype=np.int64)
    usable = 0
    print("B2 pass 1/2: checking candidate availability in ALL training rows", flush=True)
    for batch in reader.iter_batches(batch_size=65536, columns=META):
        frame = valid_rows(batch.to_pandas())
        usable += len(frame)
        for key, positions in group_positions(frame).items():
            q = query_groups.get(key)
            if q is None:
                continue
            reference_mass = np.sort(frame.precursor_mz.to_numpy(dtype=float)[positions])
            reference_mass = reference_mass[np.isfinite(reference_mass)]
            compatible[q] += len(positions)
            strict[q] += (np.searchsorted(reference_mass, upper[q], side="right")
                          - np.searchsorted(reference_mass, lower[q], side="left"))
    if not usable:
        raise ValueError("No labelled reference spectra")
    # 0 = strict mass window; 1 = compatible group; 2 = entire library.
    levels = np.where(strict > 0, 0, np.where(compatible > 0, 1, 2))
    global_queries = np.flatnonzero(levels == 2)
    vectors = np.stack([vector(r.ms2_mzs, r.ms2_normalized_intensities, bin_width, power)
                        for r in queries.itertuples()])
    molecule_ids = queries.molecule_id.astype(str).to_numpy()
    best = {m: {} for m in dict.fromkeys(molecule_ids)}
    read_rows = scored_rows = 0
    peak_batch = 0
    print(f"B2 pass 2/2: {usable} reference spectra; "
          f"{int((levels > 0).sum())}/{len(queries)} queries need relaxed filtering", flush=True)
    for batch in reader.iter_batches(batch_size=batch_size, columns=META + PEAKS):
        frame = valid_rows(batch.to_pandas())
        read_rows += batch.num_rows
        selected = {}
        for qi in global_queries:
            selected[int(qi)] = np.arange(len(frame))
        reference_mass = frame.precursor_mz.to_numpy(dtype=float)
        for key, positions in group_positions(frame).items():
            q = query_groups.get(key)
            if q is None:
                continue
            order = np.argsort(reference_mass[positions])
            sorted_positions = positions[order]
            sorted_mass = reference_mass[sorted_positions]
            for qi in q:
                if levels[qi] == 0:
                    left = np.searchsorted(sorted_mass, lower[qi], side="left")
                    right = np.searchsorted(sorted_mass, upper[qi], side="right")
                    chosen = sorted_positions[left:right]
                else:
                    chosen = positions
                if len(chosen):
                    selected[int(qi)] = chosen
        if selected:
            union = np.unique(np.concatenate(list(selected.values())))
            matrix = np.stack([vector(r.ms2_mzs, r.ms2_normalized_intensities, bin_width, power)
                               for r in frame.iloc[union].itertuples()])
            scored_rows += len(union)
            peak_batch = max(peak_batch, len(union))
            keys = frame.inchikey14.astype(str).to_numpy()
            smiles = frame.normalized_smiles.astype(str).to_numpy()
            for qi, chosen in selected.items():
                scores = matrix[np.searchsorted(union, chosen)] @ vectors[qi]
                candidates = best[molecule_ids[qi]]
                for ri, score in zip(chosen, scores):
                    key = keys[ri]
                    old = candidates.get(key)
                    if old is None or score > old[0]:
                        candidates[key] = (float(score), smiles[ri])
                best[molecule_ids[qi]] = dict(sorted(candidates.items(),
                    key=lambda item: (-item[1][0], item[0]))[:25])
        if read_rows % (batch_size * 50) == 0 or read_rows == reader.metadata.num_rows:
            print(f"Scanned {read_rows}/{reader.metadata.num_rows} training spectra", flush=True)
    rows = []
    for molecule_id, candidates in best.items():
        if not candidates:
            raise ValueError(f"No predictions for {molecule_id}")
        ranking = sorted(candidates, key=lambda k: (-candidates[k][0], k))
        rows.append(dict(molecule_id=molecule_id,
                         smiles=";".join(candidates[k][1] for k in ranking)))
    stats = dict(reference_source="full official train.parquet", training_rows=reader.metadata.num_rows,
                 reference_spectra=usable, scanned_spectra=read_rows,
                 vectorized_spectra=scored_rows, peak_vector_batch=peak_batch,
                 query_spectra=len(queries), molecules=len(rows),
                 relaxed_spectra=int((levels > 0).sum()),
                 zero_query_spectra=int((np.linalg.norm(vectors, axis=1) == 0).sum()))
    return pd.DataFrame(rows), stats


def official_file(name):
    paths = [Path("/kaggle/input") / COMPETITION / name,
             Path("/kaggle/input/competitions") / COMPETITION / name]
    existing = [p for p in paths if p.is_file()]
    if len(existing) != 1:
        raise FileNotFoundError(f"Attach the official competition data; cannot locate {name}")
    return existing[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train")
    parser.add_argument("--test")
    parser.add_argument("--out", default="/kaggle/working")
    parser.add_argument("--batch-size", type=int, default=4096)
    args = parser.parse_args()
    train = Path(args.train) if args.train else official_file("train.parquet")
    test = Path(args.test) if args.test else official_file("test.parquet")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if (out / "submission.csv").exists():
        raise FileExistsError("Use a new output folder")
    start = time.monotonic()
    queries = pd.read_parquet(test)
    predictions, stats = predict_full(train, queries, batch_size=args.batch_size)
    assert predictions.molecule_id.is_unique
    assert set(predictions.molecule_id) == set(queries.molecule_id.astype(str))
    assert predictions.smiles.str.split(";").str.len().between(1, 25).all()
    stats["elapsed_seconds"] = round(time.monotonic() - start, 3)
    config = dict(reference=str(train), queries=str(test), bin_width=1.0, power=0.5,
                  ppm=20.0, merge="max", batch_size=args.batch_size)
    (out / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    (out / "run_summary.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    predictions.to_csv(out / "submission.csv", index=False)
    print(json.dumps(stats, indent=2), flush=True)


if __name__ == "__main__":
    main()
