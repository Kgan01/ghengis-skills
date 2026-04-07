---
name: home-lighting
description: Use when helping with home lighting design, smart light setup, or ambiance -- covers color theory, circadian rhythms, room profiles, Philips Hue patterns, and scene design
---

# Home Lighting

When helping with home lighting design, smart light configuration, or ambiance planning, apply these principles covering color temperature science, circadian rhythms, room-specific profiles, and scene composition.

## Core Concepts

### Color Temperature Science

Color temperature is measured in Kelvin (K):

```
2000K - Candlelight       [Warm Orange] Deep relaxation, romantic
2700K - Incandescent      [Soft White]  Evening, cozy, bedroom
3000K - Halogen           [Warm White]  Living room, dining
4000K - Cool White        [Neutral]     Office, kitchen, focus work
5000K - Daylight          [Bright]      Task lighting, makeup
6500K - Overcast Sky      [Blue White]  Alertness, morning boost
10000K - Clear Sky        [Deep Blue]   Rarely used, harsh

Human perception:
- <3000K = "Warm" (relaxing, sleepy, intimate)
- 3000-5000K = "Neutral" (functional, clear)
- >5000K = "Cool" (energizing, alert, clinical)
```

### Brightness Curves

```
Human perception is logarithmic, not linear.

Brightness levels by activity:
1-10%:   Night light, hallway safety, minimal disturbance
10-25%:  Ambient, TV watching, winding down
25-50%:  Relaxed activities, casual reading
50-75%:  Normal activities, conversation, cooking
75-90%:  Task lighting, detailed work, makeup
90-100%: Maximum output, cleaning, searching for items

Transition speeds (avoid jarring changes):
Gradual: 5-10 seconds (morning wake-up, evening wind-down)
Normal:  2-3 seconds (switching scenes)
Instant: <1 second (emergency, motion-activated)
```

### Circadian Rhythm Lighting

Optimizing light to support the human circadian cycle:

```
Morning (6-9am):
- Start: 2700K, 30% brightness
- Ramp to: 5000K, 80% brightness over 30min
- Goal: Suppress melatonin, boost alertness

Midday (10am-4pm):
- Maintain: 4000-5000K, 70-90% brightness
- Goal: Sustained focus and energy

Evening (5-8pm):
- Gradual shift: 4000K -> 2700K over 3 hours
- Brightness: 80% -> 40%
- Goal: Prepare body for sleep

Night (9pm+):
- 2000-2700K, 10-30% brightness
- Avoid blue light (>4000K)
- Goal: Maximize melatonin production

Override for:
- Night shift workers (invert cycle)
- Jet lag recovery (force new timezone)
- Winter blues (increase daytime brightness 20%)
```

### Color Theory for Scenes

```
RGB vs HSB:
- RGB (Red, Green, Blue): Hardware native, 0-255 per channel
- HSB (Hue, Saturation, Brightness): More intuitive
  - Hue: 0-360 degrees on color wheel (0=red, 120=green, 240=blue)
  - Saturation: 0-100% (0=white, 100=pure color)
  - Brightness: 0-100% (0=off, 100=max)

Common color moods:
- Red (0 deg):     Energetic, romantic, alert (avoid before sleep)
- Orange (30 deg): Warm, social, appetizing (dining)
- Yellow (60 deg): Happy, creative, attention-grabbing
- Green (120 deg): Calm, natural, balanced (study)
- Cyan (180 deg):  Cool, fresh, spa-like (bathroom)
- Blue (240 deg):  Calm, focus, sleep-friendly (bedroom)
- Purple (280 deg): Luxurious, creative, calming
- Magenta (320 deg): Energetic, playful, party

Saturation guidelines:
- 0-20%:   Subtle accent, avoid eye strain
- 20-50%:  Noticeable color, still comfortable
- 50-80%:  Bold statement, party/event mode
- 80-100%: Maximum impact, short duration only
```

## Patterns and Procedures

### Room-Based Lighting Profiles

```python
# Room lighting profiles: (kelvin, brightness%)
ROOM_PROFILES = {
    "bedroom": {
        "default":  (2700, 40),
        "wake_up":  (4500, 70),
        "sleep":    (2000, 5),
        "reading":  (3000, 60),
        "romantic": (2000, 20),   # add warm red accent
    },
    "kitchen": {
        "default":  (4000, 80),   # bright neutral for tasks
        "cooking":  (4500, 90),   # maximum visibility
        "dining":   (2700, 50),   # warm for meals
        "party":    (3000, 70),   # warm orange accent
    },
    "office": {
        "default":  (4500, 75),
        "focus":    (5000, 85),   # cool, bright for concentration
        "meeting":  (4000, 70),
        "break":    (3000, 50),   # warmer, dimmer for rest
    },
    "living_room": {
        "default":  (3000, 60),
        "tv":       (2700, 20),   # dim warm to reduce screen glare
        "reading":  (3500, 70),
        "party":    (3000, 80),   # purple accent
        "relax":    (2700, 30),
    },
    "bathroom": {
        "default":  (4000, 70),
        "morning":  (5000, 90),   # bright cool for grooming
        "shower":   (4500, 80),
        "night":    (2700, 15),   # gentle for night visits
    },
}
```

### Scene Composition Strategy

When designing multi-light scenes, coordinate lights by role:

```python
def compose_scene(lights, mood):
    """
    lights: list of light entities with type hints (ceiling, lamp, strip)
    mood: "energize", "relax", "focus", "party", "sleep"
    """
    if mood == "energize":
        # All lights bright and cool
        return [{"light": l, "temp": 5000, "bri": 85} for l in lights]

    elif mood == "relax":
        # Main lights: warm, dimmed. Accent lights: very warm, low.
        main = [l for l in lights if "ceiling" in l or "main" in l]
        accent = [l for l in lights if "lamp" in l or "strip" in l]

        scene = []
        scene.extend([{"light": l, "temp": 2700, "bri": 40} for l in main])
        scene.extend([{"light": l, "temp": 2000, "bri": 20} for l in accent])
        return scene

    elif mood == "focus":
        # Bright neutral, eliminate shadows
        return [{"light": l, "temp": 4500, "bri": 80} for l in lights]

    elif mood == "party":
        # Colorful, dynamic, high saturation
        colors = [0, 30, 120, 240, 280]  # red, orange, green, blue, purple
        scene = []
        for i, light in enumerate(lights):
            hue = colors[i % len(colors)]
            scene.append({"light": light, "hue": hue, "sat": 70, "bri": 70})
        return scene

    elif mood == "sleep":
        # Minimal, very warm
        return [{"light": l, "temp": 2000, "bri": 5} for l in lights]
```

### Adaptive Circadian Automation

```python
def calculate_circadian_settings(current_hour, wake_time=7, sleep_time=23):
    """
    Returns (kelvin, brightness%) for current time.
    """
    # Morning ramp (wake_time to wake_time+2)
    if wake_time <= current_hour < wake_time + 2:
        progress = (current_hour - wake_time) / 2
        kelvin = 2700 + (5000 - 2700) * progress
        brightness = 30 + (80 - 30) * progress
        return (int(kelvin), int(brightness))

    # Daytime (wake_time+2 to sleep_time-3)
    elif wake_time + 2 <= current_hour < sleep_time - 3:
        return (4500, 75)

    # Evening ramp (sleep_time-3 to sleep_time)
    elif sleep_time - 3 <= current_hour < sleep_time:
        progress = (current_hour - (sleep_time - 3)) / 3
        kelvin = 4500 - (4500 - 2700) * progress
        brightness = 75 - (75 - 30) * progress
        return (int(kelvin), int(brightness))

    # Night (sleep_time to wake_time)
    else:
        return (2000, 10)
```

### Philips Hue API Patterns

```python
import requests

HUE_BRIDGE_IP = "192.168.1.x"
HUE_API_KEY = "your-api-key"

# Set white temperature
def set_temp(light_id, kelvin, brightness_pct, transition_sec=2):
    # Hue uses "mired" not kelvin: mired = 1000000 / kelvin
    mired = int(1000000 / kelvin)
    bri = int(brightness_pct * 2.54)        # 0-100 -> 0-254
    transition = transition_sec * 10         # API uses deciseconds

    url = f"http://{HUE_BRIDGE_IP}/api/{HUE_API_KEY}/lights/{light_id}/state"
    payload = {"ct": mired, "bri": bri, "transitiontime": transition}
    requests.put(url, json=payload)

# Set color (HSB)
def set_color(light_id, hue_deg, sat_pct, bri_pct, transition_sec=2):
    # Hue API: hue 0-65535, sat 0-254, bri 0-254
    hue_api = int(hue_deg * 65535 / 360)
    sat_api = int(sat_pct * 2.54)
    bri_api = int(bri_pct * 2.54)
    transition = transition_sec * 10

    url = f"http://{HUE_BRIDGE_IP}/api/{HUE_API_KEY}/lights/{light_id}/state"
    payload = {"hue": hue_api, "sat": sat_api, "bri": bri_api, "transitiontime": transition}
    requests.put(url, json=payload)

# Activate a scene
def activate_scene(scene_name):
    url = f"http://{HUE_BRIDGE_IP}/api/{HUE_API_KEY}/groups/0/action"
    payload = {"scene": scene_name}
    requests.put(url, json=payload)
```

### Common Commands and Actions

When someone requests a lighting change, map it to the appropriate action:

```
"Turn on bedroom lights"     -> default room profile, 3sec transition
"Dim the lights"             -> reduce brightness by 30%, keep temperature
"Brighten living room"       -> increase brightness by 30%
"Set lights to 50%"          -> exact brightness, keep temperature
"Warm up the lights"         -> decrease kelvin by 500, keep brightness
"Cool down office"           -> increase kelvin by 500
"Movie mode living room"     -> tv scene (2700K, 20%)
"Focus mode office"          -> focus scene (5000K, 85%)
"Romantic bedroom"           -> red accent, 2000K, 20%
"Party lights"               -> colorful rotation, 70% brightness
"Goodnight"                  -> all lights to sleep mode (2000K, 5%), 10sec transition
"Good morning"               -> bedroom wake-up ramp (2700K->5000K over 30min)
```

### Energy Efficiency Tips

```
LED smart bulbs: ~9W each
100% brightness 8hrs/day = ~2.6 kWh/month per bulb
At $0.12/kWh = ~$0.31/month per bulb

Savings strategies:
- Default to 70% brightness (save ~30% energy)
- Motion sensors for hallways/bathrooms (50% reduction)
- Auto-off after 30min no motion in empty rooms
- Daylight harvesting (dim when natural light available)
- Scheduled off times (2am-6am if no one awake)

Typical home (20 bulbs):
- Always-on 100%: ~$75/year
- Smart automation: ~$35/year
- Savings: ~$40/year + extended bulb life
```

## Common Pitfalls

| Pitfall | Problem | Fix |
|---------|---------|-----|
| **Blue light before bed** | 4000K+ after 8pm disrupts sleep | Enforce <3000K after sunset or wind-down time |
| **Harsh transitions** | Instant bright light causes discomfort | Always transition over 2-5 seconds, 10+ for wake-up |
| **Ignoring natural light** | Full brightness at midday when sun is bright | Dim indoor lights when natural light is sufficient |
| **One-size-fits-all scenes** | Same "relax" in bedroom and living room | Room-specific scene configurations |
| **Color overload** | High saturation for extended periods = eye strain | Limit saturated colors to <30min, offer white light option |
| **Forgetting energy mode** | All lights at 100% wastes energy | Default to 70-80%, reserve 100% for specific tasks |

## Checklists

### Before Setting a Light Scene
- [ ] Identify room/zone for context-appropriate settings
- [ ] Check current time for circadian appropriateness
- [ ] Verify transition time (gradual for comfort)
- [ ] Confirm color temperature in acceptable range (2000-6500K)
- [ ] Ensure brightness level appropriate for activity
- [ ] Check if scene involves multiple lights (coordinate them)

### Scene Design Quality
- [ ] Color temperature matches room function
- [ ] Brightness level suits intended activity
- [ ] Transition speed comfortable (not jarring)
- [ ] Color saturation not too high for extended use
- [ ] Multiple lights coordinated (not random)
- [ ] Energy efficiency considered

### Circadian Health
- [ ] Morning: cool (4500K+) and bright (70%+)
- [ ] Evening: warm (<3000K) and dimming
- [ ] Night: very warm (2000K) and minimal (5-15%)
- [ ] Blue light avoided 2hrs before bed
- [ ] Gradual transitions support natural rhythms
