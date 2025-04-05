# whats-new

A Python tool that generates "What's New" release notes from git history using Claude AI to create clear, user-friendly summaries.

## Features

- Automatically extracts commits between semantic version tags
- Uses Claude AI to generate well-organized, human-readable summaries
- Falls back to basic formatting if AI service is unavailable
- Supports semantic versioning (e.g., 1.2.3 or v1.2.3)

## Installation

1. Clone this repository
2. Install dependencies: `pip install anthropic packaging`
3. Set your Anthropic API key: `export ANTHROPIC_API_KEY=your_key_here`

## Usage

```bash
python whats_new.py /path/to/repo 1.2.3
```

Where:

- `/path/to/repo` is the path to your git repository
- `1.2.3` is the version number to generate release notes for

## Requirements

- Python 3.x
- Git
- Anthropic API key

## License

MIT

```
This README provides essential information about what the tool does, how to install it, how to use it, and its requirements, while keeping things concise and clear.
```
