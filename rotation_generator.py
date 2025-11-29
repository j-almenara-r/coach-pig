#!/usr/bin/env python3
"""
Basketball Rotation Generator for 3K Pigs

Generates a rotation schedule for a basketball game, distributing playing time
evenly among all attending players while ensuring balanced stints and rest periods.

Game duration: 40 minutes (4 quarters of 10 minutes each)
Minimum stint duration: 2.5 minutes
"""

import argparse
import csv
import math
import sys
from typing import List, Tuple


# Game constants
GAME_DURATION_MINUTES = 40
QUARTERS = 4
QUARTER_DURATION = GAME_DURATION_MINUTES // QUARTERS  # 10 minutes per quarter
PLAYERS_ON_COURT = 5
MIN_STINT_DURATION = 2.5


def calculate_rotation_schedule(num_players: int) -> Tuple[List[List[str]], float, float]:
    """
    Calculate the rotation schedule for a given number of players.
    
    Args:
        num_players: Total number of players attending the game
        
    Returns:
        A tuple containing:
        - Schedule matrix: list of time slots, each containing players on court
        - Minutes per player
        - Stint duration
    """
    if num_players < PLAYERS_ON_COURT:
        raise ValueError(f"Need at least {PLAYERS_ON_COURT} players to play basketball")
    
    # Calculate total available playing time and time per player
    total_court_minutes = GAME_DURATION_MINUTES * PLAYERS_ON_COURT  # 200 player-minutes
    minutes_per_player = total_court_minutes / num_players
    
    # Calculate the number of slots needed
    # We need enough slots so that all players can have balanced playing time
    # The number of slots should allow each player to play roughly equal time
    
    # For balanced rotation, we need slots where num_players / PLAYERS_ON_COURT
    # determines how we cycle through players
    ratio = num_players / PLAYERS_ON_COURT
    
    # Calculate ideal slot count that allows for even distribution
    # and respects the minimum stint duration
    max_slots = int(GAME_DURATION_MINUTES / MIN_STINT_DURATION)
    
    # Find optimal number of slots that gives even distribution
    # We want slots that divide evenly into player combinations
    best_slots = 4  # Start with quarters
    best_variance = float('inf')
    
    for test_slots in range(4, max_slots + 1):
        slot_duration = GAME_DURATION_MINUTES / test_slots
        if slot_duration < MIN_STINT_DURATION:
            break
        
        # Simulate this slot count
        test_schedule = []
        test_played = {i: 0 for i in range(num_players)}
        
        for s in range(test_slots):
            # Select 5 players with least time so far
            sorted_players = sorted(range(num_players), key=lambda p: (test_played[p], p))
            on_court = sorted_players[:PLAYERS_ON_COURT]
            for p in on_court:
                test_played[p] += 1
            test_schedule.append(on_court)
        
        # Calculate variance in playing time
        times = [test_played[p] * slot_duration for p in range(num_players)]
        avg_time = sum(times) / len(times)
        variance = sum((t - avg_time) ** 2 for t in times) / len(times)
        
        if variance < best_variance:
            best_variance = variance
            best_slots = test_slots
    
    # Use the optimal number of slots
    num_slots = best_slots
    actual_slot_duration = GAME_DURATION_MINUTES / num_slots
    
    # Create player list
    players = [f"Player {i+1}" for i in range(num_players)]
    
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


def generate_detailed_schedule(num_players: int) -> List[dict]:
    """
    Generate a detailed schedule with time ranges and quarter information.
    
    Args:
        num_players: Total number of players attending
        
    Returns:
        List of dictionaries with schedule details
    """
    schedule, minutes_per_player, slot_duration = calculate_rotation_schedule(num_players)
    
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
            'on_bench': [f"Player {i+1}" for i in range(num_players) if f"Player {i+1}" not in players_on_court]
        })
    
    return detailed


def format_time(minutes: float) -> str:
    """Format minutes as MM:SS string."""
    total_seconds = int(minutes * 60)
    mins = total_seconds // 60
    secs = total_seconds % 60
    return f"{mins:02d}:{secs:02d}"


def generate_csv(num_players: int, filename: str = None) -> str:
    """
    Generate a CSV file with the rotation schedule.
    
    Args:
        num_players: Total number of players attending
        filename: Output filename (optional, will print to stdout if not provided)
        
    Returns:
        CSV content as string
    """
    schedule = generate_detailed_schedule(num_players)
    _, minutes_per_player, slot_duration = calculate_rotation_schedule(num_players)
    
    output_lines = []
    
    # Summary header
    output_lines.append(f"# Rotation Schedule for {num_players} Players")
    output_lines.append(f"# Minutes per player: {minutes_per_player:.1f}")
    output_lines.append(f"# Stint duration: {slot_duration:.1f} minutes")
    output_lines.append("")
    
    # CSV header
    header = ["Slot", "Quarter", "Start", "End", "Duration (min)"]
    header.extend([f"Player {i+1}" for i in range(num_players)])
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
        for i in range(num_players):
            player_name = f"Player {i+1}"
            row.append("1" if player_name in entry['players'] else "0")
        
        output_lines.append(",".join(row))
    
    content = "\n".join(output_lines)
    
    if filename:
        with open(filename, 'w', newline='') as f:
            f.write(content)
        print(f"CSV saved to {filename}")
    
    return content


def generate_markdown(num_players: int, filename: str = None) -> str:
    """
    Generate a Markdown table with the rotation schedule.
    
    Args:
        num_players: Total number of players attending
        filename: Output filename (optional)
        
    Returns:
        Markdown content as string
    """
    schedule = generate_detailed_schedule(num_players)
    _, minutes_per_player, slot_duration = calculate_rotation_schedule(num_players)
    
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
    
    # Rotation table
    lines.append("## Rotation Schedule")
    lines.append("")
    
    # Table header
    header = "| Slot | Quarter | Time | "
    header += " | ".join([f"P{i+1}" for i in range(num_players)])
    header += " |"
    lines.append(header)
    
    # Separator
    separator = "|------|---------|------|"
    separator += "|".join(["----" for _ in range(num_players)])
    separator += "|"
    lines.append(separator)
    
    # Data rows
    for entry in schedule:
        time_range = f"{format_time(entry['start_time'])}-{format_time(entry['end_time'])}"
        row = f"| {entry['slot']} | Q{entry['quarter']} | {time_range} |"
        for i in range(num_players):
            player_name = f"Player {i+1}"
            row += " ✅ |" if player_name in entry['players'] else " ⬜ |"
        lines.append(row)
    
    lines.append("")
    
    # Per-player summary
    lines.append("## Player Minutes Summary")
    lines.append("")
    lines.append("| Player | Total Minutes | Stints |")
    lines.append("|--------|---------------|--------|")
    
    # Calculate actual minutes per player
    player_minutes = {f"Player {i+1}": 0 for i in range(num_players)}
    player_stints = {f"Player {i+1}": 0 for i in range(num_players)}
    
    prev_on_court = set()
    for entry in schedule:
        current_on_court = set(entry['players'])
        for player in entry['players']:
            player_minutes[player] += entry['duration']
            if player not in prev_on_court:
                player_stints[player] += 1
        prev_on_court = current_on_court
    
    for i in range(num_players):
        player = f"Player {i+1}"
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
        description="Generate basketball rotation schedule for a given number of players",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python rotation_generator.py 8
  python rotation_generator.py 10 --output rotation
  python rotation_generator.py 12 --format markdown --output schedule
        """
    )
    
    parser.add_argument(
        "players",
        type=int,
        help="Number of players attending the game (minimum 5)"
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
    
    # Validate player count
    if args.players < PLAYERS_ON_COURT:
        print(f"Error: Need at least {PLAYERS_ON_COURT} players for basketball", file=sys.stderr)
        sys.exit(1)
    
    if args.players > 20:
        print("Warning: More than 20 players may result in very short stints", file=sys.stderr)
    
    # Generate output
    csv_content = None
    md_content = None
    
    if args.format in ["csv", "both"]:
        csv_filename = f"{args.output}.csv" if args.output else None
        csv_content = generate_csv(args.players, csv_filename)
    
    if args.format in ["markdown", "both"]:
        md_filename = f"{args.output}.md" if args.output else None
        md_content = generate_markdown(args.players, md_filename)
    
    # Print to console if requested or no output file specified
    if args.print or not args.output:
        if csv_content and args.format == "csv":
            print(csv_content)
        elif md_content:
            print(md_content)
    
    print(f"\n✅ Rotation schedule generated for {args.players} players")


if __name__ == "__main__":
    main()
