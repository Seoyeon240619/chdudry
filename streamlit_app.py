import random
import string
import streamlit as st


def make_noise(n):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(n))


def build_strip(words, noise=5):
    parts = []
    order = words[:]
    random.shuffle(order)
    for w in order:
        parts.append(make_noise(noise))
        parts.append(w)
    parts.append(make_noise(noise))
    return ''.join(parts)


PROBLEMS = [
    {
        "situation": "🍋 [레모네이드 가판대]",
        "words": ["drink", "sour", "want", "more", "please"],
        "sentences": [
            "A: Please ____ some lemonade.",
            "B: Thank you. It’s ____.",
            "A: Do you ____ some ____?",
            "B: Yes, ____."
        ]
    },
    {
        "situation": "🍟 [감자튀김 가게]",
        "words": ["eat", "salty", "want", "more", "thanks"],
        "sentences": [
            "A: Please ____ some fries.",
            "B: Thank you. They’re ____.",
            "A: Do you ____ some ____?",
            "B: No, ____."
        ]
    },
    {
        "situation": "🍰 [케이크 생일파티]",
        "words": ["have", "sweet", "want", "more", "please"],
        "sentences": [
            "A: Please ____ some cake.",
            "B: Thank you. It’s ____.",
            "A: Do you ____ some ____?",
            "B: Yes, ____."
        ]
    },
    {
        "situation": "🌶️ [카레 식당]",
        "words": ["try", "spicy", "want", "more", "thanks"],
        "sentences": [
            "A: Please ____ some curry.",
            "B: Thank you. It’s ____.",
            "A: Do you ____ some ____?",
            "B: No, ____."
        ]
    }
]

st.set_page_config(page_title="Taste Finder", layout="wide")

st.title("🍭 Taste Finder — 문장 채우기 활동")

st.write("종이띠에서 단어를 찾아 아래 문장의 빈칸(____)에 넣어보세요. 문제는 차례대로 풀어주세요.")

col_strip = st.container()
st.write("---")
st.header("학생용 모드 — 문장 채우기")
st.write("문제를 하나씩 차례대로 풀어보세요.")
noise = 3


# 문제별 상태 관리 (학생용: 각 문제에 대한 strip/used/answers 보관)
if 'problem_idx' not in st.session_state:
    st.session_state.problem_idx = 0
if 'strips' not in st.session_state:
    st.session_state.strips = [build_strip(p["words"], noise=noise) for p in PROBLEMS]
if 'useds' not in st.session_state:
    st.session_state.useds = [[False] * len(s) for s in st.session_state.strips]
if 'problem_answers' not in st.session_state:
    st.session_state.problem_answers = [[""] * len(p["words"]) for p in PROBLEMS]
if 'current' not in st.session_state:
    st.session_state.current = 0
# track which problems the student has checked
if 'checked' not in st.session_state:
    st.session_state.checked = [False] * len(PROBLEMS)
# whether to reveal all answers at the end
if 'revealed_all' not in st.session_state:
    st.session_state.revealed_all = False
# per-problem checked/reveal flags removed for student-only mode

with col_strip:
    idx = st.session_state.problem_idx
    problem = PROBLEMS[idx]
    st.subheader(f"문제 {idx+1} / {len(PROBLEMS)}")
    st.write(problem["situation"])
    strip = st.session_state.strips[idx]
    used = st.session_state.useds[idx]
    answers = st.session_state.problem_answers[idx]
    st.write("아래 종이띠에서 글자를 클릭해 빈칸을 채우세요. (🔤: 사용 가능, ✅: 사용된 글자)")

    # display letters in several rows so they don't overlap and are all visible
    row_size = 15
    st.write("**글자 버튼 (🔤: 사용 가능, ✅: 사용된 글자)**")
    for row_start in range(0, len(strip), row_size):
        row = strip[row_start:row_start+row_size]
        cols = st.columns(len(row))
        for offset, ch in enumerate(row):
            i = row_start + offset
            key = f"l_{idx}_{i}"
            disabled = used[i]
            # show emoji to indicate state; keep label short so buttons fit
            label = f"{ch}"
            if disabled:
                label = f"✅ {ch}"
            else:
                label = f"🔤 {ch}"
            with cols[offset]:
                if st.button(label, key=key, disabled=disabled):
                    cur = st.session_state.current if 'current' in st.session_state else 0
                    answers[cur] += ch
                    used[i] = True
                    # write back
                    st.session_state.problem_answers[idx] = answers
                    st.session_state.useds[idx] = used

    st.markdown("---")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("초기화(문제만)"):
            new_strip = build_strip(problem["words"], noise=3)
            st.session_state.strips[idx] = new_strip
            st.session_state.useds[idx] = [False] * len(new_strip)
            st.session_state.problem_answers[idx] = [""] * len(problem["words"])
            st.session_state.current = 0
    with c2:
        if st.button("선택 단어 지우기"):
            cur = st.session_state.current if 'current' in st.session_state else 0
            word = answers[cur]
            if word:
                cnt = len(word)
                freed = 0
                for i in range(len(strip)-1, -1, -1):
                    if used[i] and freed < cnt:
                        used[i] = False
                        freed += 1
                answers[cur] = ""
                st.session_state.problem_answers[idx] = answers
                st.session_state.useds[idx] = used
    # no per-problem public reveal in student mode

    st.markdown("---")
    blanks = [f"Blank {i+1}" for i in range(len(problem["words"]))]
    choice = st.radio("현재 빈칸 선택:", options=blanks, index=st.session_state.get('current', 0))
    st.session_state.current = int(choice.split()[1]) - 1

    st.subheader("대화문")
    for idx2, sent in enumerate(problem["sentences"]):
        ans = answers[idx2] if idx2 < len(answers) else ""
        display_word = ans if ans != "" else "____"
        st.markdown(f"{sent.replace('____', f'**{display_word}**')}")

    st.markdown("---")
    if st.button("정답 확인"):
        results = []
        for i, w in enumerate(problem["words"]):
            ans = answers[i].lower()
            results.append(ans == w)
        correct_count = sum(results)
        st.success(f"맞은 개수: {correct_count} / {len(problem['words'])}")
        for i, ok in enumerate(results):
            if ok:
                st.write(f"{i+1}. ✅")
            else:
                st.write(f"{i+1}. ❌  (입력: '{answers[i]}')")
        # student completed this problem (answers are kept)
        st.session_state.checked[idx] = True

    # 모든 문제를 확인하면 전체 정답 보기 버튼을 표시
    if all(st.session_state.checked) and not st.session_state.revealed_all:
        if st.button("모든 문제 정답 보기"):
            st.session_state.revealed_all = True

    if st.session_state.revealed_all:
        st.markdown("---")
        st.header("정답 (모든 문제)")
        for p_idx, p in enumerate(PROBLEMS):
            st.subheader(f"문제 {p_idx+1}: {p['situation']}")
            for s_idx, s in enumerate(p['sentences']):
                word = p['words'][s_idx]
                student_ans = st.session_state.problem_answers[p_idx][s_idx]
                st.markdown(f"{s.replace('____', f'**{word}**')} → 학생입력: **{student_ans or '(빈칸)'}**")

    st.markdown("---")
    c_prev, c_next = st.columns([1, 1])
    with c_prev:
        if st.button("이전 문제", disabled=st.session_state.problem_idx==0):
            st.session_state.problem_idx -= 1
            st.session_state.current = 0
    with c_next:
        if st.button("다음 문제", disabled=st.session_state.problem_idx==len(PROBLEMS)-1):
            st.session_state.problem_idx += 1
            st.session_state.current = 0
