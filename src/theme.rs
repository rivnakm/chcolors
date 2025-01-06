use serde::Deserialize;
use strum::Display;

#[derive(Clone, Debug, Deserialize, Display)]
pub enum ThemeType {
    Dark,
    Light,
}

#[derive(Clone, Debug, Deserialize)]
pub struct Theme {
    pub name: String,

    #[serde(rename = "type")]
    pub theme_type: ThemeType,
}
