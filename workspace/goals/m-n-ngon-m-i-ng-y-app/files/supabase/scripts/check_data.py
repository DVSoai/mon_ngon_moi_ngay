#!/usr/bin/env python3
"""Kiểm chứng gói dữ liệu Supabase (Lệnh 1). In PASS/FAIL từng dòng; có FAIL thì exit 1.

    python scripts/check_data.py

Tùy chọn:
  BASE_REF=main        nhánh/commit gốc để so diff bữa & cách nấu (mặc định: main)
  PGTEST_DSN=...       chuỗi kết nối tới một database Postgres TRỐNG để chạy thật
                       schema.sql + seed.sql (không dùng Supabase thật). Không đặt → SKIP.

Script không kết nối Supabase, không đọc hay ghi key nào.
"""
import csv
import io
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pglast

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
sys.path.insert(0, str(HERE))
import build_from_json  # noqa: E402

REL = "workspace/goals/m-n-ngon-m-i-ng-y-app/files/supabase"
BANH_MI_RECIPE = "bca0edab-223b-5c76-aff1-a12df464ce9c"

EXPECTED_MEAL = {
    "canh-chua-ca-loc": ("trua", None),
    "bo-luc-lac": (None, "trua"),
    "dau-phu-sot-ca-chua": (None, "toi"),
    "trung-duc-thit": (None, "toi"),
    "canh-bi-nau-tom": (None, "toi"),
}
EXPECTED_COOK = {
    "su-hao-xao": (None, "xao"),
    "oc-len-xao-dua": (None, "xao"),
    "nom-hoa-chuoi": (None, "goi_cuon"),
    "mit-tron": (None, "goi_cuon"),
    "banh-trang-tron": (None, "goi_cuon"),
    "ga-chi-xoi-mo": (None, "chien_ran"),
    "ga-xoi-mo-com-chien": (None, "chien_ran"),
    "com-tam-suon-bi-cha": (None, "nuong"),
    "thit-heo-luoc-cuon-banh-trang": ("hap_luoc", None),
}
NUTRI_MODES = {"an_kieng_giam_can", "it_dau_mo", "giau_protein", "it_tinh_bot"}

failures = 0


def check(no, label, ok, detail=""):
    global failures
    status = "PASS" if ok else "FAIL"
    if not ok:
        failures += 1
    print(f"[{status}] {no}. {label}" + (f" — {detail}" if detail else ""))


def schema_columns(sql):
    cols = {}
    for raw in pglast.parse_sql(sql):
        st = raw.stmt
        if type(st).__name__ == "CreateStmt":
            cols[st.relation.relname] = [e.colname for e in st.tableElts if type(e).__name__ == "ColumnDef"]
    return cols


def main():
    data = build_from_json.load()
    schema_sql = (BASE / "schema.sql").read_text(encoding="utf-8")
    seed_path = BASE / "seed.sql"
    D = data["dishes"]
    slug_of = {x["id"]: x["slug"] for x in D}

    # 1
    reg = Counter(x["region"] for x in D)
    uniq = len({x["slug"] for x in D}) == len({x["id"] for x in D}) == len({x["name"] for x in D}) == len(D)
    check(1, "dishes 90 món; Bac 30 / Trung 30 / Nam 30; slug, id, name không trùng",
          len(D) == 90 and reg == Counter(Bac=30, Trung=30, Nam=30) and uniq,
          f"tổng={len(D)} miền={dict(reg)} không_trùng={uniq}")

    # 2
    R = data["recipes"]
    in90 = sum(1 for r in R if r["in_90"])
    dbt = sum(1 for x in D if x["status"] == "dang_bien_tap")
    check(2, "recipes in_90 = 6; tổng recipes = 6; dang_bien_tap = 84",
          in90 == 6 and len(R) == 6 and dbt == 84, f"in_90={in90} tổng={len(R)} dang_bien_tap={dbt}")

    # 3
    bad = [x["slug"] for x in D if x["status"] == "dang_bien_tap" and x["time_band"] is not None]
    check(3, "món dang_bien_tap có time_band khác NULL = 0", not bad, f"vi_phạm={len(bad)} {bad}")

    # 4
    T = data["dish_diet_tags"]
    bt = sum(1 for t in T if t["diet_mode_code"] == "binh_thuong" and t["is_applicable"] is True)
    chay = Counter(t["is_applicable"] for t in T if t["diet_mode_code"] == "an_chay")
    nutri_nonnull = sum(1 for t in T if t["diet_mode_code"] in NUTRI_MODES and t["is_applicable"] is not None)
    decided = sum(1 for t in T if t["status"] == "da_xac_dinh")
    check(4, "binh_thuong true = 90; an_chay false 59 / true 0 / NULL 31; 4 tag dinh dưỡng khác NULL = 0",
          bt == 90 and chay[False] == 59 and chay[True] == 0 and chay[None] == 31 and nutri_nonnull == 0
          and len(T) == 540,
          f"binh_thuong={bt} an_chay(false={chay[False]}, true={chay[True]}, null={chay[None]}) "
          f"dinh_dưỡng_khác_null={nutri_nonnull} tổng_tag={len(T)} đã_xác_định={decided} null={len(T) - decided}")

    # 5
    base_ref = os.environ.get("BASE_REF", "main")
    try:
        old = json.loads(subprocess.check_output(
            ["git", "show", f"{base_ref}:{REL}/mon-ngon-supabase-data.json"], cwd=BASE, text=True))
        old_by = {x["slug"]: x for x in old["dishes"]}
        meal_diff = {x["slug"]: (old_by[x["slug"]]["meal"], x["meal"]) for x in D if old_by[x["slug"]]["meal"] != x["meal"]}
        cook_diff = {x["slug"]: (old_by[x["slug"]]["cooking_method"], x["cooking_method"])
                     for x in D if old_by[x["slug"]]["cooking_method"] != x["cooking_method"]}
        n_cook = sum(1 for x in D if x["cooking_method"])
        n_meal = sum(1 for x in D if x["meal"])
        print(f"    diff bữa so với {base_ref}:")
        for s, (a, b) in sorted(meal_diff.items()):
            print(f"      {s}: {a} → {b}")
        print(f"    diff cách nấu so với {base_ref}:")
        for s, (a, b) in sorted(cook_diff.items()):
            print(f"      {s}: {a} → {b}")
        check(5, "cách nấu đã gán = 44; bữa đã gán = 27; diff khớp đúng danh sách Lệnh 1 mục 4.4 và 4.5",
              n_cook == 44 and n_meal == 27 and meal_diff == EXPECTED_MEAL and cook_diff == EXPECTED_COOK,
              f"cách_nấu={n_cook} bữa={n_meal} diff_bữa={len(meal_diff)} diff_cách_nấu={len(cook_diff)}")
    except subprocess.CalledProcessError as e:
        check(5, f"đọc bản gốc từ {base_ref}", False, str(e))

    # 6
    I = data["ingredients"]
    dot = [i["text"] for i in I if i["text"].rstrip().endswith(".")]
    bien = [i["text"] for i in I if "Biến thể" in i["text"]]
    bm = [r for r in R if r["id"] == BANH_MI_RECIPE] + [i for i in I if i["recipe_id"] == BANH_MI_RECIPE]
    check(6, "ingredients = 50; không dòng nào kết thúc bằng '.' hay chứa 'Biến thể'; không còn Bánh mì",
          len(I) == 50 and not dot and not bien and not bm,
          f"ingredients={len(I)} có_dấu_chấm={len(dot)} biến_thể={len(bien)} bánh_mì={len(bm)}")

    # 7
    regions = sorted({r["region"] for r in R}, key=str)
    check(7, "recipes.region chỉ có Bac/Trung/Nam", set(regions) <= {"Bac", "Trung", "Nam"}, f"giá_trị={regions}")

    # 8 + 9a
    try:
        cols = schema_columns(schema_sql)
        check("9a", "pglast parse schema.sql", True, f"{len(cols)} bảng")
        bad_keys = []
        for t in build_from_json.TABLES:
            for r in data[t]:
                extra = set(r) - set(cols.get(t, []))
                if extra:
                    bad_keys.append((t, sorted(extra)))
        bad_keys = sorted(set((t, tuple(k)) for t, k in bad_keys))
        check(8, "mọi key JSON là cột có thật (lấy cột bằng pglast từ schema.sql)", not bad_keys, f"sai={bad_keys}")
    except Exception as e:  # noqa: BLE001
        check("9a", "pglast parse schema.sql", False, repr(e))

    # 9b
    try:
        n = len(pglast.parse_sql(seed_path.read_text(encoding="utf-8")))
        check("9b", "pglast parse seed.sql", True, f"{n} câu lệnh")
    except Exception as e:  # noqa: BLE001
        check("9b", "pglast parse seed.sql", False, repr(e))

    # 10
    gen = build_from_json.generate(data)
    same = {f: (BASE / f).exists() and (BASE / f).read_text(encoding="utf-8") == c for f, c in gen.items()}
    n_d = len(list(csv.reader(io.StringIO(gen["dishes.csv"])))) - 1
    nut = list(csv.DictReader(io.StringIO(gen["nutrition.csv"])))
    nb = Counter(r["basis"] for r in nut)
    check(10, "seed.sql / dishes.csv / nutrition.csv giống byte-by-byte bản sinh từ JSON; dishes.csv 90; nutrition.csv 21 (8 + 13)",
          all(same.values()) and n_d == 90 and len(nut) == 21 and nb == Counter(per_100g=8, per_serving=13),
          f"giống={same} dishes.csv={n_d} nutrition.csv={len(nut)} {dict(nb)}")

    # 11
    dsn = os.environ.get("PGTEST_DSN")
    if not dsn:
        print("[SKIP] 11. SKIP: không có Postgres")
    else:
        def psql(args, inp=None):
            return subprocess.run(["psql", dsn, "-v", "ON_ERROR_STOP=1", "-q", "-At", *args],
                                  input=inp, text=True, capture_output=True)
        r1 = psql(["-f", str(BASE / "schema.sql")])
        r2 = psql(["-f", str(seed_path)])
        r3 = psql(["-f", str(seed_path)])  # chạy lại lần 2: phải không lỗi, không trùng
        ok_run = r1.returncode == r2.returncode == r3.returncode == 0
        q = {
            "món theo miền": "select string_agg(region||'='||c, ' ' order by region) from (select region, count(*) c from dishes group by region) s",
            "tổng món": "select count(*) from dishes",
            "recipes in_90": "select count(*) from recipes where in_90",
            "tổng recipes": "select count(*) from recipes",
            "dang_bien_tap": "select count(*) from dishes where status='dang_bien_tap'",
            "ingredients": "select count(*) from ingredients",
            "nutrition theo basis": "select string_agg(basis||'='||c, ' ' order by basis) from (select basis, count(*) c from nutrition_estimates group by basis) s",
            "tag đã xác định / null": "select sum((status='da_xac_dinh')::int)||' / '||sum((status='chua_co_du_lieu')::int) from dish_diet_tags",
            "cách nấu / bữa đã gán": "select count(cooking_method)||' / '||count(meal) from dishes",
            "weekly_menu": "select count(*) from weekly_menu",
            "sources": "select count(*) from sources",
        }
        res = {}
        for k, sql in q.items():
            out = psql(["-c", sql])
            res[k] = out.stdout.strip() if out.returncode == 0 else "LỖI: " + out.stderr.strip()
        for k, v in res.items():
            print(f"      {k}: {v}")
        exp_ok = (res["tổng món"] == "90" and res["recipes in_90"] == "6" and res["tổng recipes"] == "6"
                  and res["dang_bien_tap"] == "84" and res["ingredients"] == "50"
                  and res["tag đã xác định / null"] == "149 / 391" and res["cách nấu / bữa đã gán"] == "44 / 27"
                  and res["weekly_menu"] == "21" and res["món theo miền"] == "Bac=30 Nam=30 Trung=30")
        check(11, "Postgres thật: chạy schema.sql + seed.sql (2 lần) không lỗi, số đếm khớp", ok_run and exp_ok,
              "" if ok_run else (r1.stderr + r2.stderr + r3.stderr).strip())

    print()
    print("KẾT QUẢ:", "TẤT CẢ PASS" if failures == 0 else f"{failures} FAIL")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
