use std::collections::HashMap;
use std::error::Error;
use std::path::PathBuf;

use serde::Deserialize;

use crate::program::Program;
use crate::theme::Theme;

const CHCOLORS_CONFIG_DIR: &str = "CHCOLORS_CONFIG_DIR";

#[derive(Clone, Debug, Deserialize)]
pub struct Config {
    pub themes: Vec<Theme>,
    pub aliases: HashMap<String, String>,
    pub programs: Vec<Program>,
}

fn config_path() -> PathBuf {
    let config_dir = match std::env::var(CHCOLORS_CONFIG_DIR).ok() {
        Some(path) => PathBuf::from(path),
        None => dirs::config_dir().unwrap().join("chcolors"),
    };

    config_dir.join("config.json")
}

pub fn read_config() -> Result<Config, Box<dyn Error>> {
    let config_path = config_path();
    let json = std::fs::read_to_string(config_path)?;

    Ok(serde_json::from_str::<Config>(json.as_str()).map_err(Box::new)?)
}
