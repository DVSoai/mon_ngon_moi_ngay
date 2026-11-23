-- Món Ngon Mỗi Ngày — schema.sql (Postgres 15+ / Supabase) — thiết kế Lệnh 2
-- CÀI MỚI: chạy trên database chưa có bảng nào, rồi chạy seed.sql.
-- Chạy lại được (if not exists / or replace), nhưng KHÔNG phải migration từ schema cũ.
--
-- Dữ liệu: 90 món = Bắc 30 / Trung 30 / Nam 30, chỉ 3 miền. 6 món có công thức đầy đủ,
-- 84 món 'dang_bien_tap'. Không bịa nguyên liệu / thời gian / dinh dưỡng.
-- Nguồn dinh dưỡng chuẩn duy nhất: Bảng Thành phần Thực phẩm Việt Nam (QĐ1=B);
-- FitArchive chỉ tham khảo, không dùng để tính tag hay hiển thị.
--
-- Nhãn filter (miền, cách nấu, bữa, thời gian, dịp, loại món, chế độ ăn) nằm trong các
-- bảng tra cứu — web/app render chip filter thẳng từ DB, không viết cứng ở UI.
-- Truy cập dữ liệu từ web/app chỉ qua lớp data (repository), không gọi SQL trong UI.

create schema if not exists extensions;
create extension if not exists pgcrypto with schema extensions;
create extension if not exists pg_trgm with schema extensions;
create extension if not exists unaccent with schema extensions;

-- ============================================================
-- Hàm dùng chung
-- ============================================================

create or replace function public.set_updated_at()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- Bỏ dấu tiếng Việt để tìm kiếm không dấu ("pho bo" ra "Phở bò").
create or replace function public.f_unaccent(t text)
returns text
language sql
immutable
parallel safe
set search_path = ''
as $$
  select extensions.unaccent('extensions.unaccent'::regdictionary, t)
$$;

-- ============================================================
-- Bảng tra cứu (nhãn filter dùng chung cho web và app)
-- ============================================================

create table if not exists regions (
  code text primary key,
  name_vi text not null,
  sort_order int not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists cooking_methods (
  code text primary key,
  name_vi text not null,
  sort_order int not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists meals (
  code text primary key,
  name_vi text not null,
  sort_order int not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists time_bands (
  code text primary key,
  name_vi text not null,
  sort_order int not null,
  min_minutes int not null check (min_minutes >= 0),
  max_minutes int check (max_minutes is null or max_minutes >= min_minutes),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists occasions (
  code text primary key,
  name_vi text not null,
  sort_order int not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists dish_types (
  code text primary key,
  name_vi text not null,
  sort_order int not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists sources (
  code text primary key,
  name text not null,
  note text,
  url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- ============================================================
-- Món, công thức, nguyên liệu
-- ============================================================

create table if not exists dishes (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  name text not null,
  region text not null references regions (code),
  dish_type text references dish_types (code),
  locality text,
  difficulty text check (difficulty in ('de', 'trung_binh', 'kho')),
  image_url text,
  description text,
  has_full_recipe boolean not null default false,
  status text not null default 'dang_bien_tap'
    check (status in ('co_cong_thuc', 'tham_khao_online', 'dang_bien_tap')),
  is_published boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists idx_dishes_region on dishes (region);
create index if not exists idx_dishes_status on dishes (status);
create index if not exists idx_dishes_dish_type on dishes (dish_type);
create index if not exists idx_dishes_name_unaccent_trgm
  on dishes using gin (public.f_unaccent(lower(name)) extensions.gin_trgm_ops);

create table if not exists dish_cooking_methods (
  dish_id uuid not null references dishes (id) on delete cascade,
  cooking_method_code text not null references cooking_methods (code),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  primary key (dish_id, cooking_method_code)
);
create index if not exists idx_dish_cooking_methods_code on dish_cooking_methods (cooking_method_code);

create table if not exists dish_meals (
  dish_id uuid not null references dishes (id) on delete cascade,
  meal_code text not null references meals (code),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  primary key (dish_id, meal_code)
);
create index if not exists idx_dish_meals_code on dish_meals (meal_code);

create table if not exists dish_occasions (
  dish_id uuid not null references dishes (id) on delete cascade,
  occasion_code text not null references occasions (code),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  primary key (dish_id, occasion_code)
);
create index if not exists idx_dish_occasions_code on dish_occasions (occasion_code);

create table if not exists recipes (
  id uuid primary key default gen_random_uuid(),
  dish_id uuid references dishes (id),
  dish_name text not null,
  region text references regions (code),
  in_90 boolean not null default true,
  servings_text text,
  servings int check (servings > 0),
  time_text text,
  total_minutes int check (total_minutes > 0),
  ingredients_text text,
  steps_text text,
  tip text,
  source_code text not null default 'kich_ban_15_trang' references sources (code),
  recipe_source text,
  source_url text,
  source_accessed_date date,
  recipe_status text check (recipe_status in ('tham_khao_online', 'da_nau_thu')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint uq_recipes_dish unique (dish_id),
  constraint ck_recipes_in_90 check (in_90 = (dish_id is not null)),
  constraint ck_recipes_online_source check (
    recipe_status is distinct from 'tham_khao_online'
    or (recipe_source is not null and source_url is not null and source_accessed_date is not null)
  )
);

create table if not exists ingredients (
  id uuid primary key default gen_random_uuid(),
  recipe_id uuid not null references recipes (id) on delete cascade,
  sort_order int not null,
  text text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint uq_ingredients_recipe_order unique (recipe_id, sort_order)
);

-- ============================================================
-- Dinh dưỡng
-- ============================================================

create table if not exists nutrition_estimates (
  id uuid primary key default gen_random_uuid(),
  dish_id uuid references dishes (id),
  recipe_id uuid references recipes (id),
  source_item_name text not null,
  basis text not null check (basis in ('per_100g', 'per_serving')),
  serving_g numeric check (serving_g > 0),
  serving_label text,
  kcal numeric check (kcal >= 0),
  protein_g numeric check (protein_g >= 0),
  carb_g numeric check (carb_g >= 0),
  fat_g numeric check (fat_g >= 0),
  source_code text not null references sources (code),
  method text not null,
  confidence text not null check (confidence in ('cao', 'trung_binh_uoc_tinh')),
  note text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint uq_nutrition_dish_basis_source unique (dish_id, basis, source_code),
  constraint uq_nutrition_recipe_basis_source unique (recipe_id, basis, source_code)
);
create index if not exists idx_nutrition_basis on nutrition_estimates (basis);
create index if not exists idx_nutrition_source on nutrition_estimates (source_code);

-- ============================================================
-- Chế độ ăn
-- ============================================================

-- Ngưỡng là QUYẾT ĐỊNH SẢN PHẨM (không lấy từ nguồn dinh dưỡng nào), lưu ở đây
-- để đổi ngưỡng không phải sửa view.
create table if not exists diet_modes (
  code text primary key,
  name_vi text not null,
  description_vi text not null,
  rule_vi text not null,
  sort_order int not null,
  max_kcal_per_serving numeric,
  max_fat_g numeric,
  excluded_cooking_methods text[],
  min_protein_g numeric,
  min_protein_per_100kcal numeric,
  max_carb_g numeric,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Ăn chay KHÔNG tính từ số liệu dinh dưỡng: lưu riêng theo tên món / công thức.
create table if not exists dish_vegetarian (
  dish_id uuid primary key references dishes (id) on delete cascade,
  is_vegetarian boolean,
  basis text,
  confirmed_by_recipe boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- ============================================================
-- Thực đơn tuần mẫu
-- ============================================================

create table if not exists weekly_menu (
  id uuid primary key default gen_random_uuid(),
  day_of_week int not null check (day_of_week between 1 and 7),
  day_name_vi text not null,
  meal text not null references meals (code),
  meal_text text not null,
  note text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint uq_weekly_day_meal unique (day_of_week, meal)
);

-- Một bữa có thể gồm nhiều món ("Cơm: cá kho tộ, canh chua").
-- dish_id / recipe_id chỉ điền khi cụm tên khớp DUY NHẤT 1 món; còn lại NULL.
create table if not exists weekly_menu_items (
  id uuid primary key default gen_random_uuid(),
  weekly_menu_id uuid not null references weekly_menu (id) on delete cascade,
  sort_order int not null,
  item_text text not null,
  dish_id uuid references dishes (id),
  recipe_id uuid references recipes (id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint uq_weekly_item_order unique (weekly_menu_id, sort_order)
);
create index if not exists idx_weekly_items_dish on weekly_menu_items (dish_id);

-- ============================================================
-- Trigger updated_at cho mọi bảng
-- ============================================================

do $$
declare t text;
begin
  foreach t in array array[
    'regions', 'cooking_methods', 'meals', 'time_bands', 'occasions', 'dish_types', 'sources',
    'dishes', 'dish_cooking_methods', 'dish_meals', 'dish_occasions', 'recipes', 'ingredients',
    'nutrition_estimates', 'diet_modes', 'dish_vegetarian', 'weekly_menu', 'weekly_menu_items'
  ] loop
    execute format(
      'create or replace trigger trg_%1$s_updated_at before update on public.%1$I '
      'for each row execute function public.set_updated_at()', t);
  end loop;
end $$;

-- ============================================================
-- View: khoảng thời gian nấu (tính từ recipes.total_minutes)
-- ============================================================

create or replace view dish_time_band
with (security_invoker = true) as
select r.dish_id, r.total_minutes, tb.code as time_band_code, tb.name_vi as time_band_name_vi
from public.recipes r
join public.time_bands tb
  on r.total_minutes >= tb.min_minutes
 and (tb.max_minutes is null or r.total_minutes <= tb.max_minutes)
where r.dish_id is not null and r.total_minutes is not null;

-- ============================================================
-- View: đánh giá chế độ ăn cho từng món (thay bảng tag lưu cứng)
-- 4 chế độ dinh dưỡng CHỈ tính từ số liệu theo khẩu phần của Bảng TPTP VN
-- (fao_vn_fct_2017 ưu tiên, sau đó calocalo_vn_fct). Không dùng fitarchive_usda.
-- ============================================================

create or replace view dish_diet_eval
with (security_invoker = true) as
with vn as (
  select distinct on (n.dish_id)
    n.dish_id, n.kcal, n.protein_g, n.carb_g, n.fat_g
  from public.nutrition_estimates n
  where n.basis = 'per_serving'
    and n.dish_id is not null
    and n.source_code in ('fao_vn_fct_2017', 'calocalo_vn_fct')
  order by n.dish_id, (n.source_code = 'fao_vn_fct_2017') desc
),
ref_only as (
  select distinct n.dish_id
  from public.nutrition_estimates n
  where n.basis = 'per_serving'
    and n.dish_id is not null
    and n.source_code not in ('fao_vn_fct_2017', 'calocalo_vn_fct')
),
methods as (
  select dish_id, array_agg(cooking_method_code) as codes
  from public.dish_cooking_methods
  group by dish_id
),
base as (
  select d.id as dish_id, m.*, vn.dish_id is not null as has_vn,
         vn.kcal, vn.protein_g, vn.carb_g, vn.fat_g,
         ro.dish_id is not null as has_ref_only,
         dm.codes as cooking_codes,
         v.is_vegetarian, v.basis as veg_basis
  from public.dishes d
  cross join public.diet_modes m
  left join vn on vn.dish_id = d.id
  left join ref_only ro on ro.dish_id = d.id
  left join methods dm on dm.dish_id = d.id
  left join public.dish_vegetarian v on v.dish_id = d.id
),
eval as (
  select dish_id, code as diet_mode_code, has_vn, has_ref_only,
    case code
      when 'binh_thuong' then true
      when 'an_chay' then is_vegetarian
      when 'an_kieng_giam_can' then case when has_vn then kcal <= max_kcal_per_serving end
      when 'it_dau_mo' then case
        when not has_vn or fat_g is null then null
        when fat_g > max_fat_g then false
        when cooking_codes && excluded_cooking_methods then false
        when cooking_codes is null then null
        else true end
      when 'giau_protein' then case when has_vn and kcal > 0
        then protein_g >= min_protein_g and protein_g / kcal * 100 >= min_protein_per_100kcal end
      when 'it_tinh_bot' then case when has_vn then carb_g <= max_carb_g end
    end as is_applicable,
    veg_basis, cooking_codes, fat_g, max_fat_g
  from base
)
select dish_id, diet_mode_code, is_applicable,
  case when is_applicable is null then 'chua_co_du_lieu' else 'da_xac_dinh' end as status,
  case
    when diet_mode_code = 'binh_thuong' then 'Quy tắc: không loại trừ món nào'
    when diet_mode_code = 'an_chay' then veg_basis
    when has_vn and diet_mode_code = 'it_dau_mo' and is_applicable is null
         and fat_g is not null and cooking_codes is null then 'Chưa có cách nấu'
    when has_vn then 'Số liệu theo khẩu phần từ Bảng TPTP VN; ngưỡng trong diet_modes'
    when has_ref_only then 'Chờ cân khẩu phần, tính theo Bảng TPTP VN (QĐ1=B)'
    else 'Chưa có số liệu dinh dưỡng theo khẩu phần để kiểm tra quy tắc — không đoán.'
  end as basis
from eval;

-- ============================================================
-- Tìm kiếm món theo tên, không dấu (RPC: supabase.rpc('search_dishes', { q }))
-- ============================================================

create or replace function public.search_dishes(q text)
returns setof public.dishes
language sql
stable
set search_path = ''
as $$
  select d.*
  from public.dishes d
  where d.is_published
    and public.f_unaccent(lower(d.name)) like '%' || public.f_unaccent(lower(coalesce(q, ''))) || '%'
  order by d.name
$$;

-- ============================================================
-- Hàm mục tiêu protein (tham khảo, KHÔNG phải chỉ định y tế).
-- target_g_per_kg: 0.93 = nhu cầu khuyến nghị cho người bình thường (Viện Dinh dưỡng 2026);
-- 1.6 = mốc tham khảo cho người tập kháng lực. Không duy trì >2 g/kg/ngày dài hạn.
-- ============================================================

create or replace function public.protein_target_grams(weight_kg numeric, target_g_per_kg numeric)
returns numeric
language sql
immutable
set search_path = ''
as $$
  select round(weight_kg * target_g_per_kg, 1)
$$;

create or replace function public.protein_remaining_grams(weight_kg numeric, target_g_per_kg numeric, eaten_g numeric)
returns numeric
language sql
immutable
set search_path = ''
as $$
  select greatest(0, round(weight_kg * target_g_per_kg - coalesce(eaten_g, 0), 1))
$$;

-- ============================================================
-- RLS: đọc công khai cho anon + authenticated, KHÔNG có policy ghi.
-- Ghi dữ liệu chỉ qua service_role (server/admin) hoặc Supabase Dashboard.
-- ============================================================

do $$
declare t text;
begin
  foreach t in array array[
    'regions', 'cooking_methods', 'meals', 'time_bands', 'occasions', 'dish_types', 'sources',
    'dishes', 'dish_cooking_methods', 'dish_meals', 'dish_occasions', 'recipes', 'ingredients',
    'nutrition_estimates', 'diet_modes', 'dish_vegetarian', 'weekly_menu', 'weekly_menu_items'
  ] loop
    execute format('alter table public.%I enable row level security', t);
    if not exists (
      select 1 from pg_policies
      where schemaname = 'public' and tablename = t and policyname = 'public_read_' || t
    ) then
      execute format(
        'create policy %I on public.%I for select to anon, authenticated using (true)',
        'public_read_' || t, t);
    end if;
  end loop;
end $$;
