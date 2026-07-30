# ttvttm QML UI Layout Sketch

Use this document as the editable reference for the new QML redesign. Update sections as the layout evolves.

## Top Border

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                        ttvttm  v0.1.0                                    [ - ] [ □ ] [ X ] │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

- The top border is the native window title area.
- The app title and version are centered.
- Window control icons are aligned to the right.
- This row is the OS title bar / window chrome, not a QML-drawn menu bar.

## Menu / Action Bar

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [Library] [Playlist] [View] [Preferences]    Default 80%       LIVE [progress bar]       [<<] [Play/Pause] [>>]│
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

- Left: primary action groups.
- Center/right: active output device name and volume, live status, progress, playback controls.
- This row is the QML-rendered menu/action bar and should never duplicate the top native title border.

### icons

Library - icons/music_note_add_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg
Playlist - icons/queue_music_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg
View - icons/visibility_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg
Preferences - icons/tune_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg
Output - icons/speaker_group_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg
LIVE on - icons/radio_button_checked_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg
LIVE off - icons/radio_button_unchecked_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg
Skip back - icons/skip_previous_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg
Play - icons/play_circle_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg
Pause - icons/pause_circle_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg
Skip forward - icons/skip_next_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg

play displays when nothing is playing, pause displays when playing

## Now Playing - Track Info

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
|                                             Track Title                                                     | 
|                                             Artist                                                          | 
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Search area

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  [Search box] [toggle to apply search filters] [by artist-dropdown][by album-dropdown][by type-dropdown][scope-dropdown]│
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### WIP / Live split panels

```
┌─────────────────────────────┬───────────────────────────────────────────────────────────────────────────────┐
│ WIP panel                   │ Live panel                                                                     │
│                             │                                                                               │
│  - library list             │  - live playlist                                                              │
│  - playlist browser         │  - currently playing / queued tracks                                          │
│  - playlist controls        │  - output meter / LED status                                                  │
└─────────────────────────────┴───────────────────────────────────────────────────────────────────────────────┘
```

- The WIP panel and live panel should be visible together by default.
- View mode toggles can hide one panel or show both.

## Footer / Status Bar

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [Selected track info]                     [Total duration]  [WIP count]  [Live playlist duration]        │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

- Footer shows current selection and playback/playlist summary.
- Keep the footer minimal and status-focused.

## Notes

- Use this sketch as the canonical layout reference for QML development.
- Update the labels, control names, and panel names as the design changes.
- The top border and menu bar are intentionally separate visual regions.
- The app title should always be centered in the top native title area.
