# Telex

![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![GTK](https://img.shields.io/badge/gtk-4.0-green.svg)
![Platform](https://img.shields.io/badge/platform-Linux%20|%20Windows%20|%20macOS-lightgrey.svg)

A modern, native Reddit client built with GTK4, LibAdwaita and Python. Telex provides a clean, fast, and feature-rich interface for browsing Reddit on Linux, Windows, and macOS.

## Features

- Clean, native GTK4 interface
- OAuth2 authentication with Reddit
- Secure credential storage using AWS Secrets Manager
- Responsive design that adapts to window size
- Cross-platform support

### System Requirements

- GTK 4
- Libadwaita 1.1
- Python 3.12+

## Development

Install system dependencies:

```bash
# Ubuntu/Debian
sudo apt install libgirepository-2.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-4.0 libadwaita-1-dev

# Fedora
sudo dnf install gcc gobject-introspection-devel cairo-gobject-devel pkg-config python3-devel gtk4 libadwaita-devel

# Arch Linux
sudo pacman -S python cairo pkgconf gobject-introspection gtk4 libadwaita
```

Clone the repository:

```bash
git clone --single-branch -b main https://github.com/believemanasseh/telex-python
cd telex-python
```

Install Python dependencies:

```bash
pipenv --python 3.12
source .venv/bin/activate
pipenv install --dev
```

Build with meson and run:

```bash
chmod +x build.sh
./build.sh
```

Alternatively, you can run entrypoint:

```bash
python src/app.py
```

### VSCode Development

For the best development experience, we recommend using Visual Studio Code with the Flatpak extension:

1. Install the [Flatpak VSCode Extension](https://marketplace.visualstudio.com/items?itemName=bilelmoussaoui.flatpak-vscode)
2. Open the project in VSCode
3. Use the extension's build and run commands

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your branch
5. Create a Pull Request

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [GTK Team](https://gtk.org/) for the amazing GUI toolkit
- [Reddit API](https://www.reddit.com/dev/api/) documentation
