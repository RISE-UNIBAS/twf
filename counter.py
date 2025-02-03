import os
from collections import defaultdict

# Define file extensions to track
file_types = {
    ".py": "Python Files",
    ".html": "Django Template Files",
    ".js": "JavaScript Files",
    ".css": "CSS Files",
    ".json": "JSON Files",
    ".md": "Markdown Files",
    ".txt": "Text Files",
    ".sh": "Shell Scripts",
}

ignored_types = [".pyc", ".log", ".db", ".sqlite3"]

# Directories to ignore
IGNORED_DIRS = {".venv", "venv", "media", "static"}

# Initialize counters
file_counts = defaultdict(int)
total_files = 0

# Set your project directory
project_dir = os.getcwd()  # Change this if needed

# Walk through all files in the project directory
for root, _, files in os.walk(project_dir):
    # Ignore unwanted directories at the base level
    if any(ignored in root.split(os.sep) for ignored in IGNORED_DIRS):
        continue

    other_types = []
    for file in files:
        total_files += 1
        ext = os.path.splitext(file)[1]
        if ext in file_types:
            file_counts[file_types[ext]] += 1
        else:
            if ext in ignored_types:
                file_counts["Ignored Files"] += 1
            else:
                file_counts["Other Files"] += 1

            if not ext in other_types and ext not in ignored_types:
                other_types.append(ext)

# Print results
print(f"📁 Scanned Directory: {project_dir}")
print(f"📊 Total Files: {total_files}\n")
print("Unknown file types:", other_types)
for category, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"{category}: {count}")
