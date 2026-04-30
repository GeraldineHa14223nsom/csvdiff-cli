"""XML export formatter for diff results."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Dict

from csvdiff.core import DiffResult


@dataclass
class XmlOptions:
    title: str = "csvdiff"
    indent: int = 2
    max_rows: int = 500


def _truncate(value: str, max_len: int = 200) -> str:
    if len(value) > max_len:
        return value[:max_len] + "..."
    return value


def _row_elem(parent: ET.Element, tag: str, row: Dict[str, str]) -> ET.Element:
    elem = ET.SubElement(parent, tag)
    for key, value in row.items():
        child = ET.SubElement(elem, key)
        child.text = _truncate(str(value))
    return elem


def _section(
    parent: ET.Element,
    section_tag: str,
    item_tag: str,
    rows: List[Dict[str, str]],
    max_rows: int,
) -> None:
    section = ET.SubElement(parent, section_tag)
    section.set("count", str(len(rows)))
    for row in rows[:max_rows]:
        _row_elem(section, item_tag, row)


def format_xml(result: DiffResult, options: XmlOptions | None = None) -> str:
    if options is None:
        options = XmlOptions()

    root = ET.Element(options.title)

    _section(root, "added", "row", result.added, options.max_rows)
    _section(root, "removed", "row", result.removed, options.max_rows)

    modified_section = ET.SubElement(root, "modified")
    modified_section.set("count", str(len(result.modified)))
    for pair in result.modified[: options.max_rows]:
        change = ET.SubElement(modified_section, "change")
        _row_elem(change, "before", pair["before"])
        _row_elem(change, "after", pair["after"])

    ET.indent(root, space=" " * options.indent)
    return ET.tostring(root, encoding="unicode", xml_declaration=False)
