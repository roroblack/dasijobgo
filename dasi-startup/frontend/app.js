/* 다시,출근 — 창업 지원 트랙 SPA (START + 7 STEP).
   결정론 계산(적합도 4축·후보 필터·상권 지표)은 백엔드 호출 결과를 그대로 표시.
   AI는 후보·근거·위험까지, 결정과 확신은 사람의 몫(계획서 경계선 원칙). 프론트는 '표현'만. */
'use strict';
const API = '';

// ── 접근성: 글자 크기 ──
(function () {
  const label = { '15': '작게 (15px)', '17': '보통 (17px)', '20': '크게 (20px)' };
  const cur = document.getElementById('fsCur');
  document.querySelectorAll('.fs-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      document.documentElement.style.setProperty('--fs-base', btn.dataset.fs + 'px');
      document.querySelectorAll('.fs-btn').forEach((b) => b.setAttribute('aria-pressed', String(b === btn)));
      if (cur) cur.textContent = label[btn.dataset.fs] || (btn.dataset.fs + 'px');
    });
  });
})();

// ── 세션 상태 ──
const S = {
  session_id: 'demo-' + Math.floor(Date.now() / 1000),
  profile: { years: 0, skills: [], region: '' }, jobKind: '', onbStep: 0,
  startup: { capital: 'unknown', storefront_ok: true, physical_ok: true }, slotStep: 0,
  fitAxes: { business_orientation: 50, interpersonal: 50, problem_solving: 50, persuasion: 50 },
  fitQ: 0, fitResult: null,
  candidates: [], chosen: null, chosenName: '', reviewed: [], programs: [],
};

// ── 화면 크롬 ──
const ORDER = ['start', 'onboard', 'slots', 'fit', 'candidates', 'market', 'roadmap', 'handoff'];
const TITLE = {
  start: '다시,출근', onboard: '경력 들려주기', slots: '창업 정보 보충', fit: '진로 성향 진단',
  candidates: '업종 후보', market: '상권·리스크', roadmap: '준비 로드맵', handoff: '전문가 연결',
};
const $ = (id) => document.getElementById(id);
let cur = null; const histStack = [];
const RENDER = {};

function srcPill(s) {
  const cls = s === 'live' ? 'src-live' : s === 'seed' ? 'src-seed' : s === 'rule' ? 'src-rule' : 'src-fallback';
  return `<span class="src-pill ${cls}">${s}</span>`;
}
async function api(path, payload, method) {
  const opt = { method: method || 'POST' };
  if (payload) { opt.headers = { 'Content-Type': 'application/json' }; opt.body = JSON.stringify(payload); }
  const res = await fetch(API + path, opt);
  const json = await res.json();
  if (!json.ok) throw new Error(json.error ? json.error.message : ('HTTP ' + res.status));
  return json;
}
function chrome(key, titleOverride) {
  const idx = ORDER.indexOf(key);
  const isStart = key === 'start';
  $('logo').style.display = isStart ? '' : 'none';
  $('title').style.display = isStart ? 'none' : '';
  $('title').textContent = titleOverride || TITLE[key] || '';
  $('prog').textContent = isStart ? '' : (idx + 1) + ' / ' + ORDER.length;
  $('pbarFill').style.width = Math.round(((idx + 1) / ORDER.length) * 100) + '%';
  $('backBtn').disabled = histStack.length === 0;
}
function paint(html) { $('main').innerHTML = html; window.scrollTo(0, 0); }
function loading(msg) { paint(`<div class="loading"><span class="spin"></span>${msg}</div>`); }
function bind(id, fn) { const el = $(id); if (el) el.onclick = fn; }
function goto(key, opts = {}) { if (cur && opts.push !== false) histStack.push(cur); cur = key; RENDER[key](); }
function goBack() { if (!histStack.length) return; cur = histStack.pop(); RENDER[cur](); }
$('backBtn').onclick = goBack;
function showError(e, retry) {
  paint(`<div class="err">문제가 생겼어요: ${e.message}</div><button class="cta" id="rt">다시 시도</button>`);
  bind('rt', retry);
}

// ── 브라우저 TTS(상담사 음성 안내) ──
let _koVoice = null;
function _pickVoice() { const vs = window.speechSynthesis ? speechSynthesis.getVoices() : []; _koVoice = vs.find((v) => /ko/i.test(v.lang || '')) || null; }
if (window.speechSynthesis) { _pickVoice(); try { speechSynthesis.onvoiceschanged = _pickVoice; } catch (e) {} }
function speak(t) {
  try { if (!window.speechSynthesis || !t) return; speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(String(t).replace(/^"|"$/g, '')); u.lang = 'ko-KR'; if (_koVoice) u.voice = _koVoice; u.rate = 0.98; speechSynthesis.speak(u);
  } catch (e) {}
}
// ── 온보딩 마이크: 눌러 녹음 → /stt 전사 ──
let _micRec = null, _micChunks = [], _micStream = null;
async function micToggle(btn, onText) {
  if (_micRec && _micRec.state === 'recording') { _micRec.stop(); return; }
  try { _micStream = await navigator.mediaDevices.getUserMedia({ audio: true }); } catch (e) { onText('__nomic__'); return; }
  _micChunks = []; _micRec = new MediaRecorder(_micStream);
  _micRec.ondataavailable = (ev) => { if (ev.data && ev.data.size) _micChunks.push(ev.data); };
  _micRec.onstop = async () => {
    if (_micStream) { _micStream.getTracks().forEach((t) => t.stop()); _micStream = null; }
    btn.textContent = '🎤';
    const blob = new Blob(_micChunks, { type: 'audio/webm' });
    if (blob.size < 2500) { onText('__tooshort__'); _micRec = null; return; }
    onText('__transcribing__');
    try { const fd = new FormData(); fd.append('audio', blob, 'clip.webm');
      const r = await fetch(API + '/stt', { method: 'POST', body: fd }); const j = await r.json();
      onText(j.ok ? (j.data.text || '') : '__unavail__');
    } catch (e) { onText('__unavail__'); }
    _micRec = null;
  };
  _micRec.start(); btn.textContent = '⏹'; onText('__recording__');
}
function matchChip(step, text) {
  const t = (text || '').replace(/\s/g, '');
  if (step.key === 'years') { const m = t.match(/(\d+)/); if (m) { const n = +m[1]; let bi = -1, bd = 1e9; step.chips.forEach((c, i) => { const d = Math.abs(c[1] - n); if (d < bd) { bd = d; bi = i; } }); return bi; } }
  for (let i = 0; i < step.chips.length; i++) { const toks = step.chips[i][0].split(/[·\s]+/).filter((x) => x.length >= 2); if (toks.some((k) => t.includes(k.replace(/\s/g, '')))) return i; }
  return -1;
}

// ===== START =====
RENDER.start = function () {
  chrome('start'); histStack.length = 0;
  paint(`
    <div class="eyebrow">상담사와 함께하는 AI 경력 진단</div>
    <div class="k-h">내 경력, 다시 보면<br><span class="u">새로운 길</span>이 보여요</div>
    <div class="k-sub">복잡한 입력은 상담사님이 도와드려요. 편하게 말씀만 하시면 됩니다.</div>
    <div class="i4"><div class="n gold">🏆</div><div class="tx"><b>완주하면 리워드를 드려요.</b> 진단·후보 탐색·준비 로드맵까지 마치면 실물 혜택으로 교환할 수 있어요.</div></div>
    <div class="hero-consult"><div class="av">🧑‍💼</div><div><div style="font-size:15px;font-weight:700">담당 상담사: 김은주 팀장</div><div style="font-size:12.5px;color:var(--ink-2);margin-top:3px">한마음 재취업지원센터 · 오늘 진단을 함께 진행해요</div></div></div>
    <div class="terms"><span>이용약관</span><span>개인정보처리방침</span></div>
    <button class="cta gold" id="go">상담사와 진단 시작하기 🏆</button>`);
  bind('go', () => goto('onboard'));
};

// ===== STEP 1: 경력 온보딩(공통 재사용) =====
const ONB = [
  { q: '어떤 일을 해오셨는지 편하게 말씀해 주세요.', key: 'job',
    chips: [['품질관리·검사', ['품질관리', '검사장비', '불량분석'], '품질관리·검사'],
            ['생산관리', ['생산관리', '공정관리'], '생산관리'],
            ['설비보전', ['설비보전', '전기', '정비'], '설비보전'],
            ['물류·현장', ['현장관리', '안전관리'], '물류·현장']] },
  { q: '그 일을 몇 년 정도 하셨어요?', key: 'years', chips: [['5년', 5], ['10년', 10], ['15년', 15], ['20년 이상', 20]] },
  { q: '어느 지역에서 하실 생각이세요?', key: 'region',
    chips: [['인천 남동구', '인천 남동구'], ['인천 부평구', '인천 부평구'], ['경기 시흥시', '경기 시흥시'], ['서울', '서울']] },
];
function chipStep(scr, list, step, q, onPick, extra) {
  const answered = [];
  for (let i = 0; i < step; i++) { answered.push(`<div class="bubble ai">${list[i].q}</div>`); if (list[i]._picked !== undefined) answered.push(`<div class="bubble me">"${list[i]._picked}"</div>`); }
  paint(`
    ${extra || ''}
    <div class="chat">${answered.join('')}<div class="bubble ai"><div class="who">AI 상담사</div>${q.q}</div></div>
    <div class="chips" id="chips">${q.chips.map((c, i) => `<span class="chip" data-i="${i}">${c[0]}</span>`).join('')}</div>
    <div class="big-input"><div class="txt" id="micTxt">눌러서 말하기…</div><button class="mic-btn" id="micBtn">🎤</button></div>`);
  if (S._spoken !== scr + step) { speak(q.q); S._spoken = scr + step; }
  $('chips').querySelectorAll('.chip').forEach((el) => { el.onclick = () => onPick(q.chips[+el.dataset.i]); });
  const micTxt = $('micTxt');
  bind('micBtn', () => micToggle($('micBtn'), (t) => {
    const M = { __recording__: '● 녹음 중… (다 말씀하고 다시 누르세요)', __transcribing__: '전사 중…', __tooshort__: '🎤 너무 짧아요 · 다시 눌러 주세요', __nomic__: '🎤 마이크 없음 · 아래에서 골라주세요', __unavail__: 'STT 미설정 · 아래에서 골라주세요' };
    if (M[t]) { micTxt.textContent = M[t]; return; }
    micTxt.textContent = t ? '“' + t + '”' : '(안 들렸어요) 다시 말씀해 주세요';
    const idx = matchChip(q, t); if (idx >= 0) setTimeout(() => $('chips').querySelectorAll('.chip')[idx].click(), 500);
  }));
}
RENDER.onboard = function () {
  chrome('onboard');
  if (S.onbStep < ONB.length) {
    const step = ONB[S.onbStep];
    chipStep('onb', ONB, S.onbStep, step, (c) => {
      step._picked = c[0];
      if (step.key === 'job') { S.jobKind = c[2]; S.profile.skills = c[1]; }
      else if (step.key === 'years') S.profile.years = c[1];
      else if (step.key === 'region') S.profile.region = c[1];
      S.onbStep++; RENDER.onboard();
    }, `<div class="eyebrow">STEP 1 · 경력 온보딩</div><div class="k-h" style="font-size:22px">어떤 일을 <span class="u">해오셨나요?</span></div>`);
  } else {
    loading('경력을 정리하는 중…');
    api('/onboarding', { session_id: S.session_id, years: S.profile.years, skills: S.profile.skills, region: S.profile.region })
      .then(() => goto('slots')).catch((e) => showError(e, () => RENDER.onboard()));
  }
};

// ===== STEP 2: 창업 슬롯 3종 =====
const SLOTS = [
  { q: '준비하신 자금은 어느 정도 범위인가요?', key: 'capital',
    chips: [['3천만원 이하', 'under_3000'], ['3천~7천만원', '3000_7000'], ['7천만원~1.5억', '7000_15000'], ['잘 모르겠어요', 'unknown']] },
  { q: '가게 자리를 얻으실 생각인가요?', key: 'storefront_ok', chips: [['점포 없이 시작', false], ['점포를 얻을 생각', true]] },
  { q: '몸을 많이 쓰는 일도 괜찮으세요?', key: 'physical_ok', chips: [['괜찮아요', true], ['무리는 어려워요', false]] },
];
RENDER.slots = function () {
  chrome('slots');
  if (S.slotStep < SLOTS.length) {
    const step = SLOTS[S.slotStep];
    chipStep('slot', SLOTS, S.slotStep, step, (c) => {
      step._picked = c[0]; S.startup[step.key] = c[1]; S.slotStep++; RENDER.slots();
    }, `<div class="eyebrow">STEP 2 · 창업 정보 보충</div><div class="k-h" style="font-size:22px">세 가지만 <span class="u">더 여쭐게요</span></div><div class="k-sub">${S.jobKind || '현장'} ${S.profile.years}년 경력은 이미 알고 있어요.</div>`);
  } else { goto('fit'); }
};

// ===== STEP 3: 성향 진단 + 분기 =====
const FITQ = [
  { q: '퇴직 후 다시 일한다면, 어느 쪽이 더 끌리세요?', a: [
      { t: '새로운 조직에 소속되고 싶다', d: { business_orientation: -20, interpersonal: 15 } },
      { t: '내 이름을 걸고 혼자 해보고 싶다', d: { business_orientation: 25, persuasion: 10 } }] },
  { q: '언제 더 뿌듯하셨어요?', a: [
      { t: '후배를 가르칠 때', d: { interpersonal: 20, persuasion: 15 } },
      { t: '직접 현장을 뛸 때', d: { problem_solving: 20 } }] },
  { q: '익숙함과 새로움, 어느 쪽이세요?', a: [
      { t: '익숙한 걸 잘하는 게 편해요', d: { business_orientation: -10, problem_solving: -5 } },
      { t: '새로운 문제 해결이 즐거워요', d: { problem_solving: 20, business_orientation: 10 } }] },
];
RENDER.fit = function () {
  chrome('fit');
  if (S.fitQ < FITQ.length) {
    const q = FITQ[S.fitQ];
    const answered = [];
    for (let i = 0; i < S.fitQ; i++) if (FITQ[i]._picked !== undefined) { answered.push(`<div class="bubble ai">${FITQ[i].q}</div>`); answered.push(`<div class="bubble me">"${FITQ[i]._picked}"</div>`); }
    paint(`
      <div class="eyebrow">STEP 3 · 진로 성향 진단</div>
      <div class="k-h" style="font-size:22px">정답은 없어요, <span class="u">편하게</span></div>
      <div class="chat">${answered.join('')}<div class="bubble ai"><div class="who">AI 진단 도우미</div>${q.q}</div></div>
      <div class="chips" id="chips">${q.a.map((o, i) => `<span class="chip" data-i="${i}">${o.t}</span>`).join('')}</div>`);
    if (S._spoken !== 'fit' + S.fitQ) { speak(q.q); S._spoken = 'fit' + S.fitQ; }
    $('chips').querySelectorAll('.chip').forEach((el) => { el.onclick = () => {
      const o = q.a[+el.dataset.i]; q._picked = o.t;
      Object.entries(o.d).forEach(([k, v]) => { S.fitAxes[k] = (S.fitAxes[k] || 50) + v; });
      S.fitQ++; RENDER.fit();
    }; });
  } else {
    loading('성향을 분석하는 중…');
    api('/fit', { axis_scores: S.fitAxes }).then((r) => {
      S.fitResult = r.data;
      const d = r.data;
      paint(`
        <div class="eyebrow">두 갈래 길, 함께 볼 수 있어요</div>
        <div class="k-h" style="font-size:22px">회사로 <span class="u">돌아가는 길</span>과<br>내 일을 <span class="u">시작하는 길</span></div>
        <div class="fitcard">
          <div class="fit-label">참고용 적합도 · 방금 나눈 대화를 바탕으로 ${srcPill(r.meta.source)}</div>
          <div class="fitrow"><span class="fit-name">재취업이 좀 더 편한 편이에요<span class="pct">${d.reemploy_fit}%</span></span><div class="fitbar"><i style="width:${d.reemploy_fit}%"></i></div></div>
          <div class="fitrow"><span class="fit-name">창업 성향도 있는 편이에요<span class="pct">${d.startup_fit}%</span></span><div class="fitbar alt"><i style="width:${d.startup_fit}%"></i></div></div>
          <div class="fit-note">고용24 창업적성검사와 같은 4개 기준(사업지향성·대인관계·문제해결·설득력)으로 계산했어요. <b>점수와 상관없이 두 갈래 다 선택하실 수 있어요.</b> 결정은 회원님 몫입니다.</div>
        </div>
        <div class="forkcard" id="forkReemploy"><div class="fk-ic">🏢</div><div class="fk-t">다시, 출근하기</div><div class="fk-d">경력에 맞는 회사를 찾아 이력서부터 면접까지. (재취업 트랙)</div><div class="fk-tag">기존 재취업 트랙</div></div>
        <div class="forkcard on" id="forkStartup"><div class="fk-ic">🏪</div><div class="fk-t">내 일 시작하기</div><div class="fk-d">30년 경력으로 할 수 있는 업종 후보를 근거·위험과 함께 보여드립니다. <b>결정을 대신하지 않습니다.</b></div><div class="fk-tag" style="color:var(--apricot);background:#fff">창업 탐색 트랙 · 선택됨</div></div>
        <button class="cta" id="go">창업 탐색 시작하기</button>`);
      bind('go', () => goto('candidates'));
      bind('forkStartup', () => goto('candidates'));
      bind('forkReemploy', () => paint2Reemploy());
    }).catch((e) => showError(e, () => RENDER.fit()));
  }
};
function paint2Reemploy() {
  $('main').insertAdjacentHTML('beforeend', `<div class="info-strip">🏢 재취업 트랙은 별도 앱(포트 8090)에서 진행돼요. 여기서는 <b>창업 탐색</b>을 이어갑니다.</div>`);
}

// ===== STEP 4: 업종 후보 카드(킬러) =====
RENDER.candidates = function () {
  chrome('candidates');
  loading('경력을 해석해 업종 후보를 찾는 중…');
  api('/candidates', { skills: S.profile.skills, capital: S.startup.capital, storefront_ok: S.startup.storefront_ok, physical_ok: S.startup.physical_ok, top: 4 })
    .then((r) => {
      const d = r.data; S.candidates = d.candidates;
      const cards = d.candidates.map((c) => `
        <div class="bcard">
          <div class="top"><div><div class="co">${c.name}</div><div class="role">${c.sub}</div></div><div class="fit">${c.fit_label}</div></div>
          <div class="why">💡 <b>왜 추천?</b> ${c.why}</div>
          <div class="risk">⚠ <b>위험</b> ${c.risk}</div>
          <div class="fund">🏛 <b>지원</b> ${c.fund}</div>
          <div class="meta"><span>초기비용 ~${c.init_cost}만</span><span>${c.storefront ? '점포' : '무점포'}</span><span>신체부담 ${c.physical_load === 'high' ? '높음' : c.physical_load === 'mid' ? '보통' : '낮음'}</span>${c.matched_skills.length ? `<span>경력 매칭: ${c.matched_skills.join('·')}</span>` : ''}</div>
          <button class="detail-btn" data-id="${c.id}" data-name="${c.name}">상권·리스크 자세히 보기</button>
        </div>`).join('');
      paint(`
        <div class="eyebrow">STEP 4 · 업종 후보 ${srcPill(r.meta.source)}</div>
        <div class="k-h" style="font-size:22px">경력으로 할 수 있는 <span class="u">${d.count}가지</span></div>
        <div class="k-sub">근거와 위험을 <b>함께</b> 보세요. 장밋빛 추천은 하지 않아요.</div>
        ${d.filtered_out ? `<div class="info-strip">🔎 조건(자금·점포·신체)에 맞지 않는 ${d.filtered_out}개 후보는 제외했어요.</div>` : ''}
        ${cards}
        <div class="info-strip danger">🚫 <b>수익 예측은 하지 않습니다.</b> "월 얼마 법니다"는 아무도 보장할 수 없어요. 판단에 필요한 사실만 보여드립니다.</div>`);
      $('main').querySelectorAll('.detail-btn').forEach((el) => { el.onclick = () => { S.chosen = el.dataset.id; S.chosenName = el.dataset.name; if (!S.reviewed.includes(S.chosen)) S.reviewed.push(S.chosen); goto('market'); }; });
    }).catch((e) => showError(e, () => RENDER.candidates()));
};

// ===== STEP 5: 상권·리스크 리포트 =====
RENDER.market = function () {
  chrome('market', S.chosenName + ' · 상세');
  loading('동네 데이터로 검증하는 중…');
  api('/market/' + S.chosen, null, 'GET').then((r) => {
    const d = r.data;
    paint(`
      <div class="eyebrow">STEP 5 · 상권·리스크 검증 ${srcPill(r.meta.source)}</div>
      <div class="k-h" style="font-size:22px">${d.name}</div>
      <div class="stats">${d.stats.map((s) => `<div class="stat"><div class="v ${s.tone}">${s.value}</div><div class="l">${s.label}</div></div>`).join('')}</div>
      <div class="k-sub">${d.market_note}</div>
      <div class="cite">📄 <b>출처를 반드시 함께 보여드립니다</b><span class="src">${d.sources.map((s) => `· ${s.label}: ${s.org}`).join('<br>')}</span></div>
      <div class="info-strip danger">🚫 <b>수익 예측은 하지 않습니다.</b> 판단에 필요한 사실(잠재고객·경쟁·생존율)과 출처만 제공합니다.</div>
      <button class="cta" id="go">준비 절차 보기</button>`);
    bind('go', () => goto('roadmap'));
  }).catch((e) => showError(e, () => RENDER.market()));
};

// ===== STEP 6: 준비 로드맵 + 지원사업 =====
RENDER.roadmap = function () {
  chrome('roadmap', S.chosenName + ' · 준비');
  loading('준비 절차와 지원사업을 찾는 중…');
  api('/roadmap/' + S.chosen, null, 'GET').then((r) => {
    const d = r.data; S.programs = d.programs.map((p) => p.title);
    const icons = { education: '🎓', fund: '💰', space: '🏢' };
    paint(`
      <div class="eyebrow">STEP 6 · 준비 로드맵 ${srcPill(r.meta.source)}</div>
      <div class="k-h" style="font-size:22px"><span class="u">순서대로</span> 하나씩</div>
      <div class="k-sub">신청 가능한 지원사업은 자동으로 찾았어요.</div>
      <div class="cart">${d.checklist.map((c) => `<div class="citem"><div class="chk ${c.kind === 'ok' ? 'ok' : c.kind === 'link' ? 'link' : ''}">${c.n}</div><div><div class="co">${c.title}</div><div class="st ${c.kind === 'ok' ? 'ok' : c.kind === 'link' ? 'link' : ''}">${c.note}</div></div></div>`).join('')}</div>
      <div style="font-size:13px;font-weight:700;color:var(--ink-3);margin-top:4px">매칭된 지원사업</div>
      <div class="cart">${d.programs.map((p) => `<div class="pol"><div class="ic ${p.kind === 'fund' ? 'a' : p.kind === 'space' ? 'b' : ''}">${icons[p.kind] || '📌'}</div><div><div class="tt">${p.title}</div><div class="ds">${p.org} · ${p.amount}</div></div><span class="badge ${p.badge === '자격 충족' ? '' : 'cond'}">${p.badge}</span></div>`).join('')}</div>
      <button class="cta" id="go">이 계획서로 전문가 만나기</button>`);
    bind('go', () => goto('handoff'));
  }).catch((e) => showError(e, () => RENDER.roadmap()));
};

// ===== STEP 7: 전문가 핸드오프 =====
RENDER.handoff = function () {
  chrome('handoff');
  loading('개인 리포트를 만드는 중…');
  api('/handoff', { name: '김○○', career: `${S.jobKind || '현장'} ${S.profile.years}년`, candidate_ids: S.reviewed, programs: S.programs })
    .then((r) => {
      const d = r.data;
      paint(`
        <div class="eyebrow">STEP 7 · 전문가 핸드오프</div>
        <div class="k-h" style="font-size:22px">확인은 <span class="u">사람과 함께</span></div>
        <div class="paper">
          <h4>나의 창업 탐색 리포트</h4>
          <div class="pl">이름 · 경력</div><div class="pv">${d.name} 님 · ${d.career}</div>
          <div class="pl">검토한 후보</div><div class="pv">${d.reviewed.length ? d.reviewed.map((x, i) => `${i + 1}. ${x.name} (${x.risk})`).join('<br>') : '검토한 후보 없음'}</div>
          <div class="pl">확인된 지원사업</div><div class="pv">${d.programs.length ? d.programs.join(', ') : '—'}</div>
          <div class="pl">요약</div><div class="pv">${d.summary} ${srcPill(r.meta.source)}</div>
        </div>
        <div class="k-sub" style="font-size:13.5px">이 리포트를 <b style="color:var(--brand)">인쇄해 들고 가시면</b> 상담사님이 처음부터 다시 묻지 않고 바로 본론으로 들어갈 수 있어요.</div>
        <div class="confirm"><div class="big">📅 ${d.handoff.org} 상담 예약</div><div class="k-sub" style="font-size:13px;margin:0">인천 남동구 센터 · 목요일 오전 10시 가능</div><div class="meet">🖨 리포트 인쇄 · 문자로 받기</div></div>
        <div class="loopbanner">
          <div class="badge">설계 원칙 — 제출 버튼은 사람이 누른다의 창업판</div>
          <div class="lt">AI는 <span class="em">후보와 근거</span>까지,<br><span class="em">결정과 확신</span>은 사람의 몫</div>
          <div class="bound">
            <div class="bcol yes"><h5>AI가 하는 것</h5><ul><li>경력→업종 후보 도출</li><li>상권·폐업률로 필터</li><li>위험 요인 병기</li><li>지원사업 매칭</li></ul></div>
            <div class="bcol no"><h5>AI가 안 하는 것</h5><ul><li>"이 업종 하세요" 단정</li><li>매출·성공률 예측</li><li>자금 투입 판단</li><li>전문가 상담 대체</li></ul></div>
          </div>
        </div>
        <button class="cta brand" id="go">상담 예약하고 마치기</button>
        <button class="text-link" id="go2">처음부터 다시 체험</button>`);
      bind('go', () => {
        paint(`<div class="loading" style="padding:70px 0">✅ 상담 예약이 접수됐어요.<br>수고하셨습니다 — 결정은 천천히, 전문가와 함께 하세요.</div><button class="cta" id="again">처음부터 다시</button>`);
        bind('again', resetAll);
      });
      bind('go2', resetAll);
    }).catch((e) => showError(e, () => RENDER.handoff()));
};

function resetAll() {
  Object.assign(S, {
    profile: { years: 0, skills: [], region: '' }, jobKind: '', onbStep: 0,
    startup: { capital: 'unknown', storefront_ok: true, physical_ok: true }, slotStep: 0,
    fitAxes: { business_orientation: 50, interpersonal: 50, problem_solving: 50, persuasion: 50 },
    fitQ: 0, fitResult: null, candidates: [], chosen: null, chosenName: '', reviewed: [], programs: [],
  });
  ONB.forEach((o) => delete o._picked); SLOTS.forEach((o) => delete o._picked); FITQ.forEach((o) => delete o._picked);
  histStack.length = 0; goto('start', { push: false });
}

// ── 부팅 ──
goto('start', { push: false });
