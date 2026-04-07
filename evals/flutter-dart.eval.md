# Flutter + Dart -- Evaluation

## TC-1: StatelessWidget for Display
- **prompt:** "Create a badge widget that shows a label and changes color based on active/inactive state"
- **context:** Pure display component with no local mutable state. Should be StatelessWidget.
- **assertions:**
  - Uses `StatelessWidget` (not `StatefulWidget` since there is no local mutable state)
  - Uses `const` constructor with `super.key`
  - Colors come from `Theme.of(context).colorScheme.*` (not hardcoded `Color()` or `Colors.*`)
  - Text styling uses `theme.textTheme.*` (not hardcoded font sizes)
  - Widget parameters use `required` keyword for mandatory fields
- **passing_grade:** 4/5 assertions must pass

## TC-2: StatefulWidget with Animation
- **prompt:** "Create a button that animates its scale when tapped"
- **context:** Widget needs local mutable state (AnimationController). StatefulWidget is correct.
- **assertions:**
  - Uses `StatefulWidget` with a separate `State` class
  - `AnimationController` is created in `initState()` (not in `build()`)
  - `AnimationController` is disposed in `dispose()` method
  - Uses `SingleTickerProviderStateMixin` for the vsync parameter
  - Does not create controllers or streams inside `build()`
- **passing_grade:** 4/5 assertions must pass

## TC-3: Platform Channel Communication
- **prompt:** "I need to call a native Android method 'getDeviceStatus' from Dart and get a string result"
- **context:** Cross-platform native communication. Tests MethodChannel knowledge.
- **assertions:**
  - Uses `MethodChannel` with a proper channel name (e.g., `'com.example/native'`)
  - Method call uses `invokeMethod<String>('getDeviceStatus')`
  - Handles null return value (e.g., `result ?? 'unknown'`)
  - Function signature is `Future<String>` (async operation)
  - Mentions that method names must match exactly between Dart and native side (typos fail silently)
- **passing_grade:** 4/5 assertions must pass

## TC-4: Anti-Pattern -- setState After Dispose
- **prompt:** "My app crashes with 'setState called after dispose'. Here's my code:\n```dart\nFuture<void> _load() async {\n  final data = await fetchData();\n  setState(() => _data = data);\n}\n```"
- **context:** Classic async callback after widget disposal. Tests mounted guard pattern.
- **assertions:**
  - Identifies the issue: `setState` is called after the widget is disposed
  - Adds `if (!mounted) return;` guard before the `setState` call
  - Explains that async callbacks can complete after the widget is removed from the tree
  - Does not suggest catching the error as the fix (prevention is correct)
- **passing_grade:** 3/4 assertions must pass

## TC-5: Hardcoded Colors Warning
- **prompt:** "Style this container with background color #1A1A2E and text color white"
- **context:** User requests hardcoded colors. Skill should enforce theme system usage.
- **assertions:**
  - Does not use `Color(0xFF1A1A2E)` or equivalent hardcoded color
  - Uses `Theme.of(context).colorScheme.*` (e.g., `.surface`, `.onSurface`)
  - Explains why hardcoding bypasses dark/light mode switching
  - Suggests defining the color in the app's theme definition file if it is a custom brand color
- **passing_grade:** 3/4 assertions must pass
