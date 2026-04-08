---
name: esp32
description: Use when working with ESP32 firmware or IoT hardware projects — covers PlatformIO build system, I2S audio, WiFi/BLE patterns, memory management, and state machine design
allowed-tools: Read Write Edit Glob Grep Bash(pio *)
---

# PlatformIO + ESP32-S3

## When This Applies

Working on any ESP32 firmware or IoT hardware project — C++ source, `platformio.ini`, audio capture/playback, network connectivity, BLE, or FreeRTOS task management.

## Key Concepts

The ESP32-S3 has **520 KB SRAM** and **8 MB PSRAM**. SRAM is the hot constraint — allocate large buffers (audio, network) once at startup in PSRAM and never allocate inside ISRs or audio loops. Use a strict state machine for device behavior. Audio I/O uses I2S: an INMP441 MEMS microphone for input and a MAX98357A amplifier for output. DMA buffers are pre-allocated so the I2S driver never stalls. Network and audio workloads should be pinned to different FreeRTOS cores — audio on **core 1**, network/WiFi on **core 0** — to prevent WiFi interrupt jitter from corrupting audio timing. Connectivity is layered: WiFiManager for captive-portal provisioning, mDNS for local discovery, WebSocket for real-time server communication, and NimBLE for BLE peripheral mode.

## Common Patterns

**Pre-allocated DMA audio buffer (PSRAM):**
```cpp
// In global scope — allocated once at startup, never inside a function
static uint8_t* audioBuf = nullptr;
constexpr size_t AUDIO_BUF_BYTES = 4096;

void setup() {
  audioBuf = (uint8_t*)ps_malloc(AUDIO_BUF_BYTES);  // PSRAM allocation
  assert(audioBuf != nullptr);
}
```

**I2S microphone (INMP441) initialization:**
```cpp
#include <driver/i2s.h>

void i2s_mic_init() {
  i2s_config_t cfg = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = 16000,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 8,
    .dma_buf_len = 256,
    .use_apll = false,
  };
  i2s_driver_install(I2S_NUM_0, &cfg, 0, nullptr);
  // pin assignment follows...
}
```

**State machine transitions:**
```cpp
enum class State { IDLE, LISTENING, PROCESSING, SPEAKING };
State currentState = State::IDLE;

void transitionTo(State next) {
  // validate legal transitions before applying
  currentState = next;
}

void loop() {
  switch (currentState) {
    case State::IDLE:      handleIdle();      break;
    case State::LISTENING: handleListening(); break;
    case State::PROCESSING:handleProcessing();break;
    case State::SPEAKING:  handleSpeaking();  break;
  }
}
```

**FreeRTOS task pinning:**
```cpp
// Audio task pinned to core 1
xTaskCreatePinnedToCore(
  audioTask, "audio", 8192, nullptr, 5, &audioTaskHandle, 1
);

// Network/WebSocket task pinned to core 0
xTaskCreatePinnedToCore(
  networkTask, "network", 8192, nullptr, 3, &networkTaskHandle, 0
);
```

**WiFiManager captive portal:**
```cpp
#include <WiFiManager.h>

void startWiFi() {
  WiFiManager wm;
  wm.setConfigPortalTimeout(180);
  if (!wm.autoConnect("MyDevice-Setup")) {
    ESP.restart();
  }
}
```

**mDNS service advertisement:**
```cpp
#include <ESPmDNS.h>

void startMDNS() {
  if (MDNS.begin("my-device")) {
    MDNS.addService("http", "tcp", 8080);
  }
}
```

**WebSocket client with auto-reconnect:**
```cpp
#include <WebSocketsClient.h>

WebSocketsClient ws;

void wsEvent(WStype_t type, uint8_t* payload, size_t length) {
  if (type == WStype_DISCONNECTED) {
    // reconnect is handled automatically by the library's reconnect interval
  }
}

void setupWebSocket(const char* host, uint16_t port) {
  ws.begin(host, port, "/ws");
  ws.onEvent(wsEvent);
  ws.setReconnectInterval(3000);
}

// In network task loop:
// ws.loop();
```

**BLE peripheral via NimBLE:**
```cpp
#include <NimBLEDevice.h>

void startBLE() {
  NimBLEDevice::init("MyDevice");
  auto* server = NimBLEDevice::createServer();
  auto* svc = server->createService("180D");
  auto* chr = svc->createCharacteristic("2A37",
    NIMBLE_PROPERTY::READ | NIMBLE_PROPERTY::NOTIFY);
  svc->start();
  NimBLEDevice::startAdvertising();
}
```

**Heap check guard:**
```cpp
void assertHeapHealthy() {
  if (ESP.getFreeHeap() < 50 * 1024) {
    ESP_LOGE("heap", "Free heap critical: %u bytes", ESP.getFreeHeap());
  }
}
```

## Anti-Patterns

**`malloc` / `new` inside the audio loop** — heap allocation is non-deterministic and can block for milliseconds, causing audio glitches and DMA underruns. Allocate all buffers once at startup with `ps_malloc()`.

**`String` concatenation in hot paths** — Arduino `String` objects allocate and free heap on every `+` operation, fragmenting SRAM rapidly. Use `char[]` buffers and `snprintf()` for all formatting in loops and callbacks.

**`delay()` in event-responsive tasks** — `delay()` blocks the calling task entirely, preventing it from processing incoming events (WebSocket messages, BLE writes). Use `vTaskDelay()` in FreeRTOS tasks or restructure to non-blocking state polling.

**Blocking WiFi operations on the audio core** — WiFi driver callbacks and `WiFi.begin()` can block for hundreds of milliseconds. All WiFi/network work must run on core 0; the audio task on core 1 must never call WiFi APIs directly.

**`Serial.println()` in production / ISR context** — serial output is slow and unsafe inside ISRs. Gate all debug output behind a compile-time flag (`#ifdef DEBUG_SERIAL`) and use the ESP-IDF logging macros (`ESP_LOGI`, `ESP_LOGD`) which respect log levels and can be silenced at build time.

## Validation

- `pio run` — compiles firmware; zero errors and zero warnings is the standard
- `pio run -t upload` — flashes to the connected ESP32; watch serial output for boot messages confirming I2S, WiFi, and WebSocket init
- After boot, query `ESP.getFreeHeap()` via serial console or a debug endpoint — must stay above **50 KB** during normal operation; values below that indicate a memory leak or over-allocation
- Verify state machine never gets stuck: add `ESP_LOGD` at each transition during development and confirm the full cycle completes cleanly under load
