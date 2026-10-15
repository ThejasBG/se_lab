# Known Issues in Helpdesk Ticket Management System

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---:|---|---|
| Mutable default argument | Bug | Original: 10; fixed version: 14 | Using `audit_trail=[]` would share the same list across calls, causing entries to accumulate unexpectedly. | Change the default to `None` and initialize a new list inside the function. |
| Global statement | Code quality | Fixed version: 15 | `raise_ticket()` uses `global TICKET_COUNTER`, which couples the function to global state and may trigger Pylint `W0603`. | Keep it if preserving the current design; otherwise manage the counter through a class or another state-management approach. |
| Hardcoded administrator password | Security | Original: 8; fixed version: 12 | Storing the password directly in source code exposes it to anyone who can read the file. | Read the password from the `HELPDESK_ADMIN_PASSWORD` environment variable. |
| Shell command injection risk | Security | Original: 37; earlier fixed version: 70 | Concatenating a hostname into a command executed with `shell=True` could allow shell command injection. | Avoid shell execution. The revised implementation uses Python's `socket` module instead. |
| Subprocess Bandit warnings | Security / static analysis | Earlier fixed version: 7, 78 | Bandit flagged the `subprocess` import (`B404`) and call (`B603`). | Remove `subprocess`; use `socket.getaddrinfo()` for hostname resolution. Note that this checks DNS resolution, not actual ICMP ping reachability. |
| Urgency accepts invalid values | Bug / input validation | Original: 24; fixed version: 26 | The program accepts values such as `-7`, even though the prompt specifies an urgency range of 1–5. | Validate that urgency is an integer from 1 through 5 before creating a ticket. This was not changed because the requested fixes were limited to lint/security findings. |
| Closing a nonexistent ticket | Bug robustness | Original: 28; fixed version: 42 | `del tickets[ticket_id]` raises `KeyError` if the ticket ID does not exist. | Use `tickets.pop(ticket_id, None)` to avoid an exception for missing IDs. |
| Missing ticket ID in `add_note()` | Robustness | Original: 25; fixed version: 34 | Adding a note for a nonexistent ticket raises `KeyError`; the function silently ignores it. | Catch only `KeyError`, as in the revised version. Consider returning a success/failure status if callers need to know whether the note was added. |
| Audit trail is not persisted or returned | Functional limitation | Original: 10–23; fixed version: 14–29 | The audit trail is appended to a local list, but `main()` does not pass a list or save the trail, so those entries are not retained by the program. | Pass an audit list explicitly and save it if persistent auditing is required. |
| DNS lookup is not a real ping | Functional limitation | Fixed version: 64–82 | `ping_user_machine()` now checks whether a hostname resolves and measures lookup time; it does not establish that the host is reachable. | Use a suitable ICMP library or a carefully designed platform-specific ping implementation if actual reachability testing is required. |
| JSON ticket IDs become strings | Data-format behavior | Fixed version: 88–90 | JSON object keys are strings, so integer ticket IDs become strings when serialized to `tickets.json`. | Convert keys back to integers when loading the file, or store tickets as a list with an explicit ID field. |

## Notes

- Line numbers can change as the source file is edited; the line references above are approximate and refer to the original or revised versions identified in the table.
- Flake8 producing an empty report means it found no violations under the configured rules. It does not prove that the program has no bugs or security issues.
- Rerun Pylint and Bandit after the latest changes to confirm the current reports.
