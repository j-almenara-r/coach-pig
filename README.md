# coach-pig
Repositorio para albergar la herramienta de gestión de minutos de los 3K Pigs

## Rotation Generator

A basketball rotation generator that creates fair playing time schedules for all attending players.

### Features

- **Game Configuration**: 40-minute game divided into 4 quarters (10 minutes each)
- **Fair Distribution**: Evenly distributes playing time among all players
- **Balanced Stints**: Ensures similar stint and rest period lengths
- **Minimum Stint Duration**: 2.5 minutes minimum per stint
- **Multiple Outputs**: Generates both CSV and Markdown formats

### Requirements

- Python 3.6+
- No external dependencies

### Usage

```bash
# Basic usage - outputs to console
python rotation_generator.py <number_of_players>

# Generate output files
python rotation_generator.py <number_of_players> --output <filename>

# Examples
python rotation_generator.py 8                      # 8 players, console output
python rotation_generator.py 10 --output rotation   # 10 players, creates rotation.csv and rotation.md
python rotation_generator.py 12 --format csv        # 12 players, CSV format only
python rotation_generator.py 9 --format markdown    # 9 players, Markdown format only
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `players` | Number of players attending (required, minimum 5) |
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

For 8 players:
```
# Rotation Schedule - 8 Players

## Summary
- **Total game duration:** 40 minutes (4 quarters)
- **Players attending:** 8
- **Minutes per player:** 25.0
- **Stint duration:** 5.0 minutes
- **Number of rotations:** 8

| Slot | Quarter | Time | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 |
|------|---------|------|----|----|----|----|----|----|----|----|
| 1 | Q1 | 00:00-05:00 | ✅ | ✅ | ✅ | ✅ | ✅ | ⬜ | ⬜ | ⬜ |
| 2 | Q1 | 05:00-10:00 | ✅ | ✅ | ⬜ | ⬜ | ⬜ | ✅ | ✅ | ✅ |
...
```
