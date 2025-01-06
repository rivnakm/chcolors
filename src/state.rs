use std::{error::Error, path::PathBuf};

use serde::{Deserialize, Serialize};

const CHCOLORS_STATE_DIR: &str = "CHCOLORS_STATE_DIR";

#[derive(Clone, Debug, Default, Deserialize, Serialize)]
pub struct State {
    pub current: Option<String>,
}

fn state_path() -> PathBuf {
    let state_dir = match std::env::var(CHCOLORS_STATE_DIR).ok() {
        Some(path) => PathBuf::from(path),
        None => dirs::state_dir().unwrap().join("chcolors"),
    };

    state_dir.join("state.json")
}

pub fn read_state() -> Result<State, Box<dyn Error>> {
    let state_path = state_path();

    if !state_path.exists() {
        write_state(&State::default())?;
    }

    let json = std::fs::read_to_string(state_path)?;

    Ok(serde_json::from_str::<State>(json.as_str()).map_err(Box::new)?)
}

pub fn write_state(state: &State) -> Result<(), Box<dyn Error>> {
    let state_path = state_path();

    let state_path_parent = state_path.parent().unwrap();
    if !state_path_parent.exists() {
        std::fs::create_dir_all(state_path_parent)?;
    }

    std::fs::write(&state_path, serde_json::to_string(state)?)?;

    Ok(())
}
