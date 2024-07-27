from copy import deepcopy
from typing import Set

import numpy as np


class HitBlock:
    def __init__(
        self,
        token: str,
        inner_patents: Set[str],
        n_inner: int,
        n_outer: int,
        n_danger: int,
    ):
        self.token = token
        self.inner_patents = inner_patents
        self.n_inner = n_inner
        self.n_outer = n_outer
        self.n_danger = n_danger


class State:
    def __init__(self, cpcs, query_patents, target_ids):
        self.cpcs = cpcs
        self.query_patents = query_patents
        self.target_ids = target_ids

        # 各cpcの各queryが使われているかどうか
        self.query_is_using = [[False] * len(query_patents[i]) for i in range(len(query_patents))]

        # 各cpcのトークン数
        self.n_tokens_per_cpc = [0] * len(query_patents)

        # 使用中のCPCの数
        self.total_cpcs = 0

        # 全体のトークン数
        self.total_tokens = 0

        # 各patentのカウンター. これが1以上のものがhit
        self.patent_counter = {patent: 0 for patent in target_ids}

        # hitしているpatentの数
        self.hit_patent_count = 0

        # outerの個数
        self.outer_count = 0

        # dangerの個数
        self.danger_count = 0

        # 使ってるクエリのindex
        self.used_query_indices = set()

    def copy(self) -> "State":
        state = State(
            self.cpcs,
            self.query_patents,
            self.target_ids,
        )
        state.query_is_using = deepcopy(self.query_is_using)
        state.n_tokens_per_cpc = deepcopy(self.n_tokens_per_cpc)
        state.total_cpcs = self.total_cpcs
        state.total_tokens = self.total_tokens
        state.patent_counter = deepcopy(self.patent_counter)
        state.hit_patent_count = self.hit_patent_count
        state.outer_count = self.outer_count
        state.danger_count = self.danger_count
        state.used_query_indices = deepcopy(self.used_query_indices)
        return state

    def bit_flip(self, r_cpc, r_query):
        """queryの使用状態を反転する"""
        cpc = self.cpcs[r_cpc]
        tokens = self.query_patents[r_cpc][r_query].token
        token_len = len(tokens.split())

        if self.query_is_using[r_cpc][r_query]:
            # 使用 -> 未使用
            self.query_is_using[r_cpc][r_query] = False
            self.used_query_indices.remove((r_cpc, r_query))

            # トークン数のカウントを減らす
            if self.n_tokens_per_cpc[r_cpc] == 1:
                # このCPCが完全に消える場合：

                # まずtokenを1つ削除する
                # (今から削除するqueryしかないので、ORトークンは存在しない)
                # TODO: n_tokenの意味が曖昧。複数トークンのqueryでもここでは1とカウントする
                self.n_tokens_per_cpc[r_cpc] -= 1
                self.total_tokens -= token_len

                # (OR,) CPCも不要になるので削除
                self.total_cpcs -= 1
                if self.total_cpcs == 0:
                    # このCPCが消えるだけ
                    self.total_tokens -= cpc is not None
                else:
                    # 他にもCPCがあるので、ORトークンも消える
                    self.total_tokens -= 1 + (cpc is not None)

            else:
                # CPCから1つ OR token が消えるだけ
                # query ORを削除するだけ
                self.n_tokens_per_cpc[r_cpc] -= 2
                self.total_tokens -= 1 + token_len

            # hit countを減らす
            for patent in self.query_patents[r_cpc][r_query].inner_patents:
                self.patent_counter[patent] -= 1
                if self.patent_counter[patent] == 0:
                    self.hit_patent_count -= 1
                assert self.patent_counter[patent] >= 0

            # outerの個数を減らす
            self.outer_count -= self.query_patents[r_cpc][r_query].n_outer
            self.danger_count -= self.query_patents[r_cpc][r_query].n_danger

        else:
            # 未使用 -> 使用
            self.query_is_using[r_cpc][r_query] = True
            self.used_query_indices.add((r_cpc, r_query))

            if self.n_tokens_per_cpc[r_cpc] == 0:
                # 新しいCPCが追加される場合：

                # tokenが増える (最初の1個なのでORは不要)
                self.n_tokens_per_cpc[r_cpc] += 1
                self.total_tokens += token_len

                # cpcも増える
                self.total_cpcs += 1
                if self.total_cpcs == 1:
                    # このCPCが最初のものなので、CPCだけ増やせばいい
                    self.total_tokens += cpc is not None
                else:
                    # 他にもCPCがあるので、CPCとORトークンを増やす
                    self.total_tokens += 1 + (cpc is not None)
            else:
                # query OR
                self.n_tokens_per_cpc[r_cpc] += 2
                self.total_tokens += 1 + token_len

            for patent in self.query_patents[r_cpc][r_query].inner_patents:
                self.patent_counter[patent] += 1
                if self.patent_counter[patent] == 1:
                    self.hit_patent_count += 1

            self.outer_count += self.query_patents[r_cpc][r_query].n_outer
            self.danger_count += self.query_patents[r_cpc][r_query].n_danger

        # assert self.total_tokens == len(self.get_query().split())

    def get_query(self):
        """queryを生成する"""
        query = []
        for cpc, is_using, query_patents in zip(self.cpcs, self.query_is_using, self.query_patents):
            if not any(is_using):
                continue

            tokens = []
            for query_patent, using in zip(query_patents, is_using):
                if using:
                    tokens.append(query_patent.token)
            if cpc is None:
                this_query = f"({' OR '.join(tokens)})"
            else:
                this_query = f"({cpc} ({' OR '.join(tokens)}))"
            query.append(this_query)

        query = " OR ".join(query)
        return query

    def answer(self):
        """解答を生成する"""
        query = self.get_query()
        if query == "":
            query = "hogefugafoo"
        return query

    def evaluate(self):
        """最適化の評価関数"""
        if self.total_tokens > 50:
            return -self.total_tokens

        return self.ap()

    def ap(self):
        """コンペの評価指標"""
        if self.total_tokens > 50 or self.hit_patent_count == 0:
            return 0

        all_inner_patents = []
        for i, j in self.used_query_indices:
            block = self.query_patents[i][j]
            all_inner_patents.append(
                (
                    block.n_inner + round(block.n_outer / 50) + block.n_danger,
                    block.n_inner,
                    block.inner_patents,
                )
            )
        all_inner_patents = sorted(all_inner_patents)

        corrects = []
        used_patents = set()
        for all_count, inner_count, inner_patents in all_inner_patents:
            dup_count = 0
            for patent in inner_patents:
                if patent in used_patents:
                    dup_count += 1
                used_patents.add(patent)
            inner_count -= dup_count
            all_count -= dup_count
            if all_count == 0:
                continue
            corrects += [inner_count / all_count] * all_count
            if len(corrects) >= 50:
                break
        corrects = corrects[:50]
        cumsum = np.cumsum(corrects)

        scores = []
        for i in range(50):
            expected_hit = cumsum[i] if i < len(cumsum) else cumsum[-1]
            assert expected_hit <= i + 1
            scores.append(expected_hit / (i + 1))
        ap = np.mean(scores)
        assert 0 <= ap <= 1
        return ap
