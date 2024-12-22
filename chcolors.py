import argparse
import json
import os
import re
import sys

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from termcolor import cprint
from typing import List, Dict

# TODO: load this dynamically
config_path = os.path.expanduser("~/.config/chcolors/config.json")
state_path = os.path.expanduser("~/.local/state/chcolors/state.json")


class ThemeType(Enum):
    LIGHT = 1
    DARK = 2

    @staticmethod
    def from_str(string: str) -> "ThemeType":
        match string.lower():
            case "light":
                return ThemeType.LIGHT
            case "dark":
                return ThemeType.DARK
            case _:
                raise ValueError(f'Invalid theme type "{string}"')

    def __str__(self) -> str:
        match self:
            case ThemeType.LIGHT:
                return "Light"
            case ThemeType.DARK:
                return "Dark"


@dataclass
class Theme:
    name: str
    type: ThemeType


@dataclass
class Program:
    name: str
    root_dir: Path
    patterns: List[str]


@dataclass
class Config:
    themes: List[Theme]
    aliases: Dict[str, str]
    programs: List[Program]


@dataclass
class State:
    current: str | None


def read_config() -> Config:
    data = {}
    with open(config_path, "r") as file:
        data = json.load(file)

    themes = [Theme(theme["name"], theme["type"]) for theme in data["themes"]]
    programs = [
        Program(
            program["name"], Path(program["root_dir"]).expanduser(), program["patterns"]
        )
        for program in data["programs"]
    ]

    return Config(themes, data["aliases"], programs)


def read_state() -> State:
    data = {}
    with open(state_path, "r") as file:
        data = json.load(file)

    return State(data["current"])


def write_state(state: State):
    data = {"current": state.current}
    with open(state_path, "w") as file:
        json.dump(data, file)


def stitch(match, string, name) -> str:
    head = string[: match.start("name")]
    tail = string[match.end("name") :]

    result = f"{head}{name}{tail}"
    print(f"head: {head}\n\ntail: {tail}\n\nmatch: {match.string}\n\nresult: {result}")

    return result


def set_theme(pattern: str, string: str, name: str, type: ThemeType) -> str:
    result = string
    for match in re.finditer(pattern, result, re.MULTILINE):
        for group_name in ["name", "type"]:
            try:
                head = result[: match.start(group_name)]
                tail = result[match.end(group_name) :]
                replacement = ""
                match group_name:
                    case "name":
                        replacement = name
                    case "type":
                        replacement = str(type)

                result = f"{head}{replacement}{tail}"
            except IndexError:
                # group name is unused
                pass

    return result


def cmd_status(_):
    state = read_state()
    if state.current is None:
        print("Current: unset")
    else:
        config = read_config()
        current = next((t for t in config.themes if t.name == state.current))

        print(f"Current: {current.name} [{str(current.type)}]")


def cmd_list(_):
    config = read_config()
    state = read_state()

    print("Themes:")
    for theme in config.themes:
        if theme.name == state.current:
            cprint(f"\t{theme.name} *", attrs=["bold"])
        else:
            print(f"\t{theme.name}")

    print("Aliases: ")
    for alias, target in config.aliases.items():
        print(f"\t{alias} -> {target}")


def cmd_set(args):
    config = read_config()

    theme_name = args.name
    if args.name in config.aliases:
        theme_name = config.aliases[theme_name]

    theme = next((t for t in config.themes if t.name == theme_name), None)
    if theme is None:
        print(f'Error: Theme "{theme_name}" not registered', file=sys.stderr)
        sys.exit(1)

    state = read_state()
    if state.current == theme.name and not args.force:
        print(f'Theme "{theme_name}" is already set (use --force to override)')
        sys.exit(0)

    for prog in config.programs:
        for file in filter(lambda entry: entry.is_file(), prog.root_dir.iterdir()):
            contents = ""
            with open(file, "r") as f:
                contents = f.read()

            modified = False

            for pattern in prog.patterns:
                if re.search(pattern, contents, re.MULTILINE) is None:
                    continue

                contents = set_theme(pattern, contents, theme.name, theme.type)
                modified = True

            if modified:
                with open(file, "w") as f:
                    f.write(contents)

    state.current = theme_name
    write_state(state)


def main():
    parser = argparse.ArgumentParser(
        prog="chcolors",
        description="Script for simultaneously switching color schemes in multiple config files",
        # TODO: can I grab this from pyproject.toml as a build step?
    )

    subparsers = parser.add_subparsers(title="subcommands")

    parser_status = subparsers.add_parser("status")
    parser_status.set_defaults(func=cmd_status)

    parser_list = subparsers.add_parser("list")
    parser_list.set_defaults(func=cmd_list)

    parser_set = subparsers.add_parser("set")
    parser_set.set_defaults(func=cmd_set)
    parser_set.add_argument(
        "--force", help="Set theme even if it is marked as 'current'"
    )
    parser_set.add_argument("name", help="Color scheme name")

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
