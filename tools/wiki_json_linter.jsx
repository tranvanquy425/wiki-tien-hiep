import { useState, useCallback } from "react";

const GH_BASE =
  "https://raw.githubusercontent.com/tranvanquy425/wiki-tien-hiep/main/data";

const VALID_CATS = new Set([
  "baovat","bua","congphap","dandung","khanang","tienthuat","vatpham",
]);
const VALID_ROLES  = new Set(["main","foe","friend","neutral"]);
const VALID_PHE    = new Set(["chinh","hangnhac","huyendao","thiamtong","hohang","khac"]);
const VALID_STATUS = new Set(["known","unknown"]);

function findUnclosedTags(text = "") {
  const tags = ["strong","em","b","i","u","span","p","div","a"];
  const issues = [];
  for (const tag of tags) {
    const opens  = (text.match(new RegExp(`<${tag}[\\s>]`, "gi")) || []).length;
    const closes = (text.match(new RegExp(`</${tag}>`, "gi")) || []).length;
    if (opens !== closes)
      issues.push(`<${tag}>: ${opens} mở / ${closes} đóng`);
  }
  return issues;
}

function normalizeName(name = "") {
  return name
    .replace(/\s*\([^)]*[\u4e00-\u9fff][^)]*\)/g, "")
    .replace(/\s*\(cập nhật[^)]*\)/gi, "")
    .replace(/\s*[—–-]\s*.+$/, "")
    .trim()
    .toLowerCase();
}

function auditChar(char) {
  const errs = [];
  if (!char.name)        errs.push("Thiếu name");
  if (!char.role)        errs.push("Thiếu role");
  else if (!VALID_ROLES.has(char.role))   errs.push(`role không hợp lệ: "${char.role}"`);
  if (!char.affiliation) errs.push("Thiếu affiliation (phe)");
  else if (!VALID_PHE.has(char.affiliation)) errs.push(`affiliation không hợp lệ: "${char.affiliation}"`);
  if (!char.blurb)       errs.push("blurb trống");
  else if (char.blurb.length < 8) errs.push(`blurb quá ngắn (${char.blurb.length} ký tự)`);
  if (!char.detail || char.detail.length === 0) errs.push("detail rỗng");
  const htmlSrc = [char.blurb || "", ...(char.detail || []).map(d => d.text || "")];
  for (const txt of htmlSrc) {
    const issues = findUnclosedTags(txt);
    if (issues.length) errs.push(`Thẻ HTML hở: ${issues.join(", ")}`);
  }
  return errs;
}

function auditRealm(realm) {
  const errs = [];
  if (!realm.name)   errs.push("Thiếu name");
  if (!realm.cn)     errs.push("Thiếu cn");
  if (!realm.status) errs.push("Thiếu status");
  else if (!VALID_STATUS.has(realm.status)) errs.push(`status không hợp lệ: "${realm.status}"`);
  if (!realm.blurb || realm.blurb.length < 5) errs.push("blurb trống/quá ngắn");
  const htmlSrc = [realm.blurb || "", ...(realm.detail || []).map(d => d.text || "")];
  for (const txt of htmlSrc) {
    const issues = findUnclosedTags(txt);
    if (issues.length) errs.push(`Thẻ HTML hở: ${issues.join(", ")}`);
  }
  return errs;
}

function auditArtifact(art) {
  const errs = [];
  if (!art.name)     errs.push("Thiếu name");
  if (!art.category) errs.push("Thiếu category");
  else if (!VALID_CATS.has(art.category)) errs.push(`category không hợp lệ: "${art.category}"`);
  if (!art.status)   errs.push("Thiếu status");
  if (!art.blurb || art.blurb.length < 5) errs.push("blurb trống/quá ngắn");
  const htmlSrc = [art.blurb || "", ...(art.detail || []).map(d => d.text || "")];
  for (const txt of htmlSrc) {
    const issues = findUnclosedTags(txt);
    if (issues.length) errs.push(`Thẻ HTML hở: ${issues.join(", ")}`);
  }
  return errs;
}

function auditFaction(fac) {
  const errs = [];
  if (!fac.name) errs.push("Thiếu name");
  if (!fac.type) errs.push("Thiếu type");
  if (!fac.blurb || fac.blurb.length < 5) errs.push("blurb trống/quá ngắn");
  const htmlSrc = [fac.blurb || "", ...(fac.detail || []).map(d => d.text || "")];
  for (const txt of htmlSrc) {
    const issues = findUnclosedTags(txt);
    if (issues.length) errs.push(`Thẻ HTML hở: ${issues.join(", ")}`);
  }
  return errs;
}

function findDuplicateChars(chars) {
  const map = new Map();
  for (const c of chars) {
    const key = normalizeName(c.name);
    if (!key) continue;
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(c.name);
  }
  return [...map.entries()]
    .filter(([, names]) => names.length > 1)
    .map(([key, names]) => ({ key, names }));
}

function runAudit(data) {
  const rep = {
    characters: { count: 0, actual: 0, itemErrors: [], duplicates: [] },
    realms:     { count: 0, actual: 0, itemErrors: [] },
    artifacts:  { count: 0, actual: 0, itemErrors: [] },
    factions:   { count: 0, actual: 0, itemErrors: [] },
    totalErrors: 0,
  };
  if (data.characters) {
    const d = data.characters; const items = d.chars || [];
    rep.characters.count = d.count || 0; rep.characters.actual = items.length;
    items.forEach((c, i) => { const e = auditChar(c); if (e.length) rep.characters.itemErrors.push({ name: c.name || `#${i}`, errs: e }); });
    rep.characters.duplicates = findDuplicateChars(items);
  }
  if (data.realms) {
    const d = data.realms; const items = d.realms || [];
    rep.realms.count = d.count || 0; rep.realms.actual = items.length;
    items.forEach((r, i) => { const e = auditRealm(r); if (e.length) rep.realms.itemErrors.push({ name: r.name || `#${i}`, errs: e }); });
  }
  if (data.artifacts) {
    const d = data.artifacts; const items = d.artifacts || [];
    rep.artifacts.count = d.count || 0; rep.artifacts.actual = items.length;
    items.forEach((a, i) => { const e = auditArtifact(a); if (e.length) rep.artifacts.itemErrors.push({ name: a.name || `#${i}`, errs: e }); });
  }
  if (data.factions) {
    const d = data.factions; const items = d.factions || [];
    rep.factions.count = d.count || 0; rep.factions.actual = items.length;
    items.forEach((f, i) => { const e = auditFaction(f); if (e.length) rep.factions.itemErrors.push({ name: f.name || `#${i}`, errs: e }); });
  }
  const allSec = [rep.characters, rep.realms, rep.artifacts, rep.factions];
  for (const s of allSec) {
    if (s.count !== s.actual && (s.count > 0 || s.actual > 0)) rep.totalErrors++;
    rep.totalErrors += s.itemErrors.length;
    rep.totalErrors += (s.duplicates || []).length;
  }
  return rep;
}

const pill = (color, text) => (
  <span style={{background:color,color:"#fff",borderRadius:12,padding:"2px 10px",fontSize:12,fontWeight:700,marginLeft:6}}>{text}</span>
);

function SectionReport({ title, rep, hasDuplicates }) {
  const [open, setOpen] = useState(true);
  const countOk = rep.count === rep.actual;
  const noErr = rep.itemErrors.length === 0;
  const noDup = !hasDuplicates || rep.duplicates.length === 0;
  const allOk = countOk && noErr && noDup;
  return (
    <div style={{marginBottom:20,border:"1px solid #e0e0e0",borderRadius:10,overflow:"hidden"}}>
      <div onClick={()=>setOpen(o=>!o)} style={{background:allOk?"#e8f5e9":"#fce4ec",padding:"10px 16px",display:"flex",alignItems:"center",gap:8,cursor:"pointer",userSelect:"none"}}>
        <span style={{fontSize:18}}>{allOk?"✅":"❌"}</span>
        <strong style={{fontSize:15}}>{title}</strong>
        {pill("#555",`${rep.actual} mục`)}
        {!countOk&&pill("#c62828",`count sai: ${rep.count}→${rep.actual}`)}
        {rep.itemErrors.length>0&&pill("#e65100",`${rep.itemErrors.length} item lỗi`)}
        {hasDuplicates&&rep.duplicates.length>0&&pill("#6a1b9a",`${rep.duplicates.length} nhóm trùng`)}
        <span style={{marginLeft:"auto",color:"#888"}}>{open?"▲":"▼"}</span>
      </div>
      {open&&!allOk&&(
        <div style={{padding:"10px 16px"}}>
          {!countOk&&<div style={{color:"#c62828",marginBottom:8}}>⚠️ <strong>count không khớp</strong>: khai báo {rep.count}, thực {rep.actual}. Sửa field <code>count</code> trong JSON.</div>}
          {rep.itemErrors.length>0&&<>
            <div style={{fontWeight:600,marginBottom:6,color:"#e65100"}}>Lỗi theo item:</div>
            {rep.itemErrors.map(({name,errs},i)=>(
              <div key={i} style={{background:"#fff8f0",border:"1px solid #ffe0b2",borderRadius:6,padding:"6px 12px",marginBottom:6}}>
                <strong>{name}</strong>
                <ul style={{margin:"4px 0 0 16px",padding:0}}>
                  {errs.map((e,j)=><li key={j} style={{color:"#bf360c",fontSize:13}}>{e}</li>)}
                </ul>
              </div>
            ))}
          </>}
          {hasDuplicates&&rep.duplicates.length>0&&<>
            <div style={{fontWeight:600,marginBottom:6,color:"#6a1b9a"}}>Nhân vật trùng (1 người nhiều thẻ):</div>
            {rep.duplicates.map(({key,names},i)=>(
              <div key={i} style={{background:"#f3e5f5",border:"1px solid #ce93d8",borderRadius:6,padding:"6px 12px",marginBottom:6}}>
                <strong>Khóa: "{key}"</strong> — {names.length} bản:
                <ul style={{margin:"4px 0 0 16px"}}>
                  {names.map((n,j)=><li key={j} style={{fontSize:13}}>{n}</li>)}
                </ul>
              </div>
            ))}
          </>}
        </div>
      )}
    </div>
  );
}

export default function WikiJsonLinter() {
  const [loading, setLoading] = useState(false);
  const [report, setReport]   = useState(null);
  const [error, setError]     = useState("");
  const [tab, setTab]         = useState("auto");
  const [paste, setPaste]     = useState({characters:"",realms:"",artifacts:"",factions:""});
  const [updatedAt, setUpdatedAt] = useState({});

  const fetchAndAudit = useCallback(async () => {
    setLoading(true); setError(""); setReport(null);
    try {
      const keys = ["characters","realms","artifacts","factions"];
      const fetched = {}; const dates = {};
      await Promise.all(keys.map(async k => {
        const r = await fetch(`${GH_BASE}/${k}.json?t=${Date.now()}`);
        if (!r.ok) throw new Error(`Không tải được ${k}.json (HTTP ${r.status})`);
        const d = await r.json();
        fetched[k] = d; dates[k] = d.updatedAt || "?";
      }));
      setUpdatedAt(dates); setReport(runAudit(fetched));
    } catch(e) { setError(e.message); }
    finally { setLoading(false); }
  }, []);

  const auditPaste = useCallback(() => {
    setError(""); setReport(null);
    try {
      const parsed = {};
      for (const k of ["characters","realms","artifacts","factions"]) {
        if (paste[k].trim()) parsed[k] = JSON.parse(paste[k]);
      }
      if (!Object.keys(parsed).length) { setError("Chưa dán JSON nào."); return; }
      setReport(runAudit(parsed));
    } catch(e) { setError("Lỗi parse JSON: "+e.message); }
  }, [paste]);

  return (
    <div style={{fontFamily:"'Segoe UI',sans-serif",maxWidth:860,margin:"0 auto",padding:"20px 16px"}}>
      <div style={{textAlign:"center",marginBottom:24}}>
        <h1 style={{margin:0,fontSize:22,color:"#1a237e"}}>🔍 Wiki JSON Linter — Tiên Nghịch</h1>
        <p style={{color:"#555",margin:"6px 0 0"}}>Soát lỗi 4 JSON trước commit: thẻ HTML hở · count lệch · category sai · trùng nhân vật · thẻ mỏng</p>
      </div>
      <div style={{display:"flex",gap:8,marginBottom:16}}>
        {["auto","paste"].map(t=>(
          <button key={t} onClick={()=>setTab(t)} style={{padding:"8px 20px",borderRadius:8,border:"none",cursor:"pointer",fontWeight:600,background:tab===t?"#1a237e":"#e8eaf6",color:tab===t?"#fff":"#333"}}>
            {t==="auto"?"🌐 Kéo từ GitHub":"📋 Dán JSON tay"}
          </button>
        ))}
      </div>
      {tab==="auto"&&(
        <div style={{background:"#e8eaf6",borderRadius:10,padding:16,marginBottom:20}}>
          <p style={{margin:"0 0 10px",fontSize:13}}>Fetch <code>data/*.json</code> từ repo <strong>tranvanquy425/wiki-tien-hiep</strong> (branch main).</p>
          <button onClick={fetchAndAudit} disabled={loading} style={{padding:"10px 28px",background:loading?"#9e9e9e":"#1a237e",color:"#fff",border:"none",borderRadius:8,fontWeight:700,fontSize:15,cursor:loading?"not-allowed":"pointer"}}>
            {loading?"⏳ Đang tải...":"▶ Chạy soát"}
          </button>
          {Object.keys(updatedAt).length>0&&<div style={{marginTop:10,fontSize:12,color:"#555"}}>updatedAt: {Object.entries(updatedAt).map(([k,v])=>`${k}=${v}`).join(" · ")}</div>}
        </div>
      )}
      {tab==="paste"&&(
        <div style={{background:"#f3e5f5",borderRadius:10,padding:16,marginBottom:20}}>
          <p style={{margin:"0 0 12px",fontSize:13}}>Dán nội dung từng JSON (bỏ trống file không cần soát).</p>
          {["characters","realms","artifacts","factions"].map(k=>(
            <div key={k} style={{marginBottom:12}}>
              <label style={{fontWeight:600,display:"block",marginBottom:4}}>{k}.json:</label>
              <textarea rows={4} style={{width:"100%",borderRadius:6,border:"1px solid #ce93d8",padding:8,fontFamily:"monospace",fontSize:12,boxSizing:"border-box"}}
                placeholder={`Dán ${k}.json vào đây...`} value={paste[k]}
                onChange={e=>setPaste(p=>({...p,[k]:e.target.value}))}/>
            </div>
          ))}
          <button onClick={auditPaste} style={{padding:"10px 28px",background:"#6a1b9a",color:"#fff",border:"none",borderRadius:8,fontWeight:700,fontSize:15,cursor:"pointer"}}>▶ Soát JSON đã dán</button>
        </div>
      )}
      {error&&<div style={{background:"#ffebee",border:"1px solid #ef9a9a",borderRadius:8,padding:12,color:"#b71c1c",marginBottom:16}}>❌ {error}</div>}
      {report&&<>
        <div style={{background:report.totalErrors===0?"#e8f5e9":"#fce4ec",border:`2px solid ${report.totalErrors===0?"#66bb6a":"#ef5350"}`,borderRadius:10,padding:"12px 16px",marginBottom:20,display:"flex",alignItems:"center",gap:12}}>
          <span style={{fontSize:28}}>{report.totalErrors===0?"🎉":"⚠️"}</span>
          <div>
            <strong style={{fontSize:16}}>{report.totalErrors===0?"Tất cả OK — commit an toàn!":report.totalErrors+" lỗi cần sửa trước khi commit"}</strong>
            <div style={{fontSize:13,color:"#555",marginTop:2}}>chars:{report.characters.actual} · realms:{report.realms.actual} · artifacts:{report.artifacts.actual} · factions:{report.factions.actual}</div>
          </div>
        </div>
        <SectionReport title="👤 characters.json" rep={report.characters} hasDuplicates />
        <SectionReport title="🏔️ realms.json"     rep={report.realms}     hasDuplicates={false}/>
        <SectionReport title="⚔️  artifacts.json" rep={report.artifacts}  hasDuplicates={false}/>
        <SectionReport title="🏯 factions.json"   rep={report.factions}   hasDuplicates={false}/>
        <div style={{background:"#f5f5f5",borderRadius:8,padding:14,fontSize:13,color:"#444"}}>
          <strong>Hướng dẫn sửa nhanh:</strong>
          <ul style={{margin:"6px 0 0 16px"}}>
            <li><strong>Thẻ HTML hở</strong>: sửa file .md nguồn (He_thong/Nhan_vat) → chạy lại pipeline → commit.</li>
            <li><strong>category không hợp lệ</strong>: sửa <code>cat:</code> trong He_thong .md. Hợp lệ: <code>baovat bua congphap dandung khanang tienthuat vatpham</code>.</li>
            <li><strong>count không khớp</strong>: sửa field <code>count</code> trong JSON bằng số phần tử thực.</li>
            <li><strong>Nhân vật trùng</strong>: gộp detail, xóa bản thừa → chạy lại pipeline → commit.</li>
          </ul>
        </div>
      </>}
    </div>
  );
}
