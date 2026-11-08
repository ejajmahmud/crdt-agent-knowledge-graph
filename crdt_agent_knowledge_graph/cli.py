"""CLI for crdt-agent-knowledge-graph."""
import sys
import argparse
from .graph import CRDTAgentKnowledgeGraph


def main():
    parser = argparse.ArgumentParser(description="CRDT Agent Knowledge Graph CLI")
    parser.add_argument("--demo", action="store_true", help="Run multi-agent CRDT graph convergence demo")
    args = parser.parse_args()

    if args.demo:
        graph_a = CRDTAgentKnowledgeGraph("agent-alpha")
        graph_b = CRDTAgentKnowledgeGraph("agent-beta")

        graph_a.add_triple("Project", "uses", "Python", timestamp=10.0)
        graph_b.add_triple("Project", "target", "Production", timestamp=12.0)
        graph_b.remove_triple("Project", "uses", "Python", timestamp=15.0)

        print("[*] Merging Agent Beta into Agent Alpha...")
        graph_a.merge(graph_b)
        active_triples = graph_a.query()
        print(f"[+] Converged Active Triples ({len(active_triples)}):")
        for t in active_triples:
            print(f"    ({t.subject}) -[{t.predicate}]-> ({t.obj})")
    else:
        parser.print_help()
    sys.exit(0)


if __name__ == "__main__":
    main()
