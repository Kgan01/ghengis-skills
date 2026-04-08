# Home Lighting -- Evaluation

## TC-1: Circadian Evening Wind-Down
- **prompt:** "It's 9pm and I want to set up my bedroom lights for sleep. What settings should I use?"
- **context:** User is preparing for sleep. Circadian rhythm knowledge should drive the recommendation.
- **assertions:**
  - Color temperature is 2000-2700K (very warm, no blue light)
  - Brightness is low (5-30%)
  - Transition is gradual (5-10 seconds, not instant)
  - Warns against anything above 4000K at this hour (disrupts melatonin)
  - Uses the bedroom "sleep" profile or equivalent (2000K, 5%)
- **passing_grade:** 4/5 assertions must pass

## TC-2: Multi-Light Scene Composition
- **prompt:** "I have a ceiling light, two table lamps, and an LED strip in my living room. Set up a 'movie mode' scene."
- **context:** Multiple light types in one room. Skill should coordinate them by role, not apply uniform settings.
- **assertions:**
  - Ceiling light is dimmed significantly or turned off (avoid screen glare)
  - Table lamps are set to very warm temperature (2700K or below) at low brightness (10-25%)
  - LED strip is set to a warm accent color or very low brightness
  - Overall brightness reduces screen glare (TV watching profile: ~2700K, ~20%)
  - Lights are coordinated (main vs accent distinction), not all set identically
- **passing_grade:** 4/5 assertions must pass

## TC-3: Focus Mode for Home Office
- **prompt:** "I need my office lights set for deep focus work at 2pm"
- **context:** Midday focus session. Should be cool and bright per circadian and room profile guidelines.
- **assertions:**
  - Color temperature is 4500-5000K (cool white, energizing)
  - Brightness is high (75-90%)
  - Matches the office "focus" profile from room-based profiles
  - Appropriate for midday circadian cycle (sustained alertness)
  - Does not use warm/dim settings that would induce drowsiness
- **passing_grade:** 4/5 assertions must pass

## TC-4: Party Lighting with Color
- **prompt:** "Set up party lights in my living room with colorful rotating colors"
- **context:** Event mode. Tests color theory knowledge and saturation limits.
- **assertions:**
  - Uses multiple hue values from the color wheel (red, orange, green, blue, purple)
  - Saturation is high but within recommended range (50-80%)
  - Brightness is medium-high (60-80%)
  - Different lights are assigned different colors (not all the same)
  - Mentions that high saturation should be limited to shorter durations to avoid eye strain
- **passing_grade:** 4/5 assertions must pass

## TC-5: Blue Light Before Bed Warning
- **prompt:** "Set my bedroom to 5000K bright white at 10pm, I want to read"
- **context:** User requests settings that violate circadian health principles. Skill should warn.
- **assertions:**
  - Warns that 5000K at 10pm will disrupt melatonin production and sleep
  - Recommends a lower temperature (3000K or below) for nighttime reading
  - Suggests the bedroom "reading" profile (3000K, 60%) as an alternative
  - Does not silently comply without mentioning the health concern
  - Provides the requested setting if user insists, but flags the trade-off
- **passing_grade:** 3/5 assertions must pass
