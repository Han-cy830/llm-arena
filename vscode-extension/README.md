# LLM Arena - VS Code Extension

Make 50+ LLMs compete directly from VS Code.

## Features

- **Sidebar Model Tree** - See all models ranked with Elo, mood emoji, efficiency score
- **Rankings Panel** - Full rankings table with daily/weekly/monthly/all time views
- **Record Matches** - Input model performance data from the editor
- **Switch Providers** - Quick pick to switch between 50+ API providers
- **Model Details** - Click any model to see full 10-dimension profile
- **Status Bar** - Quick access to rankings

## Requirements

- Python 3.10+ with llm-arena installed
- Run `npx github:Han-cy830/llm-arena` first to set up

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `llmArena.pythonPath` | `python` | Path to Python executable |
| `llmArena.cliPath` | auto | Path to cli.py (auto-detected) |

## Commands

| Command | Description |
|---------|-------------|
| LLM Arena: Show Rankings | Open rankings panel |
| LLM Arena: Show Status | Show full status |
| LLM Arena: Model Detail | View model details |
| LLM Arena: Record Match | Record model performance |
| LLM Arena: Refresh | Refresh model tree |
| LLM Arena: Switch Provider | Switch API provider |
