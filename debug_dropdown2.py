#!/usr/bin/env python3
"""Debug script to diagnose dropdown rendering by opening it."""

from pathlib import Path
from PySide6.QtCore import QUrl, QTimer
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
    sys.exit(1)

root = engine.rootObjects()[0]
search_panel = root.findChild(QQuickItem, "searchPanel")

if not search_panel:
    print("❌ SearchPanel not found")
    sys.exit(1)

print("✓ SearchPanel found")

# Find combobox via direct property access
def find_combo_by_id(parent, combo_id):
    """Find a ComboBox by searching through property."""
    # Try direct property access
    try:
        combo = parent.property(combo_id) if hasattr(parent, 'property') else None
        if combo:
            return combo
    except:
        pass
    
    # Try findChild with empty name and matching class
    children = parent.childItems() if hasattr(parent, 'childItems') else []
    for child in children:
        if child.__class__.__name__ == 'QQuickComboBox':
            if hasattr(child, 'property'):
                try:
                    model = child.property('model')
                    print(f"    Found ComboBox with model: {model}")
                except:
                    pass
    return None

# Let's try to access it differently - through the contentItem
content_items = search_panel.childItems()
print(f"\nSearchPanel direct children: {len(content_items)}")

def find_all_combos(item, depth=0):
    """Recursively find all ComboBox items."""
    prefix = "  " * depth
    if hasattr(item, '__class__'):
        classname = item.__class__.__name__
        if 'Combo' in classname:
            print(f"{prefix}Found {classname}!")
            try:
                print(f"{prefix}  Model: {item.property('model')}")
                print(f"{prefix}  Width: {item.property('width')}")
                print(f"{prefix}  Height: {item.property('height')}")
                print(f"{prefix}  Visible: {item.property('visible')}")
                print(f"{prefix}  Has popup: {item.property('popup') is not None}")
            except Exception as e:
                print(f"{prefix}  Error reading properties: {e}")
    
    children = item.childItems() if hasattr(item, 'childItems') else []
    for child in children:
        find_all_combos(child, depth + 1)

print("\n--- Searching for all ComboBox items recursively ---")
find_all_combos(search_panel)

# Try to check the text rendering in a delegate
print("\n--- Checking Text rendering constraints ---")
print("""
Potential issues:
1. Text element width (324) with leftPadding (8) - text only gets ~316px
2. leftPadding property doesn't work on all Text elements
3. wrapMode: Text.NoWrap requires proper width constraint
4. Text positioned at default (0,0) within Rectangle
5. elide: Text.ElideRight only works if width is explicitly constrained

Recommended fix:
- Use anchors.left/right with margins instead of fixed width
- Or use x positioning: x: 8, width: parent.width - 8
- Ensure Text element is visible (color, font set)
""")

app.quit()
