# Shopping -- Evaluation

## TC-1: Happy Path -- Product Recommendation with Tiers
- **prompt:** "I need a good pair of wireless headphones for working from home."
- **context:** No budget specified, general use case. Tests the 3-tier presentation and default mid-range recommendation.
- **assertions:**
  - Response presents options in 3 price tiers (budget, mid-range, premium)
  - Each tier includes product name, price, and key tradeoff or differentiator
  - Default recommendation is the mid-tier option (since no budget was specified)
  - Review data is referenced (rating AND review count, not just star average)
  - Decision factors relevant to headphones are considered (sound, comfort, battery, ANC, mic)
- **passing_grade:** 4/5 assertions must pass

## TC-2: Edge Case -- Budget Constraint
- **prompt:** "Find me a laptop under $500. I just need it for web browsing and documents."
- **context:** Hard budget ceiling with simple use case. Tests budget interpretation and price tier adjustment.
- **assertions:**
  - All recommended options are under $500 (hard ceiling respected)
  - Options include some at 10-20% below the ceiling (not all at exactly $499)
  - Shipping costs are factored in or mentioned (a $495 laptop with $15 shipping breaks budget)
  - Decision factors for laptops are applied (RAM, SSD prioritized for the use case)
  - Refurbished or open-box options are mentioned as budget-friendly alternatives
- **passing_grade:** 4/5 assertions must pass

## TC-3: Edge Case -- Fake Review Signals
- **prompt:** "I found this amazing blender on Amazon with 4.9 stars. Should I buy it?"
- **context:** User trusts a high star rating without scrutiny. Tests review quality evaluation methodology.
- **assertions:**
  - Response asks about or checks the number of reviews (not just the star average)
  - Warns about fake review signals (all 5-star, generic phrasing, reviews posted same day)
  - Recommends reading negative reviews (1-3 stars) to find real problems
  - Notes the threshold: under 50 reviews is unreliable
  - Suggests checking the seller (sold by Amazon vs third-party) and its impact on returns
- **passing_grade:** 4/5 assertions must pass

## TC-4: Happy Path -- Gift Shopping
- **prompt:** "I need a birthday gift for my 30-year-old brother who likes cooking. Budget is around $75."
- **context:** Gift shopping scenario with recipient details, occasion, and budget. Tests the gift shopping flow.
- **assertions:**
  - Response generates multiple gift ideas (at least 3-5) spanning different categories within cooking
  - Each suggestion includes approximate price and why it fits the recipient
  - At least one "wildcard" or unexpected-but-thoughtful option is included
  - All suggestions fall within or near the $75 budget
  - Options are not all from the same subcategory (e.g., not all knives -- mix of tools, books, experiences)
- **passing_grade:** 4/5 assertions must pass

## TC-5: Quality Check -- Per-Unit Price and Subscription Traps
- **prompt:** "Should I buy this 24-pack of protein bars for $36 on Amazon or the 12-pack for $22 at Walmart?"
- **context:** Bulk comparison requiring per-unit math and awareness of hidden costs. Tests price pitfall methodology.
- **assertions:**
  - Per-unit price is calculated for both options ($1.50/bar vs $1.83/bar)
  - Shipping cost is factored in for the Amazon option (free shipping threshold or Prime)
  - Response checks whether the Amazon price requires Subscribe & Save (subscription trap)
  - Response notes whether the seller is Amazon or third-party (return policy difference)
  - A clear recommendation is made based on true per-unit cost after all factors
- **passing_grade:** 4/5 assertions must pass
