# Món Ngon Mỗi Ngày — Gói dữ liệu Supabase

Gói dữ liệu chuẩn để deploy lên Supabase trước, rồi web và app cùng dùng chung một nguồn. **Không làm lại demo web trong gói này.**

> **Nguyên tắc của gói này:** chỉ đưa số liệu đã kiểm chứng. Món nào chưa có công thức thì để `status = 'dang_bien_tap'`, không bịa nguyên liệu, thời gian hay dinh dưỡng.

## 1. Trong gói có gì

Thư mục: `workspace/goals/m-n-ngon-m-i-ng-y-app/files/supabase/`

| File | Nội dung |
|---|---|
| `schema.sql` | Schema Postgres/Supabase: `dishes`, `recipes`, `ingredients`, `nutrition_estimates`, `diet_modes`, `dish_diet_tags`, `weekly_menu`, `sources`. UUID, slug, `numeric` cho kcal/protein/carb/fat, index trên miền/slug/chế độ ăn, RLS đọc công khai — không ghi công khai. Kèm 2 hàm `protein_target_grams()` và `protein_remaining_grams()`. |
| `seed.sql` | INSERT cho toàn bộ dữ liệu dưới đây. Chạy sau `schema.sql`. Dùng `ON CONFLICT DO NOTHING` nên chạy lại được. |
| `dishes.csv` | 90 món, cùng dữ liệu với `seed.sql`, UTF-8, để import CSV trong Supabase. |
| `nutrition.csv` | 22 dòng dinh dưỡng, cùng dữ liệu với `seed.sql`, UTF-8. |
| `mon-ngon-supabase-data.json` | Bản JSON mirror của `seed.sql` (món, công thức, nguyên liệu, dinh dưỡng, chế độ ăn, thực đơn tuần, nguồn). |
| `README.md` | File này. |
| Nguồn chuẩn (không sửa) | `../mon-ngon-90-mon-data.json` — 90 món đã đếm đủ Bắc 30 / Trung 30 / Nam 30. |

### Số lượng đã kiểm chứng

- **Món: 90** — Bắc 30 / Trung 30 / Nam 30. Không có Tây Nguyên, không có món toàn quốc, không có Biển & Đảo trong 90 món.
- **Công thức đầy đủ trong 90: 6 món** — Phở bò, Bún chả, Bún bò Huế, Mì Quảng, Hủ tiếu Nam Vang, Cơm tấm sườn bì chả.
- **Công thức đầy đủ ngoài 90: 1 món** — Bánh mì thịt nguội, món toàn quốc, không nằm trong 90. Tổng công thức đầy đủ trong seed: **7**.
- **Nguyên liệu đã tách dòng: 56 dòng** — tách từ chuỗi nguyên liệu trong kịch bản bằng dấu `;`, không thêm/bớt nguyên liệu.
- **Dinh dưỡng: 22 dòng** — 8 dòng theo 100 g + 14 dòng theo khẩu phần (xem mục 2).
- **Chế độ ăn: 6 chế độ**, **540 tag món × chế độ** (90 × 6). Trong đó **72 tag đã xác định** (12 món có số liệu theo khẩu phần × 6 chế độ), **468 tag chưa có dữ liệu** (78 món × 6) — xem mục 4.
- **Thực đơn tuần mẫu: 21 bữa** — 7 ngày × 3 bữa (Thứ 2–Chủ nhật, theo kịch bản trang 13).
- **Cách nấu đã gán: 37/90 món. Bữa đã gán: 24/90 món. Thời gian đã gán: 6/90 món** (chỉ 6 món có công thức đầy đủ). Còn lại để `null` — xem mục 3.

## 2. Nguồn số liệu — chỉ dùng những nguồn này

### 2.1. Món ăn và công thức — kịch bản 15 trang (nguồn nội bộ)

Kịch bản 15 trang Món Ngon Mỗi Ngày: danh mục 90 món (trang 8), 7 công thức mẫu (trang 9–12), thực đơn 7 ngày (trang 13), bản đồ tính năng (trang 6), lộ trình (trang 14–15).

### 2.2. Dinh dưỡng theo 100 g — Bảng Thành phần Thực phẩm Việt Nam, Viện Dinh dưỡng Quốc gia (Bộ Y tế), qua CaloCalo

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

Lưu ý: “Bánh cuốn” trong bảng được gán cho món “Bánh cuốn Thanh Trì” trong kho. “Bánh mì thập cẩm” **chỉ tham chiếu** — không phải Bánh mì thịt nguội trong kịch bản, không gán cho món đó.

### 2.3. Dinh dưỡng theo khẩu phần — FitArchive, ước tính từ USDA FoodData Central

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
| Bánh mì thịt | 1 ổ 210 g | 526 | 25 g | 50 g | 25 g |
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
- “Bánh mì thịt” gán cho công thức Bánh mì thịt nguội (ngoài 90), không gán cho món nào trong 90.
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
| **Miền** | Tất cả, Miền Bắc, Miền Trung, Miền Nam, **Tây Nguyên, Khắp cả nước, Biển & Đảo** | Tất cả, Miền Bắc, Miền Trung, Miền Nam | **Xóa Tây Nguyên, Khắp cả nước, Biển & Đảo khỏi enum miền.** Kịch bản chỉ có 3 miền. Bánh mì thịt nguội là món toàn quốc nhưng nằm ngoài 90, ghi chú riêng trong bảng `recipes` (`region = 'Toàn quốc'`, `in_90 = false`), **không tạo miền thứ 4**. |
| **Cách nấu** | Tất cả, Món nước, Kho, Canh, Nướng, Chiên / Rán, Gỏi & Cuốn, Lẩu, Hấp & Luộc, Xào, **Nhanh < 30 phút** | Tất cả, Món nước, Kho, Canh, Nướng, Chiên / Rán, Gỏi & Cuốn, Lẩu, Hấp & Luộc, Xào | **Bỏ “Nhanh < 30 phút” khỏi cách nấu** — đó là thời gian, không phải cách nấu. Chuyển sang filter riêng **THỜI GIAN** (mục 3.2). |
| **Bữa** | Tất cả, Ăn sáng, Bữa trưa, Bữa tối, **Cuối tuần** | Tất cả, Ăn sáng, Bữa trưa, Bữa tối, Ăn nhẹ | **Bỏ “Cuối tuần”** — cuối tuần không phải bữa. Chuyển sang tag dịp `cuoi_tuan_dai_khach` (mục 3.3). |
| **Chế độ ăn** | *(chưa có hàng này trong ảnh cũ)* | Tất cả, Bình thường, Ăn chay, Ăn kiêng giảm cân, Ít dầu mỡ, Giàu protein, Ít tinh bột | **Thêm hàng mới — filter thứ 4**, lọc kết hợp với 3 filter trên. |
| **Mô tả kho món** | “14 món có công thức chi tiết” | “6 món có công thức đầy đủ, 84 món công thức đang biên tập” | Chỉ có 6 món trong 90 có công thức đầy đủ. 84 món còn lại **không có nguyên liệu chính/cách làm tóm tắt từ script** — trong UI phải ghi “công thức đang biên tập”, không được ghi là có công thức chi tiết. |

Enum trong DB (`schema.sql`, cột `dishes.cooking_method`, `dishes.meal`, `dishes.time_band`, `dishes.region`, `dishes.occasion`):

- `region`: `Bac`, `Trung`, `Nam`
- `cooking_method`: `mon_nuoc`, `kho`, `canh`, `nuong`, `chien_ran`, `goi_cuon`, `lau`, `hap_luoc`, `xao`
- `meal`: `sang`, `trua`, `toi`, `an_nhe`
- `time_band`: `duoi_30`, `30_60`, `tren_60`
- `occasion`: `cuoi_tuan_dai_khach`
- `diet_modes.code`: `binh_thuong`, `an_chay`, `an_kieng_giam_can`, `it_dau_mo`, `giau_protein`, `it_tinh_bot`

### 3.2. Quy tắc gán — chỉ gán khi có căn cứ, còn lại để `null`

- **Cách nấu:** chỉ gán khi suy ra chắc chắn từ tên món hoặc công thức đầy đủ trong kịch bản. Ví dụ: tên có “kho” → `kho`; “Canh …” → `canh`; “Lẩu …” → `lau`; “xào” → `xao`; “luộc” → `hap_luoc`; “nướng” → `nuong`; “rán” → `chien_ran`; món nước dùng rõ ràng (Phở, Bún bò Huế, Hủ tiếu…) → `mon_nuoc`; Bún chả có công thức ghi “nướng than” → `nuong`. Món chưa có công thức thì `cooking_method = NULL` — sau khi nấu thử mới điền đủ. Đã gán: **37/90 món**.
- **Bữa:** chỉ gán khi có căn cứ trong thực đơn 7 ngày mẫu (trang 13) hoặc món là món tráng miệng/ăn nhẹ rõ ràng (chè, bánh da lợn, dừa sáp, bánh trôi tàu → `an_nhe`). Đã gán: **24/90 món**. Còn lại `meal = NULL`.
- **Thời gian:** chỉ điền khi có công thức đầy đủ. 6 món trong 90: Phở bò `tren_60` (~3 giờ hầm, bản rút gọn 60 phút), Bún chả `30_60` (~60 phút), Bún bò Huế `tren_60` (~90 phút), Mì Quảng `30_60` (~60 phút), Hủ tiếu Nam Vang `tren_60` (~90 phút), Cơm tấm `tren_60` (~75 phút). Bánh mì thịt nguội (ngoài 90) là `duoi_30` (~20 phút) nhưng chỉ lưu trong bảng `recipes`, không có trong bảng `dishes`. 84 món còn lại `time_band = NULL`.
- **Dịp cuối tuần:** chỉ Lẩu mắm có `occasion = 'cuoi_tuan_dai_khach'` — thực đơn 7 ngày mẫu ghi “Lẩu mắm (Nam) — bữa sum họp cuối tuần”. Các món khác không gán.
- **Chế độ ăn:** xem mục 4.

### 3.3. Sort — chỉ sort được khi món có số liệu

- **Nhiều protein nhất / Ít calo nhất / Ít béo nhất:** sort trên bảng `nutrition_estimates` với `basis = 'per_serving'`, dùng `NULLS LAST` — món chưa có số liệu xếp cuối và UI phải ghi rõ “chưa có số liệu dinh dưỡng”, không xếp lẫn với món có số liệu thấp.
- Ví dụ query ở mục 7.

## 4. Chế độ ăn — 6 chế độ, quy tắc rõ ràng

| Mã | Tên | Quy tắc (ghi trong bảng `diet_modes.rule_vi`) |
|---|---|---|
| `binh_thuong` | Bình thường | Không loại trừ món nào. |
| `an_chay` | Ăn chay | Không thịt, không cá/hải sản. Được phép trứng/sữa trừ khi ghi chú khác. Cần xác nhận khi biên tập công thức vì nước mắm/mỡ hành có thể dùng trong món chay. |
| `an_kieng_giam_can` | Ăn kiêng giảm cân | kcal/phần ≤ 450 (chỉ tính khi có số liệu theo khẩu phần). |
| `it_dau_mo` | Ít dầu mỡ | Fat/phần ≤ 10 g **và** cách nấu không phải `xao`/`chien_ran`. |
| `giau_protein` | Giàu protein | Protein/phần ≥ 25 g **và** protein/100 kcal ≥ 7 g (chỉ tính khi có số liệu theo khẩu phần). |
| `it_tinh_bot` | Ít tinh bột | Carb/phần ≤ 20 g (chỉ tính khi có số liệu theo khẩu phần). |

**Cách gán tag:** chỉ tự động gán khi quy tắc kiểm tra được từ số liệu đã biết; còn lại để `is_applicable = NULL`, `status = 'chua_co_du_lieu'`, không đoán.

- 12 món có số liệu FitArchive theo khẩu phần và gán được vào một món trong kho 90 (Phở bò, Bún chả, Bún bò Huế, Mì Quảng, Hủ tiếu Nam Vang, Cơm tấm, Gỏi cuốn, Cá kho tộ, Rau muống xào tỏi, Cháo lòng, Chè ba màu, Xôi xéo) → 72 tag đã xác định.
- 78 món còn lại trong 90 → 468 tag `chua_co_du_lieu`.
- Riêng `an_chay`: trong 12 món trên, chỉ Rau muống xào tỏi, Chè ba màu, Xôi xéo được gán `true` (món thực vật rõ ràng theo tên món); các món còn lại là `false` vì có thịt/cá/tôm. Khi biên tập công thức phải xác nhận lại (ví dụ nước mắm trong món chay).
- Riêng `it_dau_mo`: Rau muống xào tỏi có fat 10 g nhưng là món xào nên gán `false` — xào vẫn có dầu, không xếp vào ít dầu mỡ tuyệt đối.

## 5. Deploy lên Supabase

### Bước 1 — Tạo project

1. Vào Supabase Dashboard → New project, chọn region gần nhất (Singapore), đặt database password và lưu lại.
2. Mở **SQL Editor** trong project mới.

### Bước 2 — Chạy schema rồi seed

1. Mở file `schema.sql`, copy toàn bộ, dán vào SQL Editor → **Run**. Tạo xong 8 bảng + 2 hàm protein + RLS.
2. Mở file `seed.sql`, copy toàn bộ, dán vào SQL Editor → **Run**. Nạp xong 90 món, 7 công thức, 56 dòng nguyên liệu, 22 dòng dinh dưỡng, 6 chế độ ăn, 540 tag, 21 bữa thực đơn tuần, 7 nguồn.
3. Nếu chạy lại seed, `ON CONFLICT DO NOTHING` sẽ bỏ qua các dòng đã có, không tạo trùng.

### Bước 3 — Hoặc import CSV (thay cho seed, nếu thích)

- Trong Supabase Dashboard → Table Editor → `dishes` → Import data → chọn `dishes.csv`.
- Làm tương tự với `nutrition.csv` cho bảng `nutrition_estimates`.
- Lưu ý: import CSV không nạp được `recipes`, `ingredients`, `diet_modes`, `dish_diet_tags`, `weekly_menu`, `sources` — các bảng đó vẫn cần chạy `seed.sql` (hoặc import từ `mon-ngon-supabase-data.json` bằng script riêng).

### Bước 4 — Kiểm chứng bằng SQL (chạy trong SQL Editor)

```sql
-- 1. Tổng món và theo miền: phải ra 90 / 30 / 30 / 30
select region, count(*) from dishes group by region order by region;
select count(*) as tong_mon from dishes;

-- 2. Công thức đầy đủ trong 90 phải là 6; tổng công thức là 7 (6 trong 90 + Bánh mì ngoài 90)
select count(*) as cong_thuc_trong_90 from recipes where in_90 = true;
select count(*) as tong_cong_thuc from recipes;
select count(*) as mon_dang_bien_tap from dishes where status = 'dang_bien_tap';
-- phải ra 84

-- 3. Không có miền lạ trong 90 món
select distinct region from dishes;
-- chỉ được ra Bac / Trung / Nam

-- 4. Dinh dưỡng: phải ra 22 dòng, mỗi dòng đều có nguồn + phương pháp + độ tin cậy
select basis, count(*) from nutrition_estimates group by basis;
select count(*) from nutrition_estimates
 where source_code is null or method is null or confidence is null;
-- phải ra 0

-- 5. Món chưa có công thức thì không được có nguyên liệu/thời gian/dinh dưỡng bịa thêm
select count(*) from dishes d
 where d.status = 'dang_bien_tap' and d.time_band is not null;
-- phải ra 0 (thời gian chỉ có ở 6 món có công thức)
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

Tất cả query dưới đây chạy được trên schema đã tạo. Dùng Supabase JS client (`supabase.from('dishes').select(...)`) hoặc gọi trực tiếp bằng SQL.

### 7.1. Món của ngày (theo ngày thật, không hard-code)

```sql
-- Món của ngày: lấy 3 món theo ngày trong năm, không lặp trong 7 ngày gần nhất
-- (logic chọn món theo hồ sơ vị nằm ở app; DB chỉ cung cấp kho món + tag)
select d.slug, d.name, d.region, d.cooking_method, d.meal
from dishes d
where d.status = 'co_cong_thuc'
order by md5(d.slug || to_char(current_date, 'YYYY-MM-DD'))
limit 3;
```

### 7.2. Lọc kết hợp 4 trục: miền + cách nấu + bữa + chế độ ăn

```sql
-- Ví dụ: món miền Nam, món nước, bữa trưa, ăn kiêng giảm cân
select d.slug, d.name, d.region, d.cooking_method, d.meal, n.kcal, n.protein_g
from dishes d
join dish_diet_tags t on t.dish_id = d.id and t.diet_mode_code = 'an_kieng_giam_can' and t.is_applicable = true
left join nutrition_estimates n on n.dish_id = d.id and n.basis = 'per_serving'
where d.region = 'Nam'
  and d.cooking_method = 'mon_nuoc'
  and d.meal = 'trua';
-- Lưu ý: món chưa có số liệu sẽ không qua được filter chế độ ăn
-- (tag = NULL), đúng theo quy tắc "không đoán".
```

```sql
-- Lọc theo thời gian (filter riêng, không phải cách nấu)
select slug, name, time_band from dishes
where time_band = 'duoi_30';
-- Chỉ ra các món có công thức đầy đủ và thời gian đã biết.
-- Món chưa có công thức có time_band = NULL nên không lọt vào.
```

```sql
-- Lọc theo dịp cuối tuần / đãi khách
select slug, name from dishes where occasion = 'cuoi_tuan_dai_khach';
-- Chỉ ra Lẩu mắm (theo thực đơn 7 ngày mẫu).
```

### 7.3. Thực đơn tuần mẫu

```sql
select day_of_week, day_name_vi, meal, meal_text
from weekly_menu
order by day_of_week,
  case meal when 'sang' then 1 when 'trua' then 2 when 'toi' then 3 end;
```

### 7.4. Sort: nhiều protein nhất / ít calo nhất / ít béo nhất (món chưa có số liệu xếp cuối)

```sql
-- Nhiều protein nhất (theo khẩu phần)
select d.name, n.protein_g, n.kcal, n.serving_label
from dishes d
join nutrition_estimates n on n.dish_id = d.id and n.basis = 'per_serving'
order by n.protein_g desc nulls last
limit 10;

-- Ít calo nhất
select d.name, n.kcal, n.protein_g
from dishes d
join nutrition_estimates n on n.dish_id = d.id and n.basis = 'per_serving'
order by n.kcal asc nulls last
limit 10;

-- Ít béo nhất
select d.name, n.fat_g, n.kcal
from dishes d
join nutrition_estimates n on n.dish_id = d.id and n.basis = 'per_serving'
order by n.fat_g asc nulls last
limit 10;
-- UI phải ghi rõ: món không có dòng nutrition_estimates thì xếp cuối
-- và hiển thị "chưa có số liệu dinh dưỡng".
```

### 7.5. Ví dụ 1 — Người giảm cân

Quy tắc: lọc `it_dau_mo` + `an_kieng_giam_can`, loại món chiên/xào nhiều dầu, ưu tiên kcal/phần ≤ 450 và fat thấp.

```sql
select d.name, n.kcal, n.protein_g, n.fat_g, n.serving_label
from dishes d
join dish_diet_tags t1 on t1.dish_id = d.id and t1.diet_mode_code = 'it_dau_mo' and t1.is_applicable = true
join dish_diet_tags t2 on t2.dish_id = d.id and t2.diet_mode_code = 'an_kieng_giam_can' and t2.is_applicable = true
join nutrition_estimates n on n.dish_id = d.id and n.basis = 'per_serving'
where n.kcal <= 450
order by n.kcal asc;
```

Món có số liệu thật khớp ví dụ này:
- **Phở bò — 418 kcal / 38 g protein / 4 g béo** (1 tô 785 g, FitArchive ước tính).
- **Gỏi cuốn — 147 kcal / 9 g protein / 3 g béo** (1 cuốn 98 g).
- **Chè ba màu — 301 kcal / 7 g protein / 9 g béo** (1 ly 160 g).
- **Canh chua cá — 148 kcal / 14 g protein / 4 g béo** (1 tô 208 g) — số liệu thật từ FitArchive, nhưng là món chung, **không gán cho một món cụ thể** trong kho (xem mục 2.3), nên chỉ dùng làm ví dụ tham khảo, không dùng query trên để lọc ra món này.
- **Rau muống xào tỏi — 139 kcal / 5 g protein / 10 g béo** (1 đĩa 220 g) — lưu ý: đây là món **xào** nên vẫn có dầu, **không xếp vào ít dầu mỡ tuyệt đối**; trong DB tag `it_dau_mo` của món này là `false` dù fat = 10 g.

### 7.6. Ví dụ 2 — Người tập gym cần protein

Mốc tham khảo: người bình thường ~0,93 g/kg/ngày (Viện Dinh dưỡng 2026); người tập kháng lực ~1,6 g/kg/ngày là mốc mà tổng hợp nghiên cứu thấy khối nạc không tăng thêm đáng kể khi vượt qua. Đây là mốc tham khảo, không phải chỉ định y tế.

Ví dụ tính: người **70 kg** tập kháng lực → 70 × 1,6 = **112 g protein/ngày**, chia 3–4 bữa ≈ 28–37 g/bữa.

```sql
-- Mục tiêu protein của một người 70 kg, mốc 1.6
select protein_target_grams(70, 1.6) as protein_muc_tieu_g_ngay;
-- ra 112.0

-- Protein còn thiếu trong ngày nếu đã ăn 40 g
select protein_remaining_grams(70, 1.6, 40) as protein_con_thieu_g;
-- ra 72.0

-- Món giàu protein có số liệu thật (theo khẩu phần, FitArchive ước tính)
select d.name, n.protein_g, n.kcal, n.fat_g
from dishes d
join nutrition_estimates n on n.dish_id = d.id and n.basis = 'per_serving'
order by n.protein_g desc
limit 5;
-- Bún bò Huế 42 g, Mì Quảng gà 41 g, Phở bò 38 g, Cơm tấm sườn 36 g, Hủ tiếu Nam Vang 36 g
```

```sql
-- Lọc món vừa giàu protein vừa ít dầu mỡ
-- (protein >= 25 g, fat thấp, không chiên — theo tag đã tính sẵn)
select d.name, n.protein_g, n.fat_g, n.kcal
from dishes d
join dish_diet_tags t1 on t1.dish_id = d.id and t1.diet_mode_code = 'giau_protein' and t1.is_applicable = true
join dish_diet_tags t2 on t2.dish_id = d.id and t2.diet_mode_code = 'it_dau_mo' and t2.is_applicable = true
join nutrition_estimates n on n.dish_id = d.id and n.basis = 'per_serving'
order by n.protein_g desc;
-- Với dữ liệu hiện tại chỉ ra Phở bò (38 g protein, 4 g béo):
-- Bún bò Huế có 42 g protein nhưng fat 17 g nên không qua filter ít dầu mỡ.
-- Đây là kết quả thật từ số liệu hiện có, không phải do thiếu món.
```

## 8. Chưa có trong dữ liệu — việc cần làm tiếp (nấu thử và chuẩn hóa)

1. **84 món trong 90 chưa có công thức.** Trong kịch bản chúng chỉ có tên, là danh sách ứng viên để biên tập. Cần nấu thử từng món ít nhất 2 lần (theo kịch bản trang 15), chuẩn hóa định lượng theo mẫu trang 12 (tên + miền + địa phương, bữa/thời gian/độ khó, nguyên liệu theo khẩu phần, bước nấu có hẹn giờ, mẹo, món kèm, ảnh tự chụp), rồi mới điền vào `recipes` + `ingredients` và đổi `status` từ `dang_bien_tap` sang `co_cong_thuc`.
2. **84 món chưa có dinh dưỡng.** Chỉ 12 món có số liệu theo khẩu phần và 8 món có số liệu theo 100 g (một phần trùng nhau). Sau khi nấu thử và cân khẩu phần chuẩn, tính lại dinh dưỡng từ nguyên liệu (ưu tiên Bảng Thành phần Thực phẩm Việt Nam) rồi mới điền `nutrition_estimates` và tính lại `dish_diet_tags` — không điền số ước đoán tay.
3. **Cách nấu / bữa / thời gian còn thiếu.** Hiện mới gán được 37 món có cách nấu, 24 món có bữa, 6 món có thời gian. Sau khi nấu thử, điền đủ 3 cột này theo đúng quy tắc ở mục 3.2.
4. **180 món tiếp theo** (kịch bản: thêm 10–15 món/tuần sau ra mắt) chưa có trong gói này.
5. **3 món ngoài 90 và 2 thẻ miền cũ** (Thịt kho trứng, Gà nướng cơm lam, Lẩu Thái chua cay; thẻ “Tây Nguyên”, “Biển & Đảo”) chưa được quyết giữ hay bỏ — đang chờ Dev quyết, nên **không đưa vào gói này**.

## 9. RLS và bảo mật

- Tất cả 8 bảng đều bật RLS, chỉ có policy `SELECT` công khai (`using (true)`).
- **Không có policy ghi công khai.** Web/app chỉ đọc qua anon key. Mọi ghi/chỉnh sửa dữ liệu phải làm bằng service_role key (chỉ dùng ở server/admin) hoặc qua Supabase Dashboard với tài khoản đăng nhập.
- Không lưu dữ liệu người dùng (tài khoản, yêu thích, lịch sử nấu) trong gói này — đó là bảng riêng cần thiết kế sau, khi làm tính năng đăng nhập.
