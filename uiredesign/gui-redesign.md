# UI redesign spec

UI items

|                 top border                              |
|menu items        |  info   |           playback controls|
|                  Track info                             |
|search box, search filter options |name      time stats  |
| WIP panel                        |      Live panel      |
| library list                     |    live playlist     |
|                  bottom border                          |

## Top border

* app name - centred, `DJTango`
* version after the app name
  - if on main branch `release version number`
  - if on feature branch  `commit hash`
  - if local dev `DIRTY`
  
## Menu items

### Edit

Track related actions

* Open containing directory - open directory browser at the location of the selected track
* View Properties - opens pop up of the selected track properties including:
    * Metadata information (can be edited) - keyboard shortcut `Ctrl+P`
    * File details (cannot be edited): File name, path, sample rate, channels, bits per sample, bitrate, codec, encoding 
  
### Playlist

Playlist related actions

* Add  - adds selected tracks to the active playlist, default keyboard shortcut  `Ctrl+C Ctrl+V`
* Remove - removes selected tracks from playlist with context, default keyboard shortcut `Ctrl+X`
* Copy - copies selected tracks to the active playlist, default keyboard shortcut `Ctrl+C` 
* Add directory  - adds directory tracks to the playlist with context
* New - creates a new empty playlist
* Load - opens an existing playlist from the file system - currently on icon `Load milonga`, opens to the WIP panel, keyboard shortcut `Ctrl+L`.
* Close - closes the playlist, i.e. removes it from the WIP panel, keyboard shortcut `Ctrl+W`
* Save - saves the playlist that is active or selected - currently on icon `Save milonga`
* Save As - saves the playlist that is active or selected with new name - currently on icon `Save milonga as`
* Export - saves the playlist in selected format
* Import - imports playlist from another format
* Move to Live - load the selected playlist to the Live panel, keyboard shortcut `Ctrl+Shift+Right arrow`

### Library 

* Primary Library media database
This is the main library list for tango, vals, milonga, etc.. tracks that make the bulk of the playlist set

  * Rename - allows renaming of this database, default is `Library`
  * Add tracks - currently mapped to `Edit -> Library -> Add Files`
  * Add directory - currently mapped to `Edit -> Library -> Add Directory`
  * Configure - sets the base directory that should be monitored for the primary database. Currently mapped to `Edit -> Preferences -> Library [path] [Browse]` 
  * Edit - currently mapped to `Edit -> Library -> Library contents...`
  * Scan configuration
      * Refresh - performs a fresh scan of the database
      * Scan rate - Set how often to scan for updates, min,hrs,days. 
      * Pause scanning - toggle switch 

* Secondary media database 
This is the library for any other genre of music where the tracks used for `Cortinas` intro music or after party music is found

  * Rename - allows renaming of this database, default is `Library 2`
  * Add tracks - currently mapped to `Edit -> Library -> Add Files`
  * Add directory - currently mapped to `Edit -> Library -> Add Directory`
  * Configure - sets the base directory that should be monitored for the primary database. Currently mapped to `Edit -> Preferences -> Library [path] [Browse]` 
  * Edit - currently mapped to `Edit -> Library -> Library contents...`
  * Scan configuration
      * Refresh - performs a fresh scan of the database
      * Scan rate - Set how often to scan for updates, min,hrs,days. 
      * Pause scanning - toggle switch 

* Playlists
  * Configure - sets the base directory where playlists should be saved/loaded

* Filters
   * Configure - sets the base directory where EQ presets should be saved/loaded    


### View

* WIP panel - selects what to show in the WIP panel at launch, radio button
    * Library 
    * Library 2
    * Last playlist
  
* Playlist browser - opens a pop-up of the playlist directory tree.
* View modes, radio button list. Keyboard shortcut cycles through the following modes, keyboard shortcut `Ctrl+H`:
    * Live panel view, takes the full width of the UI, hides WIP panel
    * WIP panel view, takes the full width of the UI, hides Live panel
    * WIP and Live panel view, default view mode
    Some of this functionality is currently on vertical bars between the panels.
  
* Equaliser - opens a pop up for the equaliser
* Console - opens a pop up with the console output, for logs, debug etc..
  

### Preferences

* Live Output - selects the sound driver for the active playlist/live set (currently called Milonga), lists available drivers with radio button for selection
* Pre-listen Output - selects the sound driver for pre-listening from the library or an inactive playlist. Toggle switch to enable. If enabled lists available drivers with radio button for output selection.
* WIP toggle switch - work in progress switch, when enabled: 
    * Live and Pre-Listen go through the Pre-Listen output driver
    * `Cortina` duration is set to 5 seconds
  
* Volume - sets the individual volume level for Live and for Pre-listen, 0-100%
* PLayback order - radio options: Default, Random
* Replay Gain - Typically tango recordings are at a lower volume than modern tracks used as `Cortinas` so you want to normalise playlist `Cortina` tracks separately from the rest of the playlist. You may want to play `Cortinas` a bit louder or softer than the rest of the playlist. 
    * Tango gain [value]dB  how much gain should be applied to tracks (excluding `Cortinas`) once replay gain has been recalculated for a playlist. The value can be positive or negative.    

* Append silence - toggle switch - appends specified time for silence before and/or after each track during playback. When enabled silence before and after time can be configured in ms.
* Donwmix to mono - toggle switch - down mixes output channels to mono
* Cortina - list of:
    * Live Duration - currently mapped to `Edit -> Preferences -> Cortina duration (in sec) [number]`
    * WIP Duration - duration to use when in WIP mode
    * Live Fade out time - currently mapped to `Edit -> Preferences -> FadOut time (in sec) [number]`
    * WIP Fade out - fade out time when in WIP mode

* Track view - currently mapped to `Edit -> Track Appearance`
* Duplicate view - Edit Duplicate Highlight appearance. Highlights duplicate track titles within a playlist.
* List column order - select how columns in the list view should be ordered and what columns should be shown. 
    * `#` - item number
    * `Title` - track title
    * `Artist` - track artist 
    * `Duration` - track duration time min:sec, (no leading 0s for minutes)
    * `Genre` - Tango, Milonga, Vals, Cortina, etc...
    * `Year` - track date from metadata
    * `BPM`  - track beats per minute
    * `File` - file type, mp3, flac, etc..
    * `Path` - file path relative to Library path    
* Keyboard shortcuts - configures keyboard shortcuts for desired actions

### Help

* Shows the User Guide
* Shows the version number


## Other Menu bar items

### Info

Items around the centre of the menu bar

* Display the name of the driver currently selected for Live Output
* Display the volume setting for live output as a percentage
* Display mono if down mix to mono is enabled
  

### Playback Controls

Items to the right of the menu bar

* Live session mode LED - red/grey: enabled/disabled. When enabled the following settings are applied:
    * WIP mode is disabled
    * Live output and Pre-Listen outputs are split. 
    * Playback order is set to default
    * Channel down mix to mono enabled
    * `Cortina` duration and fade out to Live settings
    * Append silence enabled
    * Library scanning is paused
    When Live tick box is unticked, no changes are made, i.e. does not re-enable previous settings, for example it does not re-enable WIP mode.
* Track playing progress bar - in WIP mode keyboard shortcut `Left arrow` to rewind 10s, `Right arrow` to fast forward 10s
* Play Icon - plays the selected track, default keyboard shortcut `Enter`
* Pause Icon - pauses the selected track, default keyboard shortcut `Spacebar`
* Previous Track Icon - skips to the previous track if not playing, otherwise skips to the start of the track, default keyboard shortcut `up arrow`
* Next Track Icon - skips to the next track, default keyboard shortcut `down arrow`

##  Track Info

Displays info of the currently playing track or selected track if not currently playing. Two rows of information

* Track Title
* Artist

The default background colour goes orange if the battery drops below 20%.

## Search section

* Search box - for keyword entry, matches can be partial and incremental, can match track title, artist, album, genre, file path name, etc.. Keyboard shortcut to enter keyword, `Ctrl+Shift+F`
* Search button - re-starts the search. Keyboard shortcut, `Ctrl+F`
* Toggle filter - applies or disables search filters. Keyboard shortcut `Ctrl+Alt+F`
* Search filters:
    * By Artist
    * By Album
    * By Type/Genre  
* Scope filters:
    * Library - searches within the primary database
    * Playlists - searches within playlists
    * Library 2 - searches within the secondary database
    * Live - searches within the live playlist
    * WIP - searches within whatever has is loaded in the WIP
    * WIP context - searches within whatever is currently displayed in the WIP panel.
  
## WIP panel

This is the workspace, or work in progress panel, by default it is loaded with Library list.
The default can be changed in `View -> WIP panel`.
Other playlists can be loaded here via `Playlists -> Load playlist` or keyboard shortcut `Ctrl+L` they will automatically be added to the context drop down.
Playlists can be removed from the context via `Playlists -> Close playlist` or keyboard shortcut `Ctrl+W`

* context drop down, populated with:
    * Library
    * Library 2
    * playlists that have already been loaded 
    Selecting an item from the drop down brings it to foreground in the WIP panel.  
    keyboard shortcut to change to next context `Ctrl+PageUp` or `Ctrl+PageDown` to return to previous context. 

* WIP list, shows the primary Library list by default, with the following columns:
    * `#` - item number
    * `Title` - track title
    * `Artist` - track artist 
    * `Genre` - Tango, Milonga, Vals, Cortina, etc...
    * `Year` - track date from metadata
    * `Duration` - track duration time min:sec, (no leading 0s for minutes)

The list can be re-ordered by column by clicking on the column name. Clicking on the `#` returns the order to its original state (last saved state for playlists).

## name

Live panel playlist name, can be edited. `Ctrl+S` saves the playlist with the name entered here.

## Time Stats

Total: `total playlist time`, set: `set time`

* `total playlist time` is the sum of all durations for track and appended silences.
* `set time` is the sum of all duration of tracks between the first Tango and the last tango, vals or milonga.

## Live panel

This is the live set for the Gig/milonga. Loaded with the last set played or blank if not available. It shows the tracks in the order that they will be played, it shows the following
columns:
    * `#` - item number
    * `s` - In this column all tracks will have a radio button.
      - For `Cortina` tracks the radio button is enabled by default. If a radio button is disabled then the `Cortina` will continue to play beyond the `cortina duration` setting and fade out will occur when the radio button is re-enabled. Keyboard shortcut to toggle the radio button `Ctrl+B`
      - For `tango`, `vals` `milonga` enabling the radio button enables a predefined EQ preset for the track. Keyboard shortcut to toggle the radio button `Ctrl+T`

    * `Title` - track title
    * `Artist` - track artist 
    * `Genre` - Tango, Milonga, Vals, Cortina, etc...
    * `Duration` - track duration time min:sec, (no leading 0s for minutes)

Once in live mode, the list can still be edited, for construction on the fly.

During playback in live session mode:
   * Fast forward and rewind controls are disabled. 
   * Pause requires pressing the space bar twice, to prevent accidentally stopping playback.
   * Pausing a `Cortina` automatically applies fade out. 
   * Pressing play after pausing a `Cortina` plays the next track. 
  
## Bottom border

Left hand side: WIP list name, for example Library.
After WIP list name, `track time played`/`total track time` | `track time remaining` - for the track currently playing.
Right hand side: `total time of selected tracks` of any selected tracks, do not need to be playing.

## Implementation status

### Completed so far
* The existing app already supports a split WIP/live workflow with separate source and destination tables.
* Search/filter controls for the library are implemented in the current UI.
* Library and playlist import, add, clear, and playback actions already exist in the current app.
* The current UI includes a menu bar with Library, Edit, and View menu groups.

### Still missing for the redesign
* A dedicated top border with centered app name and branch/version status.
* Explicit Live session mode toggle and redesigned playback control layout.
* Dedicated primary/secondary library UI, playlist browser, and WIP context selector.
* The full new view-mode panel switching and bottom status bar as specified.
* Advanced preferences controls for output routing, replay gain, silence append, and Cortina settings.

Double clicking on any part of the bottom border highlights and brings to context the track currently playing. If no track is playing then the track that last played.

## Visuals

* All fonts are Liberation sans (or aerial), throughout
* Top Border - BG: #dedddac1, FG: #5E5C64, Font: 12pt Bold
* Menu Bar - BG: #dedddac1, FG: #000000, Font: 10pt
* Menu items and sub menus - BG: #dedddac1, FG: #000000, Font: 10pt
* Track info - BG:#000000, FG: #1AF0F0, Font: 36pt Bold
* Search, search filter options: BG: #0C2847, FG: #dedddac1, Font 10pt  
* Search filter dropdowns - BG: #dedddac1, FG: #000000, Font: 10pt
* Lists and playlists - default BG: alternating rows of  #071c35 and  #143964,
  Default FG: #F2F7F6, Font 12pt
* Bottom border: BG: #dedddac1, FG: black, Font: 10pt

## Icons

From https://fonts.google.com/icons

----

## Proposed plan of action

1. Audit current feature coverage
   * Compare the existing Qt app UI and behaviour with the redesign spec.
   * Identify which screens, playlist flows, and playback controls already exist.
   * Find gaps where the new design introduces new behaviors or panels.

2. Build a new GUI layer
   * Create a fresh UI implementation for the redesigned layout.
   * Use `PySide6`/Qt Designer or hand-built widgets for the top menu, WIP panel, live panel, and search area.
   * Keep the old UI code available as a reference during migration.

3. Reuse the backend engine
   * Keep existing library, playlist, playback, scan, and preference logic.
   * Wire the new UI to the current business logic instead of rewriting core functionality.
   * Refactor the large `AudioPlayerDialog` mixin structure gradually as needed.

4. Incremental rollout
   * Start with a working minimal version: library view, live playlist, playback controls, and search.
   * Add menu actions and preferences next.
   * Then add advanced features such as WIP context switching, live session mode, and track info.

5. Track progress in this document
   * Mark completed items and move unfinished tasks into a future section.
   * Keep the spec and implementation plan aligned as the redesign proceeds.







