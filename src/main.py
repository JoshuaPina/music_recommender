"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table

from src.recommender import load_songs, recommend_songs


def main() -> None:
    console = Console()
    console.rule("Music Recommender CLI", style="bright_blue")
    console.print("Initializing recommender run...", style="cyan")

    def score_style(score: float) -> str:
        if score >= 8.0:
            return "bold green"
        if score >= 5.0:
            return "bold yellow"
        return "bold red"

    console.print("Loading catalog from data/songs.csv...", style="cyan")
    songs = load_songs("data/songs.csv")
    console.print(f"Loaded Songs: {len(songs)}", style="bold green")

    # Starter example profile
    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "likes_acoustic": False,
    }

    console.print("Scoring songs against your taste profile...", style="cyan")
    recommendations = recommend_songs(user_prefs, songs, k=5)
    console.print(f"Computed top {len(recommendations)} recommendations.", style="bold green")

    console.print(
        Panel.fit(
            "Top Recommendations",
            style="cyan",
            border_style="bright_blue",
        )
    )

    table = Table(show_header=True, header_style="bold magenta", show_lines=False, expand=True)
    table.add_column("Rank", justify="right", style="bold cyan", width=6)
    table.add_column("Title", style="white", min_width=16, overflow="fold")
    table.add_column("Final Score", justify="right")
    table.add_column("Reasons", style="white", overflow="fold")

    for index, (song, score, explanation) in enumerate(recommendations):
        rank = index + 1
        reasons = "\n".join(f"- {escape(reason.strip())}" for reason in explanation.split(";") if reason.strip())
        table.add_row(f"#{rank}", song["title"], f"[{score_style(score)}]{score:.2f}[/]", reasons)
        if index < len(recommendations) - 1:
            table.add_section()

    console.print(table)
    console.print("Run complete.", style="bold cyan")
    console.rule(style="bright_blue")


if __name__ == "__main__":
    main()
