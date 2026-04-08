---
name: flutter-dart
description: Use when building or modifying Flutter/Dart applications — covers widget patterns, state management, platform channels, navigation, and common Dart conventions
allowed-tools: Read Write Edit Glob Grep Bash(flutter *) Bash(dart *)
---

# Flutter + Dart Mobile

## When This Applies

Working on any Flutter/Dart application — widgets, stores, services, native platform bridges, or Dart business logic.

## Key Concepts

Flutter uses a widget tree where everything is a widget. Prefer **StatelessWidget** for pure display and **StatefulWidget** only when local mutable state is needed. Stores follow an observable pattern (typically `ChangeNotifier` or a reactive store via Provider/Riverpod). Services are singletons that wrap platform or network concerns. Platform communication uses **MethodChannel** for request/response calls and **EventChannel** for native-to-Dart push notifications. All colors and typography should come from the app's theme system — never use hard-coded values or raw `Colors.*` constants outside the theme definition file.

## Common Patterns

**StatelessWidget (preferred for pure display):**
```dart
class StatusBadge extends StatelessWidget {
  final String label;
  final bool active;

  const StatusBadge({super.key, required this.label, this.active = false});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      color: active ? theme.colorScheme.primary : theme.colorScheme.surface,
      child: Text(label, style: theme.textTheme.bodySmall),
    );
  }
}
```

**StatefulWidget (only when local mutable state is needed):**
```dart
class AnimatedButton extends StatefulWidget {
  const AnimatedButton({super.key});

  @override
  State<AnimatedButton> createState() => _AnimatedButtonState();
}

class _AnimatedButtonState extends State<AnimatedButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(vsync: this, duration: const Duration(milliseconds: 300));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) { /* ... */ }
}
```

**MethodChannel call to native platform (Dart side):**
```dart
const _channel = MethodChannel('com.example/native');

Future<String> getDeviceStatus() async {
  final result = await _channel.invokeMethod<String>('getDeviceStatus');
  return result ?? 'unknown';
}
```

**EventChannel subscription (native push to Dart):**
```dart
const _events = EventChannel('com.example/events');

Stream<Map<String, dynamic>> get nativeEvents =>
    _events.receiveBroadcastStream().map((e) => Map<String, dynamic>.from(e as Map));
```

**Accessing a store via Provider:**
```dart
// Via Provider / inherited widget — do not instantiate in build()
final store = context.read<MyStore>();
store.doSomething();

// Listening for rebuilds
final value = context.watch<MyStore>().someProperty;
```

**Service singleton pattern:**
```dart
class AudioService {
  AudioService._();
  static final instance = AudioService._();

  Future<void> startRecording() async { /* ... */ }
}
```

## Anti-Patterns

**`setState` after `dispose()`** — causes a Flutter framework error. Always guard async callbacks:
```dart
// Wrong
Future<void> _load() async {
  final data = await fetchData();
  setState(() => _data = data); // may run after dispose

}

// Right
Future<void> _load() async {
  final data = await fetchData();
  if (!mounted) return;
  setState(() => _data = data);
}
```

**Business logic in `build()`** — `build()` is called frequently (on every frame if animating, on every parent rebuild). Computations, API calls, and store mutations belong in methods or stores, not inline in `build()`.

**`late` for nullable fields** — `late` promises non-null but crashes at runtime if accessed before assignment. Use nullable types (`String? _value`) or initialize in `initState()`.

**Hardcoding colors** — `Color(0xFF1A1A2E)` bypasses dark/light mode switching and design token updates. Always use `Theme.of(context).colorScheme.*` or your app's theme system.

**Creating objects inside `build()`** — instantiating controllers, streams, or services in `build()` creates new instances on every rebuild, leaking resources and breaking animations. Create them in `initState()` or as `static final` singletons.

## Validation

- `flutter analyze` — static analysis; zero warnings/errors is the bar before any commit
- `flutter build apk --debug` — full compile check; catches import errors and platform channel mismatches that `analyze` misses
- Verify MethodChannel method names match the native handler switch cases exactly — typos fail silently at runtime with a `MissingPluginException`
