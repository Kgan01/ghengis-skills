---
name: bookkeeping
description: Use when helping with financial record-keeping, expense categorization, tax preparation, or accounting questions — covers double-entry accounting, IRS categories, reconciliation, and financial reports
---

# Bookkeeping

## When to Use
When helping with financial record-keeping, expense categorization, tax preparation, accounting questions, journal entries, bank reconciliation, chart of accounts design, or generating financial reports.

## Core Concepts

### Double-Entry Accounting

**The Fundamental Equation**
```
Assets = Liabilities + Equity

Every transaction affects at least 2 accounts (balanced)
Debits must equal credits
```

**Account Types & Normal Balances**
- **Assets** (debit +, credit -): Cash, accounts receivable, inventory, equipment
- **Liabilities** (credit +, debit -): Accounts payable, loans, credit cards
- **Equity** (credit +, debit -): Owner's equity, retained earnings
- **Revenue** (credit +, debit -): Sales, service income, interest income
- **Expenses** (debit +, credit -): Rent, salaries, utilities, supplies

**Example Transaction**
```
Purchase office supplies for $500 cash:

Debit: Office Supplies (Asset) +$500
Credit: Cash (Asset) -$500

Effect: Cash decreases, Supplies increases (total assets unchanged)
```

### Chart of Accounts (COA)

**Structure** (Account number + name)
```
1000-1999: Assets
  1000: Cash
  1100: Accounts Receivable
  1200: Inventory
  1500: Equipment
  1600: Accumulated Depreciation (contra-asset)

2000-2999: Liabilities
  2000: Accounts Payable
  2100: Credit Card Payable
  2500: Loans Payable

3000-3999: Equity
  3000: Owner's Equity
  3500: Retained Earnings
  3900: Owner's Draws (contra-equity)

4000-4999: Revenue
  4000: Sales Revenue
  4100: Service Revenue
  4500: Interest Income

5000-9999: Expenses
  5000: Cost of Goods Sold (COGS)
  6000: Salaries & Wages
  6100: Rent
  6200: Utilities
  6300: Office Supplies
  6400: Marketing & Advertising
  6500: Travel & Meals
  6600: Insurance
  6700: Software & Subscriptions
  8000: Depreciation
  9000: Income Tax Expense
```

### Journal Entries

**Standard Entry Format**
```
Date: 2024-02-14
Description: Purchase office supplies
---
Debit   | Office Supplies (6300)      | $500
Credit  | Cash (1000)                  | $500
---
```

**Common Entry Patterns**

**Cash Sale**
```
Debit: Cash (1000) $1,000
Credit: Sales Revenue (4000) $1,000
```

**Credit Sale**
```
Debit: Accounts Receivable (1100) $1,000
Credit: Sales Revenue (4000) $1,000
```

**Receive Payment**
```
Debit: Cash (1000) $1,000
Credit: Accounts Receivable (1100) $1,000
```

**Pay Expense (cash)**
```
Debit: Rent Expense (6100) $2,000
Credit: Cash (1000) $2,000
```

**Pay Expense (credit card)**
```
Debit: Marketing Expense (6400) $500
Credit: Credit Card Payable (2100) $500
```

**Take Loan**
```
Debit: Cash (1000) $10,000
Credit: Loans Payable (2500) $10,000
```

**Owner Investment**
```
Debit: Cash (1000) $5,000
Credit: Owner's Equity (3000) $5,000
```

**Owner Draw**
```
Debit: Owner's Draws (3900) $1,000
Credit: Cash (1000) $1,000
```

### Cash vs Accrual Basis

**Cash Basis**
- Record revenue when cash received
- Record expense when cash paid
- Simple, good for small businesses
- Example: Invoice sent Jan 15, paid Feb 5 -> Record revenue Feb 5

**Accrual Basis**
- Record revenue when earned (invoice date)
- Record expense when incurred (invoice received)
- GAAP compliant, required for corporations
- Example: Invoice sent Jan 15, paid Feb 5 -> Record revenue Jan 15

**IRS Rules**
- Cash basis: Allowed for businesses <$27M revenue
- Accrual basis: Required for inventory businesses >$27M

### Bank Reconciliation

**Why Reconcile?**
- Catch errors (duplicate transactions, typos)
- Identify missing transactions (bank fees, deposits in transit)
- Detect fraud (unauthorized charges)

**Process**
```
1. Start with ending bank balance
2. Add: Deposits in transit (not yet cleared)
3. Subtract: Outstanding checks (written but not cashed)
4. Adjusted bank balance

5. Start with ending book balance (accounting records)
6. Add: Bank interest, deposits not yet recorded
7. Subtract: Bank fees, NSF checks (bounced)
8. Adjusted book balance

9. Compare: Adjusted bank = Adjusted book (should match)
10. If mismatch: Find discrepancy (missing transaction, error)
```

### IRS Expense Categories

**Deductible Business Expenses** (IRS Schedule C)
- **Advertising**: Ads, social media, SEO, business cards
- **Car & Truck**: Mileage (67c/mile 2024), gas, repairs (if business use)
- **Commissions & Fees**: Sales commissions, payment processing fees
- **Contract Labor**: 1099 contractors, freelancers
- **Depreciation**: Equipment, vehicles, computers (multi-year assets)
- **Insurance**: Business liability, E&O, health (if self-employed)
- **Interest**: Business loan interest, credit card interest (business purchases)
- **Legal & Professional**: Lawyers, accountants, consultants
- **Office Expense**: Supplies, software, postage
- **Rent**: Office space, coworking, storage
- **Repairs & Maintenance**: Equipment repairs, website maintenance
- **Supplies**: Materials, inventory (not for resale)
- **Taxes & Licenses**: Business licenses, sales tax, property tax
- **Travel**: Flights, hotels, car rental (business trips)
- **Meals**: 50% deductible (100% if with client)
- **Utilities**: Phone, internet, electricity (if home office)
- **Wages**: W-2 employee salaries

**Non-Deductible**
- Personal expenses (groceries, personal car use)
- Owner's draw (not an expense, it's equity withdrawal)
- Loan principal payments (only interest is deductible)
- Capital expenses (equipment >$2,500 -> depreciate, not expense)

## Patterns & Procedures

### Recording Daily Transactions
```
1. Collect source documents:
   - Receipts (paper or digital)
   - Invoices (sent to customers)
   - Bills (from vendors)
   - Bank statements

2. For each transaction:
   - Identify accounts affected (at least 2)
   - Determine debit/credit for each account
   - Verify debits = credits
   - Record in journal entry

3. Categorize by type:
   - Revenue: Sales, service income
   - COGS: Direct costs (materials, labor)
   - Operating expenses: Rent, salaries, utilities
   - Other: Interest, taxes, depreciation

4. Enter into accounting system:
   - Include date, description, amounts, accounts
   - Attach receipt/invoice (digital copy)
```

### Month-End Close Procedure
```
1. Record all transactions for the month (including last day)
2. Bank reconciliation:
   - Compare bank statement to accounting records
   - Add missing transactions (fees, interest)
   - Mark cleared transactions
3. Reconcile credit cards (same process as bank)
4. Review accounts receivable:
   - Follow up on overdue invoices
   - Write off uncollectible debts (if any)
5. Review accounts payable:
   - Ensure all bills are recorded
   - Plan payments for upcoming month
6. Accrue expenses (if accrual basis):
   - Unpaid bills received but not yet paid
   - Prepaid expenses (insurance, rent paid in advance)
7. Record depreciation:
   - Monthly depreciation for equipment, vehicles
8. Generate financial reports:
   - Income Statement (P&L)
   - Balance Sheet
   - Cash Flow Statement
9. Review for errors:
   - Unusual account balances
   - Negative balances (should be rare)
   - Duplicate transactions
10. Close the period (lock it to prevent changes)
```

### Expense Categorization Workflow
```
Receipt: $150 for Facebook Ads

1. Identify expense type: Marketing & Advertising
2. Check if business-related: Yes (promoting business)
3. Check if deductible: Yes (ordinary and necessary)
4. Choose COA account: 6400 (Marketing & Advertising)
5. Record entry:
   Debit: Marketing Expense (6400) $150
   Credit: Cash or Credit Card Payable $150
6. Attach receipt to transaction
7. Note: 100% deductible for business advertising
```

### Handling Loans
```
Loan received: $10,000 at 6% annual interest, 5-year term

Initial entry (loan received):
Debit: Cash (1000) $10,000
Credit: Loans Payable (2500) $10,000

Monthly payment: $193.33 (principal + interest)
- Interest: $10,000 x 6% / 12 = $50
- Principal: $193.33 - $50 = $143.33

Monthly payment entry:
Debit: Interest Expense (6600) $50
Debit: Loans Payable (2500) $143.33
Credit: Cash (1000) $193.33

Note: Only interest is expense, principal reduces liability
```

## Common Pitfalls

### Personal vs Business Expenses
- **Mistake**: Recording personal expenses as business (groceries, personal car)
- **IRS Issue**: Not deductible, can trigger audit
- **Fix**: Separate business and personal accounts, only record business expenses

### Not Recording All Transactions
- **Problem**: Forgot to record bank fee, cash purchase
- **Result**: Books don't match bank statement, can't reconcile
- **Fix**: Daily review of bank/credit card transactions, enter all

### Misclassifying Expenses
- **Error**: Recording equipment purchase as expense (should be asset + depreciation)
- **Impact**: Overstates expenses, understates assets
- **Fix**: Capitalize assets >$2,500, depreciate over useful life

### Owner's Draw vs Expense
- **Mistake**: Recording owner's draw as "salary expense"
- **Issue**: Owner's draw is not tax-deductible (equity withdrawal)
- **Fix**: Use Owner's Draws (3900) account, not expense account

### Loan Principal as Expense
- **Error**: Recording full loan payment as interest expense
- **Problem**: Principal repayment reduces liability, not an expense
- **Fix**: Split payment (interest = expense, principal = liability reduction)

### Not Reconciling Accounts
- **Symptom**: "Books balanced last I checked" (months ago)
- **Result**: Errors compound, missing transactions, can't find mistakes
- **Fix**: Monthly bank reconciliation (non-negotiable)

## Quick Reference

### Debit/Credit Quick Guide
```
Assets:        Debit to increase, Credit to decrease
Liabilities:   Credit to increase, Debit to decrease
Equity:        Credit to increase, Debit to decrease
Revenue:       Credit to increase, Debit to decrease
Expenses:      Debit to increase, Credit to decrease

Memory trick:
DEALERS (Debit increases: Expenses, Assets, Losses; Credit increases: Equity, Revenue, Sales)
```

### Common Account Numbers
```
1000: Cash
1100: Accounts Receivable
2000: Accounts Payable
2100: Credit Card Payable
3000: Owner's Equity
4000: Sales Revenue
6000: Salaries
6100: Rent
6300: Office Supplies
6400: Marketing
```

### Financial Reports
```
Income Statement (P&L):
Revenue - Expenses = Net Income

Balance Sheet:
Assets = Liabilities + Equity

Cash Flow Statement:
Operating + Investing + Financing = Net Cash Change
```

### Accounting Software Options
```
QuickBooks Online: Most popular, comprehensive ($30-90/mo)
Xero: Clean UI, strong for inventory ($13-70/mo)
FreshBooks: Best for freelancers ($17-55/mo)
Wave: Free (ad-supported), good for micro-businesses
Spreadsheet: DIY (free, requires manual work)
```

### IRS Mileage Rate (2024)
```
Business: 67c/mile (deductible)
Medical: 21c/mile
Charity: 14c/mile

Option 1: Deduct mileage (easy, no receipts needed)
Option 2: Deduct actual expenses (gas, repairs, insurance, depreciation)
Choose one (can't do both)
```

## Checklists

### Daily Bookkeeping
- [ ] Review bank/credit card transactions (new charges?)
- [ ] Record revenue (invoices sent, payments received)
- [ ] Record expenses (bills paid, purchases made)
- [ ] Attach receipts to transactions (digital or photo)
- [ ] Verify debits = credits for each entry
- [ ] Categorize by IRS expense type

### Weekly Review
- [ ] Follow up on unpaid invoices (send reminders)
- [ ] Pay bills due this week (avoid late fees)
- [ ] Review cash balance (sufficient for upcoming expenses?)
- [ ] Spot-check recent transactions (any errors?)

### Monthly Close
- [ ] Record all transactions through month-end
- [ ] Bank reconciliation (match bank statement to books)
- [ ] Credit card reconciliation (match statement to books)
- [ ] Review accounts receivable (aging report)
- [ ] Review accounts payable (upcoming bills)
- [ ] Record depreciation (if applicable)
- [ ] Accrue expenses (accrual basis only)
- [ ] Generate financial reports (P&L, Balance Sheet)
- [ ] Review for errors (negative balances, unusual amounts)
- [ ] Close period (lock to prevent changes)

### Quarterly Tasks
- [ ] Calculate estimated taxes (if self-employed)
- [ ] Review YTD financial performance (vs budget)
- [ ] Update cash flow forecast (next 3 months)
- [ ] Clean up chart of accounts (unused accounts)
- [ ] Backup accounting data (cloud + local)

### Annual Tasks
- [ ] Year-end close (final month-end close)
- [ ] Generate annual reports (P&L, Balance Sheet, Cash Flow)
- [ ] Prepare tax documents (1099s, W-2s)
- [ ] Schedule CPA review (or self-prepare taxes)
- [ ] Archive prior year records (7 years retention)
- [ ] Set up next year books (carry forward balances)

### Recording a Transaction
- [ ] Collect source document (receipt, invoice, statement)
- [ ] Identify accounts affected (minimum 2)
- [ ] Determine debit/credit for each account
- [ ] Verify debits = credits (balanced entry)
- [ ] Categorize expense (IRS category)
- [ ] Enter into accounting system (with description)
- [ ] Attach digital copy of receipt/invoice
- [ ] Double-check entry (correct amounts, accounts)
