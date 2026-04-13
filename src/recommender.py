from csv import DictReader
from typing import Any, List, Dict, Tuple, Optional
from dataclasses import dataclass


# Weighting is tuned for a small catalog where genre and mood are the clearest
# indicators of taste, and numeric features fine-tune the ranking.
GENRE_MATCH_POINTS = 4.0
MOOD_MATCH_POINTS = 3.0
ENERGY_MATCH_POINTS = 2.5
ACOUSTIC_MATCH_POINTS = 1.0

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        """Store the catalog used for generating recommendations."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs ranked by score for the given user."""
        scored_songs = []
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }

        for song in self.songs:
            score, _ = score_song(user_prefs, song.__dict__)
            scored_songs.append((song, score))

        scored_songs.sort(key=lambda item: item[1], reverse=True)
        return [song for song, _ in scored_songs[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a readable explanation of why a song was recommended."""
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }
        _, reasons = score_song(user_prefs, song.__dict__)
        return "; ".join(reasons) if reasons else "This song is a reasonable match for the user's taste profile."

def _get_value(item: Any, key: str, default: Any = None) -> Any:
    """Get a value from a dict or object attribute with a default fallback."""
    if isinstance(item, dict):
        return item.get(key, default)
    return getattr(item, key, default)


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    """Clamp a numeric value to the inclusive [minimum, maximum] range."""
    return max(minimum, min(maximum, value))


def _normalized_distance_score(value: float, target: float) -> float:
    """Convert absolute distance from target into a normalized similarity score."""
    return _clamp(1.0 - abs(value - target))


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file using Python's csv module.
    Numeric fields are converted for downstream scoring:
    - id -> int
    - energy, tempo_bpm, valence, danceability, acousticness -> float
    Required by src/main.py
    """
    songs: List[Dict[str, Any]] = []
    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        reader = DictReader(csv_file)
        for row in reader:
            songs.append(
                {
                    "id": int(row["id"]),
                    "title": row["title"],
                    "artist": row["artist"],
                    "genre": row["genre"],
                    "mood": row["mood"],
                    "energy": float(row["energy"]),
                    "tempo_bpm": float(row["tempo_bpm"]),
                    "valence": float(row["valence"]),
                    "danceability": float(row["danceability"]),
                    "acousticness": float(row["acousticness"]),
                }
            )
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    genre = _get_value(song, "genre", "")
    mood = _get_value(song, "mood", "")
    energy = float(_get_value(song, "energy", 0.0) or 0.0)
    acousticness = float(_get_value(song, "acousticness", 0.0) or 0.0)

    preferred_genre = user_prefs.get("genre") or user_prefs.get("favorite_genre")
    preferred_mood = user_prefs.get("mood") or user_prefs.get("favorite_mood")
    target_energy = user_prefs.get("energy", user_prefs.get("target_energy", 0.0))
    likes_acoustic = bool(user_prefs.get("likes_acoustic", False))

    score = 0.0
    reasons: List[str] = []

    # Strong categorical matches.
    if preferred_genre and genre == preferred_genre:
        score += GENRE_MATCH_POINTS
        reasons.append(f"genre match (+{GENRE_MATCH_POINTS:.1f})")

    if preferred_mood and mood == preferred_mood:
        score += MOOD_MATCH_POINTS
        reasons.append(f"mood match (+{MOOD_MATCH_POINTS:.1f})")

    # Distance-based numeric scoring rewards songs that are close to the user's target.
    energy_match = _normalized_distance_score(energy, float(target_energy))
    energy_points = energy_match * ENERGY_MATCH_POINTS
    score += energy_points
    reasons.append(
        f"energy similarity (+{energy_points:.2f}) [song={energy:.2f}, target={float(target_energy):.2f}]"
    )

    preferred_acousticness = 1.0 if likes_acoustic else 0.0
    acoustic_match = _normalized_distance_score(acousticness, preferred_acousticness)
    acoustic_points = acoustic_match * ACOUSTIC_MATCH_POINTS
    score += acoustic_points
    if likes_acoustic:
        reasons.append(f"acoustic preference match (+{acoustic_points:.2f}) [prefers acoustic]")
    else:
        reasons.append(f"acoustic preference match (+{acoustic_points:.2f}) [prefers less acoustic]")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored_songs = [
        (song, score, "; ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, song)]
    ]

    ranked_songs = sorted(scored_songs, key=lambda item: item[1], reverse=True)
    return ranked_songs[:k]
