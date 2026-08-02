# GUI Redesign Task Tracker

## Purpose

Track the UI redesign work for `ttvttm` in a single reference document. 
Use this to record tasks, current status, and remaining work for the new 
QML-based redesign path.

## Current status
- [x] Existing UI redesign spec documented in `uiredesign/gui-redesign.md`
- [x] Current redesign progress and stage plan documented in `uiredesign/gui-redesign-next-stage.md`
- [x] Current app/UI audit documented in `uiredesign/redesign-audit.md`
- [ ] `uiredesign/gui-layout-sketch.md` is out of date and no longer the working 
source of truth

## Overall objective
Replace/augment the legacy Qt widget UI with a new QML frontend that follows the
redesign spec while reusing existing backend logic.

## High-level milestones

### 1. Main layout and header
- [x] Define the top border and main panel structure in the redesign spec
- [x] Implement the centered app name/version header
- [x] Implement the boxed top-left menu row: `Library`, `Playlist`, `View`, `Settings`
- [x] Add the info strip for live output and volume state
- [x] Add a dedicated playback control area with transport controls and progress bar

### 2. Panel structure and view modes
- [x] Build the WIP panel and live playlist panel layout in QML
- [x] Add WIP context selection: `Library`, `Library 2`, `Last playlist`
- [x] Add explicit view modes: Live only, WIP only, WIP+Live
- [x] Support panel hide/show behavior for the live panel and WIP panel

### 3. Search and filters
- [x] Add a search box with incremental filter behavior
- [x] Add typed search filters for `Artist`, `Album`, `Genre`
- [x] Add scope filters for `Library`, `Playlists`, `Library 2`, `Live`, and `WIP`
- [x] Add a search filter toggle control to enable/disable filter set

### 4. Playlist and library workflows
- [ ] Add playlist actions: New, Load, Save, Save As, Export, Import, Close
- [ ] Add playlist browser/load UI and file-directory integration
- [ ] Add library actions: Add tracks, Add directory, Configure, Scan/Refresh
- [ ] Add playlist move-to-live and playlist copy/add semantics
- [ ] Add playlist and library context menu actions for selected items

### 5. Playback controls and live session
- [x] Add dedicated play/pause/previous/next buttons
- [x] Add live session mode toggle with spec behavior
- [x] Add current track info display (title + artist)
- [x] Add footer stats for live output: `Total Duration`, `End Time`
- [x] Add progress/status information for live output and selected track

### 6. Preferences and advanced options
- [ ] Add preferences panel or dialog in QML
- [ ] Add output routing settings for live output and pre-listen output
- [ ] Add replay gain, append silence, downmix to mono, Cortina controls
- [ ] Add list column order and track appearance options
- [ ] Add keyboard shortcut configuration entrypoints

### 7. Testing and validation
- [ ] Add QML startup and load regression tests
- [ ] Add tests for playlist actions and view state
- [ ] Add tests for search/filter scope behavior
- [ ] Add tests for live playlist footer calculations and track info

## Notes
- The legacy UI file `ttvttm/UI_ttvttm.py` remains useful for reference but 
should not be the primary redesign target.
- Keep the QML frontend in `ttvttm/qml/` and backend bindings in 
`ttvttm/qml_backend.py` and `ttvttm/quick_main.py`.
- Existing backend modules such as `ttvttm/data.py`, `ttvttm/tableModels.py`, 
and `ttvttm/library_manager.py` should continue to support the new UI.

## Work in progress
- [ ] Determine the exact QML component structure for the new panel layout
- [ ] Identify any missing backend bindings required by QML
- [ ] Update the task tracker with in-progress implementation notes as the work 
continues

## References
- `uiredesign/gui-redesign.md`
- `uiredesign/gui-redesign-next-stage.md`
- `uiredesign/redesign-audit.md`
- `uiredesign/gui-layout-sketch.md`
- `ttvttm/qml/Main.qml`
- `ttvttm/qml_backend.py`
- `ttvttm/quick_main.py`
