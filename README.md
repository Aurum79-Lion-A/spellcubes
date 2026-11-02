# SpellCubes Document Editor v1.0

A small, lightweight and multi-lingual PDF and document creating program written in Python with PySide6. Write plain text, or add headings, fonts, bold, italic, underline, tables, charts, pictures then export to PDF or save to SpellCubes' own `.cube` format.

(c) Copyright 2024-2026 Lion-A Softwares

## Features

- Plain text, chart and table editing with undo/redo, find, line/selection and select all
- Rich formatting: any size, any installed font, **bold**, *italic*, *_underline*_
- Export to PDF (`.pdf`), any supported format (`.*`) or SpellCubes format `.cube`
- Opens `.cube` files without losing tables or any rich media
- User language preference is saved. Has more than 12+ Languages
- Printing is supported
- Built-in Help window with license information
- Toolbar replaceable, moveable and resizeable
## Requirements

- Python 3.14 or above
- PySide and some additional libs.

## Installation
- Use as python file or get the setup file from releases when available
## File formats

| Format | How it is saved | Editable |
|---|---|---|
| `.pdf` | Adobes document format. Keeps colouring, pictures and charts | No, you will probably need Adobe Acrobat. |
| `.cube` | SpellCubes' own format. Keeps colouring, pictures and charts | Yes, SpellCubes can edit, convert and read .cube files |

Choose `.cube` if you want to edit it again later on SpellCubes. .cube saves all chart, media etc.
Choose `.pdf` if you want to portability and universality. .pdf saves all chart, media etc. but you can't edit them later on SpellCubes.

When a document has charts, font pictures, tables or any formatting, **Save as...** may not be able to save them. Use one of the safer save options instead, like **.cube or .pdf**.

## Keyboard shortcuts

| Shortcut | Action |
|---|---|
| Ctrl+N | New |
| Ctrl+O | Open |
| Ctrl+S | Save |
| Ctrl+Shift+S | Save as... |
| Ctrl+P | Print ||
| Ctrl+Q | Leave |
| Ctrl+Z / Alt+Z | Undo / Redo |
| Ctrl+F | Find & Replace|
| F3 | Find next |
| Ctrl+A | Select all |
| Help | Help |


## Limitations

- Can't edit or view `.pdf` files.

## License

SpellCubes is free software, licensed under the **GNU General Public License, version 3 (GPLv3)**.

This program is distributed in the hope that it will be useful, but **WITHOUT ANY WARRANTY**; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

by Mr. Cobalt, Thanks
