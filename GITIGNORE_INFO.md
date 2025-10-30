# Git Ignore Configuration

## Overview

The `.gitignore` file is configured to **preserve directory structure** while **ignoring all file contents** in specific folders. This is useful for maintaining the project structure in version control without committing large data files or temporary outputs.

## Ignored Folders (Files Only)

The following directories have their **files ignored** but their **structure preserved**:

### 1. `outputs/script_outputs/`
- Contains tag extraction outputs (JSON files)
- Files ignored: All `.json` outputs from batch processing
- Purpose: Prevents committing large generated output files

### 2. `database/`
- Contains content files (bytes, journeys, summaries) and CSV tables
- Files ignored: All `.txt`, `.csv` files
- Purpose: Keeps sensitive or large data files local

### 3. `archives/`
- Contains archived or backup files
- Files ignored: All archive files
- Purpose: Prevents committing old/backup data

### 4. `logs/`
- Contains application and API call logs
- Subdirectories: `api_call/gemini/`, `api_call/openai/`, `app/`, `script/`
- Files ignored: All `.log` files
- Purpose: Keeps logs local (can be large and sensitive)

### 5. `test/script_outputs/`
- Contains test script outputs
- Files ignored: All test output files
- Purpose: Test outputs shouldn't be committed

## How It Works

### Pattern Explanation

```gitignore
# Ignore all files in directory and subdirectories
folder/**/*

# BUT keep .gitkeep files (to preserve directory structure)
!folder/**/.gitkeep

# AND keep the directory structure itself
!folder/**/
```

### What Gets Committed

✅ **Committed to Git:**
- Directory structure (empty folders)
- `.gitkeep` files (placeholder files)
- Python scripts, markdown docs, config files
- `requirements.txt`, `.gitignore`, etc.

❌ **NOT Committed to Git:**
- Content files in `database/`
- Generated outputs in `outputs/script_outputs/`
- Log files in `logs/`
- Archive files in `archives/`
- Test outputs in `test/script_outputs/`

## Directory Structure in Git

When cloned, the repository will have this structure:

```
recommendation_v101/
├── outputs/
│   └── script_outputs/
│       ├── .gitkeep              ✓ (tracked)
│       └── others/
│           └── .gitkeep          ✓ (tracked)
├── database/
│   ├── content/
│   │   ├── bytes/
│   │   │   └── .gitkeep          ✓ (tracked)
│   │   ├── journeys/
│   │   │   └── .gitkeep          ✓ (tracked)
│   │   └── summaries/
│   │       └── .gitkeep          ✓ (tracked)
│   └── tables/
│       └── .gitkeep              ✓ (tracked)
├── archives/
│   └── .gitkeep                  ✓ (tracked)
├── logs/
│   ├── api_call/
│   │   ├── gemini/
│   │   │   └── .gitkeep          ✓ (tracked)
│   │   └── openai/
│   │       └── .gitkeep          ✓ (tracked)
│   ├── app/
│   │   └── .gitkeep              ✓ (tracked)
│   └── script/
│       └── .gitkeep              ✓ (tracked)
└── ... (other project files)
```

## Benefits

1. **Clean Repository**: No large data files in version control
2. **Preserved Structure**: Directory structure maintained for new clones
3. **No Broken Paths**: Scripts expecting these folders won't break
4. **Team Collaboration**: Everyone gets the same folder structure
5. **Reduced Repo Size**: Git history stays lean

## Adding New Ignored Folders

If you need to add more folders with this pattern:

1. Add the pattern to `.gitignore`:
   ```gitignore
   # your_folder/ - Keep dirs, ignore all files
   your_folder/**/*
   !your_folder/**/.gitkeep
   !your_folder/**/
   ```

2. Create a `.gitkeep` file in the folder:
   ```bash
   touch your_folder/.gitkeep
   ```

3. Commit both changes:
   ```bash
   git add .gitignore your_folder/.gitkeep
   git commit -m "Add your_folder to gitignore with structure preservation"
   ```

## Checking What's Ignored

To see what files would be ignored:

```bash
# Check if a specific file would be ignored
git check-ignore -v path/to/file

# List all ignored files in a directory
git status --ignored

# Dry-run to see what would be added
git add --dry-run .
```

## Force Adding Ignored Files (If Needed)

If you need to commit a specific file that's normally ignored:

```bash
git add -f path/to/ignored/file
```

⚠️ **Use sparingly** - these files are ignored for a reason!

## Environment Files

Note: `.env` files are also ignored (contains sensitive API keys):

```gitignore
.env
.env.local
.env.*.local
```

Always keep a `.env.example` file with dummy values for reference.

---

**Last Updated**: October 30, 2025  
**Maintained By**: Project Team

