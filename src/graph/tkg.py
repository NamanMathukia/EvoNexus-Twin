"""
src/graph/tkg.py
Temporal Knowledge Graph built with NetworkX.

Nodes
-----
  student:{id}   — StudentNode
  skill:{name}   — SkillNode
  job:{role}     — JobNode

Edges (with 'time' attribute in months)
---------
  has_skill   : student → skill
  worked_in   : student → job (via internship)
  applied_to  : student → job (post-placement)
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from typing import Dict, List, Any, Optional

import networkx as nx
import numpy as np


# ── Node type tags ────────────────────────────────────────────────────────────
STUDENT_PREFIX = "student:"
SKILL_PREFIX   = "skill:"
JOB_PREFIX     = "job:"


class TemporalKnowledgeGraph:
    """
    Builds and queries a Temporal Knowledge Graph over student profiles.

    Parameters
    ----------
    profiles : list of student dicts produced by generator.generate_dataset()
    """

    def __init__(self, profiles: List[Dict[str, Any]]) -> None:
        self.G: nx.MultiDiGraph = nx.MultiDiGraph()
        self._skill_freq: Dict[str, int] = defaultdict(int)
        self._n_students: int = len(profiles)
        self._graph_feature_cache: Dict[str, Dict[str, float]] = {}

        self._build(profiles)
        self._compute_centrality()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build(self, profiles: List[Dict[str, Any]]) -> None:
        for student in profiles:
            sid = student["student_id"]
            s_node = f"{STUDENT_PREFIX}{sid}"

            # Add student node
            self.G.add_node(s_node, type="student",
                            cgpa=student["final_cgpa"],
                            risk=student["risk_level"],
                            placed=student["placed"])

            # Skill edges from trajectory triplets
            for triplet in student["triplets"]:
                if triplet["event_type"] == "skill_acquired":
                    skill = triplet["entity"]
                    sk_node = f"{SKILL_PREFIX}{skill}"
                    if not self.G.has_node(sk_node):
                        self.G.add_node(sk_node, type="skill", name=skill)
                    self.G.add_edge(s_node, sk_node,
                                    relation="has_skill",
                                    time=triplet["timestamp"])
                    self._skill_freq[skill] += 1

            # Internship edges (worked_in)
            for intern in student["internships"]:
                role = intern["role"]
                job_node = f"{JOB_PREFIX}{role}"
                if not self.G.has_node(job_node):
                    self.G.add_node(job_node, type="job", role=role)
                self.G.add_edge(s_node, job_node,
                                relation="worked_in",
                                time=float(intern["semester"] * 6),
                                company=intern["company"],
                                quality=intern["quality"])

            # Placement edge (applied_to)
            if student["placed"]:
                job_node = f"{JOB_PREFIX}placement"
                if not self.G.has_node(job_node):
                    self.G.add_node(job_node, type="job", role="placement")
                self.G.add_edge(s_node, job_node,
                                relation="applied_to",
                                time=float(48.0 - student["months_to_placement"]))

    # ── Centrality ────────────────────────────────────────────────────────────

    def _compute_centrality(self) -> None:
        """Pre-compute degree and betweenness centrality for all nodes."""
        # Convert to simple graph for centrality (MultiDiGraph → DiGraph)
        simple = nx.DiGraph()
        for u, v, data in self.G.edges(data=True):
            simple.add_edge(u, v)

        self._degree_centrality     = nx.degree_centrality(simple)
        self._in_degree_centrality  = nx.in_degree_centrality(simple)
        self._out_degree_centrality = nx.out_degree_centrality(simple)

        # Betweenness is expensive — use approximate with k=100
        try:
            self._betweenness = nx.betweenness_centrality(simple, k=min(100, len(simple)))
        except Exception:
            self._betweenness = {n: 0.0 for n in simple.nodes()}

    # ── Skill rarity ─────────────────────────────────────────────────────────

    def skill_rarity(self, skill: str) -> float:
        """Inverse document frequency-style rarity score (0-1, higher = rarer)."""
        freq = self._skill_freq.get(skill, 0)
        if freq == 0:
            return 1.0
        return float(1.0 - (freq / max(self._n_students, 1)))

    # ── Per-student graph features ────────────────────────────────────────────

    def get_student_graph_features(self, student_id: str) -> Dict[str, float]:
        """
        Return a dict of graph-derived numeric features for one student.
        Results are cached after first computation.
        """
        if student_id in self._graph_feature_cache:
            return self._graph_feature_cache[student_id]

        s_node = f"{STUDENT_PREFIX}{student_id}"
        if s_node not in self.G:
            return self._zero_features()

        neighbours = list(self.G.successors(s_node))
        skill_neighbours = [n for n in neighbours if n.startswith(SKILL_PREFIX)]
        job_neighbours   = [n for n in neighbours if n.startswith(JOB_PREFIX)]

        skill_names = [n.replace(SKILL_PREFIX, "") for n in skill_neighbours]
        avg_rarity  = float(np.mean([self.skill_rarity(s) for s in skill_names])) \
                      if skill_names else 0.0

        features = {
            "graph_degree":           float(self.G.degree(s_node)),
            "graph_out_degree":       float(self.G.out_degree(s_node)),
            "graph_centrality":       float(self._degree_centrality.get(s_node, 0.0)),
            "graph_betweenness":      float(self._betweenness.get(s_node, 0.0)),
            "graph_skill_degree":     float(len(skill_neighbours)),
            "graph_job_degree":       float(len(job_neighbours)),
            "graph_avg_skill_rarity": avg_rarity,
        }
        self._graph_feature_cache[student_id] = features
        return features

    def _zero_features(self) -> Dict[str, float]:
        return {
            "graph_degree": 0.0, "graph_out_degree": 0.0,
            "graph_centrality": 0.0, "graph_betweenness": 0.0,
            "graph_skill_degree": 0.0, "graph_job_degree": 0.0,
            "graph_avg_skill_rarity": 0.5,
        }

    # ── Augment DataFrame ─────────────────────────────────────────────────────

    def augment_dataframe(self, df) -> "pd.DataFrame":
        """Add graph feature columns to an existing DataFrame (requires student_id col)."""
        import pandas as pd
        feature_rows = []
        for sid in df["student_id"]:
            feature_rows.append(self.get_student_graph_features(sid))
        gdf = pd.DataFrame(feature_rows, index=df.index)
        return pd.concat([df.reset_index(drop=True), gdf], axis=1)

    # ── Summary stats ─────────────────────────────────────────────────────────

    def summary(self) -> Dict[str, Any]:
        return {
            "n_nodes":     self.G.number_of_nodes(),
            "n_edges":     self.G.number_of_edges(),
            "n_students":  len([n for n in self.G.nodes if n.startswith(STUDENT_PREFIX)]),
            "n_skills":    len([n for n in self.G.nodes if n.startswith(SKILL_PREFIX)]),
            "n_jobs":      len([n for n in self.G.nodes if n.startswith(JOB_PREFIX)]),
            "top5_skills": sorted(self._skill_freq.items(), key=lambda x: -x[1])[:5],
        }


if __name__ == "__main__":
    from src.data.generator import generate_dataset
    print("Generating dataset …")
    _, profiles = generate_dataset(500)
    print("Building TKG …")
    tkg = TemporalKnowledgeGraph(profiles)
    print(json.dumps(tkg.summary(), indent=2))
    feats = tkg.get_student_graph_features(profiles[0]["student_id"])
    print("Graph features for first student:", feats)
