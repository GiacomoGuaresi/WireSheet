<p align="center">
  <img src="wiresheet/resources/icon.svg" width="96" alt="">
</p>

<h1 align="center">WireSheet</h1>

<p align="center"><a href="README.md">🇮🇹 Italiano</a> · <b>🇬🇧 English</b></p>

<p align="center">
  Desktop app to draw <b>cable assembly drawings</b> and export them to PDF:<br>
  end 1 → wires → end 2, with labels, a WIRE LIST and a title block.
</p>

<p align="center">
  <a href="https://github.com/GiacomoGuaresi/WireSheet/actions/workflows/ci.yml"><img src="https://github.com/GiacomoGuaresi/WireSheet/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/GiacomoGuaresi/WireSheet/releases/latest"><img src="https://img.shields.io/github/v/release/GiacomoGuaresi/WireSheet" alt="Release"></a>
  <img src="https://img.shields.io/badge/python-3.12-blue" alt="Python 3.12">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS-lightgrey" alt="Windows | macOS">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="MIT"></a>
</p>

---

Describe your cables in a card-based window (or import them from Excel/CSV) and WireSheet produces an A3 PDF ready for whoever builds them: a drawing of each cable with the real connectors, wire colours, labels and the connection table.

> [!NOTE]
> The user interface and the documentation in [`docs/`](docs/README.md) are in **Italian**. The text on the PDF drawings (WIRE LIST, FROM/TO, title block…) is in English.

<p align="center">
  <img src="docs/images/main-window.png" width="49%" alt="Main window with the stack of cable cards">
  <img src="docs/images/branched-cable.png" width="40%" alt="PDF sheet with a branched cable and its WIRE LIST">
</p>

## Features

- **Card editor**: one card per cable, with P1/P2 ends, a thumbnail of the component, a wire table (pin, colour, length, cross-section) and live validation.
- **Branched cables**: one input end and several outputs, each with its own component and label.
- **Supported components**: JST XH 2–7 pin, GM circular panel connectors (GM-1312, GM-1712, GM-2112), 5.08 mm pluggable terminal blocks 2–8 pole, ferrules, fork terminals, 6.3 mm female faston, flat cut.
- **IEC 60757 colours**, including two-colour wires (e.g. `YE/GN`), and cross-sections in mm² and/or AWG with automatic conversion.
- **A3 PDF export** with frame, title block (title, company, project, author, date, revision) and page numbers.
- **Excel and CSV import/export** with a downloadable template: one row per wire, Italian or English headers, forgiving values (`rosso`/`RD`, `12,5`).
- **Live preview** of a single cable or of the sheet it will end up on.
- **Project files** `.wiresheet` (readable JSON) with a revision number that goes up on every save.
- **Update check**: at startup (can be turned off) or from the *Aiuto* (Help) menu; when a newer version exists it offers to open the release page.

## Download

Binaries are on the [Releases](https://github.com/GiacomoGuaresi/WireSheet/releases/latest) page:

| System | File |
|---|---|
| Windows 10/11 (x64) | `WireSheet-<version>-windows-x64.zip`: extract the `WireSheet` folder anywhere and run `WireSheet.exe` |
| macOS 11+ (Apple Silicon, M1 or later) | `WireSheet-<version>-macos-arm64.zip`: extract it and move `WireSheet.app` to *Applications* |

On Intel Macs, and on Linux, run WireSheet [from source](#running-from-source). `SHA256SUMS.txt` lists the file checksums.

> [!NOTE]
> The binaries are not signed, so the system asks for confirmation the first time:
> - **Windows**: if SmartScreen blocks the app, choose *More info → Run anyway*.
> - **macOS**: open `WireSheet.app`, dismiss the warning, then go to *System Settings → Privacy & Security* and choose *Open Anyway*. Or, from Terminal: `xattr -dr com.apple.quarantine /Applications/WireSheet.app`.

## Running from source

Requires Python 3.12 or later.

```bash
git clone https://github.com/GiacomoGuaresi/WireSheet.git
cd WireSheet
python -m venv .venv

# Windows
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m wiresheet

# macOS / Linux
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m wiresheet
```

Other useful commands:

```bash
python -m wiresheet project.wiresheet   # open a project directly
python -m wiresheet.demo                # write demo.pdf with 10 sample cables
python -m pytest -q                     # tests (no display needed: Qt offscreen platform)
```

## Building the binaries

Binaries are built with [PyInstaller](https://pyinstaller.org/) from [`packaging/wiresheet.spec`](packaging/wiresheet.spec):

```bash
python -m pip install pyinstaller pillow
pyinstaller --noconfirm packaging/wiresheet.spec   # → dist/WireSheet/WireSheet.exe or dist/WireSheet.app
```

PyInstaller does not cross-compile: build the `.exe` on Windows and the `.app` on macOS. To check a binary without opening the window, run the smoke test `WireSheet --self-test <folder>`: it exports the demo PDF and the Excel template and exits with 0 when everything works.

### Pipelines

- **CI** ([`ci.yml`](.github/workflows/ci.yml)): runs the tests on Windows and macOS on every push to `main` and every pull request.
- **Release** ([`release.yml`](.github/workflows/release.yml)): on a `v*` tag it checks the tag matches the app version, runs the tests, builds the Windows and macOS binaries, smoke-tests them and publishes a GitHub Release with the zips, checksums and notes taken from [`CHANGELOG.md`](CHANGELOG.md).

For a new version: bump `__version__` in [`wiresheet/__init__.py`](wiresheet/__init__.py), add the section to [`CHANGELOG.md`](CHANGELOG.md) and push the matching tag:

```bash
git commit -am "Version 1.0.1" && git push
git tag v1.0.1
git push origin v1.0.1
```

From the *Actions* tab you can also run *Release* manually to get the binaries as artifacts without publishing a release.

## Stack

[Python 3.12](https://www.python.org/) · [PySide6 / Qt 6](https://doc.qt.io/qtforpython-6/) for the UI, vector drawing (`QPainter`) and PDF (`QPdfWriter`) · [openpyxl](https://openpyxl.readthedocs.io/) for Excel files · [pytest](https://pytest.org/) · [PyInstaller](https://pyinstaller.org/) for the binaries.

> WireSheet used to be called *CableGen*: `.cablegen` projects still open.

## License

[MIT](LICENSE) © Giacomo Guaresi
