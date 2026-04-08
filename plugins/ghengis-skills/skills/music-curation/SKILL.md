---
name: music-curation
description: Use when helping with music discovery, playlist creation, or music recommendations -- covers genre classification, BPM matching, mood mapping, playlist arc design, and energy/valence scales
---

# Music Curation

When helping with music discovery, playlist creation, or DJ-style curation, follow these principles for genre-aware, tempo-matched, emotionally coherent playlists with deliberate energy arcs.

## Core Concepts

### Genre Classification

**Main Genres**
- **Pop**: Catchy, mainstream, vocal-focused (Taylor Swift, Dua Lipa)
- **Rock**: Guitar-driven, drums, rebellious (Foo Fighters, Arctic Monkeys)
- **Hip-Hop/Rap**: Beats, rhymes, urban (Drake, Kendrick Lamar)
- **Electronic/EDM**: Synthesizers, drops, dance (Calvin Harris, Deadmau5)
- **R&B/Soul**: Smooth vocals, groove (The Weeknd, SZA)
- **Country**: Storytelling, twang, acoustic (Chris Stapleton, Kacey Musgraves)
- **Jazz**: Improvisation, complex chords (Miles Davis, Coltrane)
- **Classical**: Orchestral, formal structure (Beethoven, Mozart)
- **Latin**: Spanish/Portuguese, rhythmic (Bad Bunny, Rosalia)
- **Indie/Alternative**: Non-mainstream, experimental (Tame Impala, Bon Iver)

**Sub-Genres (Important for Curation)**
```
Pop:
- Synth-pop (The Weeknd, Dua Lipa)
- Indie pop (Lorde, Clairo)
- K-pop (BTS, BLACKPINK)

Rock:
- Indie rock (The Strokes, Vampire Weekend)
- Alternative rock (Radiohead, Muse)
- Classic rock (Led Zeppelin, Pink Floyd)

Hip-Hop:
- Trap (Migos, Travis Scott)
- Conscious rap (Kendrick, J. Cole)
- Lo-fi hip-hop (Nujabes, Joji)

Electronic:
- House (Disclosure, Duke Dumont)
- Techno (Carl Cox, Richie Hawtin)
- Dubstep (Skrillex, Excision)
- Chill/Downtempo (ODESZA, Tycho)

R&B:
- Contemporary R&B (The Weeknd, SZA)
- Neo-soul (Erykah Badu, D'Angelo)
```

### BPM Matching

**BPM Ranges by Genre**
```
Lo-fi/Chill:      70-90 BPM
Hip-Hop/Trap:     70-100 BPM
R&B/Soul:         80-110 BPM
Pop:              100-130 BPM
House:            120-130 BPM
Techno:           125-135 BPM
Dubstep:          140 BPM
Drum & Bass:      160-180 BPM
```

**Smooth Transition Rules**
- **+/- 5 BPM**: Seamless (can mix without adjustment)
- **+/- 10 BPM**: Good (slight speed change, barely noticeable)
- **+/- 20 BPM**: Jarring (obvious change, use as hard transition)
- **Double/Half**: Works if rhythmic relationship (60->120, 70->140)

**Example Transitions**
```
Good:
- 120 BPM -> 125 BPM (smooth house progression)
- 90 BPM hip-hop -> 180 BPM DnB (double-time, intentional energy jump)

Bad:
- 85 BPM trap -> 150 BPM hardcore (too abrupt, no relationship)
```

**BPM Shifting Strategy**
```
Start set:    100 BPM (chill)
Build energy: 110 -> 120 -> 128 BPM (gradually increase)
Peak:         130 BPM (highest energy)
Cool down:    125 -> 115 -> 100 BPM (wind down)
```

### Mood-to-Genre Mapping

| Mood | Recommended Genres |
|------|-------------------|
| **Happy/Uplifting** | Pop, indie pop, tropical house, feel-good hip-hop |
| **Energetic/Hype** | EDM, trap, rock, drum & bass |
| **Chill/Relaxed** | Lo-fi, downtempo, ambient, acoustic |
| **Sad/Melancholic** | Indie, alternative, R&B ballads, acoustic |
| **Focus/Productivity** | Lo-fi beats, classical, post-rock, ambient |
| **Party/Dance** | House, funk, disco, Latin, Afrobeats |
| **Romantic** | R&B, soul, jazz, slow pop |
| **Angry/Aggressive** | Metal, hard rock, dubstep, aggressive rap |

**Genre Combinations by Context**
```
Workout:
- Trap + EDM + Hard rock (high BPM, intense)

Study/Focus:
- Lo-fi hip-hop + Jazz + Classical (70-90 BPM, no lyrics)

Dinner Party:
- Jazz + Bossa nova + Indie folk (90-110 BPM, sophisticated)

Road Trip:
- Pop + Indie rock + Alternative (110-130 BPM, singable)

Late Night Chill:
- Downtempo + Ambient + Neo-soul (80-100 BPM, mellow)
```

### Playlist Arc (Energy Curve)

**Classic Arc Structure**
```
1. Intro (10% of playlist): Set the tone, ease listeners in
   - BPM: Low-medium (90-110)
   - Energy: 3-4/10
   - Example: Indie pop, chill electronic

2. Build (30%): Gradually increase energy
   - BPM: Medium (110-120)
   - Energy: 5-7/10
   - Example: Pop, upbeat indie, light EDM

3. Peak (20%): Highest energy, dancefloor bangers
   - BPM: High (125-135)
   - Energy: 9-10/10
   - Example: House, trap, hype hip-hop

4. Sustain (20%): Maintain high energy with variety
   - BPM: Medium-high (120-128)
   - Energy: 7-8/10
   - Example: Mix of genres at consistent BPM

5. Cool Down (20%): Wind down, prepare to end
   - BPM: Medium-low (100-110)
   - Energy: 4-5/10
   - Example: Slower pop, R&B, acoustic

Total: 50-100 tracks (2-5 hours)
```

**Alternative Arcs**

| Arc | Structure | Best For |
|-----|-----------|----------|
| **Wave** | Build -> Peak -> Drop -> Build -> Peak -> End | Long playlists (5+ hours), DJ sets |
| **Flat** | Set energy level -> Maintain throughout | Background music (cafe, office, study) |
| **Descending** | High energy -> Gradually decrease -> End calm | Evening playlists, bedtime, relaxation |

### Audio Features (Spotify Scale)

When working with Spotify's API or similar services, these features describe track characteristics:

| Feature | Scale | Description |
|---------|-------|-------------|
| **Energy** | 0-1 | Intensity and activity level |
| **Valence** | 0-1 | Musical positivity (happy vs sad) |
| **Danceability** | 0-1 | How suitable for dancing |
| **Acousticness** | 0-1 | Acoustic vs electronic |
| **Instrumentalness** | 0-1 | Vocal vs instrumental |
| **Speechiness** | 0-1 | Amount of spoken words |
| **Tempo** | BPM | Beats per minute |
| **Loudness** | -60 to 0 dB | Volume level |
| **Key** | 0-11 | Musical key (C through B) |
| **Mode** | 0 or 1 | Minor (0) or Major (1) |

**Energy Levels**
```
0.0-0.3: Very low (ambient, meditation)
0.3-0.5: Low (chill, study, background)
0.5-0.7: Medium (casual listening, driving)
0.7-0.9: High (workout, party, upbeat)
0.9-1.0: Very high (intense, hype, peak moments)
```

**Valence (Mood) Scale**
```
0.0-0.3: Sad, melancholic, dark
0.3-0.5: Neutral, introspective
0.5-0.7: Somewhat happy, positive
0.7-1.0: Very happy, euphoric, uplifting
```

### Crossfade Settings

| Genre | Crossfade | Notes |
|-------|-----------|-------|
| Electronic/House | 8-12 seconds | Long blend, extended outros |
| Pop | 5-8 seconds | Natural, not too long |
| Hip-Hop | 0-3 seconds | Hard cuts, respect song structure |
| Rock | 3-5 seconds | Shorter, preserve song endings |
| Classical | 0 seconds | Respect silence between movements |
| Mixed playlist | 5-8 seconds | Safe default |

## Patterns and Procedures

### Building a Playlist from Scratch

```
1. Define purpose:
   - Mood: Energetic workout? Chill study?
   - Duration: 1 hour? 4 hours?
   - Audience: Personal? Party? Background?

2. Choose arc:
   - Workout: Flat high energy (130 BPM throughout)
   - Party: Classic arc (build -> peak -> sustain -> cool)
   - Study: Flat low energy (80 BPM, instrumental)

3. Seed with core tracks:
   - Pick 10-20 tracks that define the vibe
   - Check BPMs (group by similar tempo)

4. Expand with recommendations:
   - Use seed tracks to find similar music
   - Set target energy, valence, tempo
   - Pull 50-100 candidate tracks

5. Arrange by arc:
   - Sort by BPM (low to high for build)
   - Group similar genres together (avoid jarring switches)
   - Check flow (listen to transitions)

6. Fine-tune:
   - Remove outliers (wrong vibe, wrong BPM)
   - Add variety (don't repeat artists back-to-back)
   - Adjust crossfade (5-8 seconds for most playlists)

7. Test and iterate:
   - Listen to first 10 tracks (does intro work?)
   - Skip to peak (is energy right?)
   - Check cool-down (does it wind down smoothly?)
```

### Spotify API Curation (Python)

```python
import spotipy

sp = spotipy.Spotify(auth_manager=SpotifyOAuth())

# Get user's top tracks (personalization)
top_tracks = sp.current_user_top_tracks(limit=10, time_range='short_term')
seed_tracks = [track['id'] for track in top_tracks['items'][:5]]

# Get audio features (for BPM/energy)
features = sp.audio_features(seed_tracks)
avg_energy = sum([f['energy'] for f in features]) / len(features)
avg_tempo = sum([f['tempo'] for f in features]) / len(features)

# Get recommendations (similar vibe, specific BPM)
recs = sp.recommendations(
    seed_tracks=seed_tracks,
    target_energy=avg_energy,
    target_tempo=avg_tempo,
    limit=50
)

# Create playlist
playlist = sp.user_playlist_create(
    user_id,
    'AI-Curated Workout Mix',
    description=f'High-energy tracks around {int(avg_tempo)} BPM'
)

# Add tracks
track_uris = [track['uri'] for track in recs['tracks']]
sp.playlist_add_items(playlist['id'], track_uris)
```

### Live DJ Queue Management

```
1. Start with opening track (sets tone)
2. Add next 3-5 tracks to queue (plan ahead)
3. Monitor crowd/mood:
   - High energy? -> Add faster, more intense
   - Losing interest? -> Switch genre, surprise element
   - Peak time? -> Drop the banger
4. Adjust on the fly:
   - Skip track if not working
   - Add unexpected track for variety
5. Build toward peak (last 30 min of event)
6. Cool down final 15 min (lower BPM, chill vibes)
7. End on memorable note (crowd-pleaser)
```

## Common Pitfalls

| Pitfall | Problem | Fix |
|---------|---------|-----|
| **Genre whiplash** | Chill lo-fi -> death metal -> country | Group similar genres, gradual transitions |
| **BPM chaos** | 90 -> 140 -> 75 BPM (no pattern) | Gradual BPM changes (+/- 10 per track) |
| **All climax, no arc** | Every track is a banger | Build energy gradually, create contrast |
| **Ignoring song endings** | Crossfade over epic outro | Use 0-second crossfade for important endings |
| **Over-shuffling** | Random shuffle on curated playlist | Disable shuffle to preserve planned arc |
| **Repetitive artists** | Same artist 3 times in 10 tracks | Spread out same artist (min 5 tracks apart) |

## Quick Reference

### Playlist Length Guidelines

```
Workout:     45-60 min (12-15 tracks @ 130 BPM)
Commute:     30-45 min (10-12 tracks)
Party:       3-5 hours (60-100 tracks, arc structure)
Study:       2-4 hours (30-60 tracks, consistent energy)
Background:  8+ hours (200+ tracks, variety)
```

## Checklists

### Before Building Playlist
- [ ] Define purpose (workout, party, study, road trip)
- [ ] Choose duration (1 hour, 4 hours, 8 hours)
- [ ] Identify target mood (energetic, chill, happy, sad)
- [ ] Select arc type (classic build, flat, wave)
- [ ] Determine audience (personal, public, event)

### Curating Track List
- [ ] Seed with 10-20 core tracks (define the vibe)
- [ ] Check BPMs (group by similar tempo)
- [ ] Pull 50-100 candidate tracks via recommendations
- [ ] Remove outliers (wrong genre, wrong mood)
- [ ] Check for artist repetition (spread out same artist)

### Arranging Playlist
- [ ] Sort by BPM (if building energy arc)
- [ ] Group similar genres together
- [ ] Place intro tracks (ease listeners in)
- [ ] Build to peak (30-50% through playlist)
- [ ] Sustain energy (avoid immediate drop)
- [ ] Cool down at end (wind down smoothly)
- [ ] Check transitions (listen to adjacent tracks)

### Final Review
- [ ] Listen to first 10 tracks (does intro work?)
- [ ] Jump to peak (is energy right?)
- [ ] Check cool-down (smooth wind-down?)
- [ ] Verify BPM flow (gradual changes?)
- [ ] Test crossfades (smooth transitions?)
- [ ] Check total duration (matches intent?)
