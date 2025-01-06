use clap::{Args, Parser, Subcommand};
use config::read_config;
use state::{read_state, write_state};

mod config;
mod hook;
mod pattern;
mod program;
mod state;
mod theme;

#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Command,
}

#[derive(Subcommand, Debug)]
enum Command {
    List,
    Set(SetCommandArgs),
    Status,
}

#[derive(Args, Debug)]
struct SetCommandArgs {
    name: String,

    #[arg(short, long)]
    force: bool,
}

fn cmd_list() {
    // TODO: handle error better
    let config = read_config().expect("Failed to read config");
    let state = read_state().expect("Failed to read state file");

    println!("Themes:");
    for theme in config.themes {
        if state
            .current
            .clone()
            .is_some_and(|current| theme.name == current)
        {
            println!("\t{} *", theme.name);
        } else {
            println!("\t{}", theme.name);
        }
    }

    println!("Aliases:");
    for (alias, target) in config.aliases {
        println!("\t{} -> {}", alias, target);
    }
}

fn cmd_set(args: SetCommandArgs) {
    // TODO: handle error better
    let config = read_config().expect("Failed to read config");
    let mut state = read_state().expect("Failed to read state file");

    let theme_name = match config.aliases.get(&args.name) {
        Some(alias_target) => alias_target.clone(),
        None => args.name,
    };

    let Some(theme) = config.themes.into_iter().find(|t| t.name == theme_name) else {
        eprintln!("Specified theme not found in config file");
        std::process::exit(-1);
    };

    if state.current.clone().is_some_and(|c| c == theme_name) && !args.force {
        eprintln!(
            "Theme \"{}\" is already set (use --force to override)",
            theme_name
        );
        std::process::exit(-1);
    }

    for program in config.programs {
        // TODO: handle error better
        program
            .set_theme(&theme)
            .inspect_err(|e| eprintln!("{}", e))
            .unwrap_or_else(|_| panic!("Failed to set theme for {}", program.name));
    }

    state.current = Some(theme_name);

    write_state(&state).expect("Failed to write state");
}

fn cmd_status() {
    // TODO: handle error better
    let state = read_state().expect("Failed to read state file");
    println!("Current: {}", state.current.unwrap_or("unset".into()));
}

fn main() {
    let args = Cli::parse();

    match args.command {
        Command::List => cmd_list(),
        Command::Set(args) => cmd_set(args),
        Command::Status => cmd_status(),
    }
}
