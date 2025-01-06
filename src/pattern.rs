use regex::Regex;

use crate::theme::Theme;

pub fn use_pattern(pattern: &Regex, contents: &str, theme: &Theme) -> Option<String> {
    let mut result = contents.to_owned();
    let mut found_match = false;
    for capture in pattern.captures_iter(contents) {
        found_match = true;

        for group_name in ["name", "type"] {
            if let Some(m) = capture.name(group_name) {
                let head = &result[..m.start()];
                let tail = &result[m.end()..];
                let replacement = match group_name {
                    "name" => theme.name.clone(),
                    "type" => theme.theme_type.to_string(),
                    _ => unreachable!(),
                };

                result = format!("{}{}{}", head, replacement, tail);
            }
        }
    }

    if found_match {
        Some(result)
    } else {
        None
    }
}

#[cfg(test)]
mod tests {
    use regex::RegexBuilder;

    use crate::theme::{Theme, ThemeType};

    use super::*;

    #[test]
    fn test_sub_name_single_line() {
        let pattern = Regex::new(r"^colorscheme: (?P<name>.*)$").unwrap();
        let content = "colorscheme: gruvbox";
        let new_theme = Theme {
            name: "dracula".into(),
            theme_type: ThemeType::Dark,
        };

        let output = use_pattern(&pattern, content, &new_theme);

        assert!(output.is_some_and(|o| o == "colorscheme: dracula"));
    }

    #[test]
    fn test_sub_name_multiple_lines() {
        let pattern = RegexBuilder::new(r"^colorscheme: (?P<name>.*)$")
            .multi_line(true)
            .build()
            .unwrap();
        let content = "option: true\ncolorscheme: gruvbox\nother_option: false\n";
        let new_theme = Theme {
            name: "dracula".into(),
            theme_type: ThemeType::Dark,
        };

        let output = use_pattern(&pattern, content, &new_theme);

        assert!(output
            .is_some_and(|o| o == "option: true\ncolorscheme: dracula\nother_option: false\n"));
    }

    #[test]
    fn test_sub_name_multiple_matches() {
        let pattern = RegexBuilder::new(r"^colorscheme: (?P<name>.*)$")
            .multi_line(true)
            .build()
            .unwrap();
        let content = "option: true\ncolorscheme: gruvbox\nother_option: false\ncolorscheme: gruvbox\nanother_option: 1\n";
        let new_theme = Theme {
            name: "dracula".into(),
            theme_type: ThemeType::Dark,
        };

        let output = use_pattern(&pattern, content, &new_theme);

        assert!(output.is_some_and(|o| o == "option: true\ncolorscheme: dracula\nother_option: false\ncolorscheme: dracula\nanother_option: 1\n"));
    }
}
