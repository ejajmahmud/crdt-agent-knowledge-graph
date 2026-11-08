"""Core CRDT Knowledge Graph implementation."""
import time
from typing import Dict, List, Set, Tuple, Optional, Any


class GraphTriple:
    def __init__(self, subject: str, predicate: str, obj: str, timestamp: float, replica_id: str):
        self.subject = subject
        self.predicate = predicate
        self.obj = obj
        self.timestamp = timestamp
        self.replica_id = replica_id

    @property
    def key(self) -> str:
        return f"{self.subject}:{self.predicate}:{self.obj}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subject": self.subject,
            "predicate": self.predicate,
            "obj": self.obj,
            "timestamp": self.timestamp,
            "replica_id": self.replica_id
        }


class CRDTAgentKnowledgeGraph:
    """State-based LWW-Element-Set CRDT for Subject-Predicate-Object Knowledge Graphs."""
    def __init__(self, replica_id: str):
        self.replica_id = replica_id
        # Key -> GraphTriple
        self.add_set: Dict[str, GraphTriple] = {}
        # Key -> timestamp
        self.remove_set: Dict[str, float] = {}

    def add_triple(self, subject: str, predicate: str, obj: str, timestamp: Optional[float] = None) -> GraphTriple:
        ts = timestamp if timestamp is not None else time.time()
        triple = GraphTriple(subject, predicate, obj, ts, self.replica_id)
        existing = self.add_set.get(triple.key)
        if existing is None or ts > existing.timestamp:
            self.add_set[triple.key] = triple
        return triple

    def remove_triple(self, subject: str, predicate: str, obj: str, timestamp: Optional[float] = None):
        ts = timestamp if timestamp is not None else time.time()
        key = f"{subject}:{predicate}:{obj}"
        if key not in self.remove_set or ts > self.remove_set[key]:
            self.remove_set[key] = ts

    def query(self, subject: Optional[str] = None, predicate: Optional[str] = None, obj: Optional[str] = None) -> List[GraphTriple]:
        results = []
        for key, triple in self.add_set.items():
            removed_ts = self.remove_set.get(key)
            if removed_ts is not None and removed_ts >= triple.timestamp:
                continue  # Tombstoned
            if subject and triple.subject != subject:
                continue
            if predicate and triple.predicate != predicate:
                continue
            if obj and triple.obj != obj:
                continue
            results.append(triple)
        return results

    def merge(self, other: "CRDTAgentKnowledgeGraph"):
        """Commutative, associative, and idempotent join-semilattice merge."""
        for key, other_triple in other.add_set.items():
            local_triple = self.add_set.get(key)
            if local_triple is None or other_triple.timestamp > local_triple.timestamp:
                self.add_set[key] = other_triple

        for key, other_rm_ts in other.remove_set.items():
            local_rm_ts = self.remove_set.get(key, -1.0)
            if other_rm_ts > local_rm_ts:
                self.remove_set[key] = other_rm_ts
