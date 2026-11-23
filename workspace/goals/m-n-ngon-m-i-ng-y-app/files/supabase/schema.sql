-- Món Ngon Mỗi Ngày — schema.sql (Postgres / Supabase)
-- Nguồn chuẩn: mon-ngon-90-mon-data.json (kịch bản 15 trang).
-- 90 món = Bắc 30 / Trung 30 / Nam 30, chỉ 3 miền. Không có Tây Nguyên,
-- không có món toàn quốc, không có Biển & Đảo trong 90 món.
-- Chỉ 6 món trong 90 có công thức đầy đủ; 84 món còn lại chỉ có tên,
-- trạng thái 'dang_bien_tap', không bịa nguyên liệu / thời gian / dinh dưỡng.
-- Bộ filter ĐÚNG (sửa theo ảnh demo sai ngày 2026-11-23):
--   miền: Bac / Trung / Nam
--   cách nấu: mon_nuoc, kho, canh, nuong, chien_ran, goi_cuon, lau, hap_luoc, xao
--     ("Nhanh < 30 phút" KHÔNG phải cách nấu -> filter thời gian riêng)
--   bữa: sang, trua, toi, an_nhe ("Cuối tuần" KHÔNG phải bữa -> tag dịp)
--   chế độ ăn: binh_thuong, an_chay, an_kieng_giam_can, it_dau_mo, giau_protein, it_tinh_bot
--   thời gian: duoi_30, 30_60, tren_60 (chỉ khi có công thức đầy đủ)
--   dịp: cuoi_tuan_dai_khach (chỉ Lẩu mắm, theo thực đơn 7 ngày mẫu)
-- Lệnh 1 (2026-11-23): nguồn dinh dưỡng chuẩn duy nhất là Bảng Thành phần Thực phẩm
--   Việt Nam (QĐ1=B); FitArchive chỉ tham khảo. Không còn công thức nào ngoài 90 món.
--   Thêm recipe_id (nullable) cho nutrition_estimates và weekly_menu; check region/in_90 cho recipes.

create extension if not exists "pgcrypto";

create table if not exists sources (
  code text primary key,
  name text not null,
  note text,
  url text,
  created_at timestamptz not null default now()
);

create table if not exists dishes (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  name text not null,
  region text not null check (region in ('Bac', 'Trung', 'Nam')),
  cooking_method text check (cooking_method in
    ('mon_nuoc', 'kho', 'canh', 'nuong', 'chien_ran', 'goi_cuon', 'lau', 'hap_luoc', 'xao')),
  meal text check (meal in ('sang', 'trua', 'toi', 'an_nhe')),
  time_band text check (time_band in ('duoi_30', '30_60', 'tren_60')),
  occasion text check (occasion in ('cuoi_tuan_dai_khach')),
  has_full_recipe boolean not null default false,
  status text not null check (status in ('co_cong_thuc', 'dang_bien_tap'))
    default 'dang_bien_tap',
  created_at timestamptz not null default now()
);
create index if not exists idx_dishes_region on dishes (region);
create index if not exists idx_dishes_slug on dishes (slug);
create index if not exists idx_dishes_cooking on dishes (cooking_method);
create index if not exists idx_dishes_meal on dishes (meal);
create index if not exists idx_dishes_time_band on dishes (time_band);
create index if not exists idx_dishes_status on dishes (status);

create table if not exists recipes (
  id uuid primary key default gen_random_uuid(),
  dish_id uuid references dishes (id),
  dish_name text not null,
  region text not null check (region in ('Bac', 'Trung', 'Nam') or region is null),
  in_90 boolean not null default true,
  servings_text text,
  time_text text,
  ingredients_text text,
  steps_text text,
  tip text,
  source_code text not null default 'kich_ban_15_trang' references sources (code),
  created_at timestamptz not null default now(),
  constraint uq_recipes_dish unique (dish_id),
  constraint ck_recipes_in_90 check (in_90 = (dish_id is not null))
);
create index if not exists idx_recipes_dish on recipes (dish_id);

create table if not exists ingredients (
  id uuid primary key default gen_random_uuid(),
  recipe_id uuid not null references recipes (id) on delete cascade,
  sort_order int not null,
  text text not null,
  created_at timestamptz not null default now(),
  constraint uq_ingredients_recipe_order unique (recipe_id, sort_order)
);
create index if not exists idx_ingredients_recipe on ingredients (recipe_id);

create table if not exists nutrition_estimates (
  id uuid primary key default gen_random_uuid(),
  dish_id uuid references dishes (id),
  recipe_id uuid references recipes (id),
  dish_name text not null,
  basis text not null check (basis in ('per_100g', 'per_serving')),
  serving_g numeric,
  serving_label text,
  kcal numeric,
  protein_g numeric,
  carb_g numeric,
  fat_g numeric,
  source_code text not null references sources (code),
  method text not null,
  confidence text not null check (confidence in ('cao', 'trung_binh_uoc_tinh')),
  note text,
  created_at timestamptz not null default now()
);
create index if not exists idx_nutrition_dish on nutrition_estimates (dish_id);
create index if not exists idx_nutrition_basis on nutrition_estimates (basis);

create table if not exists diet_modes (
  code text primary key,
  name_vi text not null,
  description_vi text not null,
  rule_vi text not null,
  created_at timestamptz not null default now()
);

create table if not exists dish_diet_tags (
  id uuid primary key default gen_random_uuid(),
  dish_id uuid not null references dishes (id) on delete cascade,
  diet_mode_code text not null references diet_modes (code),
  is_applicable boolean,
  status text not null check (status in ('da_xac_dinh', 'chua_co_du_lieu'))
    default 'chua_co_du_lieu',
  basis text,
  created_at timestamptz not null default now(),
  constraint uq_dish_diet unique (dish_id, diet_mode_code)
);
create index if not exists idx_dish_diet_dish on dish_diet_tags (dish_id);
create index if not exists idx_dish_diet_mode on dish_diet_tags (diet_mode_code);
create index if not exists idx_dish_diet_applicable on dish_diet_tags (diet_mode_code, is_applicable);

create table if not exists weekly_menu (
  id uuid primary key default gen_random_uuid(),
  day_of_week int not null check (day_of_week between 1 and 7),
  day_name_vi text not null,
  meal text not null check (meal in ('sang', 'trua', 'toi')),
  meal_text text not null,
  dish_id uuid references dishes (id),
  recipe_id uuid references recipes (id),
  note text,
  created_at timestamptz not null default now(),
  constraint uq_weekly_day_meal unique (day_of_week, meal)
);
create index if not exists idx_weekly_day on weekly_menu (day_of_week);

-- Hàm tính mục tiêu protein (tham khảo, KHÔNG phải chỉ định y tế).
-- target_g_per_kg: 0.93 = nhu cầu khuyến nghị cho người bình thường (Viện Dinh dưỡng 2026);
-- 1.6 = mốc tham khảo cho người tập kháng lực (tổng hợp nghiên cứu: khối nạc không tăng thêm
-- đáng kể khi vượt ~1.6 g/kg/ngày). Không duy trì >2 g/kg/ngày dài hạn.
create or replace function protein_target_grams(weight_kg numeric, target_g_per_kg numeric)
returns numeric language sql immutable as $$
  select round(weight_kg * target_g_per_kg, 1)
$$;

create or replace function protein_remaining_grams(weight_kg numeric, target_g_per_kg numeric, eaten_g numeric)
returns numeric language sql immutable as $$
  select greatest(0, round(weight_kg * target_g_per_kg - coalesce(eaten_g, 0), 1))
$$;

-- RLS: đọc công khai, không ghi công khai. Ghi chỉ qua service_role / admin.
alter table sources enable row level security;
alter table dishes enable row level security;
alter table recipes enable row level security;
alter table ingredients enable row level security;
alter table nutrition_estimates enable row level security;
alter table diet_modes enable row level security;
alter table dish_diet_tags enable row level security;
alter table weekly_menu enable row level security;

do $$ begin
  if not exists (select 1 from pg_policies where tablename = 'dishes' and policyname = 'public_read_dishes') then
    create policy public_read_dishes on dishes for select using (true);
  end if;
  if not exists (select 1 from pg_policies where tablename = 'recipes' and policyname = 'public_read_recipes') then
    create policy public_read_recipes on recipes for select using (true);
  end if;
  if not exists (select 1 from pg_policies where tablename = 'ingredients' and policyname = 'public_read_ingredients') then
    create policy public_read_ingredients on ingredients for select using (true);
  end if;
  if not exists (select 1 from pg_policies where tablename = 'nutrition_estimates' and policyname = 'public_read_nutrition') then
    create policy public_read_nutrition on nutrition_estimates for select using (true);
  end if;
  if not exists (select 1 from pg_policies where tablename = 'diet_modes' and policyname = 'public_read_diet_modes') then
    create policy public_read_diet_modes on diet_modes for select using (true);
  end if;
  if not exists (select 1 from pg_policies where tablename = 'dish_diet_tags' and policyname = 'public_read_dish_diet_tags') then
    create policy public_read_dish_diet_tags on dish_diet_tags for select using (true);
  end if;
  if not exists (select 1 from pg_policies where tablename = 'weekly_menu' and policyname = 'public_read_weekly_menu') then
    create policy public_read_weekly_menu on weekly_menu for select using (true);
  end if;
  if not exists (select 1 from pg_policies where tablename = 'sources' and policyname = 'public_read_sources') then
    create policy public_read_sources on sources for select using (true);
  end if;
end $$;
