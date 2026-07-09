/* 다시,출근 — 데스크탑 웹 컨트롤러 (init_plans/*_화면흐름_목업_PC.html GUI 재현).
   결정론 계산(매칭 점수·일정 교집합·역량 등급)은 백엔드 호출 결과를 그대로 표시한다.
   아바타·음질·합불 등 실측 없는 값은 화면에 seed 로 표기(RULE §1). 프론트는 '표현'만. */
'use strict';

const API = ''; // 같은 오리진(FastAPI StaticFiles).

// ---------- 접근성: 글자 크기 (15/17/20px, 기본 17px) ----------
(function initFontToggle() {
  const label = { '15': '작게 (15px)', '17': '보통 (17px)', '20': '크게 (20px)' };
  const cur = document.getElementById('fsCur');
  document.querySelectorAll('.fs-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const px = btn.dataset.fs;
      document.documentElement.style.setProperty('--fs-base', px + 'px');
      document.querySelectorAll('.fs-btn').forEach((b) => b.setAttribute('aria-pressed', String(b === btn)));
      if (cur) cur.textContent = label[px] || (px + 'px');
    });
  });
})();

// ---------- 세션 상태 ----------
const S = {
  session_id: 'demo-' + Math.floor(Date.now() / 1000),
  profile: { years: 0, skills: [], region: '' },
  jobKind: '', onbStep: 0,
  jobs: [], cart: [], resumeIdx: 0, resumes: {}, gapSkills: [], submitSel: {},
  interviewJob: null, interviewCompany: '', questions: [], qIndex: 0,
  scheduleJob: null, candidateSlots: [], confirmed: null,
};

// ---------- 화면 크롬 설정 ----------
const NAV = [['✍️', '내 이야기'], ['💼', '맞춤 일자리'], ['🎓', '정부 지원·교육'], ['📋', '내 지원 현황']];
const CHROME = {
  start:     { addr: '/',               nav: 0, navFirst: ['🏠', '홈'] },
  onboard:   { addr: '/onboarding',     nav: 0 },
  review:    { addr: '/resume/확인',     nav: 0 },
  match:     { addr: '/matching',       nav: 1 },
  cart:      { addr: '/cart',           nav: 1 },
  resume:    { addr: '/resume',         nav: 1 },
  submit:    { addr: '/submit',         nav: 1 },
  prep:      { addr: '/interview/setup', nav: 3, nav3: ['🎥', '면접 준비'], rec: true },
  interview: { addr: '/interview',      nav: 3, nav3: ['🎥', '면접 진행 중'], rec: true },
  feedback:  { addr: '/status',         nav: 3 },
  schedule:  { addr: '/schedule',       nav: 3 },
  reeducate: { addr: '/growth',         nav: 2 },
};
// 모바일 앱바용 순서·제목 (좁은 화면 진행 표시)
const ORDER = ['start', 'onboard', 'review', 'match', 'cart', 'resume', 'submit', 'prep', 'interview', 'feedback', 'schedule', 'reeducate'];
const MTITLE = {
  start: '다시,출근', onboard: '내 이야기 들려주기', review: '이력서 확인', match: '나에게 맞는 일자리',
  cart: '담아둔 일자리', resume: '맞춤 이력서', submit: '지원서 최종 확인', prep: 'AI 면접 준비',
  interview: 'AI 면접 진행 중', feedback: '피드백 & 결과 대기', schedule: '실면접 일정', reeducate: '다음 기회 준비',
};

// ---------- DOM ----------
const $ = (id) => document.getElementById(id);
let cur = null;
const histStack = [];
let sideCollapsed = false; // 데스크탑 사이드바 접기 상태

function srcPill(source) {
  const cls = source === 'live' ? 'src-live' : (source === 'seed' ? 'src-seed' : 'src-fallback');
  return `<span class="src-pill ${cls}">${source}</span>`;
}
async function api(path, payload) {
  const res = await fetch(API + path, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
  });
  const json = await res.json();
  if (!json.ok) throw new Error(json.error ? json.error.message : ('HTTP ' + res.status));
  return json;
}

function renderSidebar(c) {
  const items = NAV.map(([ic, label], i) => {
    if (i === 0 && c.navFirst) [ic, label] = c.navFirst;
    if (i === 3 && c.nav3) [ic, label] = c.nav3;
    return `<div class="nav-item${i === c.nav ? ' on' : ''}"><span class="ni">${ic}</span><span class="nlabel">${label}</span></div>`;
  }).join('');
  const foot = c.rec
    ? `<div class="help" style="background:var(--sage-tint);color:var(--sage)">● 녹화 중<div style="font-size:0.74rem;font-weight:400;margin-top:4px">답변은 회원님만 다시 볼 수 있어요</div></div>`
    : `<div class="collapse-btn" id="collapseBtn">${sideCollapsed ? '▶' : '◀ 메뉴 접기'}</div>`;
  const logo = sideCollapsed
    ? `<div class="logo">다</div>`
    : `<div class="logo">다시,출근<small>중장년 재취업</small></div>`;
  $('side').innerHTML = `${logo}${items}<div class="sp"></div>${foot}`;
  $('app').classList.toggle('collapsed', sideCollapsed);
  const cb = $('collapseBtn');
  if (cb) cb.onclick = () => { sideCollapsed = !sideCollapsed; renderSidebar(c); };
}
function renderChrome(key, addrOverride) {
  const c = CHROME[key];
  renderSidebar(c);
  $('addr').textContent = 'dasi-chulgeun.kr' + (addrOverride || c.addr);
  $('backBtn').disabled = histStack.length === 0;
  // 모바일 앱바(좁은 화면) — 제목·진행·뒤로가기
  const idx = ORDER.indexOf(key);
  $('mtitle').textContent = MTITLE[key] || '다시,출근';
  $('mprog').textContent = (idx + 1) + ' / ' + ORDER.length;
  $('mpbarFill').style.width = Math.round(((idx + 1) / ORDER.length) * 100) + '%';
  $('mback').disabled = histStack.length === 0;
}
function setCtx(html) {
  const ctx = $('ctx'), app = $('app');
  if (html) { ctx.innerHTML = html; ctx.style.display = ''; app.classList.add('with-ctx'); }
  else { ctx.style.display = 'none'; app.classList.remove('with-ctx'); }
}
function paint(html) { $('main').innerHTML = html; }
function loading(msg) { $('main').innerHTML = `<div class="loading"><span class="spin"></span>${msg}</div>`; }
function bind(id, fn) { const el = $(id); if (el) el.onclick = fn; }

function goto(key, opts = {}) {
  if (cur && opts.push !== false) histStack.push(cur);
  cur = key;
  RENDER[key]();
}
function goBack() {
  if (!histStack.length) return;
  cur = histStack.pop();
  RENDER[cur]();
}
$('backBtn').onclick = goBack;
$('mback').onclick = goBack;

const RENDER = {};

// ===== 시작 =====
RENDER.start = function () {
  renderChrome('start'); setCtx(null);
  paint(`
    <div class="eyebrow">45세 이상 재취업 지원</div>
    <div class="page-h">다시 일하기, <span class="u">여기서 함께</span> 시작해요</div>
    <div class="page-sub">복잡한 절차는 저희가 대신합니다. 결정은 언제나 본인이 하세요.</div>
    <div style="font-size:0.86rem;font-weight:700;color:var(--ink-3);margin:8px 0 12px">지금 받을 수 있는 정부 지원 ↓ ${srcPill('seed')}</div>
    <div class="benefit-grid">
      <div class="benefit"><div class="bic g">💰</div><div><div class="btt">중장년 취업성공수당</div><div class="bds">재취업 성공 시 단계별 지급</div><div class="bamt">예시 · 최대 150만원</div></div></div>
      <div class="benefit"><div class="bic a">🎓</div><div><div class="btt">내일배움카드 직업훈련</div><div class="bds">부족한 역량, 국비로 다시 배우기</div><div class="bamt">예시 · 최대 500만원 한도</div></div></div>
      <div class="benefit"><div class="bic b">🏢</div><div><div class="btt">고령자 고용지원금 기업</div><div class="bds">중장년 채용에 적극적인 회사 우선 매칭</div></div></div>
      <div class="benefit"><div class="bic g">📞</div><div><div class="btt">중장년내일센터 상담</div><div class="bds">가까운 센터에서 1:1 대면 지원</div></div></div>
    </div>
    <button class="cta full big brand" id="go">상담 시작하기</button>`);
  bind('go', () => goto('onboard'));
};

// ===== STEP 1: 온보딩 =====
const ONB = [
  { q: '어떤 일을 해오셨는지 편하게 말씀해 주세요. 말씀하시는 대로 이력서가 채워집니다.', key: 'job',
    chips: [['품질관리·검사', ['품질관리', '검사장비', '불량분석'], '품질관리·검사'],
            ['생산관리', ['생산관리', '공정관리', '불량분석'], '생산관리'],
            ['물류·현장', ['현장관리', '안전관리'], '물류·현장'],
            ['설비보전', ['설비보전', '전기'], '설비보전']] },
  { q: '오래 하셨네요. 그 일을 몇 년 정도 하셨어요?', key: 'years',
    chips: [['3년', 3], ['5년', 5], ['10년', 10], ['15년 이상', 15]] },
  { q: '어느 지역에서 일하고 싶으세요?', key: 'region',
    chips: [['인천 남동구', '인천 남동구'], ['인천 부평구', '인천 부평구'],
            ['경기 시흥시', '경기 시흥시'], ['서울', '서울']] },
];
function ctxResume() {
  const done = (v) => v ? '<span class="rd done">✓</span>' : '<span class="rd">○</span>';
  const now = '<span class="rd now">●</span>';
  const pct = Math.round((S.onbStep / ONB.length) * 100);
  const jobV = S.jobKind || '<span class="rv wait">듣고 있어요…</span>';
  const careerV = (S.jobKind && S.profile.years) ? `${S.jobKind} ${S.profile.years}년` : '<span class="rv wait">아직</span>';
  const skillV = S.profile.skills.length ? S.profile.skills.join(' · ') : '<span class="rv wait">아직</span>';
  const wishV = S.profile.region ? `${S.profile.region} / 주 5일` : '<span class="rv wait">아직</span>';
  return `<div class="ctx-t">실시간 지원서</div>
    <div class="resume-mini">
      <div class="rm-top"><span class="rm-t">📝 채워지는 중</span><span class="rm-pct">${pct}%</span></div>
      <div class="rm-bar"><i style="width:${pct}%"></i></div>
      <div class="rm-row"><span class="rk">직무</span><span class="rv">${jobV}</span>${S.jobKind ? done(true) : now}</div>
      <div class="rm-row"><span class="rk">경력</span><span class="rv">${careerV}</span>${done(!!(S.jobKind && S.profile.years))}</div>
      <div class="rm-row"><span class="rk">강점</span><span class="rv">${skillV}</span>${done(S.profile.skills.length > 0)}</div>
      <div class="rm-row"><span class="rk">희망 조건</span><span class="rv">${wishV}</span>${done(!!S.profile.region)}</div>
    </div>
    <div class="info-strip"><span class="ii">💡</span>말할수록 지원서가 채워집니다. 다 채우면 맞는 일자리를 찾아드려요.</div>`;
}
RENDER.onboard = function () {
  renderChrome('onboard'); setCtx(ctxResume());
  const answered = [];
  for (let i = 0; i < S.onbStep; i++) {
    answered.push(`<div class="bubble ai"><div class="who">AI 상담사</div>${ONB[i].q}</div>`);
    if (ONB[i]._picked !== undefined) answered.push(`<div class="bubble me"><div class="who">나</div>"${ONB[i]._picked}"</div>`);
  }
  if (S.onbStep < ONB.length) {
    const step = ONB[S.onbStep];
    paint(`
      <div class="page-h">어떤 일을 <span class="u">해오셨나요?</span></div>
      <div class="page-sub">편하게 말씀하시면 됩니다. 골라주시면 그대로 이력서가 채워져요.</div>
      <div class="chat">${answered.join('')}
        <div class="bubble ai"><div class="who">AI 상담사</div>${step.q}</div></div>
      <div class="opt-chips" id="chips">
        ${step.chips.map((c, i) => `<span class="opt-chip" data-i="${i}">${c[0]}</span>`).join('')}
      </div>
      <div class="big-input"><div class="txt" id="micTxt">눌러서 이어 말하기…</div><div class="mic-btn" id="micBtn" title="눌러서 말하기">🎤</div></div>
      <div class="alt-row"><div class="alt-btn brand">📎 진로 설계서 올리기</div><div class="alt-btn">⌨️ 글자로 입력하기</div></div>`);
    if (S._spokenStep !== S.onbStep) { speak(step.q); S._spokenStep = S.onbStep; }  // 상담사가 이 파트를 음성 안내(파트당 1회)
    $('chips').querySelectorAll('.opt-chip').forEach((el) => {
      el.onclick = () => {
        const c = step.chips[+el.dataset.i];
        step._picked = c[0];
        if (step.key === 'job') { S.profile.skills = c[1]; S.jobKind = c[2]; }
        else if (step.key === 'years') S.profile.years = c[1];
        else if (step.key === 'region') S.profile.region = c[1];
        S.onbStep++;
        RENDER.onboard();
      };
    });
    // 마이크 = 눌러 녹음 → (종료 시) 전사 → 현재 파트 채움 → 상담사가 다음 파트 안내
    const micTxt = $('micTxt');
    if ($('micBtn')) $('micBtn').onclick = () => micToggle($('micBtn'), (t) => {
      const M = { __recording__: '● 녹음 중… (다 말씀하시고 다시 누르세요)', __transcribing__: '전사 중…',
                  __tooshort__: '🎤 너무 짧아요 · 다시 눌러 또박또박 말씀해 주세요',
                  __nomic__: '🎤 마이크를 쓸 수 없어요 · 아래에서 골라주세요', __unavail__: 'STT 미설정 · 아래에서 골라주세요' };
      if (M[t]) { micTxt.textContent = M[t]; return; }
      micTxt.textContent = t ? '“' + t + '”' : '(안 들렸어요) 다시 말씀해 주세요';
      const idx = matchChip(step, t);       // 전사 → 현재 파트 칩 매칭 → 채움+다음 파트로(상담사 안내는 re-render의 speak)
      if (idx >= 0) setTimeout(() => $('chips').querySelectorAll('.opt-chip')[idx].click(), 500);
    });
  } else {
    loading('경력을 정리하는 중…');
    api('/onboarding', { session_id: S.session_id, years: S.profile.years, skills: S.profile.skills, region: S.profile.region })
      .then((r) => {
        setCtx(ctxResume());
        paint(`
          <div class="page-h">이력서가 <span class="u">거의 완성</span>됐어요</div>
          <div class="page-sub">말씀하신 내용으로 정리했어요. 확인만 하면 바로 일자리를 찾아드립니다.</div>
          <div class="chat">${answered.join('')}
            <div class="bubble ai"><div class="who">AI 상담사</div>${r.data.message} ${srcPill(r.meta.source)}</div></div>
          <button class="cta full brand" id="go">이 이력서 확인하기</button>`);
        bind('go', () => goto('review'));
      }).catch((e) => showError(e, () => RENDER.onboard()));
  }
};

// ===== STEP 1.5: 이력서 확인 =====
RENDER.review = function () {
  renderChrome('review'); setCtx(null);
  const skills = S.profile.skills.join(' · ') || '현장 경험';
  paint(`
    <div class="eyebrow">말씀하신 내용으로 정리했어요</div>
    <div class="page-h"><span class="u">이대로 맞나요?</span></div>
    <div class="page-sub">매칭 전에 지금까지 채워진 이력서를 확인·수정하고 넘어갑니다.</div>
    <div class="resume-doc">
      <h4>내 이력서 · ${S.jobKind || '현장 직무'}</h4>
      <div class="rfield"><div class="rl">경력</div><div class="rv">${S.jobKind || '현장'} <span class="hl">${S.profile.years}년</span></div></div>
      <div class="rfield"><div class="rl">주요 성과</div><div class="rv">현장 개선·품질 향상 경험 (상담 내용 기반 자동 정리)</div></div>
      <div class="rfield" style="margin-bottom:0"><div class="rl">보유 역량</div><div class="rv">${skills}</div></div>
    </div>
    <div class="info-strip"><span class="ii">✏️</span>각 항목을 눌러 직접 수정할 수 있어요. 빠진 곳은 이어서 채워드립니다. ${srcPill('seed')}</div>
    <button class="cta full brand" id="go">이 이력서로 일자리 찾기</button>`);
  bind('go', () => goto('match'));
};

// ===== STEP 2: 매칭 =====
RENDER.match = function () {
  renderChrome('match'); setCtx(null);
  loading('적합도를 계산하는 중…');
  api('/matching', { years: S.profile.years, skills: S.profile.skills, region: S.profile.region, top: 4 })
    .then((r) => {
      S.jobs = r.data.jobs;
      paint(`
        <div class="page-h">회원님께 맞는 <span class="u">${r.data.count}곳</span>을 찾았어요 ${srcPill(r.meta.source)}</div>
        <div class="page-sub">적합도만이 아니라 "왜 맞는지" 이유도 함께 봐주세요.</div>
        <div class="match-grid" id="grid">${S.jobs.map(jobCard).join('')}</div>
        <div class="cta-row"><button class="cta brand" id="go">${cartLabel()}</button></div>`);
      bindCards();
    }).catch((e) => showError(e, () => RENDER.match()));
};
function jobCard(j) {
  const inCart = S.cart.some((c) => c.job_id === j.job_id);
  return `<div class="ccard ${inCart ? 'added' : ''}" data-job="${j.job_id}">
    <div class="top"><div><div class="co">${j.company}</div><div class="role">${j.role} · ${j.region}</div></div>
      <div class="fit">적합도<br>${j.fit}%</div></div>
    <div class="why"><b>왜 추천?</b> ${j.reason}</div>
    <div class="meta">${j.tags.map((t) => `<span>${t}</span>`).join('')}</div>
    <div class="add">${inCart ? '✓ 담김' : '＋ 관심 목록에 담기'}</div></div>`;
}
function cartLabel() { const n = S.cart.length; return n ? `담은 ${n}곳으로 서류 지원하러 가기` : '관심 있는 곳을 담아주세요'; }
function bindCards() {
  $('grid').querySelectorAll('.ccard .add').forEach((el) => {
    el.onclick = () => {
      const id = el.closest('.ccard').dataset.job;
      const idx = S.cart.findIndex((c) => c.job_id === id);
      if (idx >= 0) S.cart.splice(idx, 1); else S.cart.push(S.jobs.find((j) => j.job_id === id));
      RENDER.match();
    };
  });
  const go = $('go'); go.disabled = S.cart.length === 0; go.onclick = () => { if (S.cart.length) goto('cart'); };
}

// ===== STEP 3: 장바구니 =====
RENDER.cart = function () {
  renderChrome('cart'); setCtx(null);
  const autoN = S.cart.filter((j) => j.auto_apply).length;
  paint(`
    <div class="page-h">담아둔 <span class="u">일자리</span></div>
    <div class="page-sub">경력은 한 번만 입력했어요. 담은 회사마다 이력서가 자동으로 만들어집니다.</div>
    <div class="cart-list">
      ${S.cart.map((j) => j.auto_apply
        ? `<div class="citem"><div class="chk">✓</div><div><div class="co">${j.company}</div><div class="st">이력서 준비됨</div></div><div class="cbtns"><span class="mini-btn">📄 이력서 확인</span></div></div>`
        : `<div class="citem"><div class="chk off"></div><div><div class="co">${j.company}</div><div class="st link">고용24 공고 · 링크 지원</div></div><div class="cbtns"><span class="mini-btn apricot">↗ 공고로</span></div></div>`
      ).join('')}
    </div>
    <div class="cart-foot">
      ${autoN ? `<div class="foot-btn brand">📄 준비된 이력서 ${autoN}건 한번에 확인</div>` : ''}
      <div class="foot-btn sage">💾 파일로 저장</div>
      <div class="foot-btn">🖨️ 프린트하기</div>
    </div>
    <button class="cta full" id="go">서류 지원하러 가기</button>`);
  S.resumeIdx = 0;
  bind('go', () => goto('resume'));
};

// ===== STEP 4: 회사별 맞춤 이력서 =====
RENDER.resume = function () {
  const job = S.cart[S.resumeIdx];
  renderChrome('resume', `/resume/${job.company}`);
  loading(`${job.company} 맞춤 이력서 작성 중…`);
  api('/resume', { job_id: job.job_id, years: S.profile.years, skills: S.profile.skills, region: S.profile.region })
    .then((r) => {
      const d = r.data; S.resumes[job.job_id] = d;
      if (d.gap_skill && !S.gapSkills.includes(d.gap_skill)) S.gapSkills.push(d.gap_skill);
      setCtx(`<div class="ctx-t">이력서에 담은 4가지 안내</div>
        <div class="i4"><div class="n">1</div><div class="tx"><b>${d.guide[0].label}</b> — ${d.guide[0].text}</div></div>
        <div class="i4"><div class="n s">2</div><div class="tx"><b>${d.guide[1].label}</b> — ${d.guide[1].text}</div></div>
        <div class="i4"><div class="n a">3</div><div class="tx"><b>${d.guide[2].label}</b> — ${d.guide[2].text}</div></div>
        <div class="i4"><div class="n">4</div><div class="tx"><b>${d.guide[3].label}</b> — ${d.guide[3].text}</div></div>
        <div class="info-strip"><span class="ii">💡</span>지원 단계부터 성장 루프(교육)를 미리 보여줍니다.</div>`);
      const last = S.resumeIdx >= S.cart.length - 1;
      paint(`
        <div class="page-h">${d.company} <span class="u">맞춤 이력서</span> ${srcPill(r.meta.source)}</div>
        <div class="page-sub">이 회사가 원하는 것에 맞춰 강조점을 자동으로 배치했어요. (${S.resumeIdx + 1}/${S.cart.length})</div>
        <div class="resume-doc">
          <h4>${d.company} · ${d.role}</h4>
          <div class="rfield"><div class="rl">핵심 문장</div><div class="rv">${d.resume_body}</div></div>
          <div class="rfield" style="margin-bottom:0"><div class="rl">이 회사 맞춤 강조</div><div class="rv">'${d.emphasis}' 를 앞세워 재구성</div></div>
        </div>
        <button class="cta full ${last ? 'brand' : ''}" id="go">${last ? '확인 완료 · 제출로' : '확인했어요 · 다음 회사'}</button>`);
      bind('go', () => { if (last) goto('submit'); else { S.resumeIdx++; RENDER.resume(); } });
    }).catch((e) => showError(e, () => RENDER.resume()));
};

// ===== STEP 5: 승인 게이트 제출 =====
RENDER.submit = function () {
  renderChrome('submit'); setCtx(null);
  S.cart.forEach((j) => { if (!(j.job_id in S.submitSel)) S.submitSel[j.job_id] = j.auto_apply; });
  paint(`
    <div class="page-h">제출 전에 <span class="u">직접 확인</span>하세요</div>
    <div class="page-sub">체크한 곳에만 지원됩니다. 마지막 제출 버튼은 본인이 누릅니다.</div>
    <div class="cart-list" id="sublist">${S.cart.map(submitItem).join('')}</div>
    <div class="info-strip"><span class="ii">🔒</span>회원님의 개인 분석 결과는 기업에 전달되지 않습니다.</div>
    <button class="cta full big" id="go"></button>`);
  bindSubmit();
};
function submitItem(j) {
  const on = S.submitSel[j.job_id];
  const st = j.auto_apply ? '<div class="st">우리 회원사 · 바로 면접 준비</div>'
    : '<div class="st link">고용24 공고 · 링크에서 직접 제출</div>';
  return `<div class="citem ${on ? 'sel' : ''}" data-job="${j.job_id}">
    <div class="chk ${on ? '' : 'off'}">✓</div><div><div class="co">${j.company}</div>${st}</div></div>`;
}
function bindSubmit() {
  $('sublist').querySelectorAll('.citem').forEach((el) => {
    el.onclick = () => { const id = el.dataset.job; S.submitSel[id] = !S.submitSel[id]; RENDER.submit(); };
  });
  const sel = S.cart.filter((j) => S.submitSel[j.job_id]);
  const member = sel.filter((j) => j.auto_apply);
  const go = $('go');
  go.textContent = sel.length ? `${sel.length}곳에 지원서 제출` : '제출할 곳을 선택하세요';
  go.disabled = sel.length === 0;
  go.onclick = () => {
    if (member.length) { S.interviewJob = member[0].job_id; goto('prep'); }
    else $('main').insertAdjacentHTML('beforeend',
      `<div class="err">선택하신 곳은 고용24 공고예요. 제공된 링크에서 직접 제출하세요. (회원사를 함께 선택하면 AI 면접 준비로 이어집니다)</div>`);
  };
};

// ===== STEP 7: 카메라·소리 + AI 면접 준비 =====
RENDER.prep = function () {
  renderChrome('prep'); setCtx(null);
  loading('AI 면접 질문을 준비하는 중…');
  api('/interview/questions', { job_id: S.interviewJob }).then((r) => {
    S.questions = r.data.questions; S.qIndex = 0; S.interviewCompany = r.data.company;
    paint(`
      <div class="eyebrow">${r.data.company} · AI 면접 준비</div>
      <div class="page-h">카메라·소리부터 <span class="u">같이 확인</span>해요</div>
      <div class="page-sub">문제 없으면 바로 시작합니다. 답변은 회원님만 다시 볼 수 있어요.</div>
      <div class="dtest">
        <div style="position:relative;border-radius:12px;overflow:hidden;background:#0E1216;aspect-ratio:16/9;max-width:380px;display:flex;align-items:center;justify-content:center">
          <video id="cam" autoplay muted playsinline style="width:100%;height:100%;object-fit:cover"></video>
          <span id="camPh" style="position:absolute;color:#7b8794;font-size:.86rem;display:none">📷 카메라를 사용할 수 없어요 (권한/장치)</span></div>
        <div class="drow"><div class="di">📷</div><div><div class="dtt">카메라</div><div class="dds">얼굴이 잘 보여요</div></div><span class="dok" id="camStat">확인 중…</span></div>
        <div class="drow"><div class="di">🎙️</div><div><div class="dtt">마이크</div><div class="dds">말씀해 보세요</div></div><span class="dok" id="micStat">확인 중…</span></div>
      </div>
      <div class="wavebox" style="margin-top:12px"><div class="wt">🔊 소리 크기 확인 중…</div>
        <div class="wave"><i style="height:40%"></i><i style="height:70%"></i><i style="height:100%"></i><i style="height:55%"></i><i style="height:85%"></i><i style="height:45%"></i><i style="height:75%"></i><i style="height:60%"></i><i style="height:50%"></i><i style="height:90%"></i></div></div>
      <div class="info-strip"><span class="ii">🤖</span>이 회사 정보로 예상 질문 ${S.questions.length}개를 자동 생성했어요 ${srcPill(r.meta.source)}. 답하시면 AI가 음성·내용을 분석해 연습 피드백을 드립니다. (기업엔 전달 안 됨)</div>
      <button class="cta full big" id="go">AI 면접 시작</button>`);
    bind('go', () => goto('interview'));
    // 실제 웹캠·마이크 권한 요청 → 미리보기(장치 없으면 폴백)
    getCam().then((s) => {
      const v = $('cam'); if (v) v.srcObject = s;
      if ($('camStat')) $('camStat').textContent = '✓ 정상';
      if ($('micStat')) $('micStat').textContent = '✓ 정상';
    }).catch(() => {
      if ($('cam')) $('cam').style.display = 'none';
      if ($('camPh')) $('camPh').style.display = '';
      if ($('camStat')) $('camStat').innerHTML = '<span style="color:var(--apricot)">⚠️ 장치 없음</span>';
      if ($('micStat')) $('micStat').innerHTML = '<span style="color:var(--apricot)">⚠️ 없음</span>';
    });
  }).catch((e) => showError(e, () => RENDER.prep()));
};

// ===== STEP 8: AI 아바타 면접 =====
// ── 브라우저 TTS (아바타 발화) — 무설치·한국어. 신경망 TTS(Qwen3-TTS 등)는 GPU/클라우드 스왑 자리. ──
let _koVoice = null;
function _pickVoice() {
  const vs = window.speechSynthesis ? speechSynthesis.getVoices() : [];
  _koVoice = vs.find((v) => /ko/i.test(v.lang || '')) || null;
}
if (window.speechSynthesis) { _pickVoice(); try { speechSynthesis.onvoiceschanged = _pickVoice; } catch (e) {} }
function speak(text) {
  try {
    if (!window.speechSynthesis || !text) return;
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(String(text).replace(/^"|"$/g, ''));
    u.lang = 'ko-KR'; if (_koVoice) u.voice = _koVoice; u.rate = 0.98;
    speechSynthesis.speak(u);
  } catch (e) { /* TTS 미지원 브라우저 → 조용히 무시 */ }
}

// ── 웹캠·마이크 (getUserMedia/MediaRecorder) — 장치 없으면 폴백. ──
async function getCam() {
  if (S.camStream) return S.camStream;
  S.camStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
  return S.camStream;
}
function stopCam() { if (S.camStream) { try { S.camStream.getTracks().forEach((t) => t.stop()); } catch (e) {} S.camStream = null; } }

// 온보딩 마이크: 녹음 토글 → /stt 전사
let _micRec = null, _micChunks = [], _micStream = null;
async function micToggle(btn, onText) {
  if (_micRec && _micRec.state === 'recording') { _micRec.stop(); return; }
  try { _micStream = await navigator.mediaDevices.getUserMedia({ audio: true }); }
  catch (e) { onText('__nomic__'); return; }
  _micChunks = [];
  _micRec = new MediaRecorder(_micStream);
  _micRec.ondataavailable = (ev) => { if (ev.data && ev.data.size) _micChunks.push(ev.data); };
  _micRec.onstop = async () => {
    if (_micStream) { _micStream.getTracks().forEach((t) => t.stop()); _micStream = null; }
    btn.textContent = '🎤';
    const blob = new Blob(_micChunks, { type: 'audio/webm' });
    if (blob.size < 2500) { onText('__tooshort__'); _micRec = null; return; }  // 너무 짧/무음
    onText('__transcribing__');
    try {
      const fd = new FormData();
      fd.append('audio', blob, 'clip.webm');
      const res = await fetch(API + '/stt', { method: 'POST', body: fd });
      const j = await res.json();
      onText(j.ok ? (j.data.text || '') : '__unavail__');
    } catch (e) { onText('__unavail__'); }
    _micRec = null;
  };
  _micRec.start();
  btn.textContent = '⏹';
  onText('__recording__');
}

// 전사 텍스트 → 현재 온보딩 스텝 칩 자동 매칭(연수는 근접값)
function matchChip(step, text) {
  const t = (text || '').replace(/\s/g, '');
  if (step.key === 'years') {
    const m = t.match(/(\d+)/);
    if (m) { const n = +m[1]; let bi = -1, bd = 1e9; step.chips.forEach((c, i) => { const d = Math.abs(c[1] - n); if (d < bd) { bd = d; bi = i; } }); return bi; }
  }
  for (let i = 0; i < step.chips.length; i++) {
    const toks = step.chips[i][0].split(/[·\s]+/).filter((x) => x.length >= 2);
    if (toks.some((k) => t.includes(k.replace(/\s/g, '')))) return i;
  }
  return -1;
}

// 면접 웹캠 녹화
function startRec() {
  if (!S.camStream || S.rec) return;
  try { S.recChunks = []; S.rec = new MediaRecorder(S.camStream); S.rec.ondataavailable = (e) => { if (e.data && e.data.size) S.recChunks.push(e.data); }; S.rec.start(); } catch (e) { S.rec = null; }
}
function stopRec() { if (S.rec) { try { if (S.rec.state !== 'inactive') S.rec.stop(); } catch (e) {} S.rec = null; } }

// ── VAD 발화단위 스트리밍 — 말 멈추면(침묵) 한 문장을 서버로 전송 ──
let _vad = null;
async function startVAD(onUtter, onState) {
  let stream;
  try { stream = await navigator.mediaDevices.getUserMedia({ audio: true }); }
  catch (e) { onState('nomic'); return false; }
  const AC = window.AudioContext || window.webkitAudioContext;
  const ac = new AC(); const src = ac.createMediaStreamSource(stream);
  const an = ac.createAnalyser(); an.fftSize = 512; src.connect(an);
  const buf = new Uint8Array(an.fftSize);
  const V = { ac, stream, active: true, speaking: false, silenceAt: 0, rec: null, chunks: [], raf: 0 };
  _vad = V;
  const THRESH = 0.02, SIL = 800;   // RMS 임계 · 침묵 지속(ms)
  const startSeg = () => {
    V.chunks = [];
    try {
      V.rec = new MediaRecorder(stream);
      V.rec.ondataavailable = (e) => { if (e.data && e.data.size) V.chunks.push(e.data); };
      V.rec.onstop = () => { const b = new Blob(V.chunks, { type: 'audio/webm' }); if (b.size > 2500) onUtter(b); };
      V.rec.start();
    } catch (e) { V.rec = null; }
  };
  const stopSeg = () => { if (V.rec && V.rec.state === 'recording') { try { V.rec.stop(); } catch (e) {} } V.rec = null; };
  const tick = () => {
    if (!V.active) return;
    an.getByteTimeDomainData(buf);
    let sum = 0; for (let i = 0; i < buf.length; i++) { const x = (buf[i] - 128) / 128; sum += x * x; }
    const rms = Math.sqrt(sum / buf.length), now = performance.now();
    if (rms > THRESH) {
      if (!V.speaking) { V.speaking = true; onState('speaking'); startSeg(); }
      V.silenceAt = 0;
    } else if (V.speaking) {
      if (!V.silenceAt) V.silenceAt = now;
      else if (now - V.silenceAt > SIL) { V.speaking = false; onState('listening'); stopSeg(); }
    }
    V.raf = requestAnimationFrame(tick);
  };
  onState('listening'); tick();
  return true;
}
function stopVAD() {
  const V = _vad; if (!V) return; V.active = false;
  if (V.raf) cancelAnimationFrame(V.raf);
  try { if (V.rec && V.rec.state === 'recording') V.rec.stop(); } catch (e) {}
  try { V.stream.getTracks().forEach((t) => t.stop()); } catch (e) {}
  try { V.ac.close(); } catch (e) {}
  _vad = null;
}

// 발화 전사+슬롯 → 프로필 반영 + 실시간 지원서(ctx) 갱신 (하이브리드 규칙 층)
function applyVoice(text, sl) {
  if (sl.jobKind && sl.skills) { ONB[0]._picked = sl.jobKind; S.jobKind = sl.jobKind; S.profile.skills = sl.skills; }
  if (sl.years) { ONB[1]._picked = sl.years + '년'; S.profile.years = sl.years; }
  if (sl.region) { ONB[2]._picked = sl.region; S.profile.region = sl.region; }
  const fi = ONB.findIndex((o) => o._picked === undefined);
  S.onbStep = fi < 0 ? ONB.length : fi;
  setCtx(ctxResume());  // 실시간 지원서만 갱신(메인 미갱신 → 마이크 유지)
  const mt = $('micTxt'); if (mt && text) mt.textContent = '“' + text + '”';
  if (S.profile.skills.length && S.profile.years && S.profile.region) {  // 3핵심 다 채워짐 → 진행
    stopVAD(); RENDER.onboard();
  }
}

RENDER.interview = function () {
  renderChrome('interview', `/interview · ${S.interviewCompany}`);
  setCtx(null);
  const q = S.questions[S.qIndex] || { n: 1, text: '' };
  const total = S.questions.length;
  const rows = S.questions.map((it, i) => {
    const cls = i < S.qIndex ? 'done' : (i === S.qIndex ? 'cur' : '');
    const badge = i < S.qIndex ? '✓' : it.n;
    const short = it.tag === 'AI 꼬리질문' ? `Q${it.n} · 꼬리질문` : `Q${it.n} · ${it.text.slice(0, 12)}…`;
    return `<div class="qrow ${cls}"><span class="qb">${badge}</span>${short}</div>`;
  }).join('');
  const last = S.qIndex >= total - 1;
  paint(`
    <div class="page-h" style="font-size:1.4rem">${S.interviewCompany} · AI 면접 <span style="font-size:0.9rem;color:var(--ink-3);font-weight:400">질문 ${q.n} / ${total}</span></div>
    <div style="height:16px"></div>
    <div class="interview">
      <div class="stage">
        <div class="vid"><div class="avatar">🧑‍💼<div class="abadge">AI 면접관 · ${S.interviewCompany}</div></div><div class="self" id="selfView">🙂</div></div>
        <div class="bar"><div class="cbtn">🎤</div><div class="cbtn">📹</div><div class="cbtn end" id="skip">⏭</div></div>
      </div>
      <div class="qpanel">
        <div class="qnow"><div class="ql">지금 질문 · Q${q.n}</div><div class="qt">"${q.text}"</div></div>
        <div class="qlist">${rows}</div>
      </div>
    </div>
    <div class="info-strip"><span class="ii">${S.camStream ? '🔴' : 'ℹ️'}</span>${S.camStream ? '<b>답변 녹화 중</b> — ' : ''}AI 아바타 면접관이 승인된 질문을 순서대로 진행합니다. 최종 판정은 사람 담당자. ${srcPill('seed')}</div>
    <button class="cta full ${last ? 'brand' : ''}" id="go">${last ? '면접 종료 · 피드백 보기' : `답변 완료 · 다음 질문 (${q.n}/${total})`}</button>`);
  // 웹캠이 있으면 셀프뷰 라이브 영상 + 녹화(prep에서 획득한 스트림 재사용)
  if (S.camStream && $('selfView')) {
    $('selfView').innerHTML = '<video autoplay muted playsinline style="width:100%;height:100%;object-fit:cover"></video>';
    $('selfView').firstChild.srcObject = S.camStream;
    startRec();
  }
  const advance = () => {
    if (S.qIndex < total - 1) { S.qIndex++; RENDER.interview(); }
    else { stopRec(); stopCam(); goto('feedback'); }
  };
  bind('skip', advance); bind('go', advance);
  speak(q.text);  // 아바타가 질문을 소리내어 읽음(브라우저 TTS)
};

// ===== STEP 9: 피드백 + 결과 대기 =====
const DELIVERY_SIGNALS = [
  { key: 'voice', label: '목소리 크기·또렷함', score: 86, val: '좋아요' },
  { key: 'specificity', label: '답변 구체성', score: 60, val: '보통' },
  { key: 'pace', label: '말 빠르기', score: 44, val: '조금 빨라요' },
];
RENDER.feedback = function () {
  renderChrome('feedback'); setCtx(null);
  loading('면접 답변을 분석하는 중…');
  api('/interview/analyze', { signals: DELIVERY_SIGNALS }).then((r) => {
    const barCls = (g) => g === 'strong' ? 'hi' : (g === 'ok' ? 'mid' : 'lo');
    const valOf = (k) => (DELIVERY_SIGNALS.find((s) => s.key === k) || {}).val || '';
    const interviewCo = (S.jobs.find((j) => j.job_id === S.interviewJob) || {}).company || '지원 회사';
    const inviteJob = S.jobs.find((j) => j.auto_apply && j.job_id !== S.interviewJob) || S.jobs.find((j) => j.auto_apply);
    S.scheduleJob = inviteJob ? inviteJob.job_id : S.interviewJob;
    const inviteCo = inviteJob ? inviteJob.company : '지원 회사';
    paint(`
      <div class="page-h">면접 <span class="u">피드백</span>과 지원 현황</div>
      <div class="page-sub">연습 피드백은 회원님만 봅니다. 기업에는 전달되지 않아요.</div>
      <div class="two-col">
        <div class="panel gap">
          <h3>🎯 면접 연습 피드백</h3><div class="psub">나만 보기 · 다음 면접 참고 ${srcPill('seed')}</div>
          ${r.data.competencies.map((c) => `<div class="grow">
            <div class="glabel"><span>${c.label}</span><span class="v">${valOf(c.key)}</span></div>
            <div class="track"><i class="${barCls(c.grade)}" style="width:${c.score}%"></i></div></div>`).join('')}
        </div>
        <div class="panel">
          <h3>📋 내 지원 현황</h3><div class="psub">언제든 열람 가능 ${srcPill('seed')}</div>
          <div class="witem"><div class="wtop"><span class="wco">${interviewCo}</span><span class="wstat wait">결과 대기 중</span></div><div class="wds">AI 면접 완료 · 담당자 검토 중이에요.</div></div>
          <div class="witem"><div class="wtop"><span class="wco">${inviteCo}</span><span class="wstat invite">면접 제안 도착</span></div><div class="wds">담당자가 대면 면접을 요청했어요.</div><div class="wact" id="goSched">일정 확인하기 →</div></div>
        </div>
      </div>
      <div class="cta-row"><button class="cta brand" id="go">면접 제안 일정 잡기</button>
        <button class="text-link" id="go2">결과 대기 중인 곳, 교육으로 준비하기</button></div>`);
    bind('goSched', () => goto('schedule'));
    bind('go', () => goto('schedule'));
    bind('go2', () => goto('reeducate'));
  }).catch((e) => showError(e, () => RENDER.feedback()));
};

// ===== STEP 6: 실면접 일정 =====
const SLOT_OPTIONS = [
  ['MON_09', '월 9시'], ['MON_11', '월 11시'], ['TUE_14', '화 2시'],
  ['WED_13', '수 1시'], ['WED_14', '수 2시'], ['THU_15', '목 3시'],
  ['THU_16', '목 4시'], ['FRI_10', '금 10시'], ['FRI_14', '금 2시'],
];
RENDER.schedule = function () {
  renderChrome('schedule', `/schedule · ${(S.jobs.find((j) => j.job_id === S.scheduleJob) || {}).company || ''}`);
  setCtx(null);
  S.confirmed = null;
  const job = S.jobs.find((j) => j.job_id === S.scheduleJob) || S.cart[0];
  paint(`
    <div class="page-h"><span class="u">${job.company}</span>이 대면 면접을 제안했어요</div>
    <div class="page-sub">가능한 시간을 고르면 양쪽 모두 되는 시간을 자동으로 찾아드려요.</div>
    <div class="sched">
      <div class="slab">내가 가능한 시간 (여러 개 선택)</div>
      <div class="slotgrid" id="slotGrid">
        ${SLOT_OPTIONS.map(([k, l]) => `<div class="slot ${S.candidateSlots.includes(k) ? 'me' : ''}" data-k="${k}">${l}</div>`).join('')}
      </div>
      <div class="scap"><span><i style="background:var(--brand-tint);border:1px solid var(--brand)"></i>내가 가능</span>
        <span><i style="background:var(--sage)"></i>양쪽 확정</span></div>
    </div>
    <div id="confirmBox"></div>
    <button class="cta full brand" id="go"></button>`);
  $('slotGrid').querySelectorAll('.slot').forEach((el) => {
    el.onclick = () => {
      const k = el.dataset.k; const i = S.candidateSlots.indexOf(k);
      if (i >= 0) S.candidateSlots.splice(i, 1); else S.candidateSlots.push(k);
      RENDER.schedule();
    };
  });
  const go = $('go');
  go.textContent = S.candidateSlots.length ? '일정 자동 확정' : '가능한 시간을 골라주세요';
  go.disabled = S.candidateSlots.length === 0;
  go.onclick = doConfirm;
};
function doConfirm() {
  $('go').disabled = true;
  api('/schedule/confirm', { job_id: S.scheduleJob, candidate_slots: S.candidateSlots }).then((r) => {
    const d = r.data; S.confirmed = d;
    if (d.confirmed) {
      const cell = $('slotGrid').querySelector(`.slot[data-k="${d.slot}"]`);
      if (cell) cell.className = 'slot match';
      $('confirmBox').innerHTML = `<div class="confirm">
          <div class="big">✓ ${d.slot_label} 확정</div>
          <div class="page-sub" style="margin:0">${d.message} ${srcPill('live')}</div>
          <div class="meet">🎥 화상/대면 안내 · <a href="${d.meet_url}" target="_blank">${d.meet_url}</a> ${srcPill(d.meet_source)}</div>
        </div>`;
      const go = $('go'); go.disabled = false; go.textContent = '다음: 결과 대기 곳 준비하기';
      go.onclick = () => goto('reeducate');
    } else {
      $('confirmBox').innerHTML = `<div class="err">${d.message} (회사 가능: ${d.company_slots.join(', ')})</div>`;
      const go = $('go'); go.disabled = false; go.textContent = '시간 다시 고르기';
      go.onclick = () => { S.confirmed = null; RENDER.schedule(); };
    }
  }).catch((e) => { $('confirmBox').innerHTML = `<div class="err">문제가 생겼어요: ${e.message}</div>`; $('go').disabled = false; });
}

// ===== STEP 10: 교육 추천 → 재지원 =====
const NCS_SIGNALS = [
  { key: 'domain_expertise', label: '직무 전문성', score: 88 },
  { key: 'communication', label: '의사소통', score: 60 },
  { key: 'quantify_achievement', label: '성과를 숫자로 설명', score: 35 },
];
RENDER.reeducate = function () {
  renderChrome('reeducate'); setCtx(null);
  loading('부족한 역량에 맞는 교육을 찾는 중…');
  api('/interview/analyze', { signals: NCS_SIGNALS }).then((r) => {
    const d = r.data, tr = d.training;
    paint(`
      <div class="eyebrow">이번엔 아쉬웠지만, 끝이 아니에요</div>
      <div class="page-h"><span class="u">이런 교육</span>을 들으면 다음엔 더 유리해요</div>
      <div class="page-sub">면접에서 가장 보완이 필요했던 <b>${d.weakest ? d.weakest.label : '역량'}</b>을 채우는 정부 지원 교육이에요. 등급 산정 ${srcPill(r.meta.source)}</div>
      ${tr ? `<div class="reco"><div class="ic">🎓</div><div><div class="tt">${tr.title}</div><div class="ds">${tr.provider} · ${tr.weeks}주 · ${tr.cost}</div><span class="gov">내일배움카드 · 국비 지원 ${srcPill('seed')}</span></div></div>` : ''}
      <div class="reco"><div class="ic">📊</div><div><div class="tt">경력 → 자격증 전환 과정</div><div class="ds">경력을 자격증으로 증명하면 매칭이 더 넓어져요.</div><span class="gov">중장년 훈련지원 · 예시 ${srcPill('seed')}</span></div></div>
      <div class="info-strip" style="background:var(--sage-tint);border-color:#C6DCC9;color:var(--sage)"><span class="ii">↻</span>한 걸음 더 성장한 모습으로 다시 도전하는 회원님을 응원합니다. 같은 회사에도 얼마든지 다시 지원할 수 있어요.</div>
      <div class="cta-row"><button class="cta brand" id="go">다시 지원하기</button>
        <button class="text-link" id="go2">처음부터 다시 체험</button></div>`);
    bind('go', () => {
      S.gapSkills.forEach((g) => { if (!S.profile.skills.includes(g)) S.profile.skills.push(g); });
      S.cart = []; S.submitSel = {}; S.resumes = {};
      goto('match');
    });
    bind('go2', resetAll);
  }).catch((e) => showError(e, () => RENDER.reeducate()));
};

// ---------- 공통 ----------
function showError(e, retry) {
  paint(`<div class="err">문제가 생겼어요: ${e.message}</div><button class="cta full" id="go">다시 시도</button>`);
  bind('go', retry);
}
function resetAll() {
  Object.assign(S, {
    profile: { years: 0, skills: [], region: '' }, jobKind: '', onbStep: 0, jobs: [], cart: [],
    resumeIdx: 0, resumes: {}, gapSkills: [], submitSel: {}, interviewJob: null, interviewCompany: '',
    questions: [], qIndex: 0, scheduleJob: null, candidateSlots: [], confirmed: null,
  });
  ONB.forEach((o) => delete o._picked);
  histStack.length = 0;
  goto('start', { push: false });
}

// ---------- 부팅 ----------
goto('start', { push: false });
