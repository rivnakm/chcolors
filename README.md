# chcolors

![Python](https://img.shields.io/badge/python-%23ffdd54?style=for-the-badge&logo=python&logoColor=black)

Script for simultaneously switching color schemes in multiple config files

## Usage

### Example config

First, create a config file, the default location is `$HOME/.config/chcolors/config.json`

```json
{
    "$schema": "https://raw.githubusercontent.com/rivnakm/chcolors/refs/heads/main/config.schema.json",
    "themes": [
        {
            "name": "modus_vivendi",
            "type": "Dark"
        },
        {
            "name": "modus_operandi",
            "type": "Light"
        }
    ],
    "aliases": {
        "dark": "modus_vivendi",
        "light": "modus_operandi"
    },
    "programs": [
        {
            "name": "alacritty",
            "root_dir": "~/.config/alacritty",
            "patterns": [
                "^import = \\[\\s+.*?\\\"~/\\.config/alacritty/(?P<name>.*)\\.toml\\\""
            ]
        },
        {
            "name": "neovim",
            "root_dir": "~/.config/nvim",
            "patterns": [
                "^vim\\.o\\.background = \\\"(?P<type>Dark|Light)\\\"$",
                "^vim\\.cmd\\.colorscheme\\(\\\"(?P<name>.*)\\\"\\)$"
            ]
        }
    ]
}
```

### Setting the current theme

```
python chcolors.py set modus_vivendi
```

