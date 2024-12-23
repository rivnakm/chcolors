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


def config_dir() -> Path:
    env_key = "CHCOLORS_CONFIG_DIR"
    if env_key in os.environ:
        return Path(os.environ[env_key]).expanduser()
    else:
        return Path(os.environ["HOME"]).joinpath(".config/chcolors")


def state_dir() -> Path:
    env_key = "CHCOLORS_STATE_DIR"
    if env_key in os.environ:
        return Path(os.environ[env_key]).expanduser()
    else:
        return Path(os.environ["HOME"]).joinpath(".local/state/chcolors")


def config_path() -> Path:
    return config_dir().joinpath("config.json")


def state_path() -> Path:
    return state_dir().joinpath("state.json")


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

    @staticmethod
    def default() -> "Config":
        return Config([], {}, [])


@dataclass
class State:
    current: str | None

    @staticmethod
    def default() -> "State":
        return State(None)


def read_config() -> Config:
    if not config_path().exists():
        config = Config.default()
        write_config(config)
        return config

    data = {}
    with open(config_path(), "r") as file:
        data = json.load(file)

    themes = [
        Theme(theme["name"], ThemeType.from_str(theme["type"]))
        for theme in data["themes"]
    ]
    programs = [
        Program(program["name"], Path(program["root_dir"]), program["patterns"])
        for program in data["programs"]
    ]

    return Config(themes, data["aliases"] if "aliases" in data else {}, programs)


def write_config(config: Config):
    schema_url = "https://raw.githubusercontent.com/rivnakm/chcolors/refs/heads/main/config.schema.json"

    data = {
        "$schema": schema_url,
        "themes": [
            {"name": theme.name, "type": str(theme.type)} for theme in config.themes
        ],
        "programs": [
            {
                "name": program.name,
                "root_dir": str(program.root_dir),
                "patterns": program.patterns,
            }
            for program in config.programs
        ],
    }
    if len(config.aliases) > 0:
        data["aliases"] = config.aliases

    if not config_path().parent.exists():
        os.makedirs(config_path().parent)

    with open(config_path(), "w") as file:
        json.dump(data, file)


def read_state() -> State:
    if not state_path().exists():
        state = State.default()
        write_state(state)
        return state

    data = {}
    with open(state_path(), "r") as file:
        data = json.load(file)

    return State(data["current"])


def write_state(state: State):
    data = {"current": state.current}

    if not state_path().parent.exists():
        os.makedirs(state_path().parent)

    with open(state_path(), "w") as file:
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
        for file in filter(
            lambda entry: entry.is_file(), prog.root_dir.expanduser().iterdir()
        ):
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
