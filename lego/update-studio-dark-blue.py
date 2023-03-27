import csv
import os

filename = os.path.expanduser("~/.local/share/Stud.io/CustomColorDefinition.txt")
out_file = filename + ".out.txt"


def update_row(row):
    if row['Studio Color Code'] == "63":
        row['Ins_RGB'] = '#014E90'
    return row


with open(filename, newline='') as tsv_input, open(out_file, 'w', newline='') as tsv_output:
    reader = csv.DictReader(tsv_input, delimiter="\t")

    writer = csv.DictWriter(tsv_output, delimiter="\t", lineterminator='\n', fieldnames=reader.fieldnames)

    writer.writeheader()
    for row in reader:
        writer.writerow(update_row(row))

os.replace(out_file, filename)  # you can comment this out if you want to inspect the new file first

print("Now click 'Apply' in 'Page Setup'.")
