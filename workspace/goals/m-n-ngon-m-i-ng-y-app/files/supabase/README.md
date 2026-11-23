# Món Ngon Mỗi Ngày — Gói dữ liệu Supabase

Gói dữ liệu chuẩn để deploy lên Supabase trước, rồi web và app cùng dùng chung một nguồn. **Không làm lại demo web trong gói này.**

> **Nguyên tắc của gói này:** chỉ đưa số liệu đã kiểm chứng. Món nào chưa có công thức thì để `status = 'dang_bien_tap'`, không bịa nguyên liệu, thời gian hay dinh dưỡng.

> **Kiến trúc cho web/app:** tách rõ data / domain / presentation (MVC hoặc Clean Architecture). Web/app chỉ truy cập Supabase qua lớp data (repository); không gọi Supabase client hay SQL trực tiếp trong UI. Nhãn filter lấy từ các bảng tra cứu trong DB, không viết cứng ở UI.

## 1. Trong gói có gì

Thư mục: `workspace/goals/m-n-ngon-m-i-ng-y-app/files/supabase/`

| File | Nội dung |
|---|---|
| `schema.sql` | Schema Postgres 15+/Supabase, **cài mới** (thiết kế Lệnh 2): 18 bảng, 2 view, 5 hàm, RLS đọc công khai — không ghi công khai. Xem danh sách bên dưới. |
| `mon-ngon-supabase-data.json` | **Nguồn gốc duy nhất** của dữ liệu. Mỗi khóa cấp 1 là một bảng; tên trường trùng đúng tên cột DB. |
| `seed.sql` | INSERT cho toàn bộ dữ liệu. **Sinh tự động từ JSON**, không sửa tay. Chạy sau `schema.sql`. Dùng `ON CONFLICT DO NOTHING` nên chạy lại được. |
| `dishes.csv` | 90 món, sinh tự động từ JSON, UTF-8. |
| `nutrition.csv` | 21 dòng dinh dưỡng, sinh tự động từ JSON, UTF-8. |
| `scripts/build_from_json.py` | Sinh lại `seed.sql`, `dishes.csv`, `nutrition.csv` từ JSON: `python scripts/build_from_json.py`. |
| `scripts/check_data.py` | Kiểm chứng toàn bộ gói (PASS/FAIL): `python scripts/check_data.py`. Cần `pip install pglast`. Đặt `PGTEST_DSN` tới một database Postgres 15+ trống để chạy thật schema + seed (không dùng Supabase thật). |
| `README.md` | File này. |
| Nguồn chuẩn (không sửa) | `../mon-ngon-90-mon-data.json` — 90 món đã đếm đủ Bắc 30 / Trung 30 / Nam 30. |

### Bảng, view và hàm trong `schema.sql`

- **Bảng tra cứu** (`code`, `name_vi`, `sort_order`) — web/app render chip filter thẳng từ đây: `regions` (3 miền), `cooking_methods` (9 cách nấu), `meals` (4 bữa), `time_bands` (3 khoảng thời gian, có `min_minutes`/`max_minutes`), `occasions` (1 dịp), `dish_types` (4 loại món, chưa món nào được gán). Mọi cột mã ở bảng khác đều có khóa ngoại tới các bảng này.
- **Món và công thức:** `dishes`, `recipes`, `ingredients`.
- **Bảng nối (một món nhiều giá trị):** `dish_cooking_methods`, `dish_meals`, `dish_occasions`.
- **Dinh dưỡng và chế độ ăn:** `nutrition_estimates`, `sources`, `diet_modes` (có cột ngưỡng), `dish_vegetarian`.
- **Thực đơn tuần:** `weekly_menu` (21 bữa) và `weekly_menu_items` (một bữa có thể gồm nhiều món).
- **View:** `dish_diet_eval` (đánh giá 6 chế độ ăn cho từng món, tính từ số liệu + ngưỡng), `dish_time_band` (khoảng thời gian tính từ `recipes.total_minutes`). Cả hai `security_invoker = true` để RLS áp dụng.
- **Hàm:** `search_dishes(q)` (tìm tên món không dấu), `f_unaccent(text)`, `set_updated_at()` (trigger), `protein_target_grams()`, `protein_remaining_grams()`. Mọi hàm đặt `search_path = ''`.
- **Cột mới cho web/app:** `dishes.dish_type`, `locality`, `difficulty`, `image_url`, `description`, `is_published`; `recipes.total_minutes`, `servings`, `recipe_source`, `source_url`, `source_accessed_date`, `recipe_status`; `updated_at` (tự cập nhật bằng trigger) ở mọi bảng. Các cột chưa có nguồn đều để `NULL` — **không lấy từ web demo**.

### Số lượng đã kiểm chứng

- **Món: 90** — Bắc 30 / Trung 30 / Nam 30. Không có Tây Nguyên, không có món toàn quốc, không có Biển & Đảo trong 90 món. Cả 90 món `is_published = true`.
- **Trạng thái món:** `co_cong_thuc` 6, `dang_bien_tap` 84, `tham_khao_online` 0.
- **Công thức: 6** — Phở bò, Bún chả, Bún bò Huế, Mì Quảng, Hủ tiếu Nam Vang, Cơm tấm sườn bì chả. Không có công thức nào ngoài 90 món. Cả 6 có `recipe_source = 'Kịch bản 15 trang Món Ngon Mỗi Ngày (nguồn nội bộ)'`, `recipe_status = NULL` (kịch bản không ghi đã nấu thử hay chưa).
- **Nguyên liệu đã tách dòng: 50 dòng** — tách từ chuỗi nguyên liệu trong kịch bản bằng dấu `;`, không thêm/bớt nguyên liệu.
- **Dinh dưỡng: 21 dòng** — 8 dòng theo 100 g (Bảng TPTP VN qua CaloCalo) + 13 dòng theo khẩu phần (FitArchive, **chỉ tham khảo**) — xem mục 2.
- **Cách nấu: 49 dòng trên 46 món** (3 món có 2 cách nấu). **Bữa: 27 món. Dịp: 1 món** (Lẩu mắm). **Thời gian: 6 món** (chỉ món có công thức). Món chưa phân loại không có dòng trong bảng nối — xem mục 3.
- **Chế độ ăn:** 6 chế độ × 90 món = 540 dòng trong view `dish_diet_eval`: **149 đã xác định** (90 `binh_thuong` + 59 `an_chay` = false), **391 chưa có dữ liệu** — xem mục 4.
- **Thực đơn tuần mẫu: 21 bữa, 27 món** — 21 món nối được với một món trong 90, 6 món không nối (xem mục 3.2).

## 2. Nguồn số liệu — chỉ dùng những nguồn này

### 2.1. Món ăn và công thức — kịch bản 15 trang (nguồn nội bộ)

Kịch bản 15 trang Món Ngon Mỗi Ngày: danh mục 90 món (trang 8), 7 công thức mẫu (trang 9–12), thực đơn 7 ngày (trang 13), bản đồ tính năng (trang 6), lộ trình (trang 14–15).

### 2.2. Dinh dưỡng theo 100 g — Bảng Thành phần Thực phẩm Việt Nam, Viện Dinh dưỡng Quốc gia (Bộ Y tế), qua CaloCalo

> **QĐ1 = B (chốt 2026-11-23):** Bảng Thành phần Thực phẩm Việt Nam là **nguồn dinh dưỡng chuẩn duy nhất** để tính tag chế độ ăn và để hiển thị. 8 dòng dưới đây đang lấy qua CaloCalo, chưa đối chiếu với bản gốc FAO 2017 — cần đối chiếu (mã thực phẩm, số trang) trước khi web hiển thị.

- Nguồn gốc bảng: Vietnamese Food Composition Table, National Institute of Nutrition (Ministry of Health, Vietnam) — https://www.fao.org/food-composition/tables-and-databases/detail/%28viet-nam--2017%29-vietnamese-food-composition-table/en
- Tra cứu qua CaloCalo: https://calocalo.app/blog/vietnamese-food-calories/
- Mỗi dòng trong `nutrition_estimates` đều ghi `source_code`, `method`, `confidence` và `note`.

| Món (tên trong bảng) | kcal/100 g | Protein | Carb | Béo |
|---|---|---|---|---|
| Phở bò chín | 69 | 4,3 g | 9,6 g | 1,5 g |
| Hủ tiếu Nam Vang | 93 | 5,2 g | 14,4 g | 1,7 g |
| Bún chả | 124 | 4,7 g | 16,2 g | 4,5 g |
| Xôi xéo | 263 | 6,6 g | 47,5 g | 5,2 g |
| Bánh cuốn | 136 | 4,6 g | 16,8 g | 5,7 g |
| Nem rán | 163 | 4,8 g | 15,6 g | 9,0 g |
| Phở cuốn | 138 | 6,9 g | 17,5 g | 4,5 g |
| Bánh mì thập cẩm | 296 | 13,4 g | 21,0 g | 17,7 g |

Lưu ý: “Bánh cuốn” trong bảng được gán cho món “Bánh cuốn Thanh Trì” trong kho. “Bánh mì thập cẩm” **chỉ tham chiếu**, không gán cho món nào (`dish_id = NULL`).

### 2.3. Dinh dưỡng theo khẩu phần — FitArchive, ước tính từ USDA FoodData Central (CHỈ THAM KHẢO)

> **QĐ1 = B:** các dòng FitArchive **chỉ để tham khảo**. Không dùng để tính tag chế độ ăn, không dùng để hiển thị trên web/app. Vì vậy 4 tag dinh dưỡng (`an_kieng_giam_can`, `it_dau_mo`, `giau_protein`, `it_tinh_bot`) hiện đều là `NULL` — chờ cân khẩu phần và tính theo Bảng TPTP VN.

- Nguồn: FitArchive — https://www.fitarchive.app/food-sources/ — “Recipes and adapted portions are FitArchive estimates”.
- Gốc nguyên liệu: USDA FoodData Central (fdc.nal.usda.gov, dữ liệu công cộng CC0).
- **Đây là ước tính, không phải đo phòng lab, sai số ±15–20%** tùy khẩu phần và cách nấu thực tế. Mỗi dòng đều ghi rõ điều này trong cột `method` và `confidence = 'trung_binh_uoc_tinh'`.

| Món | Khẩu phần | kcal | Protein | Carb | Béo |
|---|---|---|---|---|---|
| Phở bò | 1 tô 785 g | 418 | 38 g | 57 g | 4 g |
| Bún chả | 1 phần 382 g | 538 | 30 g | 63 g | 17 g |
| Bún bò Huế | 1 tô 815 g | 571 | 42 g | 61 g | 17 g |
| Mì Quảng gà | 1 tô 532 g | 622 | 41 g | 63 g | 22 g |
| Hủ tiếu Nam Vang | 1 tô 775 g | 542 | 36 g | 67 g | 13 g |
| Cơm tấm sườn | 1 đĩa 395 g | 626 | 36 g | 70 g | 21 g |
| Gỏi cuốn | 1 cuốn 98 g | 147 | 9 g | 21 g | 3 g |
| Cá kho tộ | 1 phần 160 g | 337 | 24 g | 10 g | 22 g |
| Rau muống xào tỏi | 1 đĩa 220 g | 139 | 5 g | 10 g | 10 g |
| Canh chua cá | 1 tô 208 g | 148 | 14 g | 14 g | 4 g |
| Cháo lòng | 1 tô 510 g | 426 | 19 g | 49 g | 16 g |
| Chè ba màu | 1 ly 160 g | 301 | 7 g | 51 g | 9 g |
| Xôi xéo | 1 gói 235 g | 309 | 7 g | 47 g | 11 g |

Lưu ý gán món, ghi trong cột `note` của từng dòng:
- “Mì Quảng gà” (FitArchive) ↔ công thức trong kịch bản là “Mì Quảng gà/tôm thịt”.
- “Cơm tấm sườn” (FitArchive, chỉ sườn) ↔ công thức trong kịch bản là “Cơm tấm sườn bì chả”.
- “Canh chua cá” là món chung, **không gán cho một món cụ thể**: kịch bản có Canh chua cá lóc (Nam) và Canh chua cá dìa (Trung), không có món tên đúng “Canh chua cá”. Dòng này có `dish_id = NULL` trong DB, dùng làm ví dụ tham khảo, không dùng để lọc món.

### 2.4. Hướng dẫn chế độ ăn — chỉ dùng cho quy tắc lọc, không phải tư vấn y tế

- **Viện Dinh dưỡng 2026 — Nhu cầu dinh dưỡng khuyến nghị cho người Việt Nam:** protein ~0,93 g/kg/ngày; không duy trì >2 g/kg/ngày dài hạn; chất béo 20–25% năng lượng; protein tham chiếu ghi nhãn 50 g/ngày.
- **WHO — Healthy diet:** https://www.who.int/news-room/fact-sheets/detail/healthy-diet?swcfpc=1 — carb 45–75%, chất béo <30% (Việt Nam 20–25%), đường tự do <10%, muối <5 g/ngày, rau/củ/quả ≥400 g/ngày.
- **Bộ Y tế — 10 Khuyến nghị dinh dưỡng hợp lý đến năm 2030:** hạn chế đồ chiên rán/đồ ăn nhanh, thực phẩm nhiều mỡ/mặn/ngọt.
- **Mốc 1,6 g/kg/ngày cho người tập kháng lực:** mốc tham khảo từ tổng hợp nghiên cứu — khối nạc không tăng thêm đáng kể khi vượt ~1,6 g/kg/ngày. Đây là mốc tham khảo, không phải chỉ định y tế (xem mục 6).

> **Tuyên bố miễn trừ:** Số liệu dinh dưỡng trong gói này là ước tính tham khảo, không phải tư vấn y tế. Người có bệnh tiểu đường, thận, tim mạch, dị ứng hoặc đang theo chế độ ăn điều trị cần hỏi bác sĩ/chuyên gia dinh dưỡng trước khi áp dụng.

## 3. Bộ filter ĐÚNG — sửa theo ảnh demo sai

### 3.1. Bảng đối chiếu: filter cũ sai ở đâu, filter mới sửa thế nào

| Trục lọc | Ảnh demo cũ (SAI) | Filter đúng trong DB này | Sửa thế nào |
|---|---|---|---|
| **Miền** | Tất cả, Miền Bắc, Miền Trung, Miền Nam, **Tây Nguyên, Khắp cả nước, Biển & Đảo** | Tất cả + 3 dòng của bảng `regions` | **Xóa Tây Nguyên, Khắp cả nước, Biển & Đảo.** Kịch bản chỉ có 3 miền, **không tạo miền thứ 4**. `dishes.region` và `recipes.region` đều có khóa ngoại tới `regions`. |
| **Cách nấu** | …, **Nhanh < 30 phút** | Tất cả + 9 dòng của bảng `cooking_methods` | **Bỏ “Nhanh < 30 phút” khỏi cách nấu** — đó là thời gian. Chuyển sang filter riêng **THỜI GIAN** (bảng `time_bands`). |
| **Bữa** | …, **Cuối tuần** | Tất cả + 4 dòng của bảng `meals` (Ăn sáng, Bữa trưa, Bữa tối, Ăn nhẹ) | **Bỏ “Cuối tuần”** — cuối tuần không phải bữa. Chuyển sang dịp `cuoi_tuan_dai_khach` (bảng `occasions`). |
| **Thời gian** | *(trộn vào cách nấu)* | 3 dòng của bảng `time_bands` | Filter riêng, tính qua view `dish_time_band`. |
| **Chế độ ăn** | *(chưa có)* | 6 dòng của bảng `diet_modes` | Lọc qua view `dish_diet_eval`. |
| **Mô tả kho món** | “14 món có công thức chi tiết” | “6 món có công thức đầy đủ, 84 món công thức đang biên tập” | 84 món còn lại **không có nguyên liệu/cách làm** — UI phải ghi “Công thức đang biên tập”. |

Quy ước lọc kết hợp: chọn nhiều giá trị trong **cùng một trục** là OR, giữa **các trục** là AND. Nên hiện số món trên mỗi chip (query ở mục 7.2) và dòng “X món chưa phân loại” thay vì ẩn các món đó.

### 3.2. Quy tắc gán — chỉ gán khi có căn cứ, còn lại không có dòng

- **Cách nấu (bảng `dish_cooking_methods`, một món có thể nhiều cách nấu):**
  - Khớp theo từ trọn trong tên món: `kho` → `kho`; `xào` → `xao`; `luộc` → `hap_luoc`; `nướng` → `nuong`; `rán`, `chiên`, `xối mỡ` → `chien_ran`.
  - Tên bắt đầu “Canh ” → `canh`; bắt đầu “Lẩu ” → `lau`.
  - Bắt đầu “Gỏi ”/“Nộm ”, có từ “trộn”, có “cuốn bánh tráng”, hoặc Phở cuốn → `goi_cuon`.
  - Bắt đầu Phở (trừ Phở cuốn), Hủ tiếu, Miến, Bún (trừ Bún chả, Bún đậu mắm tôm, Bún thịt nướng) → `mon_nuoc`.
  - Tên khớp 2 cách nấu → gán cả 2: Thịt heo luộc cuốn bánh tráng (`hap_luoc` + `goi_cuon`), Rau luộc kho quẹt (`hap_luoc` + `kho`).
  - Công thức đầy đủ ghi rõ bước nấu: Bún chả → `nuong` (“nướng than”); Cơm tấm → `nuong` (“Nướng sườn”) + `hap_luoc` (“Hấp chả trứng”).
  - Mì Quảng: **tạm thời chưa gán** (QĐ3, công thức vừa xào vừa chan nước nhưn; chưa chốt).
  - Kết quả: 49 dòng trên 46 món; 44 món chưa phân loại.
- **Bữa (bảng `dish_meals`):**
  - (a) Cụm tên món trong thực đơn 7 ngày (trang 13, kể cả trong dòng “Cơm: …”) khớp **duy nhất 1 món** trong 90 → gán đúng bữa đó. Khớp 0 hoặc từ 2 món trở lên → không gán.
  - (b) Món chè/bánh ngọt/trái cây ăn chơi rõ ràng theo tên → `an_nhe` (chè đậu xanh, chè đậu ván, chè ba màu, bánh trôi tàu, bánh da lợn, dừa sáp).
  - Kết quả: 27 món; 63 món chưa phân loại.
- **Thực đơn tuần (bảng `weekly_menu_items`):** tách `meal_text` theo dấu phẩy và dấu “+”, bỏ tiền tố “Cơm: ”. Chỉ nối `dish_id` khi cụm tên khớp duy nhất 1 món trong 90. Không nối: “Bánh mì thịt” (không có trong 90), “canh chua” (khớp Canh chua cá lóc và Canh chua cá dìa), “gà kho gừng” (không có trong 90), “canh rau” và “cháo nhẹ” (chung chung), “Bánh xèo” (khớp 2 món).
- **Thời gian:** lưu số phút ở `recipes.total_minutes` (chỉ món có công thức, lấy từ `time_text` của kịch bản): Phở bò 180 (bản hầm đầy đủ ~3 giờ; bản rút gọn 60 phút ghi trong `time_text`), Bún chả 60, Bún bò Huế 90, Mì Quảng 60, Hủ tiếu Nam Vang 90, Cơm tấm 75. View `dish_time_band` nối với `time_bands`. Hiện **không có món nào dưới 30 phút**.
- **Dịp (bảng `dish_occasions`):** chỉ Lẩu mắm có `cuoi_tuan_dai_khach` — thực đơn 7 ngày mẫu ghi “Lẩu mắm (Nam) — bữa sum họp cuối tuần”.
- **Loại món (`dishes.dish_type`):** bảng tra cứu đã có (`mon_mot_to`, `mon_an_kem_com`, `trang_mieng`, `an_vat`) nhưng **chưa món nào được gán** — chờ quyết định, không đoán.

### 3.3. Sort — chỉ sort được khi món có số liệu

- **Nhiều protein nhất / Ít calo nhất / Ít béo nhất:** sort trên `nutrition_estimates` với `basis = 'per_serving'` và **chỉ nguồn Bảng TPTP VN** (`source_code in ('calocalo_vn_fct','fao_vn_fct_2017')`), dùng `dishes LEFT JOIN` + `NULLS LAST` — món chưa có số liệu xếp cuối và UI phải ghi rõ “chưa có số liệu dinh dưỡng”. Hiện chưa có dòng theo khẩu phần nào từ nguồn này, nên cả 90 món đều “chưa có số liệu”.

### 3.4. Nhãn trạng thái công thức hiển thị trên web/app

| `dishes.status` | Nhãn hiển thị |
|---|---|
| `co_cong_thuc` | Công thức đầy đủ (nguồn ghi ở `recipes.recipe_source`). |
| `tham_khao_online` | “Công thức tham khảo từ `<recipe_source>`, chưa nấu thử”, kèm link `source_url` và ngày truy cập `source_accessed_date`. |
| `dang_bien_tap` | “Công thức đang biên tập”. Không hiện nút nấu từng bước, không hiện nguyên liệu. |

Bảng `recipes` có ràng buộc: `recipe_status = 'tham_khao_online'` thì `recipe_source`, `source_url`, `source_accessed_date` bắt buộc khác `NULL`.

## 4. Chế độ ăn — 6 chế độ, tính bằng view

Tag chế độ ăn **không lưu cứng**: view `dish_diet_eval` (cột `dish_id`, `diet_mode_code`, `is_applicable`, `status`, `basis`) tính trực tiếp từ số liệu + ngưỡng trong `diet_modes`. Khi thêm dòng dinh dưỡng mới, tag tự cập nhật.

| Mã | Tên | Quy tắc | Ngưỡng (cột trong `diet_modes`) |
|---|---|---|---|
| `binh_thuong` | Bình thường | Không loại trừ món nào → luôn `true`. | — |
| `an_chay` | Ăn chay | Lấy từ bảng `dish_vegetarian`, **không phụ thuộc số liệu dinh dưỡng**. `false` khi tên món (theo từ trọn) có: bò, gà, heo, thịt, cá, tôm, cua, ốc, hến, mực, vịt, lòng, sườn, chả, nem, mắm, tré, mọc — hoặc công thức đầy đủ có thịt/cá/hải sản. Chỉ `true` khi có công thức xác nhận; còn lại `NULL`. | — |
| `an_kieng_giam_can` | Ăn kiêng giảm cân | kcal/phần ≤ ngưỡng. | `max_kcal_per_serving` = 450 |
| `it_dau_mo` | Ít dầu mỡ | fat/phần > ngưỡng → `false`; món có cách nấu bị loại → `false`; **chưa có cách nấu → `NULL`**; còn lại → `true`. | `max_fat_g` = 10, `excluded_cooking_methods` = {xao, chien_ran} |
| `giau_protein` | Giàu protein | protein/phần ≥ ngưỡng **và** protein/100 kcal ≥ ngưỡng. | `min_protein_g` = 25, `min_protein_per_100kcal` = 7 |
| `it_tinh_bot` | Ít tinh bột | carb/phần ≤ ngưỡng. | `max_carb_g` = 20 |

- 4 chế độ dinh dưỡng **chỉ tính từ số liệu theo khẩu phần của Bảng TPTP VN** (`fao_vn_fct_2017` ưu tiên, sau đó `calocalo_vn_fct`). **Không dùng `fitarchive_usda`** (QĐ1 = B).
- Các ngưỡng là **quyết định sản phẩm**, không lấy từ nguồn nào ở mục 2.4. Đổi ngưỡng bằng cách sửa `diet_modes`, không cần sửa view.
- Kết quả hiện tại (chạy thật): `binh_thuong` 90 đúng; `an_chay` 59 sai / 31 chưa có dữ liệu / 0 đúng; 4 chế độ dinh dưỡng 90 chưa có dữ liệu. Tổng **149 đã xác định, 391 `chua_co_du_lieu`** — trùng 540/540 dòng với bảng tag lưu cứng của Lệnh 1 (`scripts/check_data.py` kiểm tra).
- `basis` của 12 món trước đây có số liệu FitArchive: “Chờ cân khẩu phần, tính theo Bảng TPTP VN (QĐ1=B)”. 78 món còn lại: “Chưa có số liệu dinh dưỡng theo khẩu phần để kiểm tra quy tắc — không đoán.”
- `an_chay`: Rau muống xào tỏi, Chè ba màu, Xôi xéo đang `NULL` — chưa có công thức xác nhận (ví dụ xôi xéo có thể dùng mỡ hành).

## 5. Deploy lên Supabase

### Bước 1 — Tạo project

1. Vào Supabase Dashboard → New project, chọn region gần nhất (Singapore), đặt database password và lưu lại.
2. Mở **SQL Editor** trong project mới.

### Bước 2 — Chạy schema rồi seed (CÀI MỚI)

`schema.sql` là bản **cài mới**, chạy trên project chưa có bảng nào. Nếu project đã từng chạy `schema.sql` cũ (trước Lệnh 2), phải xóa các bảng cũ trước.

1. Mở file `schema.sql`, copy toàn bộ, dán vào SQL Editor → **Run**. Tạo xong 18 bảng, 2 view, 5 hàm, trigger `updated_at`, RLS và policy đọc cho `anon` + `authenticated`. Bật extension `pg_trgm` và `unaccent` trong schema `extensions`.
2. Mở file `seed.sql`, copy toàn bộ, dán vào SQL Editor → **Run**. Nạp xong 90 món, 6 công thức, 50 dòng nguyên liệu, 21 dòng dinh dưỡng, 49 dòng cách nấu, 27 dòng bữa, 1 dịp, 6 chế độ ăn, 90 dòng ăn chay, 21 bữa + 27 món thực đơn tuần, 7 nguồn và các bảng tra cứu.
3. Chạy lại `schema.sql` hoặc `seed.sql` không tạo trùng (`if not exists`, `or replace`, `ON CONFLICT DO NOTHING`).

### Bước 3 — Import CSV (không khuyến nghị)

`dishes.csv` và `nutrition.csv` chỉ chứa 2 bảng. Các bảng tra cứu, bảng nối, công thức, thực đơn tuần phải nạp bằng `seed.sql`, nên cách nhanh và đúng nhất là chạy `seed.sql`.

### Bước 4 — Kiểm chứng bằng SQL (chạy trong SQL Editor)

```sql
-- 1. Tổng món và theo miền: phải ra 90 / 30 / 30 / 30
select region, count(*) from dishes group by region order by region;
select count(*) as tong_mon from dishes;

-- 2. Công thức: 6; trạng thái món: co_cong_thuc 6, dang_bien_tap 84
select count(*) as tong_cong_thuc from recipes;
select status, count(*) from dishes group by status order by status;

-- 3. Bảng tra cứu: 3 miền, 9 cách nấu, 4 bữa, 3 khoảng thời gian, 1 dịp, 4 loại món
select (select count(*) from regions) mien, (select count(*) from cooking_methods) cach_nau,
       (select count(*) from meals) bua, (select count(*) from time_bands) thoi_gian,
       (select count(*) from occasions) dip, (select count(*) from dish_types) loai_mon;

-- 4. Dinh dưỡng: 21 dòng (per_100g 8, per_serving 13), dòng nào cũng có nguồn + phương pháp + độ tin cậy
select basis, count(*) from nutrition_estimates group by basis order by basis;
select count(*) from nutrition_estimates where source_code is null or method is null or confidence is null;
-- phải ra 0

-- 5. Món chưa có công thức không có thời gian bịa thêm: phải ra 0
select count(*) from dish_time_band t join dishes d on d.id = t.dish_id where d.status = 'dang_bien_tap';

-- 6. Chế độ ăn: 149 đã xác định / 391 chưa có dữ liệu
select status, count(*) from dish_diet_eval group by status order by status;
```

## 6. Mục tiêu protein — bảng tham khảo (không phải bảng DB bắt buộc)

Công thức: **protein mục tiêu (g/ngày) = cân nặng (kg) × mục tiêu (g/kg/ngày)**.

Hàm trong DB: `protein_target_grams(weight_kg, target_g_per_kg)` và `protein_remaining_grams(weight_kg, target_g_per_kg, eaten_g)`.

| Cân nặng | Mức bình thường 0,93 g/kg/ngày | Mức tập kháng lực 1,6 g/kg/ngày | Cảnh báo: không duy trì >2 g/kg/ngày dài hạn |
|---|---|---|---|
| 60 kg | 55,8 g (~56 g) | 96,0 g | >120 g/ngày |
| 70 kg | 65,1 g (~65 g) | 112,0 g | >140 g/ngày |
| 80 kg | 74,4 g (~74 g) | 128,0 g | >160 g/ngày |

Ví dụ chia bữa cho người 70 kg tập kháng lực, mục tiêu 112 g/ngày: chia 3 bữa ≈ 37 g/bữa, chia 4 bữa ≈ 28 g/bữa.

## 7. Web/app dùng dữ liệu thế nào — ví dụ query

Tất cả query dưới đây chạy được trên schema đã tạo (đã chạy thật, kết quả ghi trong chú thích). Web/app gọi chúng **trong lớp data (repository)** — qua Supabase JS client (`supabase.from(...)`, `supabase.rpc(...)`) hoặc view — không gọi từ UI.

### 7.1. Món của ngày (theo ngày thật, không hard-code)

```sql
-- Món của ngày: lấy 3 món theo ngày (xáo theo md5 của slug + ngày).
-- Query này KHÔNG chống lặp: chạy thử 7 ngày 2026-11-23 → 2026-11-29 thì
-- bun-cha xuất hiện 5/7 ngày, vì chỉ có 6 món co_cong_thuc.
-- Logic chống lặp / chọn theo hồ sơ vị thuộc lớp domain của app, không nằm ở DB.
select d.slug, d.name, d.region
from dishes d
where d.status = 'co_cong_thuc' and d.is_published
order by md5(d.slug || to_char(current_date, 'YYYY-MM-DD'))
limit 3;
```

### 7.2. Chip filter từ DB, số món trên mỗi chip, lọc kết hợp

```sql
-- Chip "Cách nấu" kèm số món (làm mờ chip có 0 món)
select c.code, c.name_vi, count(x.dish_id) as so_mon
from cooking_methods c
left join dish_cooking_methods x on x.cooking_method_code = c.code
group by c.code, c.name_vi, c.sort_order
order by c.sort_order;
-- Kết quả thật: mon_nuoc 13, kho 6, canh 5, nuong 4, chien_ran 3, goi_cuon 7, lau 2, hap_luoc 4, xao 5.

-- Số món chưa phân loại (hiển thị dòng "X món chưa phân loại")
select count(*) filter (where not exists (select 1 from dish_cooking_methods x where x.dish_id = d.id)) as chua_co_cach_nau,
       count(*) filter (where not exists (select 1 from dish_meals x where x.dish_id = d.id)) as chua_co_bua
from dishes d;
-- Kết quả thật: 44 món chưa có cách nấu, 63 món chưa có bữa.
```

```sql
-- Lọc kết hợp: miền Bắc + món nước + ăn sáng + bình thường
-- (cùng trục = OR thì dùng "= any(array[...])"; khác trục = AND)
select d.slug, d.name
from dishes d
where d.is_published
  and d.region = 'Bac'
  and exists (select 1 from dish_cooking_methods x where x.dish_id = d.id and x.cooking_method_code = any(array['mon_nuoc']))
  and exists (select 1 from dish_meals x where x.dish_id = d.id and x.meal_code = any(array['sang']))
  and exists (select 1 from dish_diet_eval e where e.dish_id = d.id and e.diet_mode_code = 'binh_thuong' and e.is_applicable)
order by d.name;
-- Kết quả thật: bun-thang (Bún thang), pho-bo (Phở bò), pho-ga (Phở gà).
-- Nếu đổi chế độ ăn thành an_kieng_giam_can: 0 món — 4 chế độ dinh dưỡng đều chưa có
-- dữ liệu (QĐ1=B). Món chưa có số liệu không qua filter chế độ ăn — đúng quy tắc "không đoán".
```

```sql
-- Lọc theo thời gian (filter riêng, không phải cách nấu)
select d.slug, d.name, t.total_minutes, t.time_band_code
from dish_time_band t
join dishes d on d.id = t.dish_id
where t.time_band_code = 'tren_60'
order by t.total_minutes;
-- Kết quả thật: com-tam-suon-bi-cha 75, bun-bo-hue 90, hu-tieu-nam-vang 90, pho-bo 180.
-- 30_60: bun-cha 60, mi-quang-ga-tom-thit 60. duoi_30: 0 món.
```

```sql
-- Lọc theo dịp cuối tuần / đãi khách
select d.slug, d.name
from dishes d
join dish_occasions o on o.dish_id = d.id
where o.occasion_code = 'cuoi_tuan_dai_khach';
-- Kết quả thật: 1 dòng — lau-mam | Lẩu mắm.
```

```sql
-- Tìm kiếm không dấu (RPC: supabase.rpc('search_dishes', { q: 'pho bo' }))
select slug, name from search_dishes('pho bo');
-- Kết quả thật: pho-bo | Phở bò.
```

### 7.3. Thực đơn tuần mẫu

```sql
select w.day_of_week, w.day_name_vi, w.meal, w.meal_text,
       i.sort_order, i.item_text, d.slug, d.status
from weekly_menu w
join weekly_menu_items i on i.weekly_menu_id = w.id
left join dishes d on d.id = i.dish_id
order by w.day_of_week,
  case w.meal when 'sang' then 1 when 'trua' then 2 when 'toi' then 3 end,
  i.sort_order;
-- Kết quả thật: 27 dòng; 21 dòng có slug, 6 dòng slug NULL (xem mục 3.2).
-- Ví dụ Thứ 2 trưa "Cơm: cá kho tộ, canh chua" → 2 dòng: cá kho tộ → ca-kho-to; canh chua → NULL.
```

### 7.4. Sort: nhiều protein nhất / ít calo nhất / ít béo nhất (món chưa có số liệu xếp cuối)

Chỉ dùng nguồn Bảng TPTP VN (QĐ1 = B). Dùng `dishes LEFT JOIN` để món chưa có số liệu **vẫn xuất hiện** và xếp cuối.

```sql
-- Nhiều protein nhất (theo khẩu phần)
select d.name, n.protein_g, n.kcal, n.serving_label
from dishes d
left join nutrition_estimates n on n.dish_id = d.id and n.basis = 'per_serving'
  and n.source_code in ('calocalo_vn_fct', 'fao_vn_fct_2017')
order by n.protein_g desc nulls last, d.name;

-- Ít calo nhất
select d.name, n.kcal, n.protein_g
from dishes d
left join nutrition_estimates n on n.dish_id = d.id and n.basis = 'per_serving'
  and n.source_code in ('calocalo_vn_fct', 'fao_vn_fct_2017')
order by n.kcal asc nulls last, d.name;

-- Ít béo nhất
select d.name, n.fat_g, n.kcal
from dishes d
left join nutrition_estimates n on n.dish_id = d.id and n.basis = 'per_serving'
  and n.source_code in ('calocalo_vn_fct', 'fao_vn_fct_2017')
order by n.fat_g asc nulls last, d.name;
-- Kết quả thật với dữ liệu hiện tại: 90 dòng, cả 90 món đều chưa có số liệu
-- theo khẩu phần từ Bảng TPTP VN (protein_g/kcal/fat_g = NULL).
-- UI phải hiển thị "chưa có số liệu dinh dưỡng" cho các món này.
```

### 7.5. Ví dụ 1 — Người giảm cân

Quy tắc: lọc `it_dau_mo` + `an_kieng_giam_can` trên view `dish_diet_eval`.

```sql
select d.name, n.kcal, n.protein_g, n.fat_g, n.serving_label
from dishes d
join dish_diet_eval e1 on e1.dish_id = d.id and e1.diet_mode_code = 'it_dau_mo' and e1.is_applicable
join dish_diet_eval e2 on e2.dish_id = d.id and e2.diet_mode_code = 'an_kieng_giam_can' and e2.is_applicable
left join nutrition_estimates n on n.dish_id = d.id and n.basis = 'per_serving'
  and n.source_code in ('calocalo_vn_fct', 'fao_vn_fct_2017')
order by n.kcal asc nulls last;
-- Kết quả thật với dữ liệu hiện tại: 0 dòng — chưa có số liệu theo khẩu phần
-- từ Bảng TPTP VN, nên chưa món nào được xác định "ít dầu mỡ" hay "ăn kiêng".
```

Số liệu FitArchive (mục 2.3) chỉ để tham khảo, **không dùng để trả lời ví dụ này và không hiển thị**.

### 7.6. Ví dụ 2 — Người tập gym cần protein

Mốc tham khảo: người bình thường ~0,93 g/kg/ngày (Viện Dinh dưỡng 2026); người tập kháng lực ~1,6 g/kg/ngày là mốc mà tổng hợp nghiên cứu thấy khối nạc không tăng thêm đáng kể khi vượt qua. Đây là mốc tham khảo, không phải chỉ định y tế.

Ví dụ tính: người **70 kg** tập kháng lực → 70 × 1,6 = **112 g protein/ngày**, chia 3–4 bữa ≈ 28–37 g/bữa.

```sql
-- Mục tiêu protein của một người 70 kg, mốc 1.6
select protein_target_grams(70, 1.6) as protein_muc_tieu_g_ngay;
-- Kết quả thật: 112.0

-- Protein còn thiếu trong ngày nếu đã ăn 40 g
select protein_remaining_grams(70, 1.6, 40) as protein_con_thieu_g;
-- Kết quả thật: 72.0

-- Món vừa giàu protein vừa ít dầu mỡ (theo view dish_diet_eval)
select d.name, n.protein_g, n.fat_g, n.kcal
from dishes d
join dish_diet_eval e1 on e1.dish_id = d.id and e1.diet_mode_code = 'giau_protein' and e1.is_applicable
join dish_diet_eval e2 on e2.dish_id = d.id and e2.diet_mode_code = 'it_dau_mo' and e2.is_applicable
left join nutrition_estimates n on n.dish_id = d.id and n.basis = 'per_serving'
  and n.source_code in ('calocalo_vn_fct', 'fao_vn_fct_2017')
order by n.protein_g desc nulls last;
-- Kết quả thật với dữ liệu hiện tại: 0 dòng — tag giau_protein và it_dau_mo đều NULL
-- cho tới khi có số liệu theo khẩu phần từ Bảng TPTP VN.
```

## 8. Chưa có trong dữ liệu — việc cần làm tiếp (nấu thử và chuẩn hóa)

1. **84 món chưa có công thức** sẽ được bổ sung công thức THAM KHẢO từ nguồn uy tín trên mạng (ưu tiên nguồn Việt Nam có tác giả, nhà xuất bản hoặc trang nấu ăn uy tín), ghi rõ tên nguồn, URL và ngày truy cập. Chỉ dùng danh sách nguyên liệu; các bước được diễn đạt lại, không chép nguyên văn. Trạng thái 'tham_khao_online' = chưa nấu thử. Sau khi có công thức tham khảo mới tính dinh dưỡng theo Bảng Thành phần Thực phẩm Việt Nam. Nấu thử là bước sau, khi đó đổi sang 'da_nau_thu'. Món chưa tìm được nguồn uy tín vẫn để NULL.
2. **Dinh dưỡng chuẩn chưa có.** Theo QĐ1 = B, chỉ Bảng Thành phần Thực phẩm Việt Nam được dùng để tính tag và hiển thị. Hiện chỉ có 8 dòng theo 100 g (qua CaloCalo, cần đối chiếu bản gốc FAO 2017) và chưa có dòng theo khẩu phần nào từ nguồn này. Dinh dưỡng theo khẩu phần sẽ tính từ nguyên liệu có khối lượng rõ ràng — không điền số ước đoán tay.
3. **Cách nấu / bữa / thời gian còn thiếu.** Hiện gán được 46 món có cách nấu (49 dòng), 27 món có bữa, 6 món có thời gian; chưa món nào có loại món (`dish_type`). Cách nấu của Mì Quảng tạm giữ `NULL` (QĐ3, chưa chốt). Khi có công thức, điền tiếp theo đúng quy tắc ở mục 3.2.
4. **180 món tiếp theo** (kịch bản: thêm 10–15 món/tuần sau ra mắt) chưa có trong gói này.
5. Thịt kho trứng, Gà nướng cơm lam, Lẩu Thái chua cay: đã quyết định BỎ khỏi gói dữ liệu (2026-11-23). Có thể thêm lại sau, khi có công thức nấu thử và số liệu có nguồn. Hai thẻ miền cũ (“Tây Nguyên”, “Biển & Đảo”) chưa được quyết giữ hay bỏ — đang chờ Dev quyết, nên **không đưa vào gói này**.

## 9. RLS và bảo mật

- Cả 18 bảng đều bật RLS, mỗi bảng có đúng 1 policy `SELECT` cho `anon, authenticated` (`using (true)`). 2 view dùng `security_invoker = true` nên RLS của bảng gốc vẫn áp dụng.
- **Không có policy ghi công khai.** Web/app chỉ đọc qua anon key, trong lớp data (repository). Mọi ghi/chỉnh sửa dữ liệu phải làm bằng service_role key (chỉ dùng ở server/admin) hoặc qua Supabase Dashboard với tài khoản đăng nhập. **Không ghi URL hay key Supabase vào file trong repo.**
- Mọi hàm (`search_dishes`, `f_unaccent`, `set_updated_at`, 2 hàm protein) đặt `search_path = ''` và gọi đối tượng bằng tên đầy đủ (`public.…`, `extensions.…`).
- Không lưu dữ liệu người dùng (tài khoản, yêu thích, lịch sử nấu) trong gói này — đó là bảng riêng cần thiết kế sau, khi làm tính năng đăng nhập.
