import re
import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

def extract_block(text, block_name):
    pattern = re.compile(rf'{block_name}\s*{{', re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return ""

    start = match.end()
    depth = 1
    i = start
    while i < len(text):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return text[start:i]
        i += 1
    return ""

def parse_input(text):
    result = {}
    idx = 0

    lines_block = extract_block(text, "drawLines")
    quads_block = extract_block(text, "drawQuads")
    combined_text = lines_block + "\n" + quads_block

    # Парсинг линий
    line_pattern = re.compile(r'line\s*{line:p4=([^;]+);move:b=(true|false);}', re.IGNORECASE)
    for match in line_pattern.finditer(combined_text):
        coords = list(map(float, match.group(1).split(',')))
        result[str(idx)] = {
            "name": f"Линия{idx}",
            "type": "line",
            "start": {"x": coords[0], "y": coords[1]},
            "end": {"x": coords[2], "y": coords[3]},
            "selected": False
        }
        idx += 1

    # Парсинг четырёхугольников
    quad_pattern = re.compile(
        r'quad\s*{tl:p2\s*=\s*([^;]+);\s*tr:p2\s*=\s*([^;]+);\s*br:p2\s*=\s*([^;]+);\s*bl:p2\s*=\s*([^;]+);}',
        re.IGNORECASE
    )
    for match in quad_pattern.finditer(combined_text):
        coords = [list(map(float, group.split(','))) for group in match.groups()]
        result[str(idx)] = {
            "name": f"Четырёхугольник{idx}",
            "type": "quad",
            "pos1": {"x": coords[0][0], "y": coords[0][1]},
            "pos2": {"x": coords[1][0], "y": coords[1][1]},
            "pos3": {"x": coords[2][0], "y": coords[2][1]},
            "pos4": {"x": coords[3][0], "y": coords[3][1]},
            "selected": False
        }
        idx += 1

    return result

def convert_file():
    file_path = filedialog.askopenfilename(filetypes=[("BLK or Text files", "*.blk;*.txt")])
    if not file_path:
        return

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    data = parse_input(content)

    downloads_folder = str(Path.home() / "Downloads")
    filename = os.path.splitext(os.path.basename(file_path))[0] + ".json"
    output_path = os.path.join(downloads_folder, filename)

    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, separators=(',', ':'))

    # Показываем сообщение
    messagebox.showinfo("Готово", f"DONE!\nCHECK IT IN DOWNLOADS:\n{filename}")

def create_gui():
    window = tk.Tk()
    window.title("BLK to JSON")
    window.geometry("300x200")

    label = tk.Label(window, text="BLK to JSON", font=("Arial", 25))
    label.pack(pady=40)

    button = tk.Button(
        window,
        text="CONVERT",
        font=("Arial", 14),
        width=20,
        height=2,
        command=convert_file,
        bg="black",
        fg="white"
    )
    button.pack()

    window.mainloop()


# Запуск приложения
create_gui()
