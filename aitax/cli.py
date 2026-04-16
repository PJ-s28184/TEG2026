from __future__ import annotations

import argparse
import json

from .advisor import AiTaxAdvisor
from .rules_engine import TaxScenario


def main() -> None:
    parser = argparse.ArgumentParser(description="AiTax local backend CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("ingest", help="Build vector index and knowledge graph")

    ask_parser = subparsers.add_parser("ask", help="Ask a grounded tax question")
    ask_parser.add_argument("query")
    ask_parser.add_argument("--top-k", type=int, default=5)

    graph_parser = subparsers.add_parser("graph", help="Query the knowledge graph")
    graph_parser.add_argument("term")
    graph_parser.add_argument("--limit", type=int, default=10)

    calc_parser = subparsers.add_parser("calculate", help="Run deterministic tax calculation")
    calc_parser.add_argument("--income", type=float, required=True)
    calc_parser.add_argument("--expenses", type=float, default=0.0)
    calc_parser.add_argument("--internet-expenses", type=float, default=0.0)
    calc_parser.add_argument("--children", type=int, default=0)
    calc_parser.add_argument("--married", action="store_true")
    calc_parser.add_argument("--under-26-income", type=float, default=0.0)
    calc_parser.add_argument("--taxation-form", choices=["scale", "linear", "lump_sum"], default="scale")
    calc_parser.add_argument("--lump-sum-rate", type=float, default=0.085)

    args = parser.parse_args()
    advisor = AiTaxAdvisor()

    if args.command == "ingest":
        print(json.dumps(advisor.build_indexes(), ensure_ascii=False, indent=2))
    elif args.command == "ask":
        print(advisor.ask(args.query, top_k=args.top_k)["answer"])
    elif args.command == "graph":
        print(json.dumps(advisor.query_graph(args.term, limit=args.limit), ensure_ascii=False, indent=2))
    elif args.command == "calculate":
        scenario = TaxScenario(
            income=args.income,
            expenses=args.expenses,
            internet_expenses=args.internet_expenses,
            children=args.children,
            married=args.married,
            under_26_income=args.under_26_income,
            taxation_form=args.taxation_form,
            lump_sum_rate=args.lump_sum_rate,
        )
        print(json.dumps(advisor.calculate(scenario), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
