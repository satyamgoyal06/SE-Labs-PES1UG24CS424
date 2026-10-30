"""Insurance premium calculator used for the Lab 5 static analysis exercise."""

from __future__ import annotations

import csv
import http.client
import math
import os
import secrets
import ssl
import tarfile
from datetime import date, datetime
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO
from urllib.parse import urlsplit, urlunsplit

from defusedxml import ElementTree

QUOTES: dict[str, dict[str, str | float]] = {}
BASE_RATES = {"health": 5000, "motor": 3000, "life": 8000}
LOG_FILE = Path(os.environ.get("PREMIUM_LOG_FILE", "premium_quotes.log"))
CLAIMS_DIRECTORY = Path("claims_docs")
MAX_RATE_BYTES = 1_000_000
MAX_ARCHIVE_MEMBERS = 100
MAX_ARCHIVE_BYTES = 20_000_000


@dataclass(frozen=True)
class QuoteInputs:
    """Applicant and policy inputs used to calculate one premium."""

    policy_type: str
    age: int
    sum_insured: float
    smoker: bool
    claims: int


def calculate_premium(
    inputs: QuoteInputs,
    discounts: list[float] | None = None,
) -> float:
    """Calculate a premium after age, smoking, claims, and discounts."""
    if inputs.policy_type not in BASE_RATES:
        raise ValueError(f"Unknown policy type: {inputs.policy_type}")
    if inputs.age < 0 or inputs.sum_insured < 0 or inputs.claims < 0:
        raise ValueError("Age, sum insured, and claims must be non-negative")

    premium = BASE_RATES[inputs.policy_type] + inputs.sum_insured * 0.002
    if inputs.age > 45:
        premium *= 1.5
    if inputs.smoker:
        premium *= 1.3
    premium += inputs.claims * 1000
    for discount in discounts or []:
        if discount < 0:
            raise ValueError("Discounts must be non-negative")
        premium -= discount
    return max(0.0, premium)


def age_from_dob(dob: str, today: date | None = None) -> int:
    """Return the age on the given date, accounting for the birthday."""
    birth_date = datetime.strptime(dob, "%d-%m-%Y").date()
    reference_date = today or date.today()
    if birth_date > reference_date:
        raise ValueError("Date of birth cannot be in the future")
    return reference_date.year - birth_date.year - (
        (reference_date.month, reference_date.day)
        < (birth_date.month, birth_date.day)
    )


def policy_number() -> str:
    """Return a hard-to-guess policy reference."""
    return f"POL-{secrets.randbelow(900000) + 100000}"


def save_quote(name: str, premium: float) -> str:
    """Add a quote to the in-memory book and append it to a CSV log."""
    number = policy_number()
    QUOTES[number] = {"name": name, "premium": premium}
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", newline="", encoding="utf-8") as log_file:
        writer = csv.writer(log_file)
        writer.writerow((number, name, f"{premium:.2f}"))
    return number


def import_policies(xml_text: str) -> list[tuple[str, int, int]]:
    """Parse partner policy XML, skipping records with invalid fields."""
    root = ElementTree.fromstring(xml_text)
    result = []
    for policy in root.findall("policy"):
        try:
            policy_type = policy.get("type")
            age = int(policy.get("age", ""))
            sum_insured = int(policy.get("sum", ""))
            if policy_type not in BASE_RATES or age < 0 or sum_insured < 0:
                continue
            result.append((policy_type, age, sum_insured))
        except (TypeError, ValueError):
            continue
    return result


def fetch_rates(url: str) -> bytes:
    """Fetch a small HTTPS rate table with certificate checks and a timeout."""
    parsed_url = urlsplit(url)
    if parsed_url.scheme.lower() != "https" or not parsed_url.hostname:
        raise ValueError("Rate tables must be fetched over HTTPS")
    if parsed_url.username or parsed_url.password:
        raise ValueError("Rate table URL must not contain credentials")
    request_target = urlunsplit(
        ("", "", parsed_url.path or "/", parsed_url.query, "")
    )
    connection = http.client.HTTPSConnection(
        parsed_url.hostname,
        parsed_url.port,
        context=ssl.create_default_context(),
        timeout=10,
    )
    try:
        connection.request("GET", request_target)
        response = connection.getresponse()
        if response.status != 200:
            raise ValueError(f"Rate server returned HTTP {response.status}")
        data = response.read(MAX_RATE_BYTES + 1)
    finally:
        connection.close()
    if len(data) > MAX_RATE_BYTES:
        raise ValueError("Rate table exceeds the 1 MB size limit")
    return data


def _safe_archive_member(member: tarfile.TarInfo) -> bool:
    """Accept only regular files whose resolved path stays under the target."""
    if not member.isfile():
        return False
    target = (CLAIMS_DIRECTORY / member.name).resolve()
    return target.is_relative_to(CLAIMS_DIRECTORY.resolve())


def import_claim_documents(archive_path: str | Path) -> list[Path]:
    """Safely extract a bounded set of regular claim files."""
    CLAIMS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    extracted: list[Path] = []
    total_size = 0
    with tarfile.open(archive_path, "r:*") as archive:
        members = archive.getmembers()
        if len(members) > MAX_ARCHIVE_MEMBERS:
            raise ValueError("Archive contains too many entries")
        for member in members:
            if not _safe_archive_member(member):
                continue
            total_size += member.size
            if total_size > MAX_ARCHIVE_BYTES:
                raise ValueError("Archive exceeds the 20 MB extraction limit")
            source: BinaryIO | None = archive.extractfile(member)
            if source is None:
                continue
            destination = CLAIMS_DIRECTORY / member.name
            destination.parent.mkdir(parents=True, exist_ok=True)
            with source, destination.open("wb") as output_file:
                output_file.write(source.read(MAX_ARCHIVE_BYTES + 1))
            extracted.append(destination)
    return extracted


def monthly_instalment(premium: float, months: int = 12) -> float:
    """Return the per-month amount, rounded down to a whole rupee."""
    if months <= 0:
        raise ValueError("Months must be greater than zero")
    return float(math.floor(premium / months))


def is_authorised(token: str | None = None) -> bool:
    """Compare a supplied token with the configured environment secret."""
    expected_token = os.environ.get("UNDERWRITER_TOKEN")
    if not expected_token or not token:
        return False
    return secrets.compare_digest(token, expected_token)


def renewal_due(start: str, years: int = 1) -> str:
    """Return a renewal date, clamping leap-day renewals to February 28."""
    start_date = datetime.strptime(start, "%Y-%m-%d").date()
    try:
        renewal = start_date.replace(year=start_date.year + years)
    except ValueError:
        renewal = start_date.replace(
            month=2, day=28, year=start_date.year + years
        )
    return renewal.isoformat()


def print_quotes() -> None:
    """Print all quotes in insertion order."""
    print("===== Quote Book =====")
    for index, (number, quote) in enumerate(QUOTES.items(), start=1):
        print(index, number, quote["name"], "Rs.", quote["premium"])


def main() -> None:
    """Run sample calculations and demonstrate the calculator functions."""
    first_premium = calculate_premium(
        QuoteInputs("health", 30, 500_000, False, 0)
    )
    second_premium = calculate_premium(
        QuoteInputs("health", 30, 500_000, False, 0)
    )
    motor_premium = calculate_premium(
        QuoteInputs("motor", 50, 800_000, False, 0)
    )
    life_premium = calculate_premium(
        QuoteInputs("life", 25, 100_000, False, 0), [3000, 3000, 3000]
    )
    print("Quote 1:", first_premium)
    print("Quote 2 (same customer details):", second_premium)
    print("Non-smoker aged 50:", motor_premium)
    print("Life with stacked discounts:", life_premium)
    print("Age from DOB 31-12-1990:", age_from_dob("31-12-1990"))
    print("Monthly instalment:", monthly_instalment(motor_premium))
    print("Renewal due:", renewal_due("2025-03-15"))
    xml_text = (
        "<policies><policy type='health' age='40' sum='300000'/>"
        "<policy type='motor' age='abc' sum='1'/></policies>"
    )
    print("Imported:", import_policies(xml_text))
    print("Saved as:", save_quote("Kiran", first_premium))
    print("Authorised:", is_authorised())
    print_quotes()


if __name__ == "__main__":
    main()
