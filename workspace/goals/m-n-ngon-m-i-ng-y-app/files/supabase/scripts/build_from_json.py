#!/usr/bin/env python3
"""Sinh seed.sql, dishes.csv, nutrition.csv từ mon-ngon-supabase-data.json.

JSON là nguồn gốc duy nhất. KHÔNG sửa tay seed.sql hay CSV — sửa JSON rồi chạy lại:

    python scripts/build_from_json.py

Script không kết nối Supabase, không đọc hay ghi key nào.
"""
import csv
import io
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
JSON_PATH = BASE / "mon-ngon-supabase-data.json"

# (bảng trong JSON/DB, thứ tự nạp theo khóa ngoại)
TABLES = [
    "sources",
    "dishes",
    "recipes",
    "ingredients",
    "nutrition_estimates",
    "diet_modes",
    "dish_diet_tags",
    "weekly_menu",
]

CSV_FILES = {
    "dishes.csv": "dishes",
    "nutrition.csv": "nutrition_estimates",
}


def sql_literal(v):
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def columns_of(rows, table):
    if not rows:
        return []
    cols = list(rows[0].keys())
    for r in rows:
        if list(r.keys()) != cols:
            raise ValueError(f"{table}: các dòng không cùng bộ trường: {list(r.keys())} != {cols}")
    return cols


def build_seed(data):
    out = [
        "-- Món Ngon Mỗi Ngày — seed.sql",
        "-- FILE SINH TỰ ĐỘNG từ mon-ngon-supabase-data.json bằng scripts/build_from_json.py.",
        "-- KHÔNG sửa tay. Chạy sau schema.sql. ON CONFLICT DO NOTHING nên chạy lại được.",
        "",
        "begin;",
        "",
    ]
    for t in TABLES:
        rows = data[t]
        cols = columns_of(rows, t)
        out.append(f"-- {t}: {len(rows)} dòng")
        for r in rows:
            vals = ", ".join(sql_literal(r[c]) for c in cols)
            out.append(f"insert into {t} ({', '.join(cols)}) values ({vals}) on conflict do nothing;")
        out.append("")
    out.append("commit;")
    out.append("")
    return "\n".join(out)


def build_csv(rows, table):
    cols = columns_of(rows, table)
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(cols)
    for r in rows:
        w.writerow(["" if r[c] is None else ("true" if r[c] is True else "false" if r[c] is False else r[c])
                    for c in cols])
    return buf.getvalue()


def generate(data):
    files = {"seed.sql": build_seed(data)}
    for fname, table in CSV_FILES.items():
        files[fname] = build_csv(data[table], table)
    return files


def load():
    return json.loads(JSON_PATH.read_text(encoding="utf-8"))


def main():
    for fname, content in generate(load()).items():
        (BASE / fname).write_text(content, encoding="utf-8")
        print(f"Đã ghi {fname}")


if __name__ == "__main__":
    main()
