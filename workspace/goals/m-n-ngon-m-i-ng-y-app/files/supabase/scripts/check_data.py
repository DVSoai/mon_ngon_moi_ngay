#!/usr/bin/env python3
"""Kiểm chứng gói dữ liệu Supabase (thiết kế Lệnh 2). In PASS/FAIL từng dòng; có FAIL thì exit 1.

    python scripts/check_data.py

Tùy chọn:
  BASE_REF=main        nhánh/commit gốc (dữ liệu Lệnh 1) để kiểm tra hồi quy (mặc định: main)
  PGTEST_DSN=...       chuỗi kết nối tới một database Postgres 15+ TRỐNG để chạy thật
                       schema.sql + seed.sql (KHÔNG dùng Supabase thật). Không đặt → SKIP.
                       Script tạo role anon/authenticated nếu máy test chưa có (giống Supabase).

Script không kết nối Supabase, không đọc hay ghi key nào.
"""
import csv
import io
import json
import os
import re
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
NUTRI_MODES = {"an_kieng_giam_can", "it_dau_mo", "giau_protein", "it_tinh_bot"}
VN_SOURCES = {"calocalo_vn_fct", "fao_vn_fct_2017"}
EXTRA_COOK = {
    ("thit-heo-luoc-cuon-banh-trang", "hap_luoc"), ("thit-heo-luoc-cuon-banh-trang", "goi_cuon"),
    ("rau-luoc-kho-quet", "hap_luoc"), ("rau-luoc-kho-quet", "kho"),
    ("com-tam-suon-bi-cha", "hap_luoc"),
}
EXPECTED_ITEMS = [  # (ngày, bữa, cụm tên, slug|None) — đúng Lệnh 2 mục 4.3
    (1, "sang", "Bánh mì thịt", None),
    (1, "trua", "cá kho tộ", "ca-kho-to"), (1, "trua", "canh chua", None),
    (1, "toi", "Bún chả", "bun-cha"),
    (2, "sang", "Phở gà", "pho-ga"),
    (2, "trua", "thịt quay", "thit-quay-gion-bi"), (2, "trua", "canh cua rau đay", "canh-cua-rau-day"),
    (2, "toi", "Mì Quảng tôm thịt", "mi-quang-ga-tom-thit"),
    (3, "sang", "Bánh cuốn", "banh-cuon-thanh-tri"),
    (3, "trua", "Cơm tấm sườn bì chả", "com-tam-suon-bi-cha"),
    (3, "toi", "gà kho gừng", None), (3, "toi", "canh bí", "canh-bi-nau-tom"),
    (4, "sang", "Hủ tiếu Nam Vang", "hu-tieu-nam-vang"),
    (4, "trua", "Bún bò Huế", "bun-bo-hue"),
    (4, "toi", "đậu sốt cà", "dau-phu-sot-ca-chua"), (4, "toi", "trứng đúc thịt", "trung-duc-thit"),
    (5, "sang", "Xôi xéo", "xoi-xeo"),
    (5, "trua", "bò lúc lắc", "bo-luc-lac"), (5, "trua", "canh rau", None),
    (5, "toi", "Bánh xèo", None),
    (6, "sang", "Phở bò", "pho-bo"),
    (6, "trua", "Cao lầu", "cao-lau-hoi-an"),
    (6, "toi", "Lẩu mắm", "lau-mam"),
    (7, "sang", "Bún thang", "bun-thang"),
    (7, "trua", "Cơm gà Tam Kỳ", "com-ga-tam-ky"),
    (7, "toi", "Gỏi cuốn", "goi-cuon"), (7, "toi", "cháo nhẹ", None),
]
ALL_TABLES = build_from_json.TABLES

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
    id_of = {x["slug"]: x["id"] for x in D}
    R = data["recipes"]

    base_ref = os.environ.get("BASE_REF", "main")
    old = json.loads(subprocess.check_output(
        ["git", "show", f"{base_ref}:{REL}/mon-ngon-supabase-data.json"], cwd=BASE, text=True))
    old_dishes = {x["slug"]: x for x in old["dishes"]}

    # 1
    reg = Counter(x["region"] for x in D)
    uniq = len({x["slug"] for x in D}) == len({x["id"] for x in D}) == len({x["name"] for x in D}) == len(D)
    in90 = sum(1 for r in R if r["in_90"])
    dbt = sum(1 for x in D if x["status"] == "dang_bien_tap")
    check(1, "90 món = Bac 30 / Trung 30 / Nam 30; công thức in_90 = 6; tổng recipes = 6; dang_bien_tap = 84",
          len(D) == 90 and reg == Counter(Bac=30, Trung=30, Nam=30) and uniq and in90 == 6 and len(R) == 6 and dbt == 84,
          f"tổng={len(D)} miền={dict(reg)} không_trùng={uniq} in_90={in90} recipes={len(R)} dang_bien_tap={dbt}")

    # 2
    n_lookup = {t: len(data[t]) for t in ["regions", "cooking_methods", "meals", "time_bands", "occasions", "dish_types"]}
    check(2, "bảng tra cứu: 3 miền, 9 cách nấu, 4 bữa, 3 khoảng thời gian, 1 dịp, 4 loại món",
          n_lookup == {"regions": 3, "cooking_methods": 9, "meals": 4, "time_bands": 3, "occasions": 1, "dish_types": 4},
          str(n_lookup))

    # 3
    dcm = {(slug_of[x["dish_id"]], x["cooking_method_code"]) for x in data["dish_cooking_methods"]}
    from_l1 = {(s, d["cooking_method"]) for s, d in old_dishes.items() if d["cooking_method"]}
    meals = {(slug_of[x["dish_id"]], x["meal_code"]) for x in data["dish_meals"]}
    meals_l1 = {(s, d["meal"]) for s, d in old_dishes.items() if d["meal"]}
    occ = {(slug_of[x["dish_id"]], x["occasion_code"]) for x in data["dish_occasions"]}
    mq = [x for x in dcm if x[0] == "mi-quang-ga-tom-thit"]
    n_dish_cook = len({s for s, _ in dcm})
    check(3, "dish_cooking_methods 49 dòng / 46 món (= Lệnh 1 + 5 dòng mục 4.2); Mì Quảng 0; dish_meals 27 (= Lệnh 1); dish_occasions 1 (lau-mam)",
          len(data["dish_cooking_methods"]) == 49 and n_dish_cook == 46 and dcm == from_l1 | EXTRA_COOK and not mq
          and meals == meals_l1 and len(data["dish_meals"]) == 27 and occ == {("lau-mam", "cuoi_tuan_dai_khach")},
          f"cách_nấu={len(data['dish_cooking_methods'])}/{n_dish_cook} món, mì_quảng={len(mq)}, bữa={len(data['dish_meals'])}, dịp={sorted(occ)}")

    # 4
    W = {w["id"]: w for w in data["weekly_menu"]}
    items = sorted(data["weekly_menu_items"], key=lambda i: (W[i["weekly_menu_id"]]["day_of_week"],
                   ["sang", "trua", "toi"].index(W[i["weekly_menu_id"]]["meal"]), i["sort_order"]))
    got = [(W[i["weekly_menu_id"]]["day_of_week"], W[i["weekly_menu_id"]]["meal"], i["item_text"],
            slug_of.get(i["dish_id"])) for i in items]
    print("    weekly_menu_items (ngày, bữa, cụm tên → slug):")
    for g in got:
        print(f"      T{g[0]} {g[1]:<4} {g[2]!r} → {g[3] or 'NULL'}")
    bm = [i for i in data["weekly_menu_items"] if i["item_text"] == "Bánh mì thịt"]
    check(4, "weekly_menu 21 dòng; weekly_menu_items khớp đúng danh sách mục 4.3; 'Bánh mì thịt' dish_id & recipe_id NULL",
          len(data["weekly_menu"]) == 21 and got == EXPECTED_ITEMS and len(bm) == 1
          and bm[0]["dish_id"] is None and bm[0]["recipe_id"] is None,
          f"items={len(got)} nối_món={sum(1 for g in got if g[3])}")

    # 5
    dbt_ids = {x["id"] for x in D if x["status"] == "dang_bien_tap"}
    bad_rec = [r for r in R if r["dish_id"] in dbt_ids]
    new_vn = [n for n in data["nutrition_estimates"] if n["dish_id"] in dbt_ids and n["basis"] == "per_serving"
              and n["source_code"] in VN_SOURCES]
    same_nut = {n["id"] for n in data["nutrition_estimates"]} == {n["id"] for n in old["nutrition_estimates"]}
    check(5, "món dang_bien_tap không có recipe / total_minutes / dinh dưỡng theo khẩu phần Bảng TPTP VN; "
             "nutrition_estimates không thêm dòng nào so với Lệnh 1",
          not bad_rec and not new_vn and same_nut,
          f"recipe_vi_phạm={len(bad_rec)} dinh_dưỡng_VN_vi_phạm={len(new_vn)} cùng_bộ_id_dinh_dưỡng={same_nut}")

    # 6
    cols6 = ["locality", "difficulty", "image_url", "description", "dish_type"]
    nonnull = {c: sum(1 for x in D if x[c] is not None) for c in cols6}
    check(6, "locality, difficulty, image_url, description, dish_type đều NULL ở cả 90 món",
          all(v == 0 for v in nonnull.values()), str(nonnull))

    # 7 (phần offline): dish_vegetarian = an_chay của Lệnh 1
    old_chay = {t["dish_id"]: (t["is_applicable"], t["basis"]) for t in old["dish_diet_tags"]
                if t["diet_mode_code"] == "an_chay"}
    veg = {v["dish_id"]: (v["is_vegetarian"], v["basis"]) for v in data["dish_vegetarian"]}
    check("7a", "dish_vegetarian trùng 90/90 với tag an_chay của Lệnh 1", veg == old_chay and len(veg) == 90,
          f"dòng={len(veg)} lệch={sum(1 for k in old_chay if veg.get(k) != old_chay[k])}")

    # 8 + 9a
    cols = {}
    try:
        cols = schema_columns(schema_sql)
        check("9a", "pglast parse schema.sql", True, f"{len(cols)} bảng")
        bad = sorted({(t, k) for t in ALL_TABLES for r in data[t] for k in r if k not in cols.get(t, [])})
        missing = [t for t in ALL_TABLES if t not in cols]
        check(8, "mọi key JSON là cột có thật (lấy cột bằng pglast từ schema.sql)", not bad and not missing,
              f"sai={bad} bảng_thiếu={missing}")
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

    # 12
    rc = cols.get("recipes", [])
    need = {"recipe_source", "source_url", "source_accessed_date", "recipe_status"}
    kb = [r for r in R if r["recipe_source"] == "Kịch bản 15 trang Món Ngon Mỗi Ngày (nguồn nội bộ)"
          and r["recipe_status"] is None and r["source_url"] is None and r["source_accessed_date"] is None]
    online = sum(1 for r in R if r["recipe_status"] == "tham_khao_online")
    tm = {slug_of[r["dish_id"]]: r["total_minutes"] for r in R}
    check(12, "recipes có 4 cột nguồn; 6 công thức kịch bản: recipe_status NULL, recipe_source = kịch bản nội bộ; tham_khao_online = 0",
          need <= set(rc) and len(kb) == 6 and online == 0, f"cột_đủ={need <= set(rc)} kịch_bản={len(kb)} online={online} total_minutes={tm}")

    # 13
    st = Counter(x["status"] for x in D)
    check(13, "dishes.status: co_cong_thuc 6, dang_bien_tap 84, tham_khao_online 0",
          st.get("co_cong_thuc") == 6 and st.get("dang_bien_tap") == 84 and st.get("tham_khao_online", 0) == 0,
          str(dict(st)))

    # 11 + 7b (Postgres thật)
    dsn = os.environ.get("PGTEST_DSN")
    if not dsn:
        print("[SKIP] 7b. SKIP: không có Postgres (so view dish_diet_eval với Lệnh 1 cần Postgres)")
        print("[SKIP] 11. SKIP: không có Postgres")
    else:
        def psql(sql=None, f=None):
            args = ["psql", dsn, "-v", "ON_ERROR_STOP=1", "-q", "-At", "-F", "\t"]
            args += ["-f", str(f)] if f else ["-c", sql]
            return subprocess.run(args, text=True, capture_output=True)

        psql("do $$begin if not exists (select 1 from pg_roles where rolname='anon') then create role anon nologin; end if;"
             " if not exists (select 1 from pg_roles where rolname='authenticated') then create role authenticated nologin; end if; end$$")
        runs = [psql(f=BASE / "schema.sql"), psql(f=seed_path), psql(f=BASE / "schema.sql"), psql(f=seed_path)]
        ok_run = all(r.returncode == 0 for r in runs)
        errs = " | ".join(r.stderr.strip() for r in runs if r.returncode != 0)

        # 7b hồi quy: view vs dish_diet_tags của Lệnh 1
        out = psql("select dish_id, diet_mode_code, coalesce(is_applicable::text,'null'), status, coalesce(basis,'') from dish_diet_eval")
        view = {}
        for line in out.stdout.strip().splitlines():
            a, b, c, d, e = line.split("\t")
            view[(a, b)] = ({"true": True, "false": False, "null": None}[c], d, e)
        old_tags = {(t["dish_id"], t["diet_mode_code"]): (t["is_applicable"], t["status"], t["basis"]) for t in old["dish_diet_tags"]}
        diff = [k for k in old_tags if view.get(k) != old_tags[k]]
        nutri_nonnull = sum(1 for (dd, m), v in view.items() if m in NUTRI_MODES and v[0] is not None)
        check("7b", "dish_diet_eval trùng 540/540 với dish_diet_tags của Lệnh 1 (is_applicable, status, basis); 4 chế độ dinh dưỡng khác NULL = 0",
              len(view) == 540 and len(old_tags) == 540 and not diff and nutri_nonnull == 0,
              f"view={len(view)} lệnh1={len(old_tags)} lệch={len(diff)} dinh_dưỡng_khác_null={nutri_nonnull}")

        res = {}
        res["f_unaccent('Phở bò Đà Nẵng')"] = psql("select public.f_unaccent(lower('Phở bò Đà Nẵng'))").stdout.strip()
        res["search_dishes('pho bo')"] = psql("select string_agg(slug, ',') || ' (' || count(*) || ')' from public.search_dishes('pho bo')").stdout.strip()
        res["dish_time_band"] = psql("select string_agg(d.slug||'='||t.time_band_code, ' ' order by d.slug) from dish_time_band t join dishes d on d.id=t.dish_id").stdout.strip()
        old_tb = " ".join(f"{s}={d['time_band']}" for s, d in sorted(old_dishes.items()) if d["time_band"])
        res["bảng có RLS / có policy đọc cho anon,authenticated"] = psql(
            "select count(*) filter (where c.relrowsecurity) || ' / ' || count(*) filter (where exists ("
            "select 1 from pg_policies p where p.schemaname='public' and p.tablename=c.relname and p.cmd='SELECT' "
            "and p.roles @> array['anon','authenticated']::name[])) || ' trên ' || count(*) "
            "from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname='public' and c.relkind='r'").stdout.strip()
        res["policy ghi (khác SELECT)"] = psql("select count(*) from pg_policies where schemaname='public' and cmd <> 'SELECT'").stdout.strip()
        res["hàm public có search_path=''"] = psql(
            "select string_agg(p.proname || '=' || coalesce(array_to_string(p.proconfig, ','), 'KHÔNG'), ' ' order by p.proname) "
            "from pg_proc p join pg_namespace n on n.oid=p.pronamespace where n.nspname='public'").stdout.strip()
        res["số đếm"] = psql(
            "select (select count(*) from dishes)||' món, '||(select count(*) from recipes)||' công thức, '||"
            "(select count(*) from ingredients)||' nguyên liệu, '||(select count(*) from nutrition_estimates)||' dinh dưỡng, '||"
            "(select count(*) from dish_cooking_methods)||' cách nấu, '||(select count(*) from dish_meals)||' bữa, '||"
            "(select count(*) from weekly_menu_items)||' món trong thực đơn tuần'").stdout.strip()

        # View tính đúng khi có số liệu: DỮ LIỆU GIẢ chỉ trong giao dịch test, ROLLBACK, không lưu.
        fx = psql(
            "begin;"
            f"insert into nutrition_estimates (dish_id, source_item_name, basis, kcal, protein_g, carb_g, fat_g, source_code, method, confidence) values "
            f"('{id_of['pho-bo']}', 'TEST', 'per_serving', 400, 30, 50, 8, 'fao_vn_fct_2017', 'TEST', 'trung_binh_uoc_tinh'),"
            f"('{id_of['rau-muong-xao-toi']}', 'TEST', 'per_serving', 140, 5, 10, 8, 'fao_vn_fct_2017', 'TEST', 'trung_binh_uoc_tinh'),"
            f"('{id_of['mi-quang-ga-tom-thit']}', 'TEST', 'per_serving', 600, 40, 60, 8, 'fao_vn_fct_2017', 'TEST', 'trung_binh_uoc_tinh');"
            "select d.slug || ':' || e.diet_mode_code || '=' || coalesce(e.is_applicable::text, 'null') from dish_diet_eval e "
            "join dishes d on d.id = e.dish_id where d.slug in ('pho-bo','rau-muong-xao-toi','mi-quang-ga-tom-thit') "
            "and e.diet_mode_code in ('an_kieng_giam_can','it_dau_mo','giau_protein','it_tinh_bot') order by 1;"
            "rollback;")
        got_fx = set(fx.stdout.split())
        exp_fx = {
            "pho-bo:an_kieng_giam_can=true", "pho-bo:it_dau_mo=true", "pho-bo:giau_protein=true", "pho-bo:it_tinh_bot=false",
            "rau-muong-xao-toi:it_dau_mo=false",
            "mi-quang-ga-tom-thit:it_dau_mo=null",
        }
        after = psql("select count(*) from nutrition_estimates").stdout.strip()
        res["test view với dữ liệu giả (rollback)"] = ("đúng" if exp_fx <= got_fx else f"SAI: {sorted(got_fx)}") + f"; sau rollback còn {after} dòng dinh dưỡng"

        # Chạy toàn bộ khối SQL trong README
        blocks = re.findall(r"```sql\n(.*?)```", (BASE / "README.md").read_text(encoding="utf-8"), re.S)
        bad_blocks = []
        for i, b in enumerate(blocks):
            r = psql(b)
            if r.returncode != 0:
                bad_blocks.append((i, r.stderr.strip()[:200]))
        res["khối SQL trong README chạy được"] = f"{len(blocks) - len(bad_blocks)}/{len(blocks)}" + (f" lỗi={bad_blocks}" if bad_blocks else "")

        for k, v in res.items():
            print(f"      {k}: {v}")
        rls = res["bảng có RLS / có policy đọc cho anon,authenticated"]
        funcs_ok = "KHÔNG" not in res["hàm public có search_path=''"]
        ok11 = (ok_run and res["f_unaccent('Phở bò Đà Nẵng')"] == "pho bo da nang"
                and res["search_dishes('pho bo')"].startswith("pho-bo")
                and res["dish_time_band"] == old_tb
                and rls == "18 / 18 trên 18" and res["policy ghi (khác SELECT)"] == "0" and funcs_ok
                and res["test view với dữ liệu giả (rollback)"].startswith("đúng") and after == "21"
                and not bad_blocks)
        check(11, "Postgres thật: schema + seed chạy 2 lần không lỗi; f_unaccent; search_dishes; dish_time_band = time_band Lệnh 1; "
                  "RLS + policy đọc cả 18 bảng, 0 policy ghi; mọi hàm search_path=''; view tính đúng; README chạy được",
              ok11, errs)

    print()
    print("KẾT QUẢ:", "TẤT CẢ PASS" if failures == 0 else f"{failures} FAIL")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
