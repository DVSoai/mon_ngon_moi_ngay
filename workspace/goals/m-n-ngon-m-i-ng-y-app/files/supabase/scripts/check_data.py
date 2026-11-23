#!/usr/bin/env python3
"""Kiểm chứng gói dữ liệu Supabase sau Lệnh 3 (công thức tham khảo online theo đợt).
In PASS/FAIL từng dòng; có FAIL thì exit 1.

    python scripts/check_data.py

Tùy chọn:
  BASE_REF=main        nhánh/commit gốc để so sánh (mặc định: main). Mọi thay đổi so với gốc
                       phải nằm ở các món vừa chuyển sang tham_khao_online.
  DOT=bac              đợt đang kiểm (bac | trung | nam). Mặc định: bac. Đọc reports/dot_<DOT>.md.
  PGTEST_DSN=...       chuỗi kết nối tới một database Postgres 15+ TRỐNG trên máy test (KHÔNG dùng
                       Supabase thật). Script tạo thêm database <tên>_base để nạp bản gốc và so view.
                       Không đặt → SKIP các mục cần Postgres.

Script không kết nối Supabase, không đọc hay ghi key nào.
"""
import csv
import datetime as dt
import io
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

import pglast

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
sys.path.insert(0, str(HERE))
import build_from_json  # noqa: E402

REL = "workspace/goals/m-n-ngon-m-i-ng-y-app/files/supabase"
REGION_OF_DOT = {"bac": "Bac", "trung": "Trung", "nam": "Nam"}
KB_SOURCE = "Kịch bản 15 trang Món Ngon Mỗi Ngày (nguồn nội bộ)"
ALL_TABLES = build_from_json.TABLES
TODAY = dt.date(2026, 11, 23)

failures = 0


def check(no, label, ok, detail=""):
    global failures
    if not ok:
        failures += 1
    print(f"[{'PASS' if ok else 'FAIL'}] {no}. {label}" + (f" — {detail}" if detail else ""))


def schema_columns(sql):
    cols = {}
    for raw in pglast.parse_sql(sql):
        st = raw.stmt
        if type(st).__name__ == "CreateStmt":
            cols[st.relation.relname] = [e.colname for e in st.tableElts if type(e).__name__ == "ColumnDef"]
    return cols


def git_show(ref, name):
    return subprocess.check_output(["git", "show", f"{ref}:{REL}/{name}"], cwd=BASE, text=True)


def key(row):
    return json.dumps(row, ensure_ascii=False, sort_keys=True)


def main():
    dot = os.environ.get("DOT", "bac")
    region = REGION_OF_DOT[dot]
    base_ref = os.environ.get("BASE_REF", "main")
    data = build_from_json.load()
    old = json.loads(git_show(base_ref, "mon-ngon-supabase-data.json"))
    schema_sql = (BASE / "schema.sql").read_text(encoding="utf-8")

    D = data["dishes"]
    by_id = {x["id"]: x for x in D}
    slug_of = {x["id"]: x["slug"] for x in D}
    old_d = {x["slug"]: x for x in old["dishes"]}
    R = data["recipes"]
    online = [r for r in R if r["recipe_status"] == "tham_khao_online"]
    new_online_ids = {x["id"] for x in D if x["status"] == "tham_khao_online"
                      and old_d[x["slug"]]["status"] != "tham_khao_online"}
    new_online_slugs = sorted(slug_of[i] for i in new_online_ids)
    old_online = sum(1 for x in old["dishes"] if x["status"] == "tham_khao_online")

    # 1. Đếm món / trạng thái
    reg = Counter(x["region"] for x in D)
    st = Counter(x["status"] for x in D)
    st_reg = Counter((x["region"], x["status"]) for x in D)
    old_st_reg = Counter((x["region"], x["status"]) for x in old["dishes"])
    other_regions_same = all(st_reg[(g, s)] == old_st_reg[(g, s)] for g in ("Bac", "Trung", "Nam") if g != region
                             for s in ("co_cong_thuc", "dang_bien_tap", "tham_khao_online"))
    moved_ok = all(old_d[slug_of[i]]["status"] == "dang_bien_tap" and by_id[i]["region"] == region for i in new_online_ids)
    n_new = len(new_online_ids)
    check(1, f"90 món (30/30/30); chỉ món miền {region} đang dang_bien_tap được chuyển sang tham_khao_online; miền khác không đổi",
          len(D) == 90 and reg == Counter(Bac=30, Trung=30, Nam=30) and st["co_cong_thuc"] == 6
          and st["tham_khao_online"] == old_online + n_new and other_regions_same and moved_ok,
          f"trạng_thái={dict(st)} | {region}: " + ", ".join(f"{s}={st_reg[(region, s)]}" for s in ("co_cong_thuc", "tham_khao_online", "dang_bien_tap"))
          + f" | đợt này chuyển {n_new} món")

    # 2. Bảng không được đổi
    frozen = ["regions", "cooking_methods", "meals", "time_bands", "occasions", "dish_types", "diet_modes",
              "nutrition_estimates", "dish_meals", "dish_occasions", "weekly_menu", "weekly_menu_items"]
    changed = [t for t in frozen if sorted(map(key, data[t])) != sorted(map(key, old[t]))]
    check(2, "không đổi: bảng tra cứu, diet_modes, nutrition_estimates (không thêm dinh dưỡng), dish_meals, dish_occasions, thực đơn tuần",
          not changed, f"bảng_bị_đổi={changed} nutrition={len(data['nutrition_estimates'])}")

    # 3. Công thức kịch bản và nguyên liệu của chúng giữ nguyên
    kb_now = sorted(key(r) for r in R if r["recipe_source"] == KB_SOURCE)
    kb_old = sorted(key(r) for r in old["recipes"] if r["recipe_source"] == KB_SOURCE)
    kb_ids = {r["id"] for r in old["recipes"] if r["recipe_source"] == KB_SOURCE}
    ing_kb_now = sorted(key(i) for i in data["ingredients"] if i["recipe_id"] in kb_ids)
    ing_kb_old = sorted(key(i) for i in old["ingredients"] if i["recipe_id"] in kb_ids)
    old_rec_ids = {r["id"] for r in old["recipes"]}
    old_recs_same = sorted(key(r) for r in R if r["id"] in old_rec_ids) == sorted(key(r) for r in old["recipes"])
    check(3, "6 công thức kịch bản + nguyên liệu của chúng giữ nguyên từng byte; mọi recipe cũ không đổi",
          len(kb_now) == 6 and kb_now == kb_old and ing_kb_now == ing_kb_old and old_recs_same,
          f"kịch_bản={len(kb_now)} nguyên_liệu_kb={len(ing_kb_now)}")

    # 4. Trường nguồn của công thức online
    src_codes = {s["code"]: s for s in data["sources"]}
    bad = []
    per_dish = Counter(r["dish_id"] for r in online)
    for r in online:
        sl = slug_of.get(r["dish_id"], "?")
        try:
            dd = dt.date.fromisoformat(r["source_accessed_date"] or "")
        except ValueError:
            dd = None
        first = (r["steps_text"] or "").split("\n", 1)[0]
        n_ing = [i for i in data["ingredients"] if i["recipe_id"] == r["id"]]
        problems = [
            ("in_90", r["in_90"] is not True),
            ("recipe_source", not r["recipe_source"]),
            ("source_url", not (r["source_url"] or "").startswith("https://")),
            ("source_accessed_date", dd is None or dd > TODAY),
            ("source_code", r["source_code"] not in src_codes or r["source_code"] == "kich_ban_15_trang"),
            ("dòng_đầu_steps", first != f"Công thức tham khảo từ {r['recipe_source']}, chưa nấu thử."),
            ("tip", r["tip"] is not None),
            ("dish_name", r["dish_name"] != by_id[r["dish_id"]]["name"]),
            ("ingredients", [i["text"] for i in sorted(n_ing, key=lambda i: i["sort_order"])] != (r["ingredients_text"] or "").split("; ")
             or sorted(i["sort_order"] for i in n_ing) != list(range(1, len(n_ing) + 1))),
            ("dish_status", by_id[r["dish_id"]]["status"] != "tham_khao_online" or by_id[r["dish_id"]]["has_full_recipe"] is not True),
            ("1_công_thức/món", per_dish[r["dish_id"]] != 1),
            ("servings", r["servings"] is not None and r["servings_text"] is None),
            ("total_minutes", r["total_minutes"] is not None and r["time_text"] is None),
        ]
        bad += [(sl, p) for p, cond in problems if cond]
    online_dishes = {x["id"] for x in D if x["status"] == "tham_khao_online"}
    check(4, f"{len(online)} công thức online: đủ recipe_source / https source_url / ngày truy cập / source_code; "
             "dòng đầu 'Công thức tham khảo từ …, chưa nấu thử.'; tip NULL; ingredients khớp từng dòng; 1 công thức/món",
          not bad and online_dishes == set(per_dish), f"lỗi={bad}")

    # 5. Món dang_bien_tap không có công thức; sources cũ giữ nguyên
    dbt = {x["id"] for x in D if x["status"] == "dang_bien_tap"}
    rec_dbt = [slug_of[r["dish_id"]] for r in R if r["dish_id"] in dbt]
    old_src_same = all(key(s) == key(src_codes.get(s["code"], {})) for s in old["sources"])
    new_src = sorted(set(src_codes) - {s["code"] for s in old["sources"]})
    check(5, "món dang_bien_tap không có recipe; các dòng sources cũ không đổi, chỉ thêm nguồn mới",
          not rec_dbt and old_src_same, f"recipe_ở_dang_bien_tap={rec_dbt} nguồn_mới={new_src}")

    # 6. Cách nấu: chỉ thêm, chỉ cho món vừa chuyển; Mì Quảng vẫn NULL (QĐ3)
    cm_now = {(x["dish_id"], x["cooking_method_code"]) for x in data["dish_cooking_methods"]}
    cm_old = {(x["dish_id"], x["cooking_method_code"]) for x in old["dish_cooking_methods"]}
    added = sorted((slug_of[a], b) for a, b in cm_now - cm_old)
    mq = [b for a, b in cm_now if slug_of[a] == "mi-quang-ga-tom-thit"]
    check(6, "dish_cooking_methods: không xóa dòng nào; dòng thêm chỉ thuộc món vừa chuyển; Mì Quảng 0 dòng",
          cm_old <= cm_now and all(a in new_online_ids for a, _ in cm_now - cm_old) and not mq,
          f"tổng={len(cm_now)} (gốc {len(cm_old)}) thêm={added}")

    # 7. dish_vegetarian
    v_now = {v["dish_id"]: v for v in data["dish_vegetarian"]}
    v_old = {v["dish_id"]: v for v in old["dish_vegetarian"]}
    other_same = all(key(v_now[i]) == key(v_old[i]) for i in v_old if i not in new_online_ids)
    conf = [slug_of[i] for i in new_online_ids if not (v_now[i]["confirmed_by_recipe"] is True
            and v_now[i]["is_vegetarian"] is not None and v_now[i]["basis"].startswith("Theo công thức tham khảo"))]
    flipped = sorted(slug_of[i] for i in new_online_ids if v_old[i]["is_vegetarian"] != v_now[i]["is_vegetarian"])
    check(7, "dish_vegetarian: 90 dòng; món vừa chuyển có confirmed_by_recipe = true và basis dẫn công thức; món khác không đổi",
          len(v_now) == 90 and other_same and not conf, f"chưa_xác_nhận={conf} đổi_giá_trị={flipped}")

    # 8. Cột chưa có nguồn vẫn NULL
    cols8 = ["locality", "difficulty", "image_url", "description", "dish_type"]
    nonnull = {c: sum(1 for x in D if x[c] is not None) for c in cols8}
    check(8, "locality, difficulty, image_url, description, dish_type vẫn NULL ở cả 90 món", all(v == 0 for v in nonnull.values()), str(nonnull))

    # 9. schema.sql không đổi; pglast; key JSON là cột thật
    schema_same = schema_sql == git_show(base_ref, "schema.sql")
    cols = {}
    try:
        cols = schema_columns(schema_sql)
        badk = sorted({(t, k) for t in ALL_TABLES for r in data[t] for k in r if k not in cols.get(t, [])})
        check(9, "schema.sql giống hệt bản gốc; pglast parse được; mọi key JSON là cột có thật",
              schema_same and not badk, f"schema_giống={schema_same} bảng={len(cols)} key_sai={badk}")
    except Exception as e:  # noqa: BLE001
        check(9, "schema.sql giống hệt bản gốc; pglast parse được", False, repr(e))
    try:
        n = len(pglast.parse_sql((BASE / "seed.sql").read_text(encoding="utf-8")))
        check("9b", "pglast parse seed.sql", True, f"{n} câu lệnh")
    except Exception as e:  # noqa: BLE001
        check("9b", "pglast parse seed.sql", False, repr(e))

    # 10. File sinh ra khớp JSON
    gen = build_from_json.generate(data)
    same = {f: (BASE / f).exists() and (BASE / f).read_text(encoding="utf-8") == c for f, c in gen.items()}
    n_d = len(list(csv.reader(io.StringIO(gen["dishes.csv"])))) - 1
    nut = list(csv.DictReader(io.StringIO(gen["nutrition.csv"])))
    check(10, "seed.sql / dishes.csv / nutrition.csv giống byte-by-byte bản sinh từ JSON; dishes.csv 90; nutrition.csv 21",
          all(same.values()) and n_d == 90 and len(nut) == 21, f"giống={same} dishes.csv={n_d} nutrition.csv={len(nut)}")

    # 12. Báo cáo đợt liệt kê đủ món của miền
    rep = BASE / "reports" / f"dot_{dot}.md"
    region_pending_old = sorted(s for s, x in old_d.items() if x["region"] == region and x["status"] == "dang_bien_tap")
    txt = rep.read_text(encoding="utf-8") if rep.exists() else ""
    missing = [s for s in region_pending_old if f"`{s}`" not in txt]
    urls_missing = [r["source_url"] for r in online if by_id[r["dish_id"]]["region"] == region and r["source_url"] not in txt]
    check(12, f"reports/dot_{dot}.md có đủ {len(region_pending_old)} món miền {region} đang dang_bien_tap ở bản gốc và đủ URL nguồn",
          rep.exists() and not missing and not urls_missing, f"thiếu_món={missing} thiếu_url={urls_missing}")

    # 13. dish_time_band kỳ vọng (tính từ JSON)
    tb = data["time_bands"]
    exp_tb = {}
    for r in R:
        if r["dish_id"] and r["total_minutes"] is not None:
            for b in tb:
                if r["total_minutes"] >= b["min_minutes"] and (b["max_minutes"] is None or r["total_minutes"] <= b["max_minutes"]):
                    exp_tb[slug_of[r["dish_id"]]] = b["code"]
    exp_tb_s = " ".join(f"{s}={c}" for s, c in sorted(exp_tb.items()))

    # 11. Postgres thật
    dsn = os.environ.get("PGTEST_DSN")
    if not dsn:
        print("[SKIP] 11. SKIP: không có Postgres")
    else:
        def psql(sql=None, f=None, conn=dsn):
            args = ["psql", conn, "-v", "ON_ERROR_STOP=1", "-q", "-At", "-F", "\t"]
            args += ["-f", str(f)] if f else ["-c", sql]
            return subprocess.run(args, text=True, capture_output=True)

        m = re.search(r"dbname=(\S+)", dsn)
        base_db = (m.group(1) if m else "postgres") + "_base"
        base_dsn = re.sub(r"dbname=\S+", f"dbname={base_db}", dsn)
        psql("do $$begin if not exists (select 1 from pg_roles where rolname='anon') then create role anon nologin; end if;"
             " if not exists (select 1 from pg_roles where rolname='authenticated') then create role authenticated nologin; end if; end$$")
        psql(f"drop database if exists {base_db}")
        psql(f"create database {base_db}")
        with tempfile.TemporaryDirectory() as td:
            bs, bd = Path(td) / "schema.sql", Path(td) / "seed.sql"
            bs.write_text(git_show(base_ref, "schema.sql"), encoding="utf-8")
            bd.write_text(git_show(base_ref, "seed.sql"), encoding="utf-8")
            base_runs = [psql(f=bs, conn=base_dsn), psql(f=bd, conn=base_dsn)]
        runs = [psql(f=BASE / "schema.sql"), psql(f=BASE / "seed.sql"), psql(f=BASE / "schema.sql"), psql(f=BASE / "seed.sql")]
        ok_run = all(r.returncode == 0 for r in runs + base_runs)
        errs = " | ".join(r.stderr.strip() for r in runs + base_runs if r.returncode != 0)

        q_view = ("select d.slug, e.diet_mode_code, coalesce(e.is_applicable::text,'null'), e.status, coalesce(e.basis,'') "
                  "from dish_diet_eval e join dishes d on d.id = e.dish_id")
        def view(conn):
            out = psql(q_view, conn=conn).stdout.strip().splitlines()
            return {(l.split("\t")[0], l.split("\t")[1]): tuple(l.split("\t")[2:]) for l in out}
        v_now_db, v_base_db = view(dsn), view(base_dsn)
        diff = sorted(k for k in v_base_db if v_now_db.get(k) != v_base_db[k])
        diff_outside = [k for k in diff if k[0] not in new_online_slugs]
        print("    dish_diet_eval khác bản gốc (slug, chế độ: gốc → mới):")
        for k in diff:
            print(f"      {k[0]} {k[1]}: {v_base_db[k][0]} → {v_now_db[k][0]}")

        res = {}
        res["search_dishes('pho ga')"] = psql("select string_agg(slug, ',') from public.search_dishes('pho ga')").stdout.strip()
        res["dish_time_band"] = psql("select string_agg(d.slug||'='||t.time_band_code, ' ' order by d.slug) from dish_time_band t join dishes d on d.id=t.dish_id").stdout.strip()
        res["bảng có RLS / có policy đọc cho anon,authenticated"] = psql(
            "select count(*) filter (where c.relrowsecurity) || ' / ' || count(*) filter (where exists ("
            "select 1 from pg_policies p where p.schemaname='public' and p.tablename=c.relname and p.cmd='SELECT' "
            "and p.roles @> array['anon','authenticated']::name[])) || ' trên ' || count(*) "
            "from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname='public' and c.relkind='r'").stdout.strip()
        res["policy ghi (khác SELECT)"] = psql("select count(*) from pg_policies where schemaname='public' and cmd <> 'SELECT'").stdout.strip()
        res["số đếm"] = psql(
            "select (select count(*) from dishes)||' món, '||(select count(*) from recipes)||' công thức ('||"
            "(select count(*) from recipes where recipe_status='tham_khao_online')||' online), '||"
            "(select count(*) from ingredients)||' nguyên liệu, '||(select count(*) from nutrition_estimates)||' dinh dưỡng, '||"
            "(select count(*) from dish_cooking_methods)||' cách nấu, '||(select count(*) from sources)||' nguồn'").stdout.strip()
        res["trạng thái món"] = psql("select string_agg(status||'='||n, ' ' order by status) from (select status, count(*) n from dishes group by 1) s").stdout.strip()
        blocks = re.findall(r"```sql\n(.*?)```", (BASE / "README.md").read_text(encoding="utf-8"), re.S)
        bad_blocks = [(i, r.stderr.strip()[:200]) for i, b in enumerate(blocks) if (r := psql(b)).returncode != 0]
        res["khối SQL trong README chạy được"] = f"{len(blocks) - len(bad_blocks)}/{len(blocks)}" + (f" lỗi={bad_blocks}" if bad_blocks else "")
        for k, v in res.items():
            print(f"      {k}: {v}")
        psql(f"drop database if exists {base_db}")
        ok11 = (ok_run and "pho-ga" in res["search_dishes('pho ga')"] and res["dish_time_band"] == exp_tb_s
                and res["bảng có RLS / có policy đọc cho anon,authenticated"] == "18 / 18 trên 18"
                and res["policy ghi (khác SELECT)"] == "0" and not bad_blocks and not diff_outside
                and len(v_now_db) == 540)
        check(11, "Postgres thật: bản gốc + bản mới chạy schema/seed không lỗi (bản mới chạy 2 lần); dish_time_band đúng kỳ vọng; "
                  "RLS 18/18, 0 policy ghi; README chạy được; dish_diet_eval chỉ khác bản gốc ở món vừa chuyển",
              ok11, f"view_khác={len(diff)} khác_ngoài_đợt={diff_outside} {errs}")

    print()
    print("KẾT QUẢ:", "TẤT CẢ PASS" if failures == 0 else f"{failures} FAIL")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
