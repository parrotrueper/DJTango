#!/usr/bin/env python3
"""Debug script to diagnose dropdown text rendering issues."""

from pathlib import Path
from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication
from PySide6.QtQuick import QQuickItem
import sys

app = QApplication([])
engine = QQmlApplicationEngine()

from ttvttm.qml_backend import QmlBackend
backend = QmlBackend()
engine.rootContext().setContextProperty('backend', backend)

qml_file = str(Path('ttvttm/qml/Main.qml').resolve())
engine.load(QUrl.fromLocalFile(qml_file))

if not engine.rootObjects():
    print("❌ QML failed to load")
    for error in engine.errors():
        print(f"  {error.description()}")
    sys.exit(1)

print("✓ QML loaded successfully\n")

root = engine.rootObjects()[0]
search_panel = root.findChild(QQuickItem, "searchPanel")

if not search_panel:
    print("❌ SearchPanel not found")
    sys.exit(1)

print("✓ SearchPanel found")
print(f"  Position: ({search_panel.property('x')}, {search_panel.property('y')})")
print(f"  Size: {search_panel.property('width')} x {search_panel.property('height')}\n")

# Try to find ComboBoxes by traversing children
def print_item_tree(item, indent=0):
    """Recursively print the QML item tree."""
    prefix = "  " * indent
    name = item.objectName() or "unnamed"
    classname = item.__class__.__name__
    width = item.property('width') if hasattr(item, 'property') else 'N/A'
    height = item.property('height') if hasattr(item, 'property') else 'N/A'
    
    if 'Combo' in classname or 'Text' in classname:
        print(f"{prefix}• {classname} '{name}' - size: {width}x{height}")
    
    # Get children
    children = item.childItems() if hasattr(item, 'childItems') else []
    for child in children:
        print_item_tree(child, indent + 1)

print("QML Item Tree (search panel):")
print_item_tree(search_panel)

# Check if comboboxes are accessible
print("\n--- Searching for ComboBox elements ---")
artist_combo = search_panel.findChild(QQuickItem, "artistFilterCombo")
album_combo = search_panel.findChild(QQuickItem, "albumFilterCombo")
genre_combo = search_panel.findChild(QQuickItem, "genreFilterCombo")
scope_combo = search_panel.findChild(QQuickItem, "scopeCombo")

for combo, name in [(artist_combo, "Artist"), (album_combo, "Album"), 
                     (genre_combo, "Genre"), (scope_combo, "Scope")]:
    if combo:
        print(f"✓ {name} ComboBox found")
        print(f"    Width: {combo.property('width')}")
        print(f"    Height: {combo.property('height')}")
        print(f"    Visible: {combo.property('visible')}")
    else:
        print(f"❌ {name} ComboBox not found")

print("\n--- Checking SearchPanel ColumnLayout ---")
# The ColumnLayout inside search panel
children = search_panel.childItems()
print(f"SearchPanel has {len(children)} direct children")
for i, child in enumerate(children):
    print(f"  Child {i}: {child.__class__.__name__} - {child.objectName()}")
    if hasattr(child, 'childItems'):
        for j, subchild in enumerate(child.childItems()):
            print(f"    Subchild {j}: {subchild.__class__.__name__} - {subchild.objectName()}")

app.quit()
print("\n✓ Debug complete")
