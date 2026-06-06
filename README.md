# tricount-extractor

Extract and save Tricount registries to Excel files.

## Setup

Install dependencies using uv:

```bash
git clone https://github.com/wenceslas-sanchez/tricount-extractor.git
cd tricount-extractor
uv sync --all-groups
```

## Usage

### Finding your registry ID

The registry ID is the token at the end of a Tricount **share link**. To get it:

1. Open the Tricount app (iOS/Android) or [tricount.com](https://tricount.com)
2. Open the group you want to export
3. Tap **Share** or **Invite** to get the sharing link
4. The link looks like `https://tricount.com/tXxXxXxXx` — the part after `tricount.com/` is your registry ID (e.g. `tXxXxXxXx`)

### Basic usage

```bash
uv run tricount-extractor -id <registry-id> -f <output-folder>
```

### Multiple registries at once

Pass multiple IDs separated by spaces to export them all in one run:

```bash
uv run tricount-extractor -id <id1> <id2> <id3> -f ./output
```

### Timeout

Large registries with many entries may take longer to fetch from the API. Use `-t` to increase the HTTP timeout (default: 5 seconds):

```bash
uv run tricount-extractor -id <registry-id> -f ./output -t 60
```

Use `-t None` to disable the timeout entirely.

### Output files

Each registry is saved as `<title>_<registry-id>.xlsx` in the output folder. Running the tool again for the same registry **overwrites** the existing file — rename or move previous exports if you want to keep them.

### Understanding amounts

Amounts preserve the sign from the API:

| type_transaction | Amount sign | Meaning |
|------------------|-------------|---------|
| NORMAL | negative | An expense (money spent) |
| INCOME | positive | Shared income or refund (money received) |
| BALANCE | negative | A settlement/reimbursement between members |

The `amount` and `currency` columns show the value converted to the registry's currency. The `original_amount` and `original_currency` columns show what was actually paid if the expense was in a different currency (e.g. paying in JPY for a EUR registry).

## Output Format

Each registry is saved as an Excel file with 5 sheets:

### 1. members
Registry participants with their details.

| Column | Description |
|--------|-------------|
| member_id | Unique member identifier |
| member_uuid | Member UUID |
| member_name | Display name |
| status | Membership status (ACTIVE, etc.) |

### 2. entries
All expense entries in the registry.

| Column | Description |
|--------|-------------|
| entry_id | Unique entry identifier |
| created | Timestamp when the entry was created (may differ from `date`) |
| date | Entry date and time |
| description | Expense description |
| amount | Total amount in registry currency (negative = expense, positive = income) |
| currency | Currency code (USD, EUR, etc.) |
| original_amount | Amount in the original currency (negative = expense, positive = income) |
| original_currency | Original currency code if different from registry currency |
| payer | Name of person who paid |
| is_reimbursement | True if this is a reimbursement |
| type_transaction | Transaction type: NORMAL (expense), INCOME, or BALANCE (reimbursement) |
| status | Entry status (ACTIVE, etc.) |
| type | Entry type (MANUAL, etc.) |
| category | Expense category (FOOD, ACCOMMODATION, etc.) |

### 3. allocations
How each expense is split among participants.

| Column | Description |
|--------|-------------|
| entry_id | Reference to the expense entry |
| date | Entry date and time |
| description | Expense description |
| payer | Name of person who paid |
| is_reimbursement | True if this is a reimbursement |
| type_transaction | Transaction type: NORMAL (expense), INCOME, or BALANCE (reimbursement) |
| participant | Name of person this allocation applies to |
| share | Amount allocated to this participant (negative = expense, positive = income) |
| currency | Currency code |
| original_share | Share in the original currency (negative = expense, positive = income) |
| original_currency | Original currency code if different from registry currency |
| split_type | How the split was calculated: RATIO (equal/weighted) or AMOUNT (fixed) |
| share_ratio | Weight used for ratio-based splits (e.g. 1, 2) |

### 4. attachments
Image URLs attached to expense entries.

| Column | Description |
|--------|-------------|
| entry_id | Reference to the expense entry |
| url | URL of the attached image |

### 5. balances
Final balance for each member (who owes/is owed).

| Column | Description |
|--------|-------------|
| member | Member name |
| balance | Net balance (positive = owed, negative = owes) |

## Development

Run tests:

```bash
uv run --all-groups pytest
```
