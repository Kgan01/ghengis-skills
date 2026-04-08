# Music Curation -- Evaluation

## TC-1: Workout Playlist
- **prompt:** "Build me a 45-minute high-energy workout playlist"
- **context:** User wants a consistent high-energy playlist for exercise. Should be flat-arc, high BPM.
- **assertions:**
  - Selects genres appropriate for workouts (trap, EDM, hard rock, hype hip-hop)
  - BPM range is consistently high (120-140 BPM)
  - Uses a flat arc (sustained energy throughout, not classic build/peak/cool)
  - Track count is approximately 12-15 tracks for 45 minutes
  - Does not include low-energy or chill tracks that would break the workout flow
- **passing_grade:** 4/5 assertions must pass

## TC-2: Dinner Party Playlist with Arc
- **prompt:** "Create a 3-hour dinner party playlist that starts chill, builds energy, then winds down at the end"
- **context:** Social event playlist. Requires a classic arc with genre-appropriate music.
- **assertions:**
  - Uses the classic arc structure: intro (low energy) -> build -> peak -> sustain -> cool down
  - Genre selection fits a dinner party (jazz, bossa nova, indie folk, light electronic)
  - BPM transitions are gradual (no jumps greater than 20 BPM between adjacent tracks)
  - Track count is approximately 60-100 tracks for 3 hours
  - No genre whiplash (similar genres grouped together)
- **passing_grade:** 4/5 assertions must pass

## TC-3: Mood-Based Recommendation
- **prompt:** "I'm feeling melancholic. What should I listen to?"
- **context:** User provides a mood, not a genre or activity. Skill should map mood to appropriate genres.
- **assertions:**
  - Maps "melancholic" to appropriate genres (indie, alternative, R&B ballads, acoustic)
  - Suggests tracks or artists with low valence (0.0-0.3 on the Spotify scale)
  - BPM is in the slower range (70-100 BPM)
  - Does not recommend high-energy party music
  - Provides specific artist or track examples (not just genre names)
- **passing_grade:** 4/5 assertions must pass

## TC-4: BPM Transition Validation
- **prompt:** "I want to transition from a lo-fi hip-hop set (85 BPM) to house music (128 BPM). How do I do that smoothly?"
- **context:** User needs to bridge a large BPM gap between genres. Tests BPM shifting strategy knowledge.
- **assertions:**
  - Acknowledges the 43 BPM gap is too large for a direct transition
  - Proposes a gradual BPM ramp (e.g., 85 -> 95 -> 110 -> 120 -> 128)
  - Suggests intermediate genre bridges (e.g., R&B, pop, light electronic)
  - Mentions the double-time relationship option (85 BPM -> 170 BPM DnB as an alternative)
  - Does not recommend a hard cut from 85 to 128 BPM
- **passing_grade:** 3/5 assertions must pass

## TC-5: Study/Focus Playlist
- **prompt:** "I need a 2-hour study playlist. No lyrics, consistent energy, nothing distracting."
- **context:** Background music for focused work. Should be flat arc, low energy, instrumental.
- **assertions:**
  - Selects instrumental genres (lo-fi beats, classical, post-rock, ambient)
  - BPM is consistently low (70-90 BPM)
  - Uses a flat arc (consistent energy throughout)
  - Track count is approximately 30-60 tracks for 2 hours
  - Explicitly avoids tracks with vocals/lyrics (instrumentalness high)
  - Recommends crossfade settings appropriate for the genre (5-8 seconds)
- **passing_grade:** 4/6 assertions must pass
