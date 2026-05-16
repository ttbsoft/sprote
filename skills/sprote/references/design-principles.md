# TTB Artisan 디자인 원칙

TTB가 생성하는 모든 UI/UX에 적용되는 품질 표준. 구현·검토·교차검증 시 반드시 준수할 것.
목표: "AI가 만들었겠다"는 말을 절대 듣지 않는 $150k 에이전시 품질.

---

## 1. 기술 스택 기본값

별도 지시 없으면 아래 스택을 기본으로 사용한다.

```html
<!-- Tailwind CSS -->
<script src="https://cdn.tailwindcss.com"></script>

<!-- Pretendard (한글 표준 폰트) -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css">

<!-- Iconify Solar 아이콘 세트 -->
<script src="https://code.iconify.design/iconify-icon/2.1.0/iconify-icon.min.js"></script>

<!-- Motion One (MOTION_INTENSITY > 5일 때만) -->
<script src="https://cdn.jsdelivr.net/npm/motion@10.16.2/dist/motion.js"></script>
```

```js
// tailwind.config 필수 설정
tailwind.config = {
  theme: {
    extend: {
      fontFamily: { sans: ['Pretendard', 'system-ui', 'sans-serif'] }
    }
  }
}
```

**출력 형식 기본값:** 단일 HTML 파일 (모든 스타일·스크립트 인라인 또는 CDN). 브라우저에서 직접 열 수 있어야 함.

---

## 2. 설계 변수 (Design Variables)

Phase 1 컨텍스트 수집 시 사용자에게 확인하거나 기본값을 적용한다.

| 변수 | 범위 | 기본값 | 의미 |
|------|------|--------|------|
| `DESIGN_VARIANCE` | 1–10 | 5 | 1=대칭·보수적 / 10=비대칭·실험적 |
| `MOTION_INTENSITY` | 1–10 | 5 | 1=정적 / 10=시네마틱 풀 애니메이션 |
| `VISUAL_DENSITY` | 1–10 | 4 | 1=럭셔리·여유 / 10=데이터 밀집 |
| `LANDING_PURPOSE` | 열거 | conversion | `conversion` / `brand` / `portfolio` / `saas` / `ecommerce` |

---

## 3. 디자인 아키타입

브랜드에 맞는 아키타입 1개를 선택한다. 같은 템플릿 반복 금지.

### Vantablack Luxe (SaaS / AI 툴 / 테크)
- 배경: `oklch(8% 0.01 250)` 근사 초다크
- 글로우 악센트 1개 (포화도 <70%)
- 유리 형태 카드, 미세한 흰색 테두리
- 타이포: 대형 굵은 헤드라인 + 얇은 서브텍스트

### Warm Editorial (라이프스타일 / 음식 / 패션 / 뷰티)
- 배경: 크림 또는 따뜻한 오프화이트 (`oklch(97% 0.008 70)`)
- 사진 중심 레이아웃
- 세리프 헤드라인 + 산세리프 본문
- 넉넉한 여백, 콘텐츠가 레이아웃을 주도

### Clean Structural (헬스케어 / 금융 / B2B SaaS / 공공)
- 배경: 순수 화이트 또는 아주 연한 회색 (`oklch(98% 0.003 250)`)
- 체계적 그리드, 명확한 위계
- 산세리프 일관성, 데이터·지표 중심
- 신뢰감·명확성 우선

---

## 4. 절대 금지 패턴 (AI Slop 지표)

이 패턴이 발견되면 즉시 다른 구조로 재작성한다.

### 금지: 사이드 스트라이프 테두리
```css
/* 금지 — 굵기·색상 무관 */
border-left: 3px solid var(--color-warning);
border-right: 4px solid oklch(...);
```
→ 대신: 전체 테두리, 배경 틴트, 선행 아이콘/번호, 또는 표시 없음

### 금지: 그래디언트 텍스트
```css
/* 금지 */
background-clip: text;
-webkit-background-clip: text;
```
→ 대신: 단색. 강조는 굵기·크기로.

### 금지: AI 색상 팔레트
- 어두운 배경 + 시안/청보라 글로우
- 보라→파랑 그래디언트 배경
- 형광 악센트 on 다크 테마
→ 대신: 브랜드 고유 색상 체계

### 금지: 반복 카드 그리드
- 아이콘 + 제목 + 텍스트의 동일한 카드가 3열로 반복
- 모든 카드 동일 크기·여백
→ 대신: 크기 대비, 비대칭, Bento 레이아웃

### 금지: 히어로 메트릭 레이아웃
- 큰 숫자 + 작은 레이블 + 그래디언트 악센트 패턴
→ 대신: 실제 사용자 목적에 맞는 레이아웃

### 금지: 중앙 정렬 과잉
- 모든 섹션이 `text-center`
- 히어로조차 분할 화면이나 비대칭 없이 중앙만
→ 대신: 분할 화면, 비대칭 Bento, 전체 이미지 오버레이

### 기타 금지 목록

```
Inter, Roboto, Open Sans, Outfit, Plus Jakarta Sans,
Instrument Sans, DM Sans, Space Grotesk, IBM Plex Sans,
Playfair Display, Fraunces, Lora, Crimson Pro, Syne,
Space Mono, IBM Plex Mono, DM Serif Display
→ 사용 금지 (AI 기본값)

Noto Sans KR → 한글에 금지. Pretendard 사용.
Lorem ipsum, 플레이스홀더 텍스트 → 실제 한국어 콘텐츠로 대체
FontAwesome, Lucide (굵은 것), Heroicons → Iconify Solar 사용
```

---

## 5. 타이포그래피 원칙

### 폰트 선택 절차
1. 브랜드를 3단어로 정의 (예: "정밀하고 따뜻하고 직관적인")
2. 반사적으로 떠오르는 폰트 3개 작성 후 거부
3. 브랜드 단어에 맞는 폰트 탐색
4. Pretendard (한글) + 프리미엄 영문 디스플레이 폰트 페어링

### 타입 스케일
```css
/* 마케팅·랜딩 페이지 — clamp() 유동 크기 */
.hero-heading { font-size: clamp(2.5rem, 6vw, 5rem); }
.section-heading { font-size: clamp(1.75rem, 3.5vw, 3rem); }

/* 앱 UI·대시보드 — 고정 rem (유동 금지) */
.heading-lg { font-size: 1.75rem; }
.body { font-size: 1rem; }
```

### 한국어 표준
```css
/* 필수 설정 */
word-break: keep-all;    /* 어절 단위 줄 바꿈 */
line-height: 1.6;        /* 한글 수직 공간 */
letter-spacing: -0.01em; /* 타이트한 자간 */
```

- 자연스럽고 구체적인 한글 사용 (번역 투 금지)
- 존댓말 일관성 유지
- AI 클리셰 금지: "혁신적인", "효율적인", "최적화된", "솔루션"

---

## 6. 색상 원칙

### OKLCH 사용 필수
```css
/* 권장 */
color: oklch(68% 0.21 250);
background: oklch(98% 0.007 250); /* 뉴트럴에 브랜드 힌트 */

/* 금지 */
color: hsl(210, 80%, 50%);
background: #ffffff; /* 순수 흰색 금지 */
```

### 뉴트럴 틴팅
모든 회색을 브랜드 색 방향으로 미세하게 틴팅 (chroma 0.005–0.01):
```css
--color-surface: oklch(98% 0.007 250);
--color-text: oklch(18% 0.01 250);
```

### 팔레트 규칙
- 악센트 색상: **페이지당 1개**
- 포화도: **<80%** (형광 금지)
- AI 기본 시안·청보라 사용 금지

---

## 7. 레이아웃·여백 원칙

### 4pt 기반 스페이싱 토큰
```css
--space-xs:  4px;  --space-sm: 8px;
--space-md: 16px;  --space-lg: 24px;
--space-xl: 48px;  --space-2xl: 96px;
```

### 섹션 여백 (럭셔리 표준)
```html
<section class="py-24 md:py-32 lg:py-40">...</section>
```

### 레이아웃 규칙
- `gap` 사용, `margin` 최소화
- 동일 여백 반복 금지 — 여백으로 위계 표현
- 카드 안에 카드 금지 (계층 평탄화)
- 전체 중앙 정렬 금지 — 좌측 정렬 + 비대칭이 더 설계적
- 본문 최대 너비: 65–75ch

---

## 8. 컴포넌트 패턴

### 더블 베젤 카드 (프리미엄 깊이)
```html
<!-- 외부 셸 -->
<div class="bg-white/5 ring-1 ring-white/10 p-1.5 rounded-[2rem]">
  <!-- 내부 코어 -->
  <div class="bg-white/8 rounded-[1.625rem] p-6">콘텐츠</div>
</div>
```

### CTA 버튼 (전환 중심)
```html
<button class="flex items-center gap-3 bg-black text-white px-8 py-4 rounded-full text-lg
               transition-all duration-500 ease-[cubic-bezier(0.16,1,0.3,1)]
               hover:scale-[1.02] active:scale-[0.98]">
  지금 시작하기
  <span class="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center
               transition-transform group-hover:translate-x-1">
    <iconify-icon icon="solar:arrow-right-linear"></iconify-icon>
  </span>
</button>
```

### 눈썹 태그 (섹션 소제목)
```html
<span class="inline-flex items-center rounded-full px-3 py-1 text-[11px]
             tracking-widest uppercase bg-black/5 text-black/50">
  주요 기능
</span>
```

---

## 9. 프리미엄 패턴

### 글래스 모피즘 (재질감·깊이)
```css
.glass-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.1);
}
```

### 서명 이징 곡선 (TTB Standard)
```css
transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
```

### IntersectionObserver 스크롤 트리거
```js
const observer = new IntersectionObserver(
  (entries) => entries.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('revealed'); observer.unobserve(e.target); }
  }),
  { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
);
document.querySelectorAll('[data-reveal]').forEach(el => observer.observe(el));
```

### 계단식 Reveal CSS
```css
[data-reveal] { opacity: 0; transform: translateY(24px); transition: all 0.6s cubic-bezier(0.16,1,0.3,1); }
[data-reveal].revealed { opacity: 1; transform: translateY(0); }
[data-reveal]:nth-child(2) { transition-delay: 0.1s; }
[data-reveal]:nth-child(3) { transition-delay: 0.2s; }
```

---

## 10. 의무 섹션 순서 (랜딩페이지)

```
1. 네비게이션 — 글래스 또는 미니멀 (sticky)
2. 히어로 — fold 위, CTA 포함, 최대 영향력
3. 소셜 프루프 — 로고 스트립 또는 수치
4. 핵심 기능 (3–5개)
5. 테스티모니얼 또는 케이스 스터디
6. 주요 CTA 섹션
7. 푸터
```

---

## 11. 모션 원칙

**사용 가능:** `transform`, `opacity`, `clip-path`, `filter`(제한), `grid-template-rows`

**금지:** `width`, `height`, `top`, `left`, `margin`, `padding`, `font-size` 직접 애니메이션

**금지 패턴:** `animation: bounce`, `elastic` 이징

**MOTION_INTENSITY 기준:**
- 1–3: CSS 전환만
- 4–6: IntersectionObserver reveal + 호버 상태
- 7–10: Motion One 시네마틱 애니메이션 추가

---

## 12. 출력 완전성 강제

### 금지된 출력 패턴
```
코드 내: <!-- ... -->  // ...  TODO  [여기에 추가]  [내용 동일]
산문: "계속할까요?"  "나머지도 동일"  "간결성을 위해 생략"
구조: 첫·마지막 섹션만 작성, 중간 생략, 스켈레톤으로 대체
```

### 완전성 기준
- 모든 섹션: 실제 한국어 콘텐츠 (플레이스홀더 없음)
- 모든 요소: `sm:`, `md:`, `lg:` 반응형 클래스
- 모든 상호작용: 호버·액티브 상태
- 모든 이미지: `loading="lazy"`, `alt`, 유효한 `src`
- 모든 아이콘: `<iconify-icon icon="solar:..."></iconify-icon>`

### 토큰 한계 시 처리
압축 금지. 섹션 종료 지점까지 작성 후:
```
[PAUSED — N of M 섹션 완료. "continue"를 보내면 다음 섹션부터 재개: {섹션명}]
```

---

## 13. 접근성 기준 (WCAG AA)

| 항목 | 기준 |
|------|------|
| 텍스트 명도 대비 | 4.5:1 이상 |
| 대형 텍스트 대비 | 3:1 이상 |
| 터치 타겟 최소 크기 | 44×44px |
| 포커스 인디케이터 | 가시적이고 명확 |
| 이미지 alt 텍스트 | 필수 |
| 시맨틱 HTML | `<button>`, `<nav>`, `<main>` 등 |

---

## 14. AI Slop 자가 테스트

```
□ "AI가 만들었겠다"는 생각이 드는가?
□ border-left/right 굵은 악센트 스트라이프가 있는가?
□ 그래디언트 텍스트가 있는가?
□ 시안/보라 글로우 on 다크 테마인가?
□ 모든 카드가 동일 크기·구조인가?
□ 금지 폰트 목록에 있는 폰트를 사용했는가?
□ Noto Sans KR을 한글에 사용했는가?
□ Lorem ipsum 또는 플레이스홀더 텍스트가 있는가?
□ 모든 섹션이 중앙 정렬인가?
□ 악센트 색상이 2개 이상인가?
```

하나라도 해당하면 수정 후 재검토.

---

## 15. 구현 품질 등급

| 등급 | 기준 |
|------|------|
| **APPROVED** | AI Slop 없음 + 접근성 AA + 반응형 + 출력 완전성 |
| **APPROVED_WITH_WARNINGS** | 경미한 P2 이슈 존재 |
| **NEEDS_REVISION** | P0 또는 P1 이슈 존재 |

---

## 16. 리디자인 감사 항목 (24개)

기존 페이지 업그레이드 시 아래 항목을 순서대로 점검한다.

### 타이포그래피 (1–4)
1. 브라우저 기본·Inter·Noto Sans KR → Pretendard로 교체
2. `word-break: keep-all` 미적용 → 적용
3. 라인 높이 < 1.5 → 1.6으로 조정
4. 스케일 비율 < 1.25× → 재설정

### 색상 (5–8)
5. `#000000` → `oklch(18% 0.01 250)`, `#ffffff` → `oklch(98% 0.007 250)`
6. 포화도 > 80% 악센트 → 조정
7. 악센트 색상 2개 이상 → 1개로 통합
8. AI 기본 팔레트(시안/청보라/형광) → 브랜드 색상으로 교체

### 레이아웃 (9–12)
9. 전 섹션 중앙 정렬 → 분할·비대칭으로 전환
10. 3단 동일 카드 그리드 → Bento 또는 지그재그
11. 히어로가 중앙 버튼만 → 분할 화면 또는 오버레이 추가
12. 섹션 여백 < `py-16` → `py-24 md:py-32`로 확장

### 상호작용 (13–16)
13. 호버 상태 없는 버튼 → `hover:scale-[1.02]` 추가
14. 링크 호버 없음 → 하이라이트·밑줄 전환 추가
15. 카드 호버 없음 → `hover:ring-1` 또는 그림자 추가
16. 전환 함수가 `ease` 또는 `linear` → 서명 곡선으로 교체

### 한국어 (17–19)
17. 번역 투 문장 → 자연스러운 한국어로 재작성
18. 경어 혼용 → 일관성 있는 존댓말/반말 통일
19. AI 클리셰("혁신적인", "솔루션") → 구체적 표현으로 교체

### 컴포넌트 (20–22)
20. Lucide·FontAwesome → Iconify Solar로 교체
21. 그래디언트 텍스트 → 단색으로 전환
22. border-left 스트라이프 → 전체 테두리 또는 배경 틴트

### 애니메이션 (23–24)
23. 애니메이션 없음 → IntersectionObserver reveal 추가
24. `bounce`, `elastic` 이징 → 서명 곡선(`cubic-bezier(0.16, 1, 0.3, 1)`)으로 교체
