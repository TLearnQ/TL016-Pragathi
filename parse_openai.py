import os
import argparse
import json
import csv

from logger_setup import get_logger
from report_generator import load_spec_from_text, extract_endpoints, aggregate, save_json
from api_client import APIClient, APIResponseError

logger = get_logger()

DEFAULT_REMOTE_SPECS = [
    "https://forge.3gpp.org/rep/all/5G_APIs/-/raw/REL-18/TS29522_ServiceParameter.yaml",
    "https://forge.3gpp.org/rep/all/5G_APIs/-/raw/REL-18/TS28532_ProvMnS.yaml",
    "https://forge.3gpp.org/rep/all/5G_APIs/-/raw/REL-18/TS28623_ComDefs.yaml",
    "https://forge.3gpp.org/rep/all/5G_APIs/-/raw/REL-18/5gcNrm.yaml",
    "https://forge.3gpp.org/rep/all/5G_APIs/-/raw/REL-18/TS29520_NEf.yaml"
]

OUTPUT_METADATA = "metadata.json"
OUTPUT_SUMMARY = "summary.json"
OUTPUT_CSV = "output.csv"

def fetch_and_parse_urls(urls, client):
    all_endpoints = []
    first_components = None

    for url in urls:
        logger.info("Fetching remote spec", extra={"meta": {"url": url}})
        try:
            text = client.get_text(url)
        except APIResponseError as ar:
            logger.error("Failed to fetch remote spec", extra={"meta": {"url": url, "status_code": ar.status_code, "error": str(ar)}})
            continue
        except Exception as e:
            logger.error("Unexpected error fetching remote spec", extra={"meta": {"url": url, "error": str(e)}})
            continue

        try:
            spec = load_spec_from_text(text)
        except Exception as e:
            logger.error("Failed to parse fetched spec", extra={"meta": {"url": url, "error": str(e)}})
            continue

        if not isinstance(spec, dict):
            logger.warning("Spec parsed but not mapping/dict; skipping", extra={"meta": {"url": url}})
            continue

        if first_components is None:
            first_components = spec.get("components")

        endpoints = extract_endpoints(spec, source_file=url)
        logger.info("Endpoints extracted from remote", extra={"meta": {"url": url, "count": len(endpoints)}})
        all_endpoints.extend(endpoints)

    return all_endpoints, first_components



def main():
    parser = argparse.ArgumentParser(description="Fetch and parse 3GPP OpenAPI YAMLs and extract metadata")
    parser.add_argument("--urls", nargs="*", help="Optional list of raw OpenAPI YAML URLs to fetch")
    parser.add_argument("--max", type=int, default=5, help="Maximum number of URLs to fetch")
    parser.add_argument("--output-metadata", default=OUTPUT_METADATA)
    parser.add_argument("--output-summary", default=OUTPUT_SUMMARY)
    parser.add_argument("--output-csv", default=OUTPUT_CSV)
    args = parser.parse_args()

    urls = args.urls if args.urls else DEFAULT_REMOTE_SPECS
    urls = urls[:args.max]

    client = APIClient(timeout=20)

    endpoints, components = fetch_and_parse_urls(urls, client)

    if not endpoints:
        logger.warning("No endpoints extracted from provided URLs", extra={"meta": {"urls": urls}})
        return

    save_json(endpoints, args.output_metadata)
    logger.info("Metadata saved", extra={"meta": {"path": args.output_metadata, "count": len(endpoints)}})

    try:
        write_csv(endpoints, csv_path=args.output_csv)
        logger.info("CSV saved", extra={"meta": {"path": args.output_csv}})
    except Exception as e:
        logger.error("Failed to save CSV", extra={"meta": {"error": str(e)}})

    summary = aggregate(endpoints, spec_components=components)
    save_json(summary, args.output_summary)
    logger.info("Summary saved", extra={"meta": {"path": args.output_summary}})

if __name__ == "__main__":
    main()
