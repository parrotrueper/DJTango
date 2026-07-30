# GUI Redesign Next Stage Implementation Plan

## Objective

Move from the current partial QML prototype to a more complete redesign aligned with `gui-redesign.md`. Focus on layout fidelity, panel behavior, playback controls, and the most valuable user workflows.

## Current status

- New QML frontend exists in `ttvttm/qml/Main.qml`.
- `ttvttm/quick_main.py` launches the QML UI and exposes `backend` to QML.
- `ttvttm/qml_backend.py` provides library and playlist models, playback toggles, playlist persistence, and app metadata.
- The UI now includes a top header with app title/version and live output state, a library panel, a playlist panel, view-mode toggles, a live session switch, search as a basic field, WIP context selection, and search scope chips.
- Core playlist workflows are partially available: add to playlist, remove from playlist, save playlist, and load saved playlists.
- Startup regression tests cover QML load, backend import, playback toggle, playlist actions, and app metadata.

## Stage 2 priorities

1. **Align the main layout to the spec**
   - Add the top border with centered app name and version/branch status.
   - Add an info strip showing live output/volume/mono status if possible.
   - Replace the current header text with a structured menu/action area.
   - These map directly to the redesign top border, info area, and playback control header.
   - Current progress: app title/version and live output info are implemented; menu/action area remains pending.

2. **Refine the panel structure**
   - Implement explicit WIP panel and live playlist panel semantics.
   - Add a WIP context drop-down for Library, Library 2, and loaded playlists.
   - Add view mode buttons that hide/show panels as described.
   - These items map to the redesign WIP/live split, WIP context selection, and view modes.
   - Current progress: basic Library/Playlist/Both view switching exists; explicit WIP context selection is now implemented via the WIP context dropdown, while full panel semantics remain pending.

3. **Improve search and filtering**
   - Add filter buttons and scope chips for Library, Playlists, Library 2, Live, and WIP.
   - Add typed filter options for Artist, Album, and Genre.
   - Keep the search field and filter UI consistent with the redesign.
   - These features map to the redesign search section and scope filters.
   - Current progress: search scope chips are implemented; typed filter options remain pending.

4. **Complete playback controls**
   - Add dedicated play/pause, previous, next, and progress controls.
   - Add a live session mode toggle with the spec behavior.
   - Add track time and playlist duration stats in the footer.
   - Current progress: play/pause and live session state exist; previous/next/progress and footer duration stats remain pending.

5. **Implement playlist workflows**
   - Add playlist browser/load/save/export/import actions.
   - Add playlist create/close/move-to-live features.
   - Add library and playlist context menus for common actions.

6. **Add preferences and advanced options**
   - Add at least a stub preferences panel for output routing, replay gain, and Cortina settings.
   - Expose the most important settings in a QML-driven panel.
   - Current progress: preferences panel not yet implemented.

7. **Test and validate**
   - Expand the test suite to cover QML startup, backend operations, and view-mode state.
   - Add tests for playlist save/load, view switching, and selected-track metadata.
   - Use the existing `tests/test_quick_gui.py` as the base for QML/ backend regression coverage.

## Implementation notes

- Keep backend logic in existing Python modules and expose only what QML needs.
- Avoid replicating the legacy widget UI; use QML for the new design only.
- Add new UI behavior incrementally and validate with tests after each step.
- Prefer clear data bindings and state properties in QML over complex imperative logic.

## Deliverables for the next stage

- A spec-aligned main QML layout.
- A WIP/live split panel mode with view toggles.
- Search/filter UI matching the redesign.
- Working playlist save/load and basic playback controls.
- A documented set of tests covering startup, QML load, playlist actions, and view state.
