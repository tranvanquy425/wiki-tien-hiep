---
name: char-kinhlịch
description: >
  Viết mục Kinh Lịch Nhân Sinh cho nhân vật trong tiểu thuyết mạng (tu tiên, huyền huyễn,
  đô thị, hệ thống...) theo hệ 3 mức: trọng đại / sự kiện / hành trình. Phân loại tường
  minh từng sự kiện, viết đúng độ dài theo mức, xuất ra khối @timeline chuẩn cho wiki.
  BẮT BUỘC dùng khi W3 viết hoặc cập nhật timeline[] cho bất kỳ nhân vật nào, bất kể bộ
  truyện. Trigger: "viết kinh lịch", "cập nhật timeline", "sự kiện nhân vật", "hành trình
  nhân vật", "lịch sử nhân vật", hoặc khi cần điền @timeline trong khối @block.
---

# char-kinhlịch — Skill viết Kinh Lịch Nhân Sinh

## 0. Nguyên tắc nền

Kinh lịch ≠ liệt kê đột phá tu vi (đã có tab Tu vi riêng).
Kinh lịch = **dòng thời gian sự kiện** từ đầu đến cuối — những gì xảy ra với nhân vật,
theo thứ tự chương, phân mức độ quan trọng để người đọc hiểu nhân vật hình thành như thế nào.

Quy tắc bất biến:
- Sắp xếp TĂNG DẦN theo chương (cũ trên, mới dưới).
- Mọi sự kiện phải truy được về chương gốc.
- KHÔNG bịa, KHÔNG suy diễn nếu không có trong văn bản.
- Field `importance` khai báo TƯỜNG MINH — không để web tự suy diễn.


## 1. Hệ 3 mức + tiêu chí phân loại

### Mức 1 — Trọng đại (`importance: "major"`, ribbon vàng)

**Định nghĩa:** Sự kiện làm thay đổi BẢN CHẤT nhân vật hoặc cục diện không thể đảo ngược.
Viết đầy đủ, chi tiết, có dẫn chứng chương.

**Cần ít nhất 1 tiêu chí:**
- Thay đổi phe/tông môn vĩnh viễn (gia nhập, phản bội, rời bỏ, bị trục xuất)
- Lần đầu sở hữu vật phẩm/năng lực **định hình cả hành trình** (bảo vật cốt lõi, thiên phú nền tảng)
- Đột phá cảnh giới **ngưỡng phân nước** lần đầu — KHÔNG phải mọi cảnh giới.
  Ví dụ tu tiên: lần đầu Trúc Cơ / Kết Đan / Nguyên Anh / Hóa Thần... (6–8 mốc/1000 chương)
- Hình thành quan hệ trụ cột: đạo lữ, sư phụ chính, kẻ thù không đội trời chung — lần đầu
- Mất điều gì vĩnh viễn: người thân, cơ thể, năng lực — không thể phục hồi
- Quyết định định hướng 50+ chương sau (rẽ nhánh lớn không thể quay lại)
- Cận kề cái chết + thoát nạn bằng cách thay đổi bản thân (không phải thoát thông thường)

**Test nhanh:** "Nếu sự kiện này không xảy ra, nhân vật về sau có còn là cùng một người không?"
→ Không → major.

**Cách viết:**
- `event`: tiêu đề ngắn, nắm bắt được bản chất (≤ 12 từ)
- `desc`: 2–5 câu. Nêu: (a) bối cảnh ngắn, (b) điều xảy ra, (c) hệ quả tức thì hoặc ý nghĩa lâu dài.
  KHÔNG liệt kê, KHÔNG copy nguyên văn — diễn giải bằng ngôn ngữ phân tích.


### Mức 2 — Sự kiện (`importance: "normal"`, ribbon xanh)

**Định nghĩa:** Sự kiện đáng nhớ, có ảnh hưởng rõ trong arc đó nhưng không thay đổi bản chất nhân vật.
Viết vừa phải: đủ ngữ cảnh + kết quả.

**Cần ít nhất 1 tiêu chí:**
- Gặp nhân vật quan trọng lần đầu (không phải nhân vật CỰC kỳ trọng yếu)
- Học/nhận công pháp, kỹ năng đáng kể — dùng nhiều lần về sau
- Thu bảo vật tốt có tên riêng, ảnh hưởng rõ trong arc
- Chiến thắng/thất bại quyết định kết cục arc hiện tại
- Đột phá cảnh giới trung gian có tình tiết đặc biệt xung quanh
- Chuyển vùng hoạt động lớn (tiểu quốc → đại giới; hạ giới → thượng giới)
- Nhiệm vụ/phụ tuyến có tình tiết riêng ≥ 3 chương

**Dấu hiệu bổ trợ (không đủ một mình):**
- Tác giả dành ≥ 3 chương mô tả → ít nhất normal
- Sự kiện được nhắc lại bởi nhân vật khác ≥ 1 lần sau đó → ít nhất normal

**Test nhanh:** "Sự kiện này ảnh hưởng rõ đến ít nhất 10 chương sau không?" → Có → normal.

**Cách viết:**
- `event`: tiêu đề ngắn (≤ 10 từ)
- `desc`: 1–3 câu. Đủ ngữ cảnh + kết quả trực tiếp. Không cần phân tích ý nghĩa sâu.


### Mức 3 — Hành trình (`importance: "minor"`, ribbon xám)

**Định nghĩa:** Mốc nhỏ, ghi lại để không bỏ sót dòng thời gian nhưng không cần mô tả nhiều.

**Không qua được 2 mức trên — ví dụ điển hình:**
- Đột phá tiểu cảnh thông thường (tầng X → tầng X+1 trong cùng đại cảnh)
- Thu thập vật phẩm vô danh, linh thạch, nguyên liệu
- Di chuyển đơn thuần, tìm đường, ẩn náu
- Chiến đấu không tên, tiêu diệt quái thú/thủ hạ bình thường
- Gặp nhân vật phụ 1 lần không tái xuất
- Nghe tin tức, thu thập manh mối nhỏ

**Cách viết:**
- `event`: 1 câu đủ chủ thể + hành động + kết quả (≤ 15 từ)
- `desc`: BỎ TRỐNG hoặc tối đa 1 câu bổ sung nếu thực sự cần
- **Gom minor:** nếu có 3+ sự kiện minor liên tiếp cùng chủ đề → gom thành 1 entry.
  `event`: "Tu luyện Ngưng Khí tầng 8→12 trong Mộng Cảnh"
  `chapter`: chương đầu của chuỗi (hoặc range "41-55")


## 2. Quy tắc chống lạm dụng (BẮT BUỘC)

### Chống lạm dụng major — 3 bẫy phổ biến:
1. Không phải mọi đột phá cảnh giới đều là major. Nhân vật chính ~1000 chương thực sự
   chỉ có 6–8 ngưỡng phân nước. Đột phá Ngưng Khí tầng 5 là minor; lần đầu Trúc Cơ là major.
2. Không phải mọi trận thắng kẻ mạnh hơn đều là major — chỉ khi kết quả thay đổi vị thế
   dài hạn (được công nhận, mở ra vùng đất/cơ hội mới, triệt tiêu mối đe dọa cốt lõi).
3. Không phải mọi lần gặp nhân vật quan trọng đều là major — chỉ lần ĐẦU gặp nhân vật
   trụ cột + trong bối cảnh có tình tiết định hình quan hệ.

### Tỷ lệ khuyến nghị:
Major ~13% · Normal ~30% · Minor ~57%.
Nếu major > 20% → xem lại, có thể đang hạ tiêu chí.


## 3. Schema JSON + @block format

### Trong @timeline block (file .md):
```
@timeline
Ch.1   | Giai đoạn Phàm Nhân | Vào Hằng Nhạc phái học nghệ       | Thiếu niên phàm nhân Triệu quốc... | major
Ch.7   | Giai đoạn Phàm Nhân | Nhặt được Nghịch Thiên châu         | Khi rời phong nhẫn...               | major
Ch.23  | Giai đoạn Phàm Nhân | Khám phá Mộng Cảnh; gặp Tư Đồ Nam  | Lần đầu khai mở không gian...       | normal
Ch.45  | Giai đoạn Phàm Nhân | Tu luyện Ngưng Khí tầng 8→12        |                                     | minor
Ch.63  | Giai đoạn Ngưng Khí | Ngưng Khí viên mãn — tầng 15        | Vượt giới hạn thông thường...       | major
@end
```

Cột: `chapter | arc | event | desc | importance`
- `arc`: tên giai đoạn (dùng để tag nội bộ, KHÔNG hiển thị trên timeline web — web dùng ribbon màu thay)
- `importance`: `major` / `normal` / `minor` (KHÔNG dùng `true`/`false`)
- `desc` bỏ trống → parser hiểu là không có desc

### Trong characters.json (sau khi parse):
```json
{
  "chapter": 7,
  "arc": "Giai đoạn Phàm Nhân",
  "event": "Nhặt được Nghịch Thiên châu",
  "desc": "Khi rời Hằng Nhạc phái bị kẹt trong phong nhẫn...",
  "importance": "major"
}
```


## 4. Quy trình áp dụng khi viết/cập nhật

1. **Liệt kê nháp** toàn bộ sự kiện (mọi chương liên quan đến nhân vật) — dùng file chương JSON.
2. **Phân loại** từng sự kiện theo tiêu chí: chạy test 2 câu hỏi → gán importance.
3. **Kiểm tra tỷ lệ**: major quá nhiều → xem lại, nâng tiêu chí.
4. **Gom minor** liên tiếp cùng chủ đề.
5. **Viết desc** đúng độ dài theo mức.
6. **Xuất @timeline block** theo format cột chuẩn.

Không phải trả lời W2 hay W1 về lý do phân loại — tự phân loại, ghi kết quả.
Khi nhân vật tái xuất sau nhiều chương, đối chiếu timeline cũ trước khi thêm mốc mới.


## 5. Ghi chú cho bộ tu tiên (Tiên Nghịch, Phàm Nhân Tu Tiên, v.v.)

- Ngưỡng phân nước major: lần đầu mỗi đại cảnh lớn (Trúc Cơ, Kết Đan, Nguyên Anh, Hóa Thần...).
  Đột phá sơ/trung/hậu kỳ BÊN TRONG đại cảnh = normal nếu có tình tiết; minor nếu không.
- Nhặt bảo vật cốt lõi lần đầu = major. Nhặt bảo vật thứ yếu = normal/minor tùy ảnh hưởng.
- Gặp đạo lữ lần đầu (lúc chính thức thành đạo lữ) = major. Gặp lại sau khi xa cách = normal.
- Áp dụng tương tự cho thể loại khác: đô thị (thăng chức, hợp đồng lớn...),
  hệ thống (nhận nhiệm vụ chính tuyến...), kiếm hiệp (lên núi học kiếm, hạ sơn...).
