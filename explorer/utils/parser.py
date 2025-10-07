import re
from datetime import datetime

def try_float(s):
    try:
        return float(s)
    except Exception:
        return None

def parse_timestamp_from_filename(filename):
    m = re.search(r'(\d{8}_\d{6})', filename)
    if m:
        try:
            return datetime.strptime(m.group(1), '%Y%m%d_%H%M%S')
        except Exception:
            pass
    m = re.search(r'(\d{14})', filename)
    if m:
        try:
            return datetime.strptime(m.group(1), '%Y%m%d%H%M%S')
        except Exception:
            pass
    return None

def parse_timestamp_str(s):
    if not s:
        return None
    s = s.strip()
    fmts = ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S',
            '%Y-%m-%d', '%Y/%m/%d')
    for fmt in fmts:
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            pass
    try:
        epoch = float(s)
        if epoch > 1e12:
            epoch = epoch / 1000.0
        return datetime.fromtimestamp(epoch)
    except Exception:
        pass
    return None

def parse_file(file_path):
    records = []
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        raw_lines = [ln.rstrip('\n') for ln in f if ln.strip() != '']
    if not raw_lines:
        return records

    candidates = ['\t', ';', ',', ' ']
    best = {'delim': None, 'score': -1}
    sample = raw_lines[:50]
    for d in candidates:
        counts = [len([p for p in line.split(d) if p.strip()!='']) for line in sample]
        if max(counts) > 1:
            score = sum(counts)
            if score > best['score']:
                best = {'delim': d, 'score': score}
    delim = best['delim'] or '\t'

    rows = [[cell.strip() for cell in line.split(delim) if cell.strip()!=''] for line in raw_lines]
    if delim == ' ':
        avg_cols = sum(len(r) for r in rows)/len(rows)
        if avg_cols > 10:
            delim = '\t'
            rows = [[cell.strip() for cell in line.split(delim) if cell.strip()!=''] for line in raw_lines]

    header = False
    if len(rows) > 1:
        first = rows[0]
        non_numeric = 0
        numeric_test_count = max(1, len(first)-1)
        for v in first[1:]:
            if try_float(v) is None and parse_timestamp_str(v) is None:
                non_numeric += 1
        if non_numeric >= numeric_test_count:
            header = True

    data_rows = rows[1:] if header else rows

    for cols in data_rows:
        if len(cols) < 7:
            continue
        filename = cols[0]
        if len(cols) >= 8:
            ts = parse_timestamp_str(cols[1]) or parse_timestamp_from_filename(filename)
            try:
                x = float(cols[2]); y = float(cols[3]); z = float(cols[4])
                roll = float(cols[5]); pitch = float(cols[6]); yaw = float(cols[7])
            except Exception:
                continue
        else:
            ts = parse_timestamp_from_filename(filename)
            try:
                x = float(cols[1]); y = float(cols[2]); z = float(cols[3])
                roll = float(cols[4]); pitch = float(cols[5]); yaw = float(cols[6])
            except Exception:
                continue

        records.append({
            'filename': filename,
            'timestamp': ts,
            'x': x, 'y': y, 'z': z,
            'roll': roll, 'pitch': pitch, 'yaw': yaw
        })

    return records
