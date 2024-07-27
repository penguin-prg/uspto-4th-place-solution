import bz2
import hashlib
import json
from typing import List

import lz4.frame
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm


def save_list_bz2(data, filename):
    serialized_data = json.dumps(data)
    compressed_data = bz2.compress(serialized_data.encode("utf-8"))

    with open(filename, "wb") as f:
        f.write(compressed_data)


def load_list_bz2(filename):
    with open(filename, "rb") as f:
        compressed_data = f.read()
        decompressed_data = bz2.decompress(compressed_data)
        return json.loads(decompressed_data.decode("utf-8"))


def calc_bytes(txt: str) -> int:
    return len(txt.encode("utf-8"))


def read_bytes_in_range(file_path, start_byte, end_byte):
    with open(file_path, "rb") as file:
        file.seek(start_byte)
        data = file.read(end_byte - start_byte)
    return data.decode("utf-8")


def stable_hash(obj, mod: int = 20):
    """
    NOTE: objは`json.dumps`する前のオブジェクト
    """
    obj_str = json.dumps(obj, sort_keys=True)
    hash_bytes = hashlib.sha256(obj_str.encode()).digest()
    hash_int = int.from_bytes(hash_bytes, byteorder="big")
    return hash_int % mod


def read_lz4_in_range(file_path, start_byte, end_byte):
    with open(file_path, "rb") as f:
        f.seek(start_byte)
        compressed_content = f.read(end_byte - start_byte)
        content = lz4.frame.decompress(compressed_content)
        return content.decode("utf-8")


def compute_ap(results: List[str], target_ids: List[str]) -> float:
    assert len(target_ids) == 50
    while len(results) < 50:
        results.append("DUMMY")
    hit = 0
    ap = 0
    for i, result in enumerate(results):
        if result in target_ids:
            hit += 1
        ap += hit / (i + 1)
    ap /= len(target_ids)
    return ap


def evaluate(all_results: List[List[str]], target_ids: List[List[str]], visualize: bool = True):
    # 集計
    true_aps = []
    true_hitcounts = []
    true_corrects = []
    for results, targets in zip(all_results, target_ids):
        target_id = targets[1:]
        ap = compute_ap(results, target_id)
        true_corrects.append([r in target_id for r in results])
        true_aps.append(ap)
        true_hitcounts.append(len(set(results) & set(target_id)))
    true_corrects = np.array(true_corrects)
    true_aps = np.array(true_aps)
    true_hitcounts = np.array(true_hitcounts)

    # ビジュアライズ
    if visualize:
        print(f"mAP: {np.mean(true_aps):.4f}  mHit: {np.mean(true_hitcounts):.2f}")
        fig, axs = plt.subplots(2, 4, figsize=(15, 7))
        axs = axs.flatten()

        # correct ratio per idx
        axs[0].bar(range(50), true_corrects.mean(axis=0))
        axs[0].set_title("Accuracy")
        axs[0].grid()
        axs[0].set_ylim(0, 1)

        # contributions per idx
        contributions = []
        for i in range(50):
            score = 0
            for j in range(i, 50):
                score += 1 / (j + 1)
            contributions.append(score / 50)
        contributions = np.array(contributions)
        assert np.isclose(sum(contributions), 1)
        axs[1].bar(range(50), contributions, label="Limit")
        axs[1].bar(range(50), true_corrects.mean(axis=0) * contributions, label="Contribution")
        axs[1].set_title("Contribution")
        axs[1].grid()
        axs[1].legend()
        axs[2].bar(range(50), np.cumsum(contributions), label="Limit")
        axs[2].bar(
            range(50), np.cumsum(true_corrects.mean(axis=0) * contributions), label="Contribution"
        )
        axs[2].set_title("Contribution Cumsum")
        axs[2].grid()
        axs[2].legend
        axs[3].bar(range(50), (1 - true_corrects.mean(axis=0)) * contributions)
        axs[3].set_title("Improvement Potential")
        axs[3].grid()

        axs[4].hist(true_hitcounts, bins=20)
        axs[4].set_title("Hit Patent Count")
        axs[4].grid()
        axs[5].hist(true_aps, bins=20)
        axs[5].set_title("AP")
        axs[5].grid()
        axs[6].hist(true_aps[true_aps > 0.8], bins=20)
        axs[6].grid()
        axs[6].set_title("AP > 0.8")

        plt.suptitle(
            f"mAP: {np.mean(true_aps):.4f}  Hit: {np.mean(true_hitcounts):.2f}", fontsize=15
        )
        plt.tight_layout()
        plt.show()

    return true_aps
