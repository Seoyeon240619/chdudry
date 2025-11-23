import random
import string
import streamlit as st
import re


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


# Global requirements used when building or re-building strips
required_words = ["try", "more", "want", "please", "thanks", "sour", "salty", "spicy", "sweet"]
required_chars = set(''.join(required_words))
required_counts = {
    'a': 4,
    'c': 1,
    'e': 4,
    'h': 1,
}

# per-problem additional letter requirements (ensure these exist in that problem's strip)
per_problem_extra = [
    {'s': 1, 'o': 1, 'u': 1, 'r': 1},
    {'s': 1, 'a': 1, 'l': 1, 't': 1, 'y': 1},
    {'s': 1, 'p': 1, 'i': 1, 'c': 1, 'y': 1},
    {'s': 1, 'w': 1, 'e': 2, 't': 1}
]


def ensure_chars_with_counts(s: str, chars: set, counts: dict, extra_counts: dict):
    # ensure all letters from 'chars' exist at least once
    s_list = list(s)
    present = set(s_list)
    miss = chars - present
    for ch in miss:
        insert_pos = random.randint(max(0, len(s_list)-5), len(s_list))
        s_list[insert_pos:insert_pos] = list(make_noise(1)) + [ch]

    # now ensure specific global counts for letters in counts dict
    for ch, need in counts.items():
        have = s_list.count(ch)
        while have < need:
            insert_pos = random.randint(max(0, len(s_list)-5), len(s_list))
            s_list[insert_pos:insert_pos] = [ch]
            have += 1

    # ensure per-problem extra counts
    for ch, need in extra_counts.items():
        have = s_list.count(ch)
        while have < need:
            insert_pos = random.randint(max(0, len(s_list)-5), len(s_list))
            s_list[insert_pos:insert_pos] = [ch]
            have += 1

    return ''.join(s_list)


PROBLEMS = [
    {
        "situation": "🍋 [레모네이드 가판대]",
        "words": ["try", "sour", "want", "more", "please"],
        # use {index} to indicate which word (by index in 'words') fills that blank
        "sentences": [
            "A: Please {0} some lemonade.",
            "B: Thank you. It’s {1}.",
            "A: Do you {2} some {3}?",
            "B: Yes, {4}."
        ]
    },
    {
        "situation": "🍟 [감자튀김 가게]",
        "words": ["try", "salty", "want", "more", "thanks"],
        "sentences": [
            "A: Please {0} some fries.",
            "B: Thank you. They’re {1}.",
            "A: Do you {2} some {3}?",
            "B: No, {4}."
        ]
    },
    {
        "situation": "🍰 [케이크 생일파티]",
        "words": ["try", "sweet", "want", "more", "please"],
        "sentences": [
            "A: Please {0} some cake.",
            "B: Thank you. It’s {1}.",
            "A: Do you {2} some {3}?",
            "B: Yes, {4}."
        ]
    },
    {
        "situation": "🌶️ [카레 식당]",
        "words": ["try", "spicy", "want", "more", "thanks"],
        "sentences": [
            "A: Please {0} some curry.",
            "B: Thank you. It’s {1}.",
            "A: Do you {2} some {3}?",
            "B: No, {4}."
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
    # build initial strips from each problem's words
    strips = [build_strip(p["words"], noise=noise) for p in PROBLEMS]
    # ensure required letters (from curriculum) are present in every strip
    required_words = ["try","more","want","please","thanks","sour","salty","spicy","sweet"]
    required_chars = set(''.join(required_words))

    # global required counts from the attached image (must be present in each strip)
    # image requested: a 4, c 1, e 4, h 1, and other letters were listed in the image
    required_counts = {
        'a': 4,
        'c': 1,
        'e': 4,
        'h': 1,
        # include other counts from the image if desired (we keep these as minimums)
    }

    # per-problem additional letter requirements (ensure these exist in that problem's strip)
    per_problem_extra = [
        # problem 1: add letters for 'sour'
        {'s': 1, 'o': 1, 'u': 1, 'r': 1},
        # problem 2: add letters for 'salty'
        {'s': 1, 'a': 1, 'l': 1, 't': 1, 'y': 1},
        # problem 3: add s,p,i,c,y as requested
        {'s': 1, 'p': 1, 'i': 1, 'c': 1, 'y': 1},
        # problem 4: add s,w,e(2),t
        {'s': 1, 'w': 1, 'e': 2, 't': 1}
    ]

    def ensure_chars_with_counts(s: str, chars: set, counts: dict, extra_counts: dict):
        # ensure all letters from 'chars' exist at least once
        s_list = list(s)
        present = set(s_list)
        miss = chars - present
        for ch in miss:
            insert_pos = random.randint(max(0, len(s_list)-5), len(s_list))
            s_list[insert_pos:insert_pos] = list(make_noise(1)) + [ch]

        # now ensure specific global counts for letters in counts dict
        for ch, need in counts.items():
            have = s_list.count(ch)
            while have < need:
                insert_pos = random.randint(max(0, len(s_list)-5), len(s_list))
                s_list[insert_pos:insert_pos] = [ch]
                have += 1

        # ensure per-problem extra counts
        for ch, need in extra_counts.items():
            have = s_list.count(ch)
            while have < need:
                insert_pos = random.randint(max(0, len(s_list)-5), len(s_list))
                s_list[insert_pos:insert_pos] = [ch]
                have += 1

        return ''.join(s_list)

    strips_checked = []
    for i, s in enumerate(strips):
        extra = per_problem_extra[i] if i < len(per_problem_extra) else {}
        strips_checked.append(ensure_chars_with_counts(s, required_chars, required_counts, extra))

    st.session_state.strips = strips_checked
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
            # ensure required chars/counts are present in the regenerated strip
            extra = per_problem_extra[idx] if idx < len(per_problem_extra) else {}
            new_strip = ensure_chars_with_counts(new_strip, required_chars, required_counts, extra)
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

    import re

    st.subheader("대화문")
    # Sentences can contain placeholders like {0}, {1} indicating which word index to fill.
    placeholder_re = re.compile(r"\{(\d+)\}")
    def render_sentence(template: str, answers_list, reveal=False, words=None):
        def repl(m):
            idxw = int(m.group(1))
            if reveal and words is not None:
                return f"**{words[idxw]}**"
            val = answers_list[idxw] if idxw < len(answers_list) else ""
            return f"**{val or '____'}**"
        return placeholder_re.sub(repl, template)

    for sent in problem["sentences"]:
        st.markdown(render_sentence(sent, answers, reveal=False, words=problem["words"]))

    st.markdown("---")
    if st.button("정답 확인"):
        results = []
        for i, w in enumerate(problem["words"]):
            raw = answers[i] if i < len(answers) else ""
            ans = re.sub('[^a-z]', '', raw.lower().strip())
            results.append(ans == w.lower())
        correct_count = sum(results)
        st.success(f"맞은 개수: {correct_count} / {len(problem['words'])}")
        for i, ok in enumerate(results):
            correct_word = problem["words"][i] if i < len(problem["words"]) else ""
            if ok:
                st.write(f"{i+1}. ✅  (입력: '{answers[i]}')")
            else:
                st.write(f"{i+1}. ❌  (입력: '{answers[i]}')")
                st.markdown(f"**정답:** `{correct_word}`")
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
            # render each sentence with teacher answers (reveal=True)
            for s in p['sentences']:
                # use the same render_sentence helper
                # get the stored answers for that problem
                stored_answers = st.session_state.problem_answers[p_idx]
                st.markdown(render_sentence(s, stored_answers, reveal=True, words=p['words']))
                # show student's filled sentence (their inputs)
                st.markdown(f"**학생입력:** {render_sentence(s, stored_answers, reveal=False, words=p['words'])}")

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
