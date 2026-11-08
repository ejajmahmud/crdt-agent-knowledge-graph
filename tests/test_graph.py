"""Unit tests for crdt-agent-knowledge-graph."""
import unittest
from crdt_agent_knowledge_graph.graph import CRDTAgentKnowledgeGraph


class TestCRDTAgentKnowledgeGraph(unittest.TestCase):
    def test_add_and_query(self):
        g = CRDTAgentKnowledgeGraph("node-1")
        g.add_triple("Agent", "status", "ready")
        triples = g.query(subject="Agent")
        self.assertEqual(len(triples), 1)
        self.assertEqual(triples[0].obj, "ready")

    def test_tombstone_removal(self):
        g = CRDTAgentKnowledgeGraph("node-1")
        g.add_triple("Server", "state", "online", timestamp=100.0)
        self.assertEqual(len(g.query()), 1)
        g.remove_triple("Server", "state", "online", timestamp=101.0)
        self.assertEqual(len(g.query()), 0)

    def test_peer_merge_convergence(self):
        g1 = CRDTAgentKnowledgeGraph("node-1")
        g2 = CRDTAgentKnowledgeGraph("node-2")

        g1.add_triple("Task", "priority", "high", timestamp=10.0)
        g2.add_triple("Task", "owner", "coder_agent", timestamp=12.0)

        g1.merge(g2)
        g2.merge(g1)

        q1 = sorted([f"{t.subject}-{t.predicate}-{t.obj}" for t in g1.query()])
        q2 = sorted([f"{t.subject}-{t.predicate}-{t.obj}" for t in g2.query()])
        self.assertEqual(q1, q2)
        self.assertEqual(len(q1), 2)
