# ESP32 -- Evaluation

## TC-1: Audio Buffer Allocation
- **prompt:** "I need to set up an audio capture buffer for my ESP32-S3 with an INMP441 microphone"
- **context:** I2S audio input setup. Tests memory management and PSRAM allocation knowledge.
- **assertions:**
  - Allocates buffer using `ps_malloc()` in PSRAM (not `malloc` or `new` on SRAM)
  - Allocation happens once at startup (global scope or `setup()`) -- not inside a loop or callback
  - Buffer size is defined as a constant (e.g., `constexpr size_t AUDIO_BUF_BYTES = 4096`)
  - Includes a null check after allocation (`assert(audioBuf != nullptr)` or equivalent)
  - I2S config uses appropriate settings (16kHz sample rate, 32-bit, left channel for INMP441)
- **passing_grade:** 4/5 assertions must pass

## TC-2: FreeRTOS Task Pinning
- **prompt:** "I have audio processing and WiFi/WebSocket tasks. How should I organize them on the ESP32?"
- **context:** Dual-core ESP32 task management. Tests core affinity knowledge.
- **assertions:**
  - Audio task is pinned to core 1 using `xTaskCreatePinnedToCore`
  - Network/WiFi task is pinned to core 0
  - Explains why: WiFi interrupts on core 0 would cause audio jitter if audio ran on the same core
  - Each task has appropriate stack size (8192 or similar)
  - Audio task has higher priority than network task
- **passing_grade:** 4/5 assertions must pass

## TC-3: State Machine Design
- **prompt:** "My ESP32 voice assistant needs states: idle, listening, processing, and speaking. How should I structure this?"
- **context:** Device behavior management. Tests state machine pattern knowledge.
- **assertions:**
  - Uses an enum class for states (e.g., `enum class State { IDLE, LISTENING, PROCESSING, SPEAKING }`)
  - Has a `transitionTo()` function that validates legal transitions
  - Main loop uses a switch statement on `currentState`
  - Each state has its own handler function (e.g., `handleIdle()`, `handleListening()`)
  - Does not use bare integers or strings for state representation
- **passing_grade:** 4/5 assertions must pass

## TC-4: Anti-Pattern -- malloc in Audio Loop
- **prompt:** "Here's my audio processing loop:\n```cpp\nvoid audioLoop() {\n  while(true) {\n    uint8_t* buf = (uint8_t*)malloc(4096);\n    i2s_read(I2S_NUM_0, buf, 4096, &bytesRead, portMAX_DELAY);\n    process(buf);\n    free(buf);\n  }\n}\n```\nIs there a problem?"
- **context:** User has heap allocation inside a hot audio loop. Classic ESP32 anti-pattern.
- **assertions:**
  - Identifies `malloc` inside the loop as a critical problem (non-deterministic, causes audio glitches)
  - Recommends pre-allocating the buffer once at startup with `ps_malloc()` (PSRAM)
  - Explains that heap allocation can block for milliseconds, causing DMA underruns
  - Mentions SRAM fragmentation as an additional risk from repeated malloc/free
  - Refactored code moves allocation outside the loop
- **passing_grade:** 4/5 assertions must pass

## TC-5: WiFi Setup with Captive Portal
- **prompt:** "I need my ESP32 to let users configure WiFi credentials through a captive portal"
- **context:** First-time device provisioning. Tests WiFiManager pattern knowledge.
- **assertions:**
  - Uses `WiFiManager` library for captive portal
  - Calls `wm.autoConnect("DeviceName-Setup")` with a descriptive AP name
  - Sets a config portal timeout (e.g., 180 seconds) to avoid hanging indefinitely
  - Restarts the device on connection failure (`ESP.restart()`)
  - WiFi setup runs on core 0 (not the audio core)
- **passing_grade:** 4/5 assertions must pass
