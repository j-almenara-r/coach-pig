#!/usr/bin/env python3
"""
Basketball Rotation Generator for 3K Pigs

Generates a rotation schedule for a basketball game, distributing playing time
evenly among all attending players while ensuring balanced stints and rest periods.

Game duration: 40 minutes (4 quarters of 10 minutes each)
Minimum stint duration: 2.5 minutes
"""

import argparse
import sys
from typing import List, Tuple


# Game constants
GAME_DURATION_MINUTES = 40
QUARTERS = 4
QUARTER_DURATION = GAME_DURATION_MINUTES // QUARTERS  # 10 minutes per quarter
PLAYERS_ON_COURT = 5
MIN_STINT_DURATION = 2.5


def calculate_rotation_schedule(players: List[str]) -> Tuple[List[List[str]], float, float]:
    """
    Calculate the rotation schedule for a given list of players.
    
    Args:
        players: List of player names attending the game
        
    Returns:
        A tuple containing:
        - Schedule matrix: list of time slots, each containing players on court
        - Minutes per player
        - Stint duration
    """
    num_players = len(players)
    if num_players < PLAYERS_ON_COURT:
        raise ValueError(f"Need at least {PLAYERS_ON_COURT} players to play basketball")
    
    # Calculate total available playing time and time per player
    total_court_minutes = GAME_DURATION_MINUTES * PLAYERS_ON_COURT  # 200 player-minutes
    minutes_per_player = total_court_minutes / num_players
    
    # Use fixed 2.5 minute slots
    # Validate that game duration divides evenly by slot duration
    if GAME_DURATION_MINUTES % MIN_STINT_DURATION != 0:
        raise ValueError(f"Game duration ({GAME_DURATION_MINUTES}) must be divisible by slot duration ({MIN_STINT_DURATION})")
    num_slots = int(GAME_DURATION_MINUTES / MIN_STINT_DURATION)
    actual_slot_duration = MIN_STINT_DURATION
    
    # Generate rotation using balanced round-robin approach
    schedule = []
    player_slots_played = {p: 0 for p in players}
    player_rested_slots = {p: 0 for p in players}  # Track rest to balance it
    
    for slot in range(num_slots):
        # Sort players by: 1) least slots played, 2) most slots rested, 3) player index
        available_players = sorted(
            players, 
            key=lambda p: (player_slots_played[p], -player_rested_slots[p], players.index(p))
        )
        
        # Select 5 players
        court_players = available_players[:PLAYERS_ON_COURT]
        
        # Update tracking
        for player in players:
            if player in court_players:
                player_slots_played[player] += 1
                player_rested_slots[player] = 0
            else:
                player_rested_slots[player] += 1
        
        schedule.append(court_players)
    
    return schedule, minutes_per_player, actual_slot_duration


def generate_detailed_schedule(players: List[str]) -> Tuple[List[dict], float, float]:
    """
    Generate a detailed schedule with time ranges and quarter information.
    
    Args:
        players: List of player names attending
        
    Returns:
        Tuple containing:
        - List of dictionaries with schedule details
        - Minutes per player
        - Slot duration
    """
    schedule, minutes_per_player, slot_duration = calculate_rotation_schedule(players)
    
    detailed = []
    for slot_idx, players_on_court in enumerate(schedule):
        start_time = slot_idx * slot_duration
        end_time = (slot_idx + 1) * slot_duration
        quarter = int(start_time // QUARTER_DURATION) + 1
        
        detailed.append({
            'slot': slot_idx + 1,
            'quarter': quarter,
            'start_time': start_time,
            'end_time': end_time,
            'duration': slot_duration,
            'players': players_on_court,
            'on_bench': [p for p in players if p not in players_on_court]
        })
    
    return detailed, minutes_per_player, slot_duration


def format_time(minutes: float) -> str:
    """Format minutes as MM:SS string."""
    total_seconds = int(minutes * 60)
    mins = total_seconds // 60
    secs = total_seconds % 60
    return f"{mins:02d}:{secs:02d}"


def generate_csv(players: List[str], filename: str = None) -> str:
    """
    Generate a CSV file with the rotation schedule.
    
    Args:
        players: List of player names attending
        filename: Output filename (optional, will print to stdout if not provided)
        
    Returns:
        CSV content as string
    """
    num_players = len(players)
    schedule, minutes_per_player, slot_duration = generate_detailed_schedule(players)
    
    output_lines = []
    
    # Summary header
    output_lines.append(f"# Rotation Schedule for {num_players} Players")
    output_lines.append(f"# Minutes per player: {minutes_per_player:.1f}")
    output_lines.append(f"# Stint duration: {slot_duration:.1f} minutes")
    output_lines.append("")
    
    # CSV header
    header = ["Slot", "Quarter", "Start", "End", "Duration (min)"]
    header.extend(players)
    output_lines.append(",".join(header))
    
    # Data rows
    for entry in schedule:
        row = [
            str(entry['slot']),
            str(entry['quarter']),
            format_time(entry['start_time']),
            format_time(entry['end_time']),
            f"{entry['duration']:.1f}"
        ]
        # Mark which players are on court (1) or bench (0)
        for player in players:
            row.append("1" if player in entry['players'] else "0")
        
        output_lines.append(",".join(row))
    
    content = "\n".join(output_lines)
    
    if filename:
        with open(filename, 'w', newline='') as f:
            f.write(content)
        print(f"CSV saved to {filename}")
    
    return content


def generate_markdown(players: List[str], filename: str = None) -> str:
    """
    Generate a Markdown table with the rotation schedule.
    
    Args:
        players: List of player names attending
        filename: Output filename (optional)
        
    Returns:
        Markdown content as string
    """
    num_players = len(players)
    schedule, minutes_per_player, slot_duration = generate_detailed_schedule(players)
    
    lines = []
    
    # Title and summary
    lines.append(f"# Rotation Schedule - {num_players} Players")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total game duration:** {GAME_DURATION_MINUTES} minutes ({QUARTERS} quarters)")
    lines.append(f"- **Players attending:** {num_players}")
    lines.append(f"- **Minutes per player:** {minutes_per_player:.1f}")
    lines.append(f"- **Stint duration:** {slot_duration:.1f} minutes")
    lines.append(f"- **Number of rotations:** {len(schedule)}")
    lines.append("")
    
    # Calculate slots per quarter (using floor division for safety)
    slots_per_quarter = int(QUARTER_DURATION // slot_duration)
    
    # Generate single table with all quarters showing substitutions
    lines.append("## Rotation Table")
    lines.append("")
    
    # Build header with Q1T1, Q1T2, ... Q4T4 format
    header = "|"
    for quarter in range(1, QUARTERS + 1):
        for slot in range(1, slots_per_quarter + 1):
            header += f" Q{quarter}T{slot} |"
    lines.append(header)
    
    # Separator row
    separator = "|"
    for _ in range(QUARTERS * slots_per_quarter):
        separator += "------|"
    lines.append(separator)
    
    # Build a matrix of players by position for each time slot
    # Each row represents a court position (1-5)
    # Show player name only when there's a substitution (change from previous slot)
    # Maintain stable positions: players stay in same position if still on court
    position_rows = [[] for _ in range(PLAYERS_ON_COURT)]  # 5 rows for 5 positions
    current_positions = [None] * PLAYERS_ON_COURT  # Track who is in each position
    
    for slot_idx, entry in enumerate(schedule):
        current_players_set = set(entry['players'])
        new_players = list(current_players_set)
        
        if slot_idx == 0:
            # First slot - assign initial positions
            for pos in range(PLAYERS_ON_COURT):
                current_positions[pos] = new_players[pos]
                position_rows[pos].append(new_players[pos])
        else:
            # Find players leaving and entering
            prev_players_set = set(current_positions)
            leaving = prev_players_set - current_players_set
            entering = current_players_set - prev_players_set
            entering_list = list(entering)
            
            # Update positions: keep players who stay, replace those who leave
            entering_idx = 0
            for pos in range(PLAYERS_ON_COURT):
                if current_positions[pos] in leaving:
                    # This player is leaving, replace with someone entering
                    if entering_idx < len(entering_list):
                        new_player = entering_list[entering_idx]
                        entering_idx += 1
                        current_positions[pos] = new_player
                        position_rows[pos].append(new_player)
                    else:
                        position_rows[pos].append("")
                else:
                    # Player stays - empty cell
                    position_rows[pos].append("")
    
    # Output the position rows
    for pos in range(PLAYERS_ON_COURT):
        row = "|"
        for cell in position_rows[pos]:
            row += f"{cell}|"
        lines.append(row)
    
    lines.append("")
    
    # Per-player summary
    lines.append("## Player Minutes Summary")
    lines.append("")
    lines.append("| Player | Total Minutes | Stints |")
    lines.append("|--------|---------------|--------|")
    
    # Calculate actual minutes per player
    player_minutes = {p: 0 for p in players}
    player_stints = {p: 0 for p in players}
    
    prev_on_court = set()
    for entry in schedule:
        current_on_court = set(entry['players'])
        for player in entry['players']:
            player_minutes[player] += entry['duration']
            if player not in prev_on_court:
                player_stints[player] += 1
        prev_on_court = current_on_court
    
    for player in players:
        lines.append(f"| {player} | {player_minutes[player]:.1f} | {player_stints[player]} |")
    
    lines.append("")
    lines.append("---")
    lines.append(f"*Generated by Coach Pig Rotation Generator*")
    
    content = "\n".join(lines)
    
    if filename:
        with open(filename, 'w') as f:
            f.write(content)
        print(f"Markdown saved to {filename}")
    
    return content


def main():
    parser = argparse.ArgumentParser(
        description="Generate basketball rotation schedule for a list of players",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python rotation_generator.py "Pedro" "Javi A." "Jesús" "Ismael" "Ana"
  python rotation_generator.py "Player1" "Player2" "Player3" "Player4" "Player5" "Player6" --output rotation
  python rotation_generator.py "Ana" "Bob" "Carlos" "Diana" "Eva" "Frank" --format markdown --output schedule
        """
    )
    
    parser.add_argument(
        "players",
        nargs='+',
        type=str,
        help="List of player names attending the game (minimum 5)"
    )
    
    parser.add_argument(
        "--format",
        choices=["csv", "markdown", "both"],
        default="both",
        help="Output format (default: both)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Base filename for output (without extension)"
    )
    
    parser.add_argument(
        "--print",
        action="store_true",
        help="Print output to console"
    )
    
    args = parser.parse_args()
    
    players = args.players
    num_players = len(players)
    
    # Validate player count
    if num_players < PLAYERS_ON_COURT:
        print(f"Error: Need at least {PLAYERS_ON_COURT} players for basketball", file=sys.stderr)
        sys.exit(1)
    
    if num_players > 20:
        print("Warning: More than 20 players may result in very short stints", file=sys.stderr)
    
    # Generate output
    csv_content = None
    md_content = None
    
    if args.format in ["csv", "both"]:
        csv_filename = f"{args.output}.csv" if args.output else None
        csv_content = generate_csv(players, csv_filename)
    
    if args.format in ["markdown", "both"]:
        md_filename = f"{args.output}.md" if args.output else None
        md_content = generate_markdown(players, md_filename)
    
    # Print to console if requested or no output file specified
    if args.print or not args.output:
        if csv_content and args.format == "csv":
            print(csv_content)
        elif md_content:
            print(md_content)
    
    print(f"\n✅ Rotation schedule generated for {num_players} players")


if __name__ == "__main__":
    main()
