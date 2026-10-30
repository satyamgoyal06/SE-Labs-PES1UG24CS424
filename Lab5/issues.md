# Static analysis findings

Line references below refer to the supplied starter `premium_calculator.py` as it appeared in the assigned repository. The fixes are present in the cleaned version included with this submission.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Unsafe archive extraction | Security (high) | 61-65 | `extractall()` can write files outside the claims directory using traversal paths or special archive entries. | Validate regular members and resolved paths, cap member count and total bytes, and write files explicitly beneath the destination. |
| TLS certificate validation disabled | Security (medium) | 54-56 | `_create_unverified_context()` makes HTTPS vulnerable to interception. | Use the default certificate-verifying SSL context, require HTTPS, set a timeout, and cap response size. |
| Unrestricted URL opening | Security (medium) | 54-56 | `urlopen()` can accept file or custom URL schemes if a caller supplies them. | Parse and validate the HTTPS URL, then use `HTTPSConnection` with the default certificate-verifying context. |
| Bind-all-interfaces setting | Security (medium) | 12 | `HOST = "0.0.0.0"` may expose a service on every network interface. The demo only printed it, but the setting was unnecessary. | Remove the unused host constant and its print statement. |
| Hard-coded temporary log path | Security (medium) | 14 | A fixed `/tmp` path is flagged as an unsafe temporary-file location. | Use a local default log path and allow an explicit `PREMIUM_LOG_FILE` override. |
| Unsafe XML parser | Security (medium) | 7, 46 | Standard ElementTree parsing of untrusted XML can expose XML entity expansion risks. | Use `defusedxml.ElementTree` for partner-supplied XML. |
| Hard-coded underwriter token | Security (low) | 13, 81-85 | A credential embedded in source can be copied from the repository. | Read the secret from `UNDERWRITER_TOKEN` environment variable and compare with `secrets.compare_digest`. |
| Predictable policy identifiers | Security (low) | 37 | The standard pseudo-random generator is not intended for security-sensitive identifiers. | Generate the numeric suffix with `secrets.randbelow`. |
| Unsafe XML parser import | Security (low) | 7 | Importing the standard XML parser for untrusted content is flagged by Bandit. | Replace the import with `defusedxml.ElementTree`. |
| Mutable default discount list | Bug | 19, 28 | `discounts=[]` is shared between calls, and appending to it causes later quotes to inherit state. | Use `None` as the default, iterate a fresh empty list when omitted, and never mutate the caller's list. |
| Incorrect age calculation | Bug | 38-41 | Subtracting birth year alone counts a person as a year older before their birthday. | Subtract one until the birthday has occurred this year, and reject future dates. |
| Renewal fails on leap day | Bug | 88-90 | Replacing the year on February 29 raises `ValueError` for a non-leap target year. | Catch that case and use February 28. |
| Shared float-point logging format | Quality | 32-36 | Manual interpolation and unmanaged file handles can corrupt CSV rows and leak the handle after errors. | Use `csv.writer`, UTF-8, and a context manager. |
| Ambiguous zero-month behavior | Bug | 73-77 | Returning the full premium for zero months silently accepts invalid input; negative months also produce nonsensical amounts. | Reject non-positive month counts. |
| String used as smoker boolean | Logic | 99 | The starter passes `"no"`, which is truthy, so a non-smoker receives a smoking surcharge. | Pass the boolean `False`. |

## Fixes made

The cleaned file addresses all listed issues. It also uses conventional snake_case names, adds docstrings and type hints, validates key inputs, represents calculator input with a dataclass, and guards the demo with `if __name__ == "__main__"` so importing the module does not write a quote to disk.
