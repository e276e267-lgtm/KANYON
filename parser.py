import re

LETTER_MAP = {
    'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8, 'i': 9,
    'j': 10, 'k': 11, 'l': 12, 'm': 13, 'n': 14, 'o': 15, 'p': 16, 'q': 17,
    'r': 18, 's': 19, 't': 20, 'u': 21, 'v': 22, 'w': 23, 'x': 24, 'y': 25, 'z': 26
}

FUNCTION_MAP = {
    't': [49, 94, 27, 72, 68, 86, 13, 31],
    's': [14, 41, 28, 82, 76, 67, 39, 93],
    'y': [62, 26, 78, 87, 19, 91, 34, 43],
    'z': [29, 92, 47, 74, 16, 61, 38, 83],
    'j': [96, 69, 48, 84, 12, 21, 73, 37],
    'g': [18, 81, 36, 63, 42, 24, 97, 79],
    'h': [46, 64, 89, 98, 23, 32, 71, 17],
    'f': [11, 22, 33, 44, 55, 66, 77, 88, 99, 0]
}

REVERSE_MAP = {}
for func, numbers in FUNCTION_MAP.items():
    for num in numbers:
        REVERSE_MAP[num] = func


def preprocess_alphanumeric(seq: str) -> str:
    result, i, n = [], 0, len(seq)
    while i < n:
        ch = seq[i]
        if ch.isdigit():
            num_part = []
            while i < n and seq[i].isdigit():
                num_part.append(seq[i]);
                i += 1
            ns = "".join(num_part)
            if i < n and seq[i].isalpha():
                val = LETTER_MAP.get(seq[i].lower())
                if val is not None:
                    result.append(f"{ns}{val}");
                    i += 1;
                    continue
            result.append(ns)
        elif ch.isalpha():
            val = LETTER_MAP.get(ch.lower())
            if val is not None: result.append(str(val))
            i += 1
        else:
            i += 1
    return "".join(result)


def find_pattern_middle(seq: str, mid: str, prefix: str):
    res, i, n = [], 0, len(seq)
    while i < n:
        if seq[i] != mid:
            j = i + 1
            while j < n and seq[j] == mid: j += 1
            if j > i + 1 and j < n:
                td = int(seq[i] + seq[j])
                func = REVERSE_MAP.get(td)
                if func:
                    res.append({'start': i, 'end': j, 'output': prefix + func, 'pat': seq[i:j + 1]})
                i = j
            else:
                i += 1
        else:
            i += 1
    return res


def rule4(seq: str):
    res, cov, pat = [], [], re.compile(r'2(\d)\1+3')
    for m in pat.finditer(seq):
        s, e, full, D = m.start(), m.end(), m.group(0), m.group(1)
        if D == '5': continue
        f1, f2 = REVERSE_MAP.get(int(full[:2])), REVERSE_MAP.get(int(full[-2:]))
        if f1 and f2:
            cov.append((s, e))
            if f1 != 'f': res.append({'pos': s, 'res': f1, 'type': '規則4', 'pat': full[:2]})
            res.append({'pos': s + 1, 'res': '+f', 'type': '規則4', 'pat': full[1:3]})
            if f2 != 'f': res.append({'pos': s + len(full) - 2, 'res': f2, 'type': '規則4', 'pat': full[-2:]})
    return res, cov


def detect_overlaps(seq: str):
    res, blk, i, n = [], set(), 0, len(seq)
    while i < n - 1:
        if i + 2 < n and seq[i] == seq[i + 1] == seq[i + 2]:
            ch, rs = seq[i], i
            while i < n and seq[i] == ch: i += 1
            rl = i - rs
            cnt = (rl - 1) // 2 + (1 if rl >= 3 else 0)
            for k in range(cnt):
                p = rs + k * 2
                if p + 1 < i:
                    res.append({'pos': p, 'res': '+f', 'type': '規則(+)', 'pat': ch * 2})
                    blk.add(p);
                    blk.add(p + 1)
        else:
            i += 1
    return res, blk


def analyze(seq: str) -> dict:
    seq = seq.strip().replace(" ", "")
    orig = seq
    proc = preprocess_alphanumeric(seq)
    if not proc.isdigit() or len(proc) < 2:
        return {"error": "輸入格式無效或長度不足"}

    blk, out = set(), []
    r4, c4 = rule4(proc)
    for s, e in c4:
        for p in range(s, e): blk.add(p)
    out.extend(r4)

    for r in find_pattern_middle(proc, '5', '+') + find_pattern_middle(proc, '0', '-'):
        if not any(p in blk for p in range(r['start'], r['end'] + 1)):
            out.append({'pos': r['start'], 'res': r['output'], 'type': f"規則({r['output'][0]})", 'pat': r['pat']})
            for p in range(r['start'] + 1, r['end']): blk.add(p)

    ov, ob = detect_overlaps(proc)
    for t in ov:
        if t['pos'] not in blk and t['pos'] + 1 not in blk:
            out.append(t);
            blk.add(t['pos']);
            blk.add(t['pos'] + 1)
    blk.update(ob)

    for i in range(len(proc) - 1):
        if i in blk or i + 1 in blk: continue
        val = int(proc[i:i + 2])
        func = REVERSE_MAP.get(val)
        if func: out.append({'pos': i, 'res': func, 'type': '規則1', 'pat': proc[i:i + 2]})

    out.sort(key=lambda x: x['pos'])
    return {
        "original": orig,
        "processed": proc,
        "results": out,
        "sequence": " ".join([x['res'] for x in out])
    }