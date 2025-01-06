use std::{error::Error, process::Command};

use glob::glob;
use regex::RegexBuilder;
use serde::Deserialize;

use crate::{pattern::use_pattern, theme::Theme};

// Hook environment
const CHCOLORS_NAME: &str = "CHCOLORS_NAME";
const CHCOLORS_TYPE: &str = "CHCOLORS_TYPE";

#[derive(Clone, Debug, Deserialize)]
pub struct Program {
    pub name: String,
    pub path: String,

    #[serde(default)]
    pub patterns: Vec<String>,

    #[serde(default)]
    pub hooks: Vec<String>,
}

impl Program {
    pub fn set_theme(&self, theme: &Theme) -> Result<(), Box<dyn Error>> {
        let files = glob(&self.path.replace(
            "~",
            String::from(dirs::home_dir().unwrap().to_string_lossy()).as_str(),
        ))
        .expect("invalid glob") // TODO: error handling
        .filter_map(|e| e.map_err(|e| eprintln!("glob error: {:?}", e)).ok())
        .filter(|e| e.as_path().is_file());

        for file in files {
            eprintln!("file: {:?}", file);
            let mut contents = std::fs::read_to_string(file.as_path())?;
            let mut modified = false;

            for pattern in self.patterns.iter() {
                let re = RegexBuilder::new(pattern)
                    .multi_line(true)
                    .build()
                    // TODO: handle error better
                    .expect("Pattern is not valid regex");

                if let Some(c) = use_pattern(&re, &contents, theme) {
                    contents = c;
                    modified = true;
                }
            }

            if modified {
                std::fs::write(file.as_path(), contents)?;
            }
        }

        for hook in self.hooks.iter() {
            // TODO: handle error better
            let mut child = Command::new("sh")
                .args(["-c", hook])
                .envs([
                    (CHCOLORS_NAME, theme.name.as_str()),
                    (CHCOLORS_TYPE, theme.theme_type.to_string().as_str()),
                ])
                .spawn()
                .expect("Failed to run hook");
            child.wait().expect("Hook returned nonzero exit code");
        }
        Ok(())
    }
}
