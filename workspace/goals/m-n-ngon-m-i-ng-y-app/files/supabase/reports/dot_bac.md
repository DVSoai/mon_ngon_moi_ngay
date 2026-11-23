# Báo cáo Lệnh 3 — đợt miền Bắc

Ngày tra cứu: 2026-11-23. Phạm vi: 28 món miền Bắc đang `dang_bien_tap` trên main (908cdd7).

Kết quả: **18 món** có công thức tham khảo online (chuyển sang `tham_khao_online`, `recipe_status = 'tham_khao_online'`), **10 món** chưa tìm được nguồn đạt tiêu chí nên giữ `dang_bien_tap`. Không thêm dòng dinh dưỡng nào. Chưa món nào được nấu thử.

Quy tắc đã áp dụng: chỉ nguồn tiếng Việt có tác giả/nhà xuất bản hoặc chuyên mục biên tập; nguyên liệu ghi đúng tên và định lượng nguồn nêu; bước nấu viết lại hoàn toàn bằng lời mới; không chép phần mở đầu, mẹo hay ảnh (`tip = NULL`); khẩu phần/thời gian chỉ ghi khi nguồn nêu (khoảng như “4–6 người” chỉ ghi vào `servings_text`, `servings` để NULL); `dish_meals` không gán từ nguồn online.

Về đối chiếu: nguồn đối chiếu chủ yếu là đoạn trích trong kết quả tìm kiếm (không mở toàn bài), dùng để xác nhận đúng món và nguyên liệu chính.

## Món có công thức tham khảo

### `pho-ga`

- Tìm được: có.
- Nguồn chính: VnExpress — Bùi Thủy, «Cách làm phở gà Hà Nội truyền thống» (18/8/2023) — https://vnexpress.net/pho-ga-ha-noi-truyen-thong-4643362.html — truy cập 2026-11-23.
- Nguồn đối chiếu: mytour.vn (đoạn trích tìm kiếm: gà ta, sá sùng, gừng, hạt mùi rang, hành khô, rễ mùi) — nguồn độ tin cậy thấp hơn.
- Khẩu phần / thời gian theo nguồn: 6–8 người / 120 phút (total_minutes = 120).
- Đoạn trùng dài nhất với nguồn: không đo tự động — bước nấu được viết lại từ bản tóm tắt ý chính (công cụ đọc trang trả về tóm tắt, không trả nguyên văn), nên không có văn bản gốc để so; không có đoạn nào được chép từ trang nguồn.
- Dinh dưỡng: không — Bảng Thành phần Thực phẩm Việt Nam 2017 (bản gốc) chỉ có bản in, không đọc được bản gốc để tra từng nguyên liệu; không dùng nguồn khác thay thế (QĐ1=B).
- Cách nấu thêm: không (đã có từ trước hoặc không khớp nhóm nào).
- Ăn chay: false — có thịt gà.

### `bun-thang`

- Tìm được: có.
- Nguồn chính: VnExpress — độc giả Phùng Thơm, «Bún thang chuẩn vị Hà Nội» (27/8/2021) — https://vnexpress.net/bun-thang-chuan-vi-ha-noi-4346677.html — truy cập 2026-11-23.
- Nguồn đối chiếu: VTC News — https://vtcnews.vn/cach-nau-bun-thang-ha-noi-thom-ngon-tai-nha-ar767645.html (gà ta, xương ống, sá sùng/tôm khô, chả lụa, trứng, bún).
- Khẩu phần / thời gian theo nguồn: 4–5 người / không nêu (total_minutes = NULL).
- Đoạn trùng dài nhất với nguồn: không đo tự động — bước nấu được viết lại từ bản tóm tắt ý chính (công cụ đọc trang trả về tóm tắt, không trả nguyên văn), nên không có văn bản gốc để so; không có đoạn nào được chép từ trang nguồn.
- Dinh dưỡng: không — Bảng Thành phần Thực phẩm Việt Nam 2017 (bản gốc) chỉ có bản in, không đọc được bản gốc để tra từng nguyên liệu; không dùng nguồn khác thay thế (QĐ1=B).
- Cách nấu thêm: không (đã có từ trước hoặc không khớp nhóm nào).
- Ăn chay: false — có thịt gà, giò lụa, tôm khô.
- Lưu ý: Nguồn chính là bài độc giả gửi đăng trên VnExpress, không phải biên tập viên.

### `bun-dau-mam-tom`

- Tìm được: có.
- Nguồn chính: VietNamNet — «Cách làm bún đậu mắm tôm ngon như của bà Nội phim Gạo nếp gạo tẻ» (19/9/2018) — https://vietnamnet.vn/cach-lam-bun-dau-mam-tom-ngon-nhu-cua-ba-noi-phim-gao-nep-gao-te-477450.html — truy cập 2026-11-23.
- Nguồn đối chiếu: hoanghamobile.com (đoạn trích tìm kiếm: bún lá, đậu phụ, chân giò/ba chỉ, chả cốm, mắm tôm, quất) — nguồn độ tin cậy thấp hơn.
- Khẩu phần / thời gian theo nguồn: không nêu / không nêu (total_minutes = NULL).
- Đoạn trùng dài nhất với nguồn: không đo tự động — bước nấu được viết lại từ bản tóm tắt ý chính (công cụ đọc trang trả về tóm tắt, không trả nguyên văn), nên không có văn bản gốc để so; không có đoạn nào được chép từ trang nguồn.
- Dinh dưỡng: không — Bảng Thành phần Thực phẩm Việt Nam 2017 (bản gốc) chỉ có bản in, không đọc được bản gốc để tra từng nguyên liệu; không dùng nguồn khác thay thế (QĐ1=B).
- Cách nấu thêm: chien_ran, hap_luoc.
- Ăn chay: false — có thịt ba chỉ, chả cốm, mắm tôm.

### `cha-ca-la-vong`

- Tìm được: có.
- Nguồn chính: VnExpress — Bùi Thủy, «Cách làm chả cá Hà Nội hương vị xưa» (23/2/2023) — https://vnexpress.net/cha-ca-ha-noi-huong-vi-xua-4574099.html — truy cập 2026-11-23.
- Nguồn đối chiếu: FPT Shop — https://fptshop.com.vn/tin-tuc/dien-may/cha-ca-la-vong-162619 (cá lăng, riềng, cơm mẻ, mắm tôm, nghệ, thì là, hành).
- Khẩu phần / thời gian theo nguồn: 4–6 người / 90 phút (total_minutes = 90).
- Đoạn trùng dài nhất với nguồn: không đo tự động — bước nấu được viết lại từ bản tóm tắt ý chính (công cụ đọc trang trả về tóm tắt, không trả nguyên văn), nên không có văn bản gốc để so; không có đoạn nào được chép từ trang nguồn.
- Dinh dưỡng: không — Bảng Thành phần Thực phẩm Việt Nam 2017 (bản gốc) chỉ có bản in, không đọc được bản gốc để tra từng nguyên liệu; không dùng nguồn khác thay thế (QĐ1=B).
- Cách nấu thêm: nuong.
- Ăn chay: false — có cá, mắm tôm, mỡ động vật.

### `banh-da-cua-hai-phong`

- Tìm được: có.
- Nguồn chính: Vietcetera — Windy, «Ra lò: Ở nhà nấu bánh đa cua như một người Hải Phòng chính hiệu» (06/04/2020) — https://vietcetera.com/ra-lo-o-nha-nau-banh-da-cua-nhu-mot-nguoi-hai-phong-chinh-hieu/ — truy cập 2026-11-23.
- Nguồn đối chiếu: FPT Shop — https://fptshop.com.vn/tin-tuc/dien-may/banh-da-cua-164786 (bánh đa đỏ, cua đồng xay, cà chua, rau muống, lá lốt, tôm khô, chả cá).
- Khẩu phần / thời gian theo nguồn: không nêu / không nêu (total_minutes = NULL).
- Đoạn trùng dài nhất với nguồn: không đo tự động — bước nấu được viết lại từ bản tóm tắt ý chính (công cụ đọc trang trả về tóm tắt, không trả nguyên văn), nên không có văn bản gốc để so; không có đoạn nào được chép từ trang nguồn.
- Dinh dưỡng: không — Bảng Thành phần Thực phẩm Việt Nam 2017 (bản gốc) chỉ có bản in, không đọc được bản gốc để tra từng nguyên liệu; không dùng nguồn khác thay thế (QĐ1=B).
- Cách nấu thêm: mon_nuoc.
- Ăn chay: false — có cua, tôm, chả cá, mắm tôm.

### `ga-luoc-la-chanh`

- Tìm được: có.
- Nguồn chính: Hello Bacsi — Ngọc Anh, tham vấn y khoa BS Nguyễn Thường Hanh, «Hướng dẫn bạn cách luộc gà ngon nhất» (cập nhật 07/11/2021) — https://hellobacsi.com/an-uong-lanh-manh/cong-thuc-nau-an-tot-cho-suc-khoe/huong-dan-ban-cach-luoc-ga-ngon-nhat/ — truy cập 2026-11-23.
- Nguồn đối chiếu: FPT Shop (đoạn trích tìm kiếm: gà mái ta, hành khô, gừng, lá chanh).
- Khẩu phần / thời gian theo nguồn: không nêu / Luộc 40–50 phút cho một con gà (total_minutes = NULL).
- Đoạn trùng dài nhất với nguồn: không đo tự động — bước nấu được viết lại từ bản tóm tắt ý chính (công cụ đọc trang trả về tóm tắt, không trả nguyên văn), nên không có văn bản gốc để so; không có đoạn nào được chép từ trang nguồn.
- Dinh dưỡng: không — Bảng Thành phần Thực phẩm Việt Nam 2017 (bản gốc) chỉ có bản in, không đọc được bản gốc để tra từng nguyên liệu; không dùng nguồn khác thay thế (QĐ1=B).
- Cách nấu thêm: không (đã có từ trước hoặc không khớp nhóm nào).
- Ăn chay: false — có thịt gà.
- Lưu ý: Nguồn là bài luộc gà chung; lá chanh chỉ là phần rắc khi bày (tùy chọn). Thời gian 40–50 phút nguồn nêu khác tổng các bước (~30 phút) nên total_minutes để NULL.

### `thit-dong`

- Tìm được: có.
- Nguồn chính: VTC News — Nhật Thùy, «Cách nấu thịt đông chuẩn ngon» (14/12/2024) — https://vtcnews.vn/cach-nau-thit-dong-chuan-ngon-ar913239.html — truy cập 2026-11-23.
- Nguồn đối chiếu: Hello Bacsi (đoạn trích tìm kiếm: chân giò, bì lợn, nấm hương, mộc nhĩ, hành khô).
- Khẩu phần / thời gian theo nguồn: không nêu / không nêu (total_minutes = NULL).
- Đoạn trùng dài nhất với nguồn: không đo tự động — bước nấu được viết lại từ bản tóm tắt ý chính (công cụ đọc trang trả về tóm tắt, không trả nguyên văn), nên không có văn bản gốc để so; không có đoạn nào được chép từ trang nguồn.
- Dinh dưỡng: không — Bảng Thành phần Thực phẩm Việt Nam 2017 (bản gốc) chỉ có bản in, không đọc được bản gốc để tra từng nguyên liệu; không dùng nguồn khác thay thế (QĐ1=B).
- Cách nấu thêm: không (đã có từ trước hoặc không khớp nhóm nào).
- Ăn chay: false — có thịt chân giò, da lợn.

### `canh-cua-rau-day`

- Tìm được: có.
- Nguồn chính: VnExpress — Bùi Thủy, «Cách nấu canh cua đóng tảng, không bị tanh trong ngày hè nóng bức» (13/5/2022) — https://vnexpress.net/doi-song-cooking-canh-cua-4462675.html — truy cập 2026-11-23.
- Nguồn đối chiếu: Điện máy XANH (đoạn trích tìm kiếm: cua đồng, rau đay, mồng tơi, mướp).
- Khẩu phần / thời gian theo nguồn: 4–5 người / 40 phút (total_minutes = 40).
- Đoạn trùng dài nhất với nguồn: không đo tự động — bước nấu được viết lại từ bản tóm tắt ý chính (công cụ đọc trang trả về tóm tắt, không trả nguyên văn), nên không có văn bản gốc để so; không có đoạn nào được chép từ trang nguồn.
- Dinh dưỡng: không — Bảng Thành phần Thực phẩm Việt Nam 2017 (bản gốc) chỉ có bản in, không đọc được bản gốc để tra từng nguyên liệu; không dùng nguồn khác thay thế (QĐ1=B).
- Cách nấu thêm: không (đã có từ trước hoặc không khớp nhóm nào).
- Ăn chay: false — có cua đồng.

### `rau-muong-xao-toi`

- Tìm được: có.
- Nguồn chính: VnExpress — Bùi Thủy, «Cách xào rau muống tỏi xanh giòn dậy mùi thơm» (29/3/2022) — https://vnexpress.net/cach-xao-rau-muong-xanh-gion-4444514.html — truy cập 2026-11-23.
- Nguồn đối chiếu: Điện máy XANH (đoạn trích tìm kiếm: trụng rau, phi tỏi, xào lửa lớn).
- Khẩu phần / thời gian theo nguồn: 4–6 người / 20 phút (total_minutes = 20).
- Đoạn trùng dài nhất với nguồn: không đo tự động — bước nấu được viết lại từ bản tóm tắt ý chính (công cụ đọc trang trả về tóm tắt, không trả nguyên văn), nên không có văn bản gốc để so; không có đoạn nào được chép từ trang nguồn.
- Dinh dưỡng: không — Bảng Thành phần Thực phẩm Việt Nam 2017 (bản gốc) chỉ có bản in, không đọc được bản gốc để tra từng nguyên liệu; không dùng nguồn khác thay thế (QĐ1=B).
- Cách nấu thêm: không (đã có từ trước hoặc không khớp nhóm nào).
- Ăn chay: false — có mắm tôm; nguồn cho phép dùng mỡ lợn.

### `nem-ran`

- Tìm được: có.
- Nguồn chính: VnExpress — Bùi Thủy, «Công thức và Cách làm nem rán Hà Nội chuẩn nhất» (25/1/2022) — https://vnexpress.net/doi-song-cooking-nem-ran-4419689.html — truy cập 2026-11-23.
- Nguồn đối chiếu: Điện máy XANH — https://www.dienmayxanh.com/vao-bep/cach-lam-mon-nem-ran-thom-ngon-chuan-vi-don-gian-tai-nha-00430 (thịt nạc vai, miến, trứng, bánh đa nem, mộc nhĩ, cà rốt, hành tây).
- Khẩu phần / thời gian theo nguồn: 4–6 người / 75 phút (total_minutes = 75).
- Đoạn trùng dài nhất với nguồn: không đo tự động — bước nấu được viết lại từ bản tóm tắt ý chính (công cụ đọc trang trả về tóm tắt, không trả nguyên văn), nên không có văn bản gốc để so; không có đoạn nào được chép từ trang nguồn.
- Dinh dưỡng: không — Bảng Thành phần Thực phẩm Việt Nam 2017 (bản gốc) chỉ có bản in, không đọc được bản gốc để tra từng nguyên liệu; không dùng nguồn khác thay thế (QĐ1=B).
- Cách nấu thêm: không (đã có từ trước hoặc không khớp nhóm nào).
- Ăn chay: false — có thịt lợn, tôm.

### `cha-com`

- Tìm được: có.
- Nguồn chính: VnExpress — Bùi Thủy, «Cách làm chả cốm Hà Nội» (27/9/2025) — https://vnexpress.net/cach-lam-cha-com-ha-noi-4944421.html — truy cập 2026-11-23.
- Nguồn đối chiếu: VietNamNet — https://vietnamnet.vn/cach-lam-cha-com-ngon-don-gian-tai-nha-2186520.html (thịt nạc vai băm, cốm, giò sống, nước mắm, lá chuối/lá sen).
- Khẩu phần / thời gian theo nguồn: 4–6 người / 50 phút (total_minutes = 50).
- Đoạn trùng dài nhất với nguồn: không đo tự động — bước nấu được viết lại từ bản tóm tắt ý chính (công cụ đọc trang trả về tóm tắt, không trả nguyên văn), nên không có văn bản gốc để so; không có đoạn nào được chép từ trang nguồn.
- Dinh dưỡng: không — Bảng Thành phần Thực phẩm Việt Nam 2017 (bản gốc) chỉ có bản in, không đọc được bản gốc để tra từng nguyên liệu; không dùng nguồn khác thay thế (QĐ1=B).
- Cách nấu thêm: hap_luoc, chien_ran.
- Ăn chay: false — có giò sống, thịt lợn, mỡ lợn.

### `xoi-xeo`

- Tìm được: có.
- Nguồn chính: VnExpress — Bùi Thủy, «Cách làm xôi xéo Hà Nội» (4/10/2024) — https://vnexpress.net/xoi-xeo-ha-noi-4800338.html — truy cập 2026-11-23.
- Nguồn đối chiếu: FPT Shop (đoạn trích tìm kiếm: gạo nếp, đậu xanh, mỡ gà, hành phi).
- Khẩu phần / thời gian theo nguồn: 5–6 người / 90 phút (total_minutes = 90).
- Đoạn trùng dài nhất với nguồn: không đo tự động — bước nấu được viết lại từ bản tóm tắt ý chính (công cụ đọc trang trả về tóm tắt, không trả nguyên văn), nên không có văn bản gốc để so; không có đoạn nào được chép từ trang nguồn.
- Dinh dưỡng: không — Bảng Thành phần Thực phẩm Việt Nam 2017 (bản gốc) chỉ có bản in, không đọc được bản gốc để tra từng nguyên liệu; không dùng nguồn khác thay thế (QĐ1=B).
- Cách nấu thêm: hap_luoc.
- Ăn chay: false — nguồn dùng mỡ gà hoặc mỡ lợn (mỡ động vật).
- Lưu ý: Món không có thịt; is_vegetarian = false chỉ vì công thức nguồn dùng mỡ động vật.

### `bun-oc`

- Tìm được: có.
- Nguồn chính: VnExpress — Bùi Thủy, «Cách làm bún ốc Hà Nội theo lối cũ» (24/8/2024) — https://vnexpress.net/bun-oc-ha-noi-theo-loi-cu-4785234.html — truy cập 2026-11-23.
- Nguồn đối chiếu: FPT Shop — https://fptshop.com.vn/tin-tuc/dien-may/bun-oc-nong-173424 (ốc, xương ống, cà chua, giấm bỗng, ớt chưng).
- Khẩu phần / thời gian theo nguồn: 6–8 người / 120 phút (total_minutes = 120).
- Đoạn trùng dài nhất với nguồn: không đo tự động — bước nấu được viết lại từ bản tóm tắt ý chính (công cụ đọc trang trả về tóm tắt, không trả nguyên văn), nên không có văn bản gốc để so; không có đoạn nào được chép từ trang nguồn.
- Dinh dưỡng: không — Bảng Thành phần Thực phẩm Việt Nam 2017 (bản gốc) chỉ có bản in, không đọc được bản gốc để tra từng nguyên liệu; không dùng nguồn khác thay thế (QĐ1=B).
- Cách nấu thêm: không (đã có từ trước hoặc không khớp nhóm nào).
- Ăn chay: false — có ốc, mắm tôm, mỡ lợn.

### `mien-ga`

- Tìm được: có.
- Nguồn chính: VnExpress — Bùi Thủy, «Miến gà ấm nóng ngày đông» (15/12/2024) — https://vnexpress.net/mien-ga-am-nong-ngay-dong-4827824.html — truy cập 2026-11-23.
- Nguồn đối chiếu: VTC News — https://vtcnews.vn/cach-nau-mien-ga-thom-ngon-cho-ca-nha-ar204774.html (gà ta, miến dong, hành lá, chanh, ớt).
- Khẩu phần / thời gian theo nguồn: 4–5 người / 40 phút (total_minutes = 40).
- Đoạn trùng dài nhất với nguồn: không đo tự động — bước nấu được viết lại từ bản tóm tắt ý chính (công cụ đọc trang trả về tóm tắt, không trả nguyên văn), nên không có văn bản gốc để so; không có đoạn nào được chép từ trang nguồn.
- Dinh dưỡng: không — Bảng Thành phần Thực phẩm Việt Nam 2017 (bản gốc) chỉ có bản in, không đọc được bản gốc để tra từng nguyên liệu; không dùng nguồn khác thay thế (QĐ1=B).
- Cách nấu thêm: không (đã có từ trước hoặc không khớp nhóm nào).
- Ăn chay: false — có thịt gà.

### `thit-quay-gion-bi`

- Tìm được: có.
- Nguồn chính: VnExpress — Bùi Thủy, «Bí quyết làm ba chỉ quay giòn bì đơn giản tại nhà» (29/6/2023) — https://vnexpress.net/doi-song-cooking-ba-chi-4623347.html — truy cập 2026-11-23.
- Nguồn đối chiếu: Điện máy XANH — https://www.dienmayxanh.com/vao-bep/cach-lam-thit-quay-gion-bi-theo-meo-don-gian-dam-bao-thanh-23489 (ba chỉ 1 kg, muối, tiêu, ngũ vị hương, paprika).
- Khẩu phần / thời gian theo nguồn: 5–6 người / 90 phút (chưa tính thời gian hong khô bì) (total_minutes = NULL).
- Đoạn trùng dài nhất với nguồn: không đo tự động — bước nấu được viết lại từ bản tóm tắt ý chính (công cụ đọc trang trả về tóm tắt, không trả nguyên văn), nên không có văn bản gốc để so; không có đoạn nào được chép từ trang nguồn.
- Dinh dưỡng: không — Bảng Thành phần Thực phẩm Việt Nam 2017 (bản gốc) chỉ có bản in, không đọc được bản gốc để tra từng nguyên liệu; không dùng nguồn khác thay thế (QĐ1=B).
- Cách nấu thêm: nuong.
- Ăn chay: false — có thịt lợn.
- Lưu ý: total_minutes để NULL vì 90 phút nguồn nêu không gồm ít nhất 6 giờ hong khô bì.

### `trung-duc-thit`

- Tìm được: có.
- Nguồn chính: VnExpress — Bùi Thủy, «Cách làm trứng đúc thịt - món ăn 'quốc dân'» (13/3/2025) — https://vnexpress.net/trung-duc-thit-mon-an-quoc-dan-4860439.html — truy cập 2026-11-23.
- Nguồn đối chiếu: VietNamNet — https://vietnamnet.vn/cach-lam-trung-duc-thit-don-gian-ma-ngon-tai-nha-2246671.html (thịt lợn 300g, trứng vịt 5-6 quả, hành khô).
- Khẩu phần / thời gian theo nguồn: 4–6 người / 30 phút (total_minutes = 30).
- Đoạn trùng dài nhất với nguồn: không đo tự động — bước nấu được viết lại từ bản tóm tắt ý chính (công cụ đọc trang trả về tóm tắt, không trả nguyên văn), nên không có văn bản gốc để so; không có đoạn nào được chép từ trang nguồn.
- Dinh dưỡng: không — Bảng Thành phần Thực phẩm Việt Nam 2017 (bản gốc) chỉ có bản in, không đọc được bản gốc để tra từng nguyên liệu; không dùng nguồn khác thay thế (QĐ1=B).
- Cách nấu thêm: chien_ran.
- Ăn chay: false — có thịt lợn.

### `bun-moc`

- Tìm được: có.
- Nguồn chính: VnExpress — Đinh Hương, «Bún mọc dọc mùng phong cách Hà Nội» (28/11/2014) — https://vnexpress.net/bun-moc-doc-mung-phong-cach-ha-noi-3112934.html — truy cập 2026-11-23.
- Nguồn đối chiếu: VnExpress — Bùi Thủy, https://vnexpress.net/doi-song-cooking-bun-moc-4215257.html (giò sống 400 g, mộc nhĩ, nấm hương, bún) — cùng báo, khác tác giả; hoanghamobile (xương ống, giò sống, nấm hương, mộc nhĩ).
- Khẩu phần / thời gian theo nguồn: 6 tô bún / không nêu (total_minutes = NULL).
- Đoạn trùng dài nhất với nguồn: không đo tự động — bước nấu được viết lại từ bản tóm tắt ý chính (công cụ đọc trang trả về tóm tắt, không trả nguyên văn), nên không có văn bản gốc để so; không có đoạn nào được chép từ trang nguồn.
- Dinh dưỡng: không — Bảng Thành phần Thực phẩm Việt Nam 2017 (bản gốc) chỉ có bản in, không đọc được bản gốc để tra từng nguyên liệu; không dùng nguồn khác thay thế (QĐ1=B).
- Cách nấu thêm: không (đã có từ trước hoặc không khớp nhóm nào).
- Ăn chay: false — có giò sống (thịt lợn), xương lợn.
- Lưu ý: Nguồn chính đăng năm 2014; bản đối chiếu chính cùng báo VnExpress (khác bài, khác tác giả).

### `chao-suon`

- Tìm được: có.
- Nguồn chính: VnExpress — Bùi Thủy, «Cháo sườn Hà Nội» (15/11/2024) — https://vnexpress.net/chao-suon-ha-noi-4816507.html — truy cập 2026-11-23.
- Nguồn đối chiếu: Điện máy XANH — https://www.dienmayxanh.com/vao-bep/cach-nau-chao-suon-ha-noi-deo-dac-thom-ngon-chuan-vi-09389 (bột gạo tẻ, bột nếp, sườn, nước mắm, quẩy).
- Khẩu phần / thời gian theo nguồn: 5–6 người / 90 phút (total_minutes = 90).
- Đoạn trùng dài nhất với nguồn: không đo tự động — bước nấu được viết lại từ bản tóm tắt ý chính (công cụ đọc trang trả về tóm tắt, không trả nguyên văn), nên không có văn bản gốc để so; không có đoạn nào được chép từ trang nguồn.
- Dinh dưỡng: không — Bảng Thành phần Thực phẩm Việt Nam 2017 (bản gốc) chỉ có bản in, không đọc được bản gốc để tra từng nguyên liệu; không dùng nguồn khác thay thế (QĐ1=B).
- Cách nấu thêm: không (đã có từ trước hoặc không khớp nhóm nào).
- Ăn chay: false — có sườn, xương lợn.

## Món chưa tìm được nguồn — giữ `dang_bien_tap`

- `banh-cuon-thanh-tri`: Chỉ tìm thấy bài văn hóa/giới thiệu làng nghề, chưa có công thức đúng món (bánh cuốn Thanh Trì không nhân) từ nguồn có tác giả.
- `ca-kho-lang-vu-dai`: Bài Điện máy XANH (06831) không đọc được (lỗi máy chủ khi tải); các nguồn khác chỉ là đoạn trích, không đủ công thức.
- `canh-rieu-cua`: VnExpress chỉ có đoạn giới thiệu trong bài tổng hợp, không định lượng; chưa có công thức đầy đủ đúng món.
- `dau-phu-sot-ca-chua`: VnExpress chỉ có biến thể đậu nhồi thịt (khác món); bài Điện máy XANH (10227) không đọc được (lỗi máy chủ).
- `canh-bi-nau-tom`: Bài Điện máy XANH (10369) không đọc được (lỗi máy chủ); chưa có nguồn thay thế đúng món.
- `su-hao-xao`: Tên món chung; nguồn uy tín chỉ có biến thể thêm đạm (su hào xào mực/thịt) — cần quyết định biến thể trước.
- `nom-hoa-chuoi`: Nguồn uy tín chỉ có biến thể thêm tai lợn/thịt — cần quyết định biến thể trước.
- `che-dau-xanh`: Chưa đọc được trang công thức đúng món (các kết quả là biến thể: đậu xanh đánh, phổ tai, nha đam…).
- `banh-troi-tau`: Bài Điện máy XANH (02273) không đọc được (lỗi máy chủ); chưa có nguồn thay thế đúng món.
- `pho-cuon`: Các bài tìm được chỉ giới thiệu quán hoặc là biến thể (thập cẩm, ngũ sắc); mục 'phở cuốn thịt bò' của Điện máy XANH không có nguyên liệu/bước.

## Việc cần Dev/Muse quyết định

- `su-hao-xao`, `nom-hoa-chuoi`: chọn biến thể (chay hay có đạm) trước khi tìm công thức.
- `has_full_recipe` của 18 món online đang đặt `true` (có đủ nguyên liệu + bước), dù chưa nấu thử — xác nhận cách hiểu cột này.
- Ba món dùng nguồn độ tin cậy thấp hơn để đối chiếu (phở gà, bún đậu mắm tôm, bún mọc một phần) và bún thang là bài độc giả gửi — có thể thay nguồn khi biên tập.
