#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify.py — 全球制裁 / 出口管制清单数据源 链接可用性校验

读取 sources.csv 与 export-control-sources.csv 中的 download_url，
逐个做 HEAD（失败回退 GET）请求，校验是否可达、返回的内容类型与文件格式是否吻合。

用法：
    python verify.py                # 校验全部，输出汇总表
    python verify.py --fail-only    # 只显示失败项
    python verify.py --csv out.csv  # 额外把结果写出到 out.csv

退出码：
    0 = 全部可达
    1 = 存在不可达项（供 CI 判定）
依赖：仅 Python 标准库
"""
import argparse
import csv
import io
import ssl
import sys
import urllib.error
import urllib.request

FILES = ["sources.csv", "export-control-sources.csv"]
UA = "Mozilla/5.0 (cn-sanctions-sources-verify)"
TIMEOUT = 20

# 期望：download_url 声明的 format 与响应 Content-Type 大致对应
FORMAT_HINTS = {
    "csv": ("text/csv", "application/csv", "application/vnd.ms-excel", "text/plain"),
    "xml": ("application/xml", "text/xml"),
    "json": ("application/json", "text/json"),
    "html": ("text/html",),
    "xlsx": ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",),
}


def check(url):
    """返回 (ok, status, content_type, error)。"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as r:
                return True, r.status, r.headers.get("Content-Type", ""), ""
        except urllib.error.HTTPError as e:
            # 4xx/5xx：HEAD 常被拒，回退 GET；否则记为失败
            if method == "HEAD" and e.code in (403, 405, 400, 501):
                continue
            return False, e.code, "", f"HTTP {e.code}"
        except Exception as e:  # 网络错误等
            if method == "HEAD":
                continue
            return False, 0, "", f"{type(e).__name__}: {e}"
    return False, 0, "", "unreachable"


def load_rows():
    rows = []
    for fn in FILES:
        try:
            with io.open(fn, encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    r["_file"] = fn
                    rows.append(r)
        except FileNotFoundError:
            print(f"[warn] 未找到 {fn}，跳过", file=sys.stderr)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fail-only", action="store_true", help="只显示失败项")
    ap.add_argument("--csv", help="把结果额外写出到此 CSV")
    args = ap.parse_args()

    rows = load_rows()
    if not rows:
        print("没有可校验的数据。", file=sys.stderr)
        sys.exit(2)

    results = []
    ok_count = 0
    print(f"{'FILE':<28}{'STATUS':<7}{'CODE':<5}{'FORMAT':<10}{'CT':<28}URL")
    print("-" * 110)
    for r in rows:
        url = (r.get("download_url") or "").strip()
        fmt = (r.get("format") or "").strip().lower()
        name = r.get("list_name_en") or r.get("list_name") or ""
        if not url:
            status, code, ct, err = False, 0, "", "no url"
        else:
            status, code, ct, err = check(url)
        ok = status
        # 格式吻合检查（仅对明确格式做宽松提示）
        fmt_ok = ""
        if ok and fmt and fmt in FORMAT_HINTS:
            fmt_ok = "ok" if any(h in (ct or "").lower() for h in FORMAT_HINTS[fmt]) else "type?"
        if ok:
            ok_count += 1
            flag = "OK " if not args.fail_only else "OK "
        else:
            flag = "FAIL"
        if args.fail_only and ok:
            continue
        print(f"{r['_file']:<28}{flag:<7}{str(code):<5}{fmt:<10}{ct[:26]:<28}{name}  {url}")
        results.append({**r, "http_status": code, "content_type": ct,
                        "reachable": "yes" if ok else "no", "error": err,
                        "format_match": fmt_ok})

    total = len(results) if args.fail_only else len(rows)
    checked = len(results)
    print("-" * 110)
    print(f"可达 {ok_count}/{len(rows)}；本表显示 {checked} 项。")

    if args.csv:
        fields = list(rows[0].keys()) + ["http_status", "content_type", "reachable", "error", "format_match"]
        with io.open(args.csv, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for r in results:
                w.writerow(r)
        print(f"结果已写出: {args.csv}")

    sys.exit(0 if ok_count == len(rows) else 1)


if __name__ == "__main__":
    main()
