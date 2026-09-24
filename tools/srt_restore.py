"""브루 SRT(붙여쓰기 판)의 시간은 그대로 두고 글자만 맞춤법판으로 되돌린다.

붙여쓰기판과 맞춤법판은 띄어쓰기만 다르므로, 글자(한글·영숫자)만 뽑아 순서대로 맞춘다.
사용법: python3 tools/srt_restore.py <에피소드 폴더> <브루 SRT>
결과: <폴더>/srt/자막_맞춤법.srt, 맞지 않는 블록은 화면에 출력
"""
import re
import sys
import os

SIG = re.compile(r"[가-힣A-Za-z0-9]")


def parse(path):
    t = open(path, encoding="utf-8-sig").read().replace("\r", "")
    rows = []
    for b in t.strip().split("\n\n"):
        L = b.strip().split("\n")
        if len(L) >= 3:
            rows.append((L[1], " ".join(L[2:]).strip()))
    return rows


def main(folder, srt):
    src = open(os.path.join(folder, "원고_전체_낭독용.txt"), encoding="utf-8").read()
    src = re.sub(r"\s+", " ", src)
    sig_idx = [i for i, c in enumerate(src) if SIG.match(c)]
    rows = parse(srt)
    pos, out, bad = 0, [], []
    for n, (tc, text) in enumerate(rows, 1):
        want = [c for c in text if SIG.match(c)]
        got = [src[i] for i in sig_idx[pos:pos + len(want)]]
        if got != want:
            bad.append((n, text))
            out.append((tc, text))  # 못 맞추면 브루 글자 그대로
            # 다음 블록에서 다시 맞출 수 있게 위치를 찾아 이동
            joined = "".join(src[i] for i in sig_idx)
            k = joined.find("".join(want), pos)
            if k != -1:
                pos = k + len(want)
            continue
        a = sig_idx[pos]
        z = sig_idx[pos + len(want) - 1] + 1
        # 브루 블록 끝의 문장부호(예: ." ?" ,)를 원고에서 그대로 이어 붙인다
        tail = re.search(r'[.?!,"]*$', text).group(0)
        if tail and src[z:z + len(tail)] == tail:
            z += len(tail)
        if src[a - 1:a] == '"' and text.startswith('"'):
            a -= 1
        out.append((tc, src[a:z].strip()))
        pos += len(want)
    dst = os.path.join(folder, "srt", "자막_맞춤법.srt")
    with open(dst, "w", encoding="utf-8") as f:
        for n, (tc, text) in enumerate(out, 1):
            f.write(f"{n}\n{tc}\n{text}\n\n")
    print(f"블록 {len(rows)}개, 맞춤법 복원 {len(rows) - len(bad)}개, 못 맞춘 블록 {len(bad)}개")
    for n, t in bad[:20]:
        print(" -", n, t)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
