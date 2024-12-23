import os
import shutil
import uuid

from chcolors import (
    ThemeType,
    config_dir,
    state_dir,
    read_config,
    read_state,
    set_theme,
)
from tempfile import TemporaryDirectory


def test_sub_name_single_line():
    pattern = r"^colorscheme: (?P<name>.*)$"
    string = "colorscheme: gruvbox"
    new_name = "dracula"

    expected = "colorscheme: dracula"

    actual = set_theme(pattern, string, new_name, ThemeType.DARK)

    assert actual == expected


def test_sub_name_multiple_line():
    pattern = r"^colorscheme: (?P<name>.*)$"
    string = "option: true\ncolorscheme: gruvbox\nother_option: false"
    new_name = "dracula"

    expected = "option: true\ncolorscheme: dracula\nother_option: false"

    actual = set_theme(pattern, string, new_name, ThemeType.DARK)

    assert actual == expected


def test_sub_name_multiple_matches():
    pattern = r"^colorscheme: (?P<name>.*)$"
    string = "option: true\ncolorscheme: gruvbox\nother_option: false\ncolorscheme: gruvbox\nanother_option: 1"
    new_name = "dracula"

    expected = "option: true\ncolorscheme: dracula\nother_option: false\ncolorscheme: dracula\nanother_option: 1"

    actual = set_theme(pattern, string, new_name, ThemeType.DARK)

    assert actual == expected


def test_set_theme_multiple_line():
    pattern = r"^colorscheme_type: (?P<type>Light|Dark)$"
    string = "option: true\ncolorscheme_type: Light\nother_option: false"

    expected = "option: true\ncolorscheme_type: Dark\nother_option: false"

    actual = set_theme(pattern, string, "", ThemeType.DARK)

    assert actual == expected


def test_get_config_dir():
    path = f"~/foo/bar/{uuid.uuid4()}"
    os.environ["CHCOLORS_CONFIG_DIR"] = path

    expected = os.path.expanduser(path)

    actual = str(config_dir())

    assert actual == expected


def test_get_state_dir():
    path = f"~/foo/bar/{uuid.uuid4()}"
    os.environ["CHCOLORS_STATE_DIR"] = path

    expected = os.path.expanduser(path)

    actual = str(state_dir())

    assert actual == expected


def test_read_config():
    with TemporaryDirectory() as tempdir:
        os.environ["CHCOLORS_CONFIG_DIR"] = tempdir
        shutil.copyfile(
            "test/examples/config.json", os.path.join(tempdir, "config.json")
        )

        config = read_config()

        assert len(config.themes) == 2
        assert len(config.aliases) == 2
        assert len(config.programs) == 3

        assert config.themes[0].name == "modus_vivendi"
        assert config.themes[0].type == ThemeType.DARK

        assert config.aliases["light"] == "modus_operandi"

        assert config.programs[1].name == "neovim"
        assert len(config.programs[1].patterns) == 2


def test_read_config_no_existing_config():
    with TemporaryDirectory() as tempdir:
        os.environ["CHCOLORS_CONFIG_DIR"] = tempdir
        file_path = os.path.join(tempdir, "config.json")

        assert not os.path.exists(file_path)

        config = read_config()

        assert os.path.exists(file_path)

        assert len(config.themes) == 0
        assert len(config.aliases) == 0
        assert len(config.programs) == 0


def test_read_state():
    with TemporaryDirectory() as tempdir:
        os.environ["CHCOLORS_STATE_DIR"] = tempdir
        shutil.copyfile("test/examples/state.json", os.path.join(tempdir, "state.json"))

        state = read_state()

        assert state.current == "modus_vivendi"


def test_read_state_no_existing_state():
    with TemporaryDirectory() as tempdir:
        os.environ["CHCOLORS_STATE_DIR"] = tempdir
        file_path = os.path.join(tempdir, "state.json")

        assert not os.path.exists(file_path)

        state = read_state()

        assert os.path.exists(file_path)

        assert state.current is None
