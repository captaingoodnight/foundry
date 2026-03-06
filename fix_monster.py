import sys
import os
import re

# Lines starting with exactly these words (at a word boundary) will be removed
REMOVE_PATTERNS = [re.compile(r'^TREASURE\b'), re.compile(r'^LOCATION\b')]


def should_remove(line):
    stripped = line.lstrip()
    return any(p.match(stripped) for p in REMOVE_PATTERNS)


def process_file(input_path):
    # Read all lines from the input file
    with open(input_path, "r") as f:
        lines = f.readlines()

    processed = []
    for i, line in enumerate(lines):
        line_num = i + 1  # 1-based line number

        # Remove lines starting with TREASURE or LOCATION at a word boundary
        if should_remove(line):
            continue

        if line_num == 1:
            # Convert entire first line to title case
            line = line.title()

        elif line_num == 6:
            # Replace leading "AC" with "Armor Class"
            stripped = line.lstrip()
            leading_spaces = line[: len(line) - len(stripped)]
            if stripped.startswith("AC"):
                line = leading_spaces + "Armor Class" + stripped[2:]

        elif line_num == 7:
            # Replace leading "HD" with "Hit Dice"
            stripped = line.lstrip()
            leading_spaces = line[: len(line) - len(stripped)]
            if stripped.startswith("HD"):
                line = leading_spaces + "Hit Dice" + stripped[2:]

        processed.append(line)

    # Build output filename: same name with _fixed appended before the extension
    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_fixed{ext}"

    # Check if output file already exists and handle accordingly
    while os.path.isfile(output_path):
        answer = input(f"'{output_path}' already exists. Overwrite? (yes/no): ").strip().lower()
        if answer in ("yes", "y"):
            break
        elif answer in ("no", "n"):
            new_name = input("Enter a new filename (with extension): ").strip()
            if not new_name:
                print("No filename entered, please try again.")
                continue
            # Use the directory of the input file for the new output path
            output_path = os.path.join(os.path.dirname(input_path), new_name)
        else:
            print("Please answer yes or no.")

    with open(output_path, "w") as f:
        f.writelines(processed)

    print(f"Done! Output written to: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fix_monster.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.isfile(input_file):
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)

    process_file(input_file)