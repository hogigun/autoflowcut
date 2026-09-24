"""TTS용 원고 만들기: 끊어 읽기를 일으키는 띄어쓰기를 붙여 쓴다.

편집용 원고(맞춤법대로)는 건드리지 않고, 별도의 TTS용 텍스트와 변경 목록을 만든다.

사용법:
    python3 tools/tts_prep.py <에피소드 폴더>
결과:
    <폴더>/원고_TTS용.txt    : 장 제목을 뺀 TTS 낭독용 원고
    <폴더>/04_TTS변환목록.md : 규칙별로 바뀐 곳 전부 (검토용)

규칙 추가·예외는 아래 표만 고치면 된다. 에피소드마다 인물 호칭은 NAME_TITLES에 더한다.
"""
import re
import sys
import glob
import os
from collections import defaultdict

# 규칙 1. 성 + 호칭 (인물표에서 가져와 에피소드마다 추가)
NAME_TITLES = ["심 대감", "노 청지기", "곽 마름", "곽 청지기", "권 진사"]

# 규칙 2. 수사 + 단위
NUMERALS = (
    "한|두|세|네|몇|다섯|여섯|일곱|여덟|아홉|열|스물|서른|마흔|쉰|예순|일흔|여든|아흔|"
    "열[한두세네]|열다섯|열여섯|열일곱|열여덟|열아홉|"
    "(?:스물|서른|마흔|쉰|예순|일흔|여든|아흔)(?:한|두|세|네|다섯|여섯|일곱|여덟|아홉)|"
    "삼|십|삼십|백|천|백[가-힣]{1,3}"
)
UNITS = "칸|땀|해|섬|살|년|필|냥|되|번|권|채|켤레|가지|달|장|톨|치|뼘|방울|줄|마디|걸음|합"  # "자"는 한자(漢字)와 헷갈려 제외
RE_NUM_UNIT = re.compile(rf"(?<![가-힣])({NUMERALS}) ({UNITS})(?![가-힣])|(?<![가-힣])({NUMERALS}) ({UNITS})(?=[가-힣])")

# 규칙 3. 굳어진 명사구 (에피소드 핵심 소품 등)
FIXED_PHRASES = ["붉은 실", "푸른 실", "나비 매듭", "굵은 매듭", "가는 땀", "새 도포", "대감 마님", "해 치", "년 치"]

# 규칙 4. 본용언 + 보조용언 (-아/-어 + 내다/주다/드리다/보다/버리다/놓다/두다)
AUX_PREFIX = ("내", "낸", "냈", "주", "준", "줬", "드리", "드린", "드렸", "보", "본", "봤", "버리", "버린", "버렸", "놓", "두", "둔")
AUX_BLOCK_NEXT = ("준이", "보자기", "보따리", "보름", "주먹", "주머니", "주변", "주인", "두루", "두 ", "내일", "내내", "내려", "주름", "보릿")
AUX_BLOCK_PREV = {"절대", "나", "너", "저", "다", "또", "더", "자", "아", "거", "그", "이", "어", "가", "왜", "뭐", "꼭", "좀", "잘"}

# 받침 없는 ㅏ/ㅓ/ㅕ/ㅐ/ㅘ/ㅝ/ㅙ/ㅚ(되어→돼) 모음으로 끝나거나 '-어/-아'로 끝나는 말
AUX_END_VOWELS = {0, 4, 6, 1, 9, 14, 10}  # ㅏ ㅓ ㅕ ㅐ ㅘ ㅝ ㅙ


# 조사·어미로 끝나는 말(에서, 누군가, 그러다, 달래와, 밤새 등)은 보조용언 앞말이 아니다
AUX_BLOCK_LAST = {"서", "다", "가", "와", "새", "나", "야", "라", "냐", "까", "지"}


def ends_with_a_eo(word: str) -> bool:
    if not word or word[-1] in AUX_BLOCK_LAST:
        return False
    ch = word[-1]
    code = ord(ch) - 0xAC00
    if not (0 <= code < 11172):
        return False
    jong = code % 28
    jung = (code // 28) % 21
    return jong == 0 and jung in AUX_END_VOWELS


RE_AUX_PAIR = re.compile(r"(?<![가-힣])([가-힣]+) (?=([가-힣]+))")


def join_aux(text, log):
    out, pos = [], 0
    for m in RE_AUX_PAIR.finditer(text):
        a, b = m.group(1), m.group(2)
        if a in AUX_BLOCK_PREV or len(a) < 2 or not ends_with_a_eo(a):
            continue
        if any(b.startswith(x.strip()) for x in AUX_BLOCK_NEXT) or not b.startswith(AUX_PREFIX):
            continue
        out.append(text[pos:m.end(1)])
        pos = m.end(1) + 1  # 공백 하나 건너뜀
        log["규칙4 보조용언"].append(f"{a} {b} → {a}{b}")
    out.append(text[pos:])
    return "".join(out)


def convert(text):
    log = defaultdict(list)
    for p in NAME_TITLES:
        n = text.count(p)
        if n:
            text = text.replace(p, p.replace(" ", ""))
            log["규칙1 성+호칭"].append(f"{p} → {p.replace(' ', '')} ({n}곳)")

    def num_repl(m):
        num = m.group(1) or m.group(3)
        unit = m.group(2) or m.group(4)
        log["규칙2 수사+단위"].append(f"{num} {unit} → {num}{unit}")
        return num + unit
    for _ in range(2):
        text = RE_NUM_UNIT.sub(num_repl, text)

    for p in FIXED_PHRASES:
        n = text.count(p)
        if n:
            text = text.replace(p, p.replace(" ", ""))
            log["규칙3 굳어진 말"].append(f"{p} → {p.replace(' ', '')} ({n}곳)")

    text = join_aux(text, log)
    return text, log


def main(folder):
    parts = sorted(glob.glob(os.path.join(folder, "*_[0-9].md")))
    body = []
    for f in parts:
        lines = open(f, encoding="utf-8").read().splitlines()
        body.append("\n".join(l for l in lines if not l.startswith("## ")).strip())
    src = re.sub(r"\n{3,}", "\n\n", "\n\n".join(body)) + "\n"
    open(os.path.join(folder, "원고_전체_낭독용.txt"), "w", encoding="utf-8").write(src)
    out, log = convert(src)
    open(os.path.join(folder, "원고_TTS용.txt"), "w", encoding="utf-8").write(out)
    rep = ["# 04. TTS 변환 목록", "", "편집용 원고는 그대로 두고 `원고_TTS용.txt`에만 적용한 변경입니다. 어색한 줄이 있으면 `tools/tts_prep.py`의 예외 목록에 넣으세요.", ""]
    for k in sorted(log):
        items = log[k]
        uniq = defaultdict(int)
        for it in items:
            uniq[it] += 1
        rep.append(f"## {k} ({len(items)}곳)")
        for it, c in sorted(uniq.items()):
            rep.append(f"- {it}" + (f" ×{c}" if c > 1 and '곳)' not in it else ""))
        rep.append("")
    open(os.path.join(folder, "04_TTS변환목록.md"), "w", encoding="utf-8").write("\n".join(rep))
    print({k: len(v) for k, v in log.items()})


if __name__ == "__main__":
    main(sys.argv[1])
