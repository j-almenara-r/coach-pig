# coach-pig
Repositorio para albergar la herramienta de gestión de minutos de los 3K Pigs

## Rotation Generator

A basketball rotation generator that creates fair playing time schedules for all attending players.

### Features

- **Game Configuration**: 40-minute game divided into 4 quarters (10 minutes each)
- **Fair Distribution**: Evenly distributes playing time among all players
- **Balanced Stints**: Uses 2.5-minute time slots for granular rotation control
- **Player Names**: Accepts actual player names for readable output tables
- **Multiple Outputs**: Generates both CSV and Markdown formats

### Requirements

- Python 3.6+
- No external dependencies

### Usage

```bash
# Basic usage - outputs to console
python rotation_generator.py "Player1" "Player2" "Player3" "Player4" "Player5"

# Generate output files
python rotation_generator.py "Pedro" "Javi A." "Jesús" "Ismael" "Ana" --output rotation

# Examples
python rotation_generator.py "Pedro" "Javi A." "Jesús A.R." "Ismael" "Ana" "Javi F" "Jose" "Sergio"
python rotation_generator.py "Ana" "Bob" "Carlos" "Diana" "Eva" "Frank" --output rotation
python rotation_generator.py "Player1" "Player2" "Player3" "Player4" "Player5" "Player6" --format csv
python rotation_generator.py "A" "B" "C" "D" "E" "F" "G" --format markdown
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `players` | List of player names attending (required, minimum 5) |
| `--format` | Output format: `csv`, `markdown`, or `both` (default: both) |
| `--output`, `-o` | Base filename for output files (without extension) |
| `--print` | Print output to console even when writing files |

### Output Formats

#### CSV Format
The CSV file includes:
- Summary header with rotation parameters
- Time slots with player assignments (1 = on court, 0 = on bench)

#### Markdown Format
The Markdown file includes:
- Summary statistics (minutes per player, stint duration)
- Visual rotation table with checkmarks
- Per-player minutes summary

### Example Output

For 8 players (Pedro, Javi A., Jesús A.R., Ismael, Ana, Javi F, Jose, Sergio):
```
# Rotation Schedule - 8 Players

## Summary
- **Total game duration:** 40 minutes (4 quarters)
- **Players attending:** 8
- **Minutes per player:** 25.0
- **Stint duration:** 2.5 minutes
- **Number of rotations:** 16

## Quarter 1

| Player | T1 | T2 | T3 | T4 |
|--------|----|----|----|----|
| Pedro | 🟢 IN | ✅ | 🔴 OUT | 🟢 IN |
| Javi A. | 🟢 IN | ✅ | 🔴 OUT | 🟢 IN |
| Jesús A.R. | 🟢 IN | 🔴 OUT | 🟢 IN | ✅ |
...
```

Legend:
- 🟢 IN: Player enters the court
- 🔴 OUT: Player exits the court
- ✅: Player continues playing
- ⬜: Player on bench
