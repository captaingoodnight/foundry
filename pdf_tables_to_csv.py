
#!/usr/bin/env python3
"""
PDF Table Extractor
Prompts the user for a PDF file path, finds all tables in it,
and saves each table as a separate CSV file.

Requirements:
    pip install pdfplumber pandas
"""

import os
import sys
import csv
import pdfplumber
import pandas as pd


def extract_tables_to_csv(pdf_path: str) -> None:
    output_dir = os.path.dirname(os.path.abspath(pdf_path))
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]

    print(f"\n📄 Opening: {pdf_path}")

    table_count = 0

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"   Pages found: {total_pages}")

        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()

            if not tables:
                continue

            for table_idx, table in enumerate(tables, start=1):
                if not table or all(all(cell is None for cell in row) for row in table):
                    continue  # skip empty tables

                table_count += 1

                # Use first row as header if it looks like one, else generate headers
                if table[0] and any(cell for cell in table[0]):
                    headers = [
                        str(cell).strip() if cell is not None else f"col_{i}"
                        for i, cell in enumerate(table[0])
                    ]
                    rows = table[1:]
                else:
                    num_cols = max(len(row) for row in table)
                    headers = [f"col_{i}" for i in range(num_cols)]
                    rows = table

                # Normalise row length to match headers
                norm_rows = []
                for row in rows:
                    padded = list(row) + [None] * (len(headers) - len(row))
                    norm_rows.append(padded[: len(headers)])

                # Create DataFrame and clean data
                df = pd.DataFrame(norm_rows, columns=headers)

                # Strip extra newlines and whitespace from all cells, and merge last two columns if they exist
                df = df.map(lambda x: str(x).replace('\n', ' ').strip() if x is not None else x)
                # Merge last two columns if they exist and are not empty
                df.iloc[:, -2] = df.iloc[:, -2].astype(str) + ' ' + df.iloc[:, -1].astype(str) 
                df = df.iloc[:, :-1]

                # Build output filename
                csv_filename = f"{base_name}_page{page_num}_table{table_idx}.csv"
                csv_path = os.path.join(output_dir, csv_filename)

                # Save to CSV with pipe delimiter to handle commas in data
                df.to_csv(csv_path, index=False, header=False, sep='|')

                print(f"   ✅ Saved table {table_count}: {csv_filename}  "
                      f"({len(df)} rows × {len(df.columns)} cols)")

    if table_count == 0:
        print("\n⚠️  No tables were found in this PDF.")
    else:
        print(f"\n🎉 Done! {table_count} table(s) saved to: {output_dir}")


def main() -> None:
    print("=" * 50)
    print("       PDF Table → CSV Extractor")
    print("=" * 50)

    # Accept path from command-line argument or interactive prompt
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1].strip()
    else:
        pdf_path = input("\nEnter the path to your PDF file: ").strip()

    # Strip accidental surrounding quotes
    pdf_path = pdf_path.strip("'\"")

    if not pdf_path:
        print("❌ No path provided. Exiting.")
        sys.exit(1)

    if not os.path.isfile(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        sys.exit(1)

    if not pdf_path.lower().endswith(".pdf"):
        print("⚠️  Warning: file does not have a .pdf extension. Proceeding anyway…")

    try:
        extract_tables_to_csv(pdf_path)
    except Exception as exc:
        print(f"\n❌ Error processing PDF: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()