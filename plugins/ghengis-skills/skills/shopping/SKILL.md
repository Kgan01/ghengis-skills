---
name: shopping
description: Use when helping with purchase decisions, product research, or deal hunting — covers price comparison frameworks, evaluation criteria, and tier-based recommendations
---

# Shopping & Product Research

## When to Use
When helping with purchase decisions, product comparisons, deal hunting, gift shopping, finding the best value, or evaluating products across price tiers.

## Core Methodology

### Price Research Strategy
```
1. Search the product across 3+ sources
2. Compare: Amazon, Target, Walmart, Best Buy, specialty retailers
3. Check for active coupons, promo codes, or cashback
4. Factor in shipping cost (free shipping thresholds matter)
5. Check refurbished/open-box options if user is budget-conscious
6. Note price history context: "This is $20 below the typical price"
```

### Product Evaluation Framework
For every product, evaluate:
- **Price**: Actual cost including shipping and tax
- **Reviews**: Average rating AND number of reviews (4.5 with 10k reviews > 4.8 with 12 reviews)
- **Quality indicators**: Brand reputation, materials, warranty
- **Availability**: In stock now vs backorder, delivery timeframe
- **Alternatives**: Always present 2-3 options at different price points

### Price Tier Presentation
Always present options in 3 tiers:
```
Budget:  $XX -- [product name] -- key tradeoff (e.g., "plastic build")
Mid:     $XX -- [product name] -- best value (RECOMMEND this one)
Premium: $XX -- [product name] -- why it costs more (e.g., "titanium, 5yr warranty")
```
Default recommendation is mid-tier unless user specifies budget or premium preference.

## Patterns & Procedures

### Standard Shopping Flow
```
1. User: "Find me a [product]" / "I need a [thing]"
2. Clarify requirements if vague: size, color, budget, use case
3. Search for the product across multiple sources
4. Pick top 3-5 candidates across price tiers
5. For top candidates, gather specs, reviews, and pricing details
6. Present comparison table: price, rating, key specs, pros/cons
7. Recommend the best value option
8. If user approves: provide purchase link or details
```

### Deal Hunting
```
1. Search for "best deals [product] [current month] [year]"
2. Check deal aggregators: Slickdeals, CamelCamelCamel, Honey
3. Compare current price vs historical low
4. Report: "Current price: $X. Historical low: $Y. This is a [good/bad/average] deal."
```

### Gift Shopping
```
1. Ask: recipient, occasion, budget range, interests
2. Generate 5 gift ideas spanning categories
3. For each: product link, price, why it fits the recipient
4. Include one "wildcard" option that's unexpected but thoughtful
```

### Restock / Repeat Purchase
```
1. Check if user has mentioned previous purchases
2. If found: "Last time you bought [product] from [retailer] for $X"
3. Check if price has changed
4. Offer to reorder same or suggest alternatives if price went up
```

## Common Pitfalls

### Price Pitfalls
- **Ignoring shipping**: A $5 cheaper product with $8 shipping is worse
- **Per-unit math**: Always calculate per-unit price for bulk items ($/oz, $/count)
- **Subscription traps**: Flag if price requires subscription (e.g., "Subscribe & Save" on Amazon)
- **Third-party seller risk**: On Amazon, note if sold by Amazon vs third-party (return policy differs)

### Review Pitfalls
- **Fake review signals**: All 5-star, generic phrasing, reviews posted on same day
- **Review count matters**: Under 50 reviews = unreliable. Over 1000 = trustworthy average.
- **Read negative reviews**: The 1-3 star reviews reveal real problems (look for patterns, not one-offs)
- **Review recency**: Ignore reviews older than 2 years for electronics (quality may have changed)

### Comparison Pitfalls
- **Spec sheet lies**: "1080p" camera could be interpolated, not native. Read fine print.
- **Model number confusion**: Samsung has 47 similar model numbers. Verify exact SKU.
- **Discontinued vs current**: Old model at low price might be a deal OR a dead-end for support/parts.

## Quick Reference

### Price Comparison Sources
| Retailer | Best for | Notes |
|----------|----------|-------|
| Amazon | Everything, fast shipping | Check third-party vs sold-by-Amazon |
| Walmart | Groceries, household, budget | Free shipping over $35 |
| Target | Home, kids, beauty | RedCard saves 5% |
| Best Buy | Electronics, appliances | Price match guarantee |
| Costco | Bulk, quality brands | Membership required |
| eBay | Used, refurbished, rare | Check seller rating |
| Wirecutter | Expert reviews | NYT-owned, thorough testing |

### Budget Interpretation
| User says | Interpret as |
|-----------|-------------|
| "cheap" / "budget" | Bottom 25% price range for category |
| "reasonable" / "good value" | Mid-range, best bang for buck |
| "best" / "top of the line" | Premium, price is secondary |
| "under $X" | Hard ceiling, include options 10-20% below |
| No budget mentioned | Default to mid-range, show all 3 tiers |

### Electronics Decision Factors
```
Laptop: RAM > SSD > CPU > Screen > Battery > Weight
Phone: Camera > Battery > Screen > Storage > CPU
Headphones: Sound > Comfort > Battery > ANC > Mic
TV: Panel type > Size > HDR > Refresh rate > Smart OS
```

### Household Decision Factors
```
Appliances: Reliability > Features > Noise > Energy rating > Price
Furniture: Comfort > Durability > Dimensions > Assembly > Style
Kitchen tools: Material > Dishwasher safe > Ergonomics > Brand
```

## Checklists

### Before Recommending
- [ ] Searched 3+ sources for price comparison
- [ ] Checked review count AND average (not just average)
- [ ] Read at least 3 negative reviews for top pick
- [ ] Verified in-stock and shipping timeframe
- [ ] Presented 3 price tiers (budget/mid/premium)
- [ ] Included per-unit price for consumables
- [ ] Flagged any subscription requirements

### Before Purchase Handoff
- [ ] User confirmed which product they want
- [ ] User confirmed budget is acceptable
- [ ] Provided direct link to the product
- [ ] Noted return policy and warranty
