# New GUI Layer Plan

## Goal

Build a new GUI layer for DJTango using Qt Quick / QML with a consistent cross-platform visual style, while reusing existing backend logic for library, playlist, playback, and preferences.

## Why Qt Quick

- Platform independent: Linux, macOS, Windows.
- Modern, fluid UI capabilities.
- Easy responsive layouts and transitions.
- Better separation between visual design and Python backend logic.
- Allows a clean new UI without forcing the existing widget-based form structure.

## Proposed architecture

1. **QML frontend**
   - Create a new QML entry point (for example `qml/Main.qml`).
   - Build the main layout using Qt Quick Controls 2.
   - Use a shared design language for colors, fonts, spacing, and icons.
   - Keep UI behavior declarative in QML, with state-driven components.

2. **Python backend**
   - Keep existing backend modules intact:
     - `djtango/data.py`
     - `djtango/dirsong.py`
     - `djtango/tracksong.py`
     - `djtango/tableModels.py`
     - `djtango/audio_playback.py`
     - `djtango/library_manager.py`
     - `djtango/milonga_manager.py`
   - Expose selected backend objects and methods to QML using `PySide6.QtQml` or `QtCore.QObject` wrappers.
   - Keep business logic separate from the new UI.

3. **Theme and style**
   - Create a QML theme module for colors, typography, and reusable component styles.
   - Define a palette for primary, secondary, accent, text, and surface colors.
   - Establish style tokens for button sizes, input fields, and panel spacing.
   - Use SVG or PNG icons consistently across buttons and menu actions.

   ### Visual style specification
   - Top border: centered `DJTango` application title with version/branch status, light or neutral background with strong contrast text.
   - Menu bar: compact horizontal menu area with grouped actions and a distinct, slightly elevated background.
   - Info area: centered driver/volume/mono indicators with status accent colors; low visual noise.
   - Playback controls: right-aligned row with icon buttons, progress bar, live session toggle, and a consistent button size/style.
   - Track info: two-row headline area for current/selected track title and artist, large readable typography.
   - Search section: search field with filter toggles and scope chips; clear separation between search and panel content.
   - WIP/Live panels: side-by-side panels with a visible split, consistent table style, and a clean row/column visual rhythm.
   - Bottom border: status bar showing current track time, remaining time, and selected tracks totals; clickable context highlight support.
   - Use a consistent accent color for important interactive elements, with muted background surfaces and readable text.
   - Ensure all controls use the same font family, rounded corner radii, and hover/pressed visual states.

4. **Incremental rollout**
   - Start with a minimal QML shell and a single reusable backend service.
   - Add the library panel first.
   - Add the live playlist panel next.
   - Add playback controls and track info.
   - Add search, filters, and playlist management.
   - Add preferences and advanced panel modes last.

5. **Data binding and state**
   - Use QML `ListModel` or backend-exposed models for track lists.
   - Keep UI state in QML: selected context, active playlist, search filters.
   - Use backend signals to notify QML of data updates.

## Implementation steps

1. Create scaffolding
   - Add `qml/` directory.
   - Add `qml/Main.qml`, `qml/Theme.qml`, and an application wrapper.
   - Add a new Python startup module for Qt Quick, e.g. `djtango/quick_main.py`.

2. Expose backend models
   - Implement `QObject` wrappers for library and playlist data.
   - Expose methods: load library, add track, play/pause, save playlist.
   - Expose signals for list changes and playback state.

3. Build the first screen
   - Render a two-panel layout with a top header and bottom status bar.
   - Bind a source track list and destination playlist list.
   - Implement the search field and filtering controls.

4. Wire controls
   - Connect Play/Pause/Next/Previous actions to existing playback code.
   - Connect list selections to backend track operations.
   - Connect preferences dialogs or panels to backend settings.

5. Refine and polish
   - Add view mode toggles and panel show/hide behavior.
   - Add the live session mode switch.
   - Add dynamic track info and time stats.
   - Test across platforms and ensure the design remains consistent.

## Current implementation status

- Step 1: Create scaffolding — completed.
  - `djtango/qml/Main.qml` and `djtango/qml/Theme.qml` exist.
  - `djtango/quick_main.py` loads the QML file with `QQmlApplicationEngine`.
  - A unit test `tests/test_quick_gui.py` verifies the QML root loads and theme properties are present.

- Step 2: Expose backend models — completed.
  - Added `djtango/qml_backend.py` with a `QmlBackend` QObject wrapper and `TrackListModel`.
  - Exposed `backend` to QML via `djtango/quick_main.py` using `engine.rootContext().setContextProperty("backend", backend)`.
  - Implemented load library, add track, play, pause, playlist add/remove, and save/load playlist methods.

- Step 3: Build the first screen — partial.
  - The QML UI now includes a header, search field, library panel, live playlist panel, and status footer.
  - The library and playlist lists are bound to `backend.libraryModel` and `backend.playlistModel`.
  - Search/filter controls are implemented in QML to hide unmatched library rows.

- Step 4: Wire controls — more complete.
  - Added Play/Pause, Add-to-playlist, Remove-from-playlist, Save playlist, and Load saved playlist controls in QML.
  - Added backend actions for playlist modification and playback state notifications.
  - Added startup regression tests for QML path and backend importability.
  - Added playback-toggle regression coverage.

- Step 5: Refine and polish — partial.
  - Added view mode toggles for Library / Playlist / Both.
  - Added a live session mode switch and dynamic selected-track metadata display.
  - Added a top header with app title, version, live output name, and volume.
  - Added WIP context selection and search scope chips for Library/Playlists/Library 2/Live/WIP.
  - Fixed QML backend binding and deprecated Connections syntax.
  - Added a clearer footer status line and button-driven view switching.
  - Added selected track title/artist display for library and playlist selections.
  - Full layout polish, advanced preferences, and time-based playback stats are still pending.

- Run-ready note:
  - `run-djt.sh` is expected to be usable once Step 1 and Step 2 are complete and the QML startup path is stable.
  - Current progress through Step 4 means the new QML app can be launched, but it is still in a partial/intermediate state.

- Integration note:
  - The QML startup module is present, but the main package entrypoint still uses the legacy widget UI (`djtango/__main__.py` remains unchanged).

## Alignment with `gui-redesign.md`

- Step 1: scaffolding should provide a QML shell capable of rendering the full redesign layout.
- Step 2: backend models should map to the spec's library, playlist, and playback actions.
- Step 3: first screen should align with the redesign structure by introducing the top header, library panel, live playlist panel, and footer.
- Step 4: wiring should align controls with the redesign behavior: play/pause, add/remove playlist, save/load playlist, view switches, and live session state.
- Step 5: polish should complete the spec alignment by adding the dedicated top border, explicit WIP/live panel behavior, track info rows, bottom status bar, filter scopes, playlist browser, and advanced preferences.

## Current stage alignment

- Completed: scaffolding, backend model exposure, basic QML shell, core playlist actions.
- In progress: view switches, selected-track display, app header metadata, backend QML startup stability.
- Next stage: full redesign alignment for menu structure, WIP context, playlist browser, playback controls, track info, and advanced preferences.

## Migration strategy

- Keep `djtango/UI_djtango.py` and existing widget UI files as a fallback during development.
- Build the new Qt Quick layer in parallel.
- Replace the widget-based launch path only once the new UI is stable.
- Use the existing backend for behavior validation.

## Notes

- Qt Quick does not require existing `.ui` files.
- Use `PySide6.QtQml` or `QQmlApplicationEngine` for QML integration.
- Keep backend modules as plain Python services where possible; only wrap the glue layer for QML.
- Create unit tests to verify functionality

## Completed so far

* Completed a design audit comparing the existing Qt widget UI with the redesign spec.
* Identified the current app's UI components and backend services that can be reused.
* Decided to build the redesign as a new Qt Quick / QML frontend rather than retrofitting the existing widget-based layout.
* Documented the proposed architecture, migration strategy, and incremental rollout plan.
