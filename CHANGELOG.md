# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-10-07

### Changed

- Tests now run on Linux, Windows and macOS. ([#84])
- `cost` on the `transaction_ledger` sheet is now signed: positive for expenses,
  negative for income (still 0 for reimbursements), so summing it gives the total
  spent net of income. It used to be an absolute value, so **the `cost` column of existing
  `transaction_ledger` exports changes sign for income**. ([#83])

## [0.2.1] - 2026-09-26

### Added

- Published on PyPI: `pip install tricount-extractor`.
- Support for Python 3.12 and 3.13 (previously 3.14 only). ([#79])
- Package metadata (README, `GPL-3.0-or-later` license, project URLs). Tests are
  no longer shipped in the wheel.

## [0.2.0] - 2026-09-26

### Added

- New `transaction_ledger` sheet: one row per entry with its date, description,
  category, type (`Expense`, `Income` or `Transfer`), cost and currency, plus one
  column per member holding their net position for that entry (positive = owed).
  Each member column sums to their value on the `balances` sheet. ([#73])
- New `is_income` column on the `entries` and `allocations` sheets. ([#72])

### Fixed

- Balances are now correct for registries containing income entries. Amounts
  used to be taken as absolute values, which treated money received by the group
  like an expense. The sign convention is unchanged (positive = owed, negative =
  owes), but **exports of registries with income will show different balances
  than with 0.1.0**. ([#71])
- Members sharing a display name are no longer merged on the `balances` sheet.
  Members are now tracked by id; when a display name is shared, or matches a
  `transaction_ledger` column name, the member id is appended to the label,
  e.g. `Alex (#301)`. ([#76])

## [0.1.0]

- Initial version: export Tricount registries to Excel with `members`, `entries`,
  `allocations`, `attachments` and `balances` sheets.

[0.3.0]: https://github.com/wenceslas-sanchez/tricount-extractor/releases/tag/v0.3.0
[0.2.1]: https://github.com/wenceslas-sanchez/tricount-extractor/releases/tag/v0.2.1
[0.2.0]: https://github.com/wenceslas-sanchez/tricount-extractor/releases/tag/v0.2.0
[#71]: https://github.com/wenceslas-sanchez/tricount-extractor/pull/71
[#72]: https://github.com/wenceslas-sanchez/tricount-extractor/pull/72
[#73]: https://github.com/wenceslas-sanchez/tricount-extractor/pull/73
[#76]: https://github.com/wenceslas-sanchez/tricount-extractor/pull/76
[#79]: https://github.com/wenceslas-sanchez/tricount-extractor/pull/79
[#83]: https://github.com/wenceslas-sanchez/tricount-extractor/pull/83
[#84]: https://github.com/wenceslas-sanchez/tricount-extractor/pull/84
