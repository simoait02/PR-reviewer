import asyncio
import json
import os
from pathlib import Path

from deepeval import evaluate
from deepeval.evaluate.configs import AsyncConfig
from deepeval.metrics import (
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
)
from deepeval.test_case import LLMTestCase
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

MCP_URL = "http://127.0.0.1:9000/reviewer/mcp"
DATASET_DIR = Path(__file__).resolve().parent.parent / "datasets"
FAILED_CASES_PATH = (
    Path(__file__).resolve().parents[2] / ".deepeval" / "failed_cases.json"
)
MAX_CONCURRENT = int(os.getenv("RAG_EVAL_MAX_CONCURRENT", "20"))


def extract_results(tool_result):
    structured = getattr(tool_result, "structuredContent", None)

    if isinstance(structured, dict):
        return structured.get("result", structured)

    for block in getattr(tool_result, "content", []):
        if getattr(block, "type", None) == "text":
            payload = json.loads(block.text)
            return payload.get("result", payload)

    return []


def build_expected_output(case):
    concepts = ", ".join(case["relevant_concepts"])
    return f"The guidance should cover: {concepts}."


def load_dataset():
    dataset = []
    dataset_paths = sorted(DATASET_DIR.glob("chapter_*.json"))
    if not dataset_paths:
        raise FileNotFoundError(f"No chapter datasets found in {DATASET_DIR}")

    for dataset_path in dataset_paths:
        dataset.extend(json.loads(dataset_path.read_text()))
    return dataset


def save_failed_cases(evaluation_result):
    failed_cases = []

    for result in evaluation_result.test_results:
        if result.success is not False:
            continue

        failed_cases.append(
            {
                "case_id": result.name,
                "input": result.input,
                "expected_output": result.expected_output,
                "expected_sections": (result.metadata or {}).get(
                    "expected_rule_sections", []
                ),
                "retrieval_context": result.retrieval_context or [],
                "failed_metrics": [
                    metric.model_dump(by_alias=True)
                    for metric in result.metrics_data or []
                    if metric.success is False
                ],
            }
        )

    FAILED_CASES_PATH.parent.mkdir(parents=True, exist_ok=True)
    FAILED_CASES_PATH.write_text(
        json.dumps(failed_cases, indent=2, ensure_ascii=False) + "\n"
    )
    print(
        f"Saved {len(failed_cases)} failed cases to {FAILED_CASES_PATH}",
        flush=True,
    )


async def collect_test_cases():
    dataset = [case for case in load_dataset() if case["answerable"]]
    test_cases = []

    print(f"Loaded {len(dataset)} answerable evaluation cases", flush=True)

    async with (
        streamable_http_client(MCP_URL) as (
            read_stream,
            write_stream,
            _,
        ),
        ClientSession(read_stream, write_stream) as session,
    ):
        await session.initialize()

        for index, case in enumerate(dataset, start=1):
            print(
                f"[{index}/{len(dataset)}] Retrieving {case['case_id']}...",
                flush=True,
            )

            tool_result = await session.call_tool(
                "search_best_practices",
                arguments={
                    "query": case["question"],
                    "limit": 5,
                },
            )

            results = extract_results(tool_result)

            print(
                f"[{index}/{len(dataset)}] Retrieved {len(results)} chunks",
                flush=True,
            )

            test_cases.append(
                LLMTestCase(
                    name=case["case_id"],
                    input=case["question"],
                    actual_output="",
                    expected_output=build_expected_output(case),
                    retrieval_context=[result["content"] for result in results],
                    metadata={
                        "expected_rule_sections": case["expected_rule_sections"],
                    },
                )
            )

    return test_cases


def main():
    test_cases = asyncio.run(collect_test_cases())

    evaluation_result = evaluate(
        test_cases=test_cases,
        metrics=[
            ContextualPrecisionMetric(
                threshold=0.7,
                model="gpt-5.6-luna",
                include_reason=False,
                async_mode=True,
                verbose_mode=False,
            ),
            ContextualRecallMetric(
                threshold=0.7,
                model="gpt-5.6-luna",
                include_reason=False,
                async_mode=True,
                verbose_mode=False,
            ),
            ContextualRelevancyMetric(
                threshold=0.7,
                model="gpt-5.6-luna",
                include_reason=False,
                async_mode=True,
                verbose_mode=False,
            ),
        ],
        async_config=AsyncConfig(
            run_async=True,
            max_concurrent=MAX_CONCURRENT,
        ),
    )
    save_failed_cases(evaluation_result)


if __name__ == "__main__":
    main()
