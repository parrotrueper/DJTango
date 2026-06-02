# GUI Redesign Audit

## Summary

The current app uses a Qt-based GUI with a single main window defined by `djtango/UI_djtango.py` and wired through `djtango/ui_setup.py`.

The redesign spec in `gui-redesign.md` is a significantly different layout and workflow. The existing implementation includes many core playback and library features, but the UI structure, view model, and menu architecture are not aligned with the new design.

## What exists today

- Main app UI is built from `djtango/UI_djtango.py`.
- The UI contains:
  - Library source table (`milongaSource`)
  - Live/playlist destination table (`milongaDest`)
  - Search/filter controls: `comboBoxArtist`, `comboBoxGenre`, `lineEditFilter`, `pushButtonClearFilter`
  - Shuffle button (`pushButtonRandom`)
  - Hide/show destination panel button (`pushButtonHideDest`)
  - Clear playlist button (`pushButtonMilongaClear`)
  - Menu bar with `Library`, `Edit`, and `View` menus
  - Preferences action and Track Appearance action
- Backend features exposed by current mixins:
  - audio playback and pause/stop via `djtango/audio_playback.py`
  - library scanning and file/directory import via `djtango/menu_actions.py`
  - library filtering and playlist data model via `djtango/library_manager.py`
  - model wiring in `djtango/ui_setup.py`
  - UI visibility controls in `djtango/visibility_controls.py`
  - connections between widgets and logic in `djtango/connections.py`
- Library filters are implemented and bound to UI controls.
- Playlist source and destination models exist and can be updated with track lists.

## What is partially present

- `Library` menu group exists and can open imports/add dialogs.
- `Edit` menu has preferences and track appearance, but not the full redesign menu hierarchy.
- `View` menu exists, but the current actions are limited to fullscreen and side-screen display.
- There is an existing concept of WIP vs live panels as source/destination tables, but not the new explicit WIP panel and live-panel split with toggled view modes.
- Some playback controls and status information appear in the UI, but the current layout and widget grouping do not match the redesign.

## What is missing or differs from redesign

- No dedicated top border with centered app name and branch/version status.
- No explicit `Live session mode` toggle with the redesign behavior.
- No separate primary/secondary library databases or library rename controls.
- No playlist load/save/export/import workflows aligned to the new spec.
- No playlist browser or playlist directory tree popup.
- No WIP context drop-down or last playlist context history.
- No bottom status bar with currently playing track time and selected track totals as described.
- No current UI support for scope filters like Live/WIP/Playlists across multiple data contexts.
- No explicit track info two-row title/artist display in the same style as the redesign spec.
- No advanced preference controls for Live Output / Pre-listen output / replay gain / silence append / cortina duration matching the new layout.
- The existing UI is a large generated form, which makes redesigning the layout in place difficult.

## New QML redesign progress

- A new Qt Quick frontend exists in `djtango/qml/Main.qml` and is launched by `djtango/quick_main.py`.
- The QML layer now exposes a backend context property and binds library/playlist models.
- Basic playback, playlist add/remove, save, and load actions are wired into the QML UI.
- View-mode toggles, live session switch state, selected-track metadata display, and top-header app metadata are now present.
- Fixed QML backend context binding and upgraded deprecated Connections syntax.
- Startup regression tests now include QML load validation and backend import checks.

## Updated recommendation

- Continue the new QML layer work as the primary redesign path.
- Use the current implementation as a prototype and incrementally align it with `gui-redesign.md`.
- Stage the work so that:
  - Step 1 builds the QML shell and backend binding,
  - Step 2 exposes library/playlist/playback models,
  - Step 3 builds the initial library/live panel layout,
  - Step 4 wires controls and playback-state behavior,
  - Step 5 polishes the redesign with header info, status bar, filters, and advanced preferences.
- Focus next on top border/header, panel visibility modes, WIP/live panel semantics, and the bottom status bar to match the spec.
- Keep the legacy widget UI as a fallback until the redesigned layer is fully stable.

## Observations

- The current GUI is functional but not architected for the redesign.
- There is an old unused secondary UI file `djtango/UI_djtango2.py` that appears to be a legacy prototype and should not be used.
- Core data and playback services are reusable, so the safest path is to build a new UI layer and wire it to the existing backend logic.
- Reusable backend modules (`djtango/data.py`, `djtango/dirsong.py`, `djtango/tracksong.py`, `djtango/tableModels.py`) have been cleaned of commented-out debug code and are ready for reuse.
- The current main window class is tightly coupled and uses many mixins, which makes incremental UI changes harder.

## Recommendation from audit

- Keep the backend logic and data models intact.
- Create a new redesigned UI implementation instead of trying to retrofit the current `djtango/UI_djtango.py` layout.
- Use the audit gaps above as the target list for the new design.
- Track progress in this file by turning missing items into milestones.

## Completed work

* Audited the current Qt-based app UI and identified where it differs from the redesign spec.
* Documented existing widgets, menus, playback controls, and backend modules in use today.
* Determined that the current UI layout does not match the new design and that a new UI layer is the safer migration path.
* Confirmed that key backend components are reusable for a redesigned frontend.

## Key conclusions

* The current UI is functional but not aligned with the redesign architecture.
* The safest path is to build a new UI layer while reusing existing backend logic.
* The audit has established the scope of work needed to complete the redesigned interface.
