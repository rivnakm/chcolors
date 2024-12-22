from chcolors import ThemeType, set_theme


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
