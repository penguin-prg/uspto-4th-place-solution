import json
from typing import Dict, List, Optional, Set, Tuple

import plyvel

from utils import read_bytes_in_range, read_lz4_in_range, stable_hash


class SingleTokenDB:
    def __init__(self, db_path: str, txt_path: str):
        self.db = plyvel.DB(db_path, create_if_missing=False)
        self.txt = txt_path

    def get(self, patent: str) -> Optional[Dict[str, List[str]]]:
        start_end = self.db.get(patent.encode("utf-8"))
        if start_end is None:
            return None
        start, end = json.loads(start_end.decode("utf-8"))
        data = read_lz4_in_range(self.txt, start, end)
        return json.loads(data)

    def close(self):
        self.db.close()


class TokinezedDB:
    def __init__(self, db_pathes: List[str], txts_pathes: List[str]):
        self.dbs = [plyvel.DB(p, create_if_missing=False) for p in db_pathes]
        self.txts = txts_pathes

    def get(self, patent: str) -> Optional[Dict[str, List[str]]]:
        split = stable_hash(patent, len(self.dbs))
        start_end = self.dbs[split].get(patent.encode("utf-8"))
        if start_end is None:
            return None
        start, end = json.loads(start_end.decode("utf-8"))
        data = read_lz4_in_range(self.txts[split], start, end)
        return json.loads(data)

    def close(self):
        for db in self.dbs:
            db.close()


class CompleteDB:
    def __init__(self, db_pathes: List[str], txts_pathes: List[str]):
        self.dbs = [plyvel.DB(p, create_if_missing=False) for p in db_pathes]
        self.txts = txts_pathes

    def get(self, patent: str) -> Optional[Dict[str, List[str]]]:
        split = stable_hash(patent, len(self.dbs))
        start_end = self.dbs[split].get(patent.encode("utf-8"))
        if start_end is None:
            return None
        start, end = json.loads(start_end.decode("utf-8"))
        data = read_lz4_in_range(self.txts[split], start, end)
        return json.loads(data)

    def close(self):
        for db in self.dbs:
            db.close()


class CpcToken2RangeDB:
    def __init__(self, db_pathes: List[str], txts_pathes: List[str]):
        self.dbs = [plyvel.DB(p, create_if_missing=False) for p in db_pathes]
        self.txts = txts_pathes

    def get(self, cpc_token: Tuple[str, str]) -> Set[str]:
        split = stable_hash(cpc_token, len(self.dbs))
        start_end = self.dbs[split].get(json.dumps(cpc_token).encode("utf-8"))
        if start_end is None:
            return set()
        start, end = json.loads(start_end.decode("utf-8"))
        patents = set(read_bytes_in_range(self.txts[split], start, end).split())
        return patents

    def close(self):
        for db in self.dbs:
            db.close()
