"""
merge_characters.py — Module GỘP nhân vật trùng cho pipeline W3 (Tiên Nghịch wiki).
Dùng ở bước parse .md -> JSON: sau khi gom tất cả bản ghi nhân vật, gọi merge_characters(chars)
để gộp các bản trùng (cùng người, khác hậu tố tên qua các đợt) thành 1 thẻ.

Quy tắc (chốt bởi W2, 2026-06-05):
- KHÓA GỘP = tên chuẩn hóa: bỏ phần Hán "(..)", bỏ hậu tố "— mô tả", bỏ chữ "cập nhật", bỏ "· ...".
- Trùng khóa -> chọn bản ĐẦY ĐỦ nhất làm canonical (nhiều detail + role/aff khác mặc định + có Hán).
- Gộp toàn bộ detail (khử trùng theo label+text), canonical trước; giữ phe/role/blurb của bản đầy đủ.
- KHÔNG tạo thẻ thứ 2. Giữ thứ tự xuất hiện đầu tiên. VL luôn ở đầu (do pipeline prepend).
"""
import re
from collections import defaultdict

def norm_key(name):
    s = name
    s = re.sub(r'[（(][^（）()]*[）)]', '', s)        # bỏ (...) kể cả Hán
    s = re.sub(r'\s*[—–-]\s*.*$', '', s)             # bỏ hậu tố "— mô tả/role"
    s = re.sub(r'(?i)\bcập nhật\b', '', s)
    s = re.sub(r'·.*$', '', s)
    return re.sub(r'\s+', ' ', s).strip().lower()

def _completeness(c):
    score = 0
    if c.get("role") not in (None, "", "neutral"): score += 2
    if c.get("affiliation") not in (None, "", "khac"): score += 2
    score += len(c.get("detail", []))
    score += len(c.get("blurb", "")) / 200.0
    if re.search(r'[（(][\u4e00-\u9fff]', c.get("name", "")): score += 0.5
    if re.search(r'(?i)cập nhật', c.get("name", "")): score -= 1
    return score

def _clean_name(name):
    s = re.sub(r'\s*[（(](?:CẬP NHẬT|cập nhật)[^（）()]*[）)]', '', name)
    s = re.sub(r'\s*[—–-]\s*\(?cập nhật[^)]*\)?', '', s, flags=re.I)
    s = re.sub(r'\s*\(cập nhật\)', '', s, flags=re.I)
    return re.sub(r'\s+', ' ', s).strip()

def merge_characters(chars):
    order, bucket = [], defaultdict(list)
    for c in chars:
        k = norm_key(c["name"])
        if k not in bucket: order.append(k)
        bucket[k].append(c)
    merged = []
    for k in order:
        items = bucket[k]
        if len(items) == 1:
            merged.append(items[0]); continue
        canon = max(items, key=_completeness)
        seen, details = set(), []
        for it in [canon] + [x for x in items if x is not canon]:
            for d in it.get("detail", []):
                sg = (d.get("label", "").strip(), d.get("text", "").strip())
                if sg in seen: continue
                seen.add(sg); details.append(d)
        out = dict(canon)
        out["name"] = _clean_name(canon["name"])
        out["detail"] = details
        out["blurb"] = max((x.get("blurb", "") for x in items), key=len)
        for x in sorted(items, key=_completeness, reverse=True):
            if x.get("role") not in (None, "", "neutral"):
                out["role"] = x["role"]; out["roleFilter"] = x["role"]; break
        for x in sorted(items, key=_completeness, reverse=True):
            if x.get("affiliation") not in (None, "", "khac"):
                out["affiliation"] = x["affiliation"]; break
        merged.append(out)
    return merged

def find_dup_groups(chars):
    g = defaultdict(list)
    for c in chars: g[norm_key(c["name"])].append(c["name"])
    return {k: v for k, v in g.items() if len(v) > 1}


# ============ FACTION DEDUP (W3, 2026-06-06) ============
# Gộp thế lực trùng: các mục "— CẬP NHẬT" / "(cập nhật)" gộp vào thế lực gốc,
# KHÔNG tạo card thứ 2. Dùng ở bước parse The_luc -> factions.json.

def fac_key(name):
    s = name
    s = re.sub(r'[（(][^（）()]*[）)]', '', s)
    s = re.sub(r'(?i)\s*[—–-]\s*cập nhật.*$', '', s)
    s = re.sub(r'(?i)\s*\(cập nhật[^)]*\)', '', s)
    s = re.sub(r'(?i)\bcập nhật\b', '', s)
    return re.sub(r'\s+', ' ', s).strip().lower()

def merge_factions(facs):
    order, bucket = [], defaultdict(list)
    for f in facs:
        k = fac_key(f["name"])
        if k not in bucket: order.append(k)
        bucket[k].append(f)
    out = []
    for k in order:
        items = bucket[k]
        if len(items) == 1:
            out.append(items[0]); continue
        canon = max(items, key=lambda x: len(x.get("detail", [])))
        seen, det = set(), []
        for it in [canon] + [x for x in items if x is not canon]:
            for d in it.get("detail", []):
                sg = (d.get("label", "").strip(), d.get("text", "").strip())
                if sg in seen: continue
                seen.add(sg); det.append(d)
        o = dict(canon)
        o["name"] = re.sub(r'(?i)\s*[—–-]\s*cập nhật.*$', '', canon["name"]).strip()
        o["name"] = re.sub(r'(?i)\s*\(cập nhật[^)]*\)', '', o["name"]).strip()
        o["detail"] = det
        for x in items:
            if x.get("type"): o["type"] = x["type"]; break
        for x in items:
            if x.get("typeLabel"): o["typeLabel"] = x["typeLabel"]; break
        for x in items:
            if x.get("blurb"): o["blurb"] = x["blurb"]; break
        out.append(o)
    return out

def find_fac_dup_groups(facs):
    g = defaultdict(list)
    for f in facs: g[fac_key(f["name"])].append(f["name"])
    return {k: v for k, v in g.items() if len(v) > 1}


# ============ SCHEMA NORMALIZATION (W3, 2026-06-06 — QC W1) ============
# Sửa GỐC LỖI: .md khai vaitro/phe ngoài schema web → pipeline phải normalize.
# role web hợp lệ: main | foe | friend | neutral
# affiliation web hợp lệ (Tiên Nghịch): chinh | hangnhac | huyendao | hohang | thiamtong | vanthientong | khac

ROLE_NORMALIZE = {"phu": "neutral", "dongminh": "friend", "main": "main",
                  "foe": "foe", "friend": "friend", "neutral": "neutral"}
AFF_NORMALIZE = {"trunglap": "khac"}  # các phe lạ khác → giữ nếu đã khai, else "khac"
VALID_AFF = {"chinh","hangnhac","huyendao","hohang","thiamtong","vanthientong","khac"}

# Heading KHÔNG phải nhân vật (parser bỏ qua) — tránh thẻ rác trên web
NOTE_HEADING_PREFIXES = ("Cập nhật hồ sơ", "Ghi chú", "=== ", "===")

def is_note_heading(name):
    n = name.strip()
    if n.lower().startswith("ghi chú"): return True
    if n.startswith("Cập nhật hồ sơ"): return True
    if n.startswith("===") or n.startswith("=== "): return True
    return False

def normalize_char(c):
    # role
    r = c.get("role", "neutral")
    c["role"] = ROLE_NORMALIZE.get(r, "neutral")
    c["roleFilter"] = c["role"]
    # affiliation
    a = c.get("affiliation", "khac")
    if a in AFF_NORMALIZE: a = AFF_NORMALIZE[a]
    if a not in VALID_AFF: a = "khac"
    c["affiliation"] = a
    # strip stray "Cập nhật:" name prefix
    c["name"] = re.sub(r'(?i)^\s*cập nhật\s*[:：]\s*', '', c["name"]).strip()
    return c

def clean_realm_status(status):
    # field status chỉ nhận known|unknown; giải thích để trong blurb/detail
    s = (status or "known").strip().lower()
    return "unknown" if s.startswith("unknown") else "known"
