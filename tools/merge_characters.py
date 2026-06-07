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


# ============ GENERIC ENTITY DEDUP (W3, 2026-06-06 — task TẬN GỐC W2) ============
# Dùng CHUNG cho artifacts/realms/factions (và characters phụ trợ). Khóa LOWERCASE,
# bỏ Hán/(..), bỏ hậu tố "— ...", bỏ "(cập nhật...)"/"cập nhật", bỏ "· ...".
# Mục tiêu: pipeline lượt sau KHÔNG tái sinh pháp bảo/cảnh giới/thế lực trùng
# (vd "Mặc Gian thạch" vs "Mặc gian thạch" — khác hoa thường vẫn gộp nhờ lowercase).

def entity_key(name):
    s = name
    s = re.sub(r'[（(][^（）()]*[）)]', '', s)
    s = re.sub(r'(?i)\s*[—–-]\s*cập nhật.*$', '', s)
    s = re.sub(r'(?i)\s*\(cập nhật[^)]*\)', '', s)
    s = re.sub(r'(?i)\bcập nhật\b', '', s)
    s = re.sub(r'·.*$', '', s)
    return re.sub(r'\s+', ' ', s).strip().lower()

def _clean_entity_name(name):
    s = re.sub(r'(?i)\s*[—–-]\s*cập nhật.*$', '', name)
    s = re.sub(r'(?i)\s*\(cập nhật[^)]*\)', '', s)
    s = re.sub(r'(?i)\s*·\s*\(?cập nhật[^)]*\)?', '', s)
    return re.sub(r'\s+', ' ', s).strip()

# các field "đặc tính" cần giữ giá trị KHÔNG rỗng/không mặc định khi gộp
_PREFER_FIELDS = ("type", "typeLabel", "category", "categoryLabel", "cn", "status", "blurb")

def merge_entities(items, keep_fields=_PREFER_FIELDS):
    """Gộp list dict có 'name' + (tùy chọn) 'detail'. Giữ thứ tự xuất hiện đầu;
    canonical = bản nhiều detail nhất; gộp detail (khử trùng theo label+text);
    với mỗi field trong keep_fields, lấy giá trị non-empty đầu tiên."""
    order, bucket = [], defaultdict(list)
    for it in items:
        k = entity_key(it.get("name", ""))
        if k not in bucket: order.append(k)
        bucket[k].append(it)
    out = []
    for k in order:
        grp = bucket[k]
        if len(grp) == 1:
            o = dict(grp[0]); o["name"] = _clean_entity_name(o["name"]); out.append(o); continue
        canon = max(grp, key=lambda x: len(x.get("detail", [])))
        seen, det = set(), []
        for it in [canon] + [x for x in grp if x is not canon]:
            for d in it.get("detail", []):
                sg = (d.get("label", "").strip(), d.get("text", "").strip())
                if sg in seen: continue
                seen.add(sg); det.append(d)
        o = dict(canon)
        o["name"] = _clean_entity_name(canon["name"])
        if "detail" in canon or det: o["detail"] = det
        for f in keep_fields:
            val = next((x[f] for x in grp if x.get(f) not in (None, "", "khac", "neutral")), None)
            if val is not None: o[f] = val
        out.append(o)
    return out

def find_entity_dups(items):
    g = defaultdict(list)
    for it in items: g[entity_key(it.get("name", ""))].append(it.get("name", ""))
    return {k: v for k, v in g.items() if len(v) > 1}

# Wrapper tiện dụng cho pipeline (gọi ở bước parse -> JSON):
def merge_artifacts(items): return merge_entities(items)
def merge_realms(items):    return merge_entities(items)
# merge_factions() đã có ở trên; merge_characters() giữ riêng (có _completeness role/aff).
# KHUYẾN NGHỊ pipeline: characters -> merge_characters(); artifacts -> merge_artifacts();
#   realms -> merge_realms(); factions -> merge_factions(). Tất cả khóa đều lowercase.


# ============ PARSE @BLOCKS STRUCTURED (W3, 2026-06-07 — KHUNG HIỂN THỊ CHUẨN v2) ============
# Đọc 5 khối @bio/@timeline/@cultivation/@relations/@inventory trong text nhân vật.
# Injected vào entry JSON dưới đúng key (bio, timeline, cultivation, relations, inventory).
# Pipeline gọi inject_at_blocks(entry, char_text) ngay sau khi tạo entry nhân vật.

_VALID_RTYPES = {"daolu", "giađình", "banhuu", "anthan", "dottu", "kethu"}
_VALID_CATS_INV = {"baovat","dandung","vatpham","thientai","congphap","khanang","tienthuat","bua"}
_VALID_INV_STATUS = {"con","mat","dalung","datang","donghop","bicuop","hong"}

def _parse_bio_block(lines):
    bio = {}
    for ln in lines:
        ln = ln.strip()
        if not ln or ":" not in ln: continue
        k, _, v = ln.partition(":")
        k, v = k.strip().lower(), v.strip()
        if not k or not v: continue
        if k in ("personality", "specialties"):
            bio[k] = [x.strip() for x in v.split("|") if x.strip()]
        elif k == "firstchapter":
            try: bio["firstChapter"] = int(v)
            except: bio["firstChapter"] = v
        else:
            bio[k] = v
    return bio

def _parse_timeline_block(lines):
    items = []
    for ln in lines:
        ln = ln.strip()
        if not ln: continue
        parts = [p.strip() for p in ln.split("|")]
        if len(parts) < 3: continue
        chapter_raw = parts[0].lstrip("Ch.").strip()
        try: ch = int(chapter_raw.split("-")[0].split("~")[-1].replace("(","").strip())
        except: ch = 0
        major = len(parts) > 4 and parts[4].strip().lower() in ("major","true","1")
        items.append({"chapter": ch, "arc": parts[1], "event": parts[2],
                      "desc": parts[3] if len(parts) > 3 else "", "major": major})
    return items

def _parse_cultivation_block(lines):
    items = []
    for ln in lines:
        ln = ln.strip()
        if not ln: continue
        parts = [p.strip() for p in ln.split("|")]
        if len(parts) < 2: continue
        chapter_raw = parts[1].lstrip("Ch.").strip()
        chapter_raw = re.sub(r"[(].*?[)]","",chapter_raw).split("-")[0].strip() or "0"
        try: ch = int(chapter_raw)
        except: ch = 0
        items.append({"realm": parts[0], "chapter": ch,
                      "location": parts[2] if len(parts) > 2 else "",
                      "gained":   parts[3] if len(parts) > 3 else "",
                      "congphap": parts[4] if len(parts) > 4 else ""})
    return sorted(items, key=lambda x: x["chapter"])

def _parse_relations_block(lines):
    items = []
    for ln in lines:
        ln = ln.strip()
        if not ln: continue
        parts = [p.strip() for p in ln.split("|")]
        if len(parts) < 2: continue
        rtype = parts[1].lower()
        if rtype not in _VALID_RTYPES: rtype = "banhuu"
        items.append({"name": parts[0], "type": rtype,
                      "desc": parts[2] if len(parts) > 2 else ""})
    return items

def _parse_inventory_block(lines):
    items = []
    for ln in lines:
        ln = ln.strip()
        if not ln: continue
        parts = [p.strip() for p in ln.split("|")]
        if len(parts) < 3: continue
        cat    = parts[1].lower() if len(parts) > 1 else "vatpham"
        status = parts[2].lower() if len(parts) > 2 else "con"
        if cat    not in _VALID_CATS_INV:  cat    = "vatpham"
        if status not in _VALID_INV_STATUS: status = "con"
        items.append({"name": parts[0], "cat": cat, "status": status,
                      "desc":   parts[3] if len(parts) > 3 else "",
                      "effect": parts[4] if len(parts) > 4 else ""})
    return items

_AT_PARSERS = {
    "bio":         _parse_bio_block,
    "timeline":    _parse_timeline_block,
    "cultivation": _parse_cultivation_block,
    "relations":   _parse_relations_block,
    "inventory":   _parse_inventory_block,
}

def parse_at_blocks(text):
    """Trích xuất tất cả @tag...@end blocks từ text nhân vật. Trả dict {tag: data}."""
    result = {}
    pattern = re.compile(
        r"@(bio|timeline|cultivation|relations|inventory)\b([\s\S]*?)@end",
        re.IGNORECASE
    )
    for m in pattern.finditer(text):
        tag   = m.group(1).lower()
        body  = m.group(2)
        lines = body.strip().splitlines()
        parser = _AT_PARSERS.get(tag)
        if parser:
            parsed = parser(lines)
            if parsed:
                result[tag] = parsed
    return result

def inject_at_blocks(entry, text):
    """Parse @blocks từ text rồi inject vào entry dict (bio/timeline/cultivation/relations/inventory)."""
    blocks = parse_at_blocks(text)
    for k, v in blocks.items():
        if v:
            entry[k] = v
    return entry
