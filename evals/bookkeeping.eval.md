# Bookkeeping -- Evaluation

## TC-1: Happy Path -- Record a Business Transaction
- **prompt:** "I paid $1,200 for office rent this month using my business checking account. How do I record this?"
- **context:** Straightforward cash expense. Tests double-entry accounting and journal entry formatting.
- **assertions:**
  - Response provides a proper double-entry journal entry (debit and credit)
  - Debit goes to Rent Expense (6100) and credit goes to Cash (1000)
  - Amounts balance ($1,200 debit = $1,200 credit)
  - Entry includes a date and description field
  - IRS expense category is identified (Rent -- deductible under Schedule C)
- **passing_grade:** 4/5 assertions must pass

## TC-2: Edge Case -- Personal vs Business Expense Confusion
- **prompt:** "I bought groceries for $200 and also picked up printer ink for $45 at the same store on my business credit card. How do I record this?"
- **context:** Mixed personal and business purchase on a business card. Tests the personal vs business expense pitfall.
- **assertions:**
  - Response separates the personal expense ($200 groceries) from the business expense ($45 printer ink)
  - Groceries are flagged as non-deductible personal expense
  - Printer ink is categorized as Office Supplies (6300) or similar deductible category
  - Response warns about the IRS risk of recording personal expenses as business expenses
  - If the full $245 was on a business credit card, response shows how to handle the personal portion (owner's draw or reimburse)
- **passing_grade:** 4/5 assertions must pass

## TC-3: Happy Path -- Loan Payment Recording
- **prompt:** "I made a $500 monthly payment on my business loan. The interest portion is $75 and the rest is principal. How do I book this?"
- **context:** Loan payment that must be split between interest expense and principal reduction. Tests the common pitfall of booking full payment as expense.
- **assertions:**
  - Response splits the payment: $75 to Interest Expense and $425 to reduce Loans Payable
  - Credit goes to Cash (1000) for the full $500
  - Response explains that only interest is deductible, not principal
  - The common pitfall "Loan Principal as Expense" is avoided
  - Debits equal credits in the journal entry
- **passing_grade:** 4/5 assertions must pass

## TC-4: Edge Case -- Equipment Purchase vs Expense
- **prompt:** "I bought a new laptop for my business for $2,800. Is that just an expense?"
- **context:** Capital expenditure above the $2,500 threshold. Tests asset capitalization vs expensing rules.
- **assertions:**
  - Response identifies this as a capital expense, not a regular operating expense
  - Explains the $2,500 threshold rule (assets above this should be capitalized and depreciated)
  - Shows the correct journal entry: debit Equipment (asset account like 1500), credit Cash
  - Mentions depreciation as the method to expense it over time
  - Does NOT record it as a single expense debit (avoiding the misclassification pitfall)
- **passing_grade:** 4/5 assertions must pass

## TC-5: Quality Check -- Cash vs Accrual Basis
- **prompt:** "I sent an invoice to a client for $5,000 on January 15th. They paid on February 5th. When do I record the revenue?"
- **context:** Tests understanding of cash vs accrual accounting basis and correct application of each.
- **assertions:**
  - Response asks which basis the user follows (cash or accrual) or explains both
  - Cash basis answer: record revenue on February 5th (when cash received)
  - Accrual basis answer: record revenue on January 15th (when earned/invoiced)
  - Explains the journal entries for each basis (Accounts Receivable for accrual, direct Cash for cash basis)
  - Mentions IRS rules on which businesses can use which basis
- **passing_grade:** 4/5 assertions must pass
