"""브루(Vrew)에 붙여 넣을 원고 만들기: 한 줄에 한 문장, 따옴표 대사는 한 줄로 유지.

사용법: python3 tools/vrew_split.py <에피소드 폴더>
결과: 브루용_붙여쓰기.txt (원고_TTS용.txt 기반), 브루용_맞춤법.txt (원고_전체_낭독용.txt 기반)
"""
import re
import sys
import os


def split_para(p):
    out = []
    for seg in re.split(r'("[^"]*")', p):
        seg = seg.strip()
        if not seg:
            continue
        if seg.startswith('"'):
            out.append(seg)
            continue
        out += [s.strip() for s in re.findall(r".+?(?:[.?!](?=\s|$)|$)", seg) if s.strip()]
    return out


def main(folder):
    for src, dst in [("원고_TTS용.txt", "브루용_붙여쓰기.txt"), ("원고_전체_낭독용.txt", "브루용_맞춤법.txt")]:
        lines = []
        for p in open(os.path.join(folder, src), encoding="utf-8").read().split("\n"):
            if p.strip():
                lines += split_para(p.strip())
        open(os.path.join(folder, dst), "w", encoding="utf-8").write("\n".join(lines) + "\n")
        print(dst, len(lines), "줄")


if __name__ == "__main__":
    main(sys.argv[1])
