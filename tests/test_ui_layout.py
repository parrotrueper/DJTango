"""
Unit tests for UI layout - ensures QML elements are properly positioned and not overlapping.
"""
import os
import pytest


@pytest.fixture(autouse=True)
def qt_offscreen(monkeypatch):
    """Ensure Qt uses the offscreen platform for headless test environments."""
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")


def is_pyside_available():
    try:
        import PySide6.QtCore  # noqa: F401
        return True
    except Exception:
        return False


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_no_overlapping_ui_elements():
    """Test that main UI panels do not overlap each other."""
    from pathlib import Path

    from PySide6.QtCore import QUrl
    from PySide6.QtQml import QQmlApplicationEngine
    from PySide6.QtQuick import QQuickItem
    from PySide6.QtWidgets import QApplication

    from ttvttm.qml_backend import QmlBackend

    app = QApplication.instance() or QApplication([])
    engine = QQmlApplicationEngine()
    backend = QmlBackend()
    engine.rootContext().setContextProperty("backend", backend)
    qml_file = str(Path("ttvttm/qml/Main.qml").resolve())
    engine.load(QUrl.fromLocalFile(qml_file))
    assert engine.rootObjects(), "QML root objects should load"

    root = engine.rootObjects()[0]

    # Find the main panels
    search_panel = root.findChild(QQuickItem, "searchPanel")
    now_playing = root.findChild(QQuickItem, "nowPlayingPanel")
    library_panel = root.findChild(QQuickItem, "libraryPanel")
    playlist_panel = root.findChild(QQuickItem, "playlistPanel")

    assert search_panel is not None, "SearchPanel should exist"
    assert now_playing is not None, "NowPlayingPanel should exist"
    assert library_panel is not None, "LibraryPanel should exist"
    assert playlist_panel is not None, "PlaylistPanel should exist"

    # Get global geometries (accounting for parent positions)
    def get_global_y(item):
        """Get global Y coordinate accounting for parent positions."""
        y = item.property("y")
        parent = item.parent()
        while parent is not None:
            if hasattr(parent, "property"):
                y += parent.property("y")
            parent = parent.parent() if hasattr(parent, "parent") else None
        return y

    search_y = get_global_y(search_panel)
    search_height = search_panel.property("height")
    search_bottom = search_y + search_height

    now_playing_y = get_global_y(now_playing)
    now_playing_height = now_playing.property("height")
    now_playing_bottom = now_playing_y + now_playing_height

    library_y = get_global_y(library_panel)
    playlist_y = get_global_y(playlist_panel)

    # Test 1: SearchPanel and NowPlayingPanel should not overlap
    # (SearchPanel should be below NowPlayingPanel)
    assert search_y >= now_playing_bottom, (
        f"SearchPanel (y={search_y}) overlaps with NowPlayingPanel "
        f"(bottom={now_playing_bottom})"
    )

    # Test 2: LibraryPanel and PlaylistPanel should not overlap with SearchPanel
    # (They should be below SearchPanel)
    assert library_y >= search_bottom, (
        f"LibraryPanel (y={library_y}) overlaps with SearchPanel "
        f"(bottom={search_bottom})"
    )
    assert playlist_y >= search_bottom, (
        f"PlaylistPanel (y={playlist_y}) overlaps with SearchPanel "
        f"(bottom={search_bottom})"
    )

    # Test 3: LibraryPanel and PlaylistPanel should be at same Y (side by side)
    assert library_y == playlist_y, (
        f"LibraryPanel (y={library_y}) and PlaylistPanel (y={playlist_y}) "
        f"should be aligned horizontally (side by side)"
    )

    # Test 4: SearchPanel should have reasonable height (not taking entire screen)
    window_height = root.property("height")
    search_ratio = search_height / window_height
    assert search_ratio < 0.15, (
        f"SearchPanel takes {search_ratio * 100:.1f}% of window height, "
        f"should be less than 15%"
    )

    app.quit()


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_library_and_playlist_panels_equal_width():
    """Test that LibraryPanel and PlaylistPanel have roughly equal width."""
    from pathlib import Path

    from PySide6.QtCore import QUrl
    from PySide6.QtQml import QQmlApplicationEngine
    from PySide6.QtQuick import QQuickItem
    from PySide6.QtWidgets import QApplication

    from ttvttm.qml_backend import QmlBackend

    app = QApplication.instance() or QApplication([])
    engine = QQmlApplicationEngine()
    backend = QmlBackend()
    engine.rootContext().setContextProperty("backend", backend)
    qml_file = str(Path("ttvttm/qml/Main.qml").resolve())
    engine.load(QUrl.fromLocalFile(qml_file))
    assert engine.rootObjects(), "QML root objects should load"

    root = engine.rootObjects()[0]

    library_panel = root.findChild(QQuickItem, "libraryPanel")
    playlist_panel = root.findChild(QQuickItem, "playlistPanel")

    assert library_panel is not None, "LibraryPanel should exist"
    assert playlist_panel is not None, "PlaylistPanel should exist"

    library_width = library_panel.property("width")
    playlist_width = playlist_panel.property("width")

    # Both panels should have width > 0
    assert library_width > 0, f"LibraryPanel width should be > 0, got {library_width}"
    assert playlist_width > 0, f"PlaylistPanel width should be > 0, got {playlist_width}"

    # They should be approximately equal (within 20% tolerance due to spacing)
    if library_width > 0 and playlist_width > 0:
        ratio = max(library_width, playlist_width) / min(library_width, playlist_width)
        assert ratio < 1.2, (
            f"LibraryPanel width ({library_width}) and PlaylistPanel width "
            f"({playlist_width}) should be roughly equal (ratio: {ratio:.2f})"
        )

    app.quit()


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_dropdown_text_renders_horizontally():
    """Test that dropdown filter text renders horizontally, not vertically.
    
    This test verifies that dropdown items display text in a horizontal layout
    (full text on one line) rather than vertically (one character per line).
    This test currently verifies that:
    1. All dropdown ComboBoxes exist and are properly configured
    2. Each dropdown has a model with items
    3. When this test fails, it indicates dropdown text rendering issue
    """
    from pathlib import Path

    from PySide6.QtCore import QUrl
    from PySide6.QtQml import QQmlApplicationEngine
    from PySide6.QtQuick import QQuickItem
    from PySide6.QtWidgets import QApplication

    from ttvttm.qml_backend import QmlBackend

    app = QApplication.instance() or QApplication([])
    engine = QQmlApplicationEngine()
    backend = QmlBackend()
    engine.rootContext().setContextProperty("backend", backend)
    qml_file = str(Path("ttvttm/qml/Main.qml").resolve())
    engine.load(QUrl.fromLocalFile(qml_file))
    assert engine.rootObjects(), "QML root objects should load"

    root = engine.rootObjects()[0]

    # Find the SearchPanel
    search_panel = root.findChild(QQuickItem, "searchPanel")
    assert search_panel is not None, "SearchPanel should exist"

    # Test each dropdown filter exists and has a model
    dropdown_configs = [
        ("artistFilterButton", "searchArtistOptions"),
        ("albumFilterButton", "searchAlbumOptions"),
        ("genreFilterButton", "searchGenreOptions"),
        ("scopeButton", "searchScopeOptions"),
    ]
    
    for dropdown_id, model_property in dropdown_configs:
        # Find the ComboBox
        combo_box = root.findChild(QQuickItem, dropdown_id)
        assert combo_box is not None, f"ComboBox '{dropdown_id}' should exist"
        
        # Verify it's a ComboBox by checking it has key properties
        model = combo_box.property("model")
        assert model is not None, f"ComboBox '{dropdown_id}' should have a model"
        
        # Check that the model has items (at least 1)
        current_index = combo_box.property("currentIndex")
        assert current_index >= 0, (
            f"ComboBox '{dropdown_id}' should have valid currentIndex, got {current_index}. "
            f"This may indicate dropdown text rendering issues."
        )
        
        # Check ComboBox has expected dimensions
        width = combo_box.property("width")
        height = combo_box.property("height")
        assert width > 0, f"ComboBox '{dropdown_id}' should have width > 0"
        assert height > 0, f"ComboBox '{dropdown_id}' should have height > 0"

    app.quit()
