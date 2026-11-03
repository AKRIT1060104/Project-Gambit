"""
bench.py - test, debug and benchmark toolkit for Project Gambit (V2)

Run with no arguments for a menu, or:
    python bench.py quick                  fast sanity pass of everything
    python bench.py perft   [--depth N]    perft suite vs known counts
    python bench.py diff --fen "..." --depth N   find the exact bad move (needs: pip install chess)
    python bench.py integrity [--depth N]  make/undo/hash/king-cache/eval checks
    python bench.py rules                  mate/stalemate/draw/repetition checks
    python bench.py tactics [--depth N]    does the engine find obvious moves
    python bench.py search  [--depth N] [--label NAME]   search bench, saved to bench_results/
    python bench.py speed                  micro-benchmarks of every hot function
    python bench.py profile [--depth N] [--fen "..."]    cProfile of one search
    python bench.py compare --label A --other B          compare two saved search benches

Extra: --dir V1  (run against another folder, e.g. to bench V1 vs V2)
Put this file in the folder that has board.py/engine.py/eval.py, or use --dir.
"""
import sys
import os
import time
import json
import random
import argparse
import cProfile
import pstats
import io
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, "bench_results")

Chessboard = Engine = evaluate = evaluate_relative = compute_hash = None

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
KIWI = "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1"
#r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1

# name, fen, known perft counts for depth 1..n
PERFT = [
    ("startpos", START_FEN, [20, 400, 8902, 197281, 4865609]),
    ("kiwipete", KIWI, [48, 2039, 97862, 4085603]),
    ("pos3", "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1", [14, 191, 2812, 43238, 674624]),
    ("pos4", "r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1", [6, 264, 9467, 422333]),
    ("pos5", "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8", [44, 1486, 62379, 2103487]),
    ("pos6", "r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10", [46, 2079, 89890, 3894594]),
]

# positions for search bench / integrity walks
SEARCH_POS = [
    ("startpos", START_FEN),
    ("kiwipete", KIWI),
    ("pos3", PERFT[2][1]),
    ("pos4", PERFT[3][1]),
    ("pos5", PERFT[4][1]),
    ("pos6", PERFT[5][1]),
    ("italian", "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4"),
    ("kp_end", "8/2k5/8/3p4/3P4/8/2K5/8 w - - 0 1"),
    ("rook_end", "8/8/4kpp1/3p1p2/3P1P2/4K1P1/8/R7 w - - 0 1"),
]

# name, fen, expected game_status()
RULES = [
    ("checkmate", "7k/6Q1/6K1/8/8/8/8/8 b - - 0 1", "checkmate"),
    ("stalemate", "7k/5Q2/6K1/8/8/8/8/8 b - - 0 1", "stalemate"),
    ("check", "4k3/8/8/8/8/8/8/4R1K1 b - - 0 1", "check"),
    ("insufficient K v K", "8/8/4k3/8/8/3K4/8/8 w - - 0 1", "draw_insufficient_material"),
    ("insufficient KN v K", "8/8/4k3/8/8/3K4/8/6N1 w - - 0 1", "draw_insufficient_material"),
    ("sufficient KR v K", "8/8/4k3/8/8/3K4/8/7R w - - 0 1", "playing"),
    ("50 move rule", "8/8/4k3/8/8/3K4/8/7R w - - 100 80", "draw_50_moves"),
    ("normal start", START_FEN, "playing"),
]

# name, fen, acceptable best moves
TACTICS = [
    ("mate in 1 (white)", "6k1/5ppp/8/8/8/8/5PPP/R5K1 w - - 0 1", ["a1a8"]),
    ("mate in 1 (black)", "r5k1/5ppp/8/8/8/8/5PPP/6K1 b - - 0 1", ["a8a1"]),
    ("take hanging queen", "4k3/8/8/3q4/8/8/8/3RK3 w - - 0 1", ["d1d5"]),
]


# ----------------------------------------------------------------- setup
def load_engine(path=None):
    global Chessboard, Engine, evaluate, evaluate_relative, compute_hash
    if path:
        sys.path.insert(0, os.path.abspath(path))
    from board import Chessboard as CB
    Chessboard = CB
    try:
        from engine import Engine as EN
        Engine = EN
    except Exception as e:
        print("(no usable Engine class here: %s)" % e)
    try:
        from eval import evaluate as ev, evaluate_relative as evr
        evaluate, evaluate_relative = ev, evr
    except Exception:
        pass
    try:
        from zobrist_hash import compute_hash as ch
        compute_hash = ch
    except Exception:
        pass


def hdr(title):
    print("\n=== %s ===" % title)


def sq(r, c):
    return chr(ord("a") + c) + str(8 - r)


def move_str(m):
    s = sq(m.from_row, m.from_col) + sq(m.to_row, m.to_col)
    if m.promotion:
        s += m.promotion[1].lower()
    return s


def new_game(fen=None):
    g = Chessboard()
    if fen:
        g.load_fen(fen)
    return g


def find_move(game, uci):
    for m in game.legal_moves():
        if move_str(m) == uci:
            return m
    return None


def snapshot(g):
    snap = {
        "board": tuple(tuple(r) for r in g.board),
        "who_to_move": g.who_to_move,
        "castling_rights": g.castling_rights,
        "en_passant_square": g.en_passant_square,
        "white_king_square": g.white_king_square,
        "black_king_square": g.black_king_square,
        "history_len": len(g.move_history),
    }
    for attr in ("halfmove_clock", "hash", "eval_score"):
        if hasattr(g, attr):
            snap[attr] = getattr(g, attr)
    if hasattr(g, "state_history"):
        snap["state_len"] = len(g.state_history)
    return snap


def fmt_rate(n, secs):
    return "%s/s" % format(int(n / secs), ",") if secs > 0 else "-"


# ----------------------------------------------------------------- perft
def run_perft(max_depth=4, budget=60.0):
    hdr("PERFT SUITE (max depth %d)" % max_depth)
    fails = []
    tot_n = 0
    tot_t = 0.0
    for name, fen, expected in PERFT:
        print(name)
        last = None
        for d in range(1, min(max_depth, len(expected)) + 1):
            if last is not None and last * 20 > budget:
                print("  d%d skipped (too slow)" % d)
                break
            g = new_game(fen)
            t = time.perf_counter()
            n = g.perft(d)
            el = time.perf_counter() - t
            last = el
            tot_n += n
            tot_t += el
            ok = n == expected[d - 1]
            status = "ok" if ok else "FAIL (want %d)" % expected[d - 1]
            print("  d%d %9d %-16s %5.2fs %s" % (d, n, status, el, fmt_rate(n, el)))
            if not ok:
                fails.append((name, d))
                break
    print("\nTotal %d nodes, %.1fs, %s" % (tot_n, tot_t, fmt_rate(tot_n, tot_t)))
    if fails:
        print("FAILED:", fails)
        print("Use:  python bench.py diff --fen \"<fen>\" --depth N")
    else:
        print("ALL PERFT OK")
    return not fails


def perft_ref(b, d):
    if d == 0:
        return 1
    if d == 1:
        return b.legal_moves.count()
    n = 0
    for m in b.legal_moves:
        b.push(m)
        n += perft_ref(b, d - 1)
        b.pop()
    return n


def perft_diff(fen, depth):
    hdr("PERFT DIFF vs python-chess")
    try:
        import chess
    except ImportError:
        print("python-chess missing. Install with: pip install chess")
        print("Fallback: divide output from your own engine:")
        new_game(fen).divide_perft(depth)
        return
    g = new_game(fen)
    b = chess.Board(fen)
    path = []
    while depth > 0:
        mine = {}
        for m in g.legal_moves():
            ms = move_str(m)
            g.make_move(m)
            mine[ms] = g.perft(depth - 1)
            g.undo_move()
        ref = {}
        for m in list(b.legal_moves):
            b.push(m)
            ref[m.uci()] = perft_ref(b, depth - 1)
            b.pop()
        print("after moves [%s] depth %d: yours=%d ref=%d" %
              (" ".join(path), depth, sum(mine.values()), sum(ref.values())))
        missing = [m for m in ref if m not in mine]
        extra = [m for m in mine if m not in ref]
        if missing or extra:
            print("  MISSING moves (you don't generate):", missing)
            print("  ILLEGAL moves (you generate):", extra)
            print("  fen path:", path)
            return
        bad = [m for m in ref if mine[m] != ref[m]]
        if not bad:
            print("  no difference found")
            return
        mv = bad[0]
        print("  count differs on %s: yours=%d ref=%d" % (mv, mine[mv], ref[mv]))
        g.make_move(find_move(g, mv))
        b.push(chess.Move.from_uci(mv))
        path.append(mv)
        depth -= 1
    print("Bug is in the last move above (look at that move type: capture/ep/castle/promo/check)")


# ----------------------------------------------------------------- integrity
def check_state(g):
    errs = []
    if compute_hash is not None and hasattr(g, "hash"):
        if g.hash != compute_hash(g):
            errs.append("hash != compute_hash")
    wk = bk = None
    for r in range(8):
        for c in range(8):
            if g.board[r][c] == "wK":
                wk = (r, c)
            elif g.board[r][c] == "bK":
                bk = (r, c)
    if wk != g.white_king_square:
        errs.append("white king cache %s but board %s" % (g.white_king_square, wk))
    if bk != g.black_king_square:
        errs.append("black king cache %s but board %s" % (g.black_king_square, bk))
    if hasattr(g, "state_history") and hasattr(g, "hash"):
        if g.state_history[-1] != g.hash:
            errs.append("state_history[-1] != hash")
    # optional: incremental eval. Name your field eval_score and it gets checked.
    if hasattr(g, "eval_score") and evaluate is not None:
        if g.eval_score != evaluate(g):
            errs.append("eval_score %s != full eval %s" % (g.eval_score, evaluate(g)))
    return errs


def walk(g, depth, path, problems):
    if depth == 0 or len(problems) >= 5:
        return
    for m in g.legal_moves():
        if len(problems) >= 5:
            return
        before = snapshot(g)
        ms = move_str(m)
        g.make_move(m)
        path.append(ms)
        errs = check_state(g)
        if errs:
            problems.append((" ".join(path), errs))
        walk(g, depth - 1, path, problems)
        g.undo_move()
        path.pop()
        after = snapshot(g)
        diff = [k for k in before if before[k] != after[k]]
        if diff:
            problems.append((" ".join(path + [ms]) + " (after undo)", ["not restored: " + ",".join(diff)]))


def run_integrity(depth=3):
    hdr("INTEGRITY (make/undo/hash/king cache) depth %d" % depth)
    bad = 0
    for name, fen in SEARCH_POS[:7]:
        g = new_game(fen)
        problems = []
        t = time.perf_counter()
        walk(g, depth, [], problems)
        el = time.perf_counter() - t
        if problems:
            bad += 1
            print("%-9s FAIL (%.1fs)" % (name, el))
            for p, e in problems[:3]:
                print("   ", p)
                for x in e:
                    print("      -", x)
        else:
            print("%-9s ok (%.1fs)" % (name, el))
    # clone check
    g = new_game(KIWI)
    c = g.clone()
    if snapshot(g) != snapshot(c):
        print("clone: FAIL (clone differs from original)")
        bad += 1
    else:
        m = c.legal_moves()[0]
        c.make_move(m)
        g2 = new_game(KIWI)
        if snapshot(g) != snapshot(g2):
            print("clone: FAIL (moving the clone changed the original)")
            bad += 1
        else:
            print("clone: ok")
    print("INTEGRITY OK" if not bad else "INTEGRITY PROBLEMS: %d" % bad)
    return not bad


# ----------------------------------------------------------------- rules
def run_rules():
    hdr("RULES / GAME STATUS")
    bad = 0
    for name, fen, want in RULES:
        try:
            got = new_game(fen).game_status()
        except Exception:
            got = "CRASH"
            traceback.print_exc()
        ok = got == want
        bad += 0 if ok else 1
        print("%-20s %s  (got %s%s)" % (name, "ok" if ok else "FAIL", got, "" if ok else ", want " + want))
    # threefold repetition
    g = new_game(START_FEN)
    seq = ["g1f3", "g8f6", "f3g1", "f6g8"] * 2
    status_mid = None
    for i, u in enumerate(seq):
        m = find_move(g, u)
        if m is None:
            print("repetition: FAIL (couldn't play %s)" % u)
            bad += 1
            break
        g.make_move(m)
        if i == 3:
            status_mid = g.game_status()
    else:
        final = g.game_status()
        ok = status_mid != "draw_by_repition" and final == "draw_by_repition"
        bad += 0 if ok else 1
        print("%-20s %s  (after 2nd rep: %s, after 3rd: %s)" %
              ("threefold repetition", "ok" if ok else "FAIL", status_mid, final))
    print("RULES OK" if not bad else "RULES FAILURES: %d" % bad)
    return not bad


# ----------------------------------------------------------------- tactics
def run_tactics(depth=3):
    hdr("TACTICS (depth %d)" % depth)
    if Engine is None:
        print("no Engine")
        return False
    bad = 0
    for name, fen, good in TACTICS:
        g = new_game(fen)
        snap = snapshot(g)
        e = Engine(depth=depth)
        t = time.perf_counter()
        mv = e.get_best_move(g, depth)
        el = time.perf_counter() - t
        ms = move_str(mv) if mv else None
        ok = ms in good
        bad += 0 if ok else 1
        extra = "" if snapshot(g) == snap else "  BOARD CHANGED BY SEARCH!"
        print("%-20s %s  played %s want %s  %d nodes %.2fs%s" %
              (name, "ok" if ok else "FAIL", ms, "/".join(good), e.nodes_searched, el, extra))
    print("TACTICS OK" if not bad else "TACTICS FAILURES: %d" % bad)
    return not bad


# ----------------------------------------------------------------- search bench
def run_search(depth=4, label=None, save=True):
    hdr("SEARCH BENCH depth %d" % depth)
    if Engine is None:
        print("no Engine")
        return
    rows = []
    for name, fen in SEARCH_POS:
        random.seed(1)
        g = new_game(fen)
        snap = snapshot(g)
        e = Engine(depth=depth)
        t = time.perf_counter()
        mv = e.get_best_move(g, depth)
        el = time.perf_counter() - t
        warn = "" if snapshot(g) == snap else " BOARD CORRUPTED"
        ms = move_str(mv) if mv else None
        rows.append({"name": name, "nodes": e.nodes_searched, "time": el, "move": ms})
        print("%-9s %9d nodes %6.2fs %9s %s%s" %
              (name, e.nodes_searched, el, fmt_rate(e.nodes_searched, el).replace("/s", ""), ms, warn))
    tn = sum(r["nodes"] for r in rows)
    tt = sum(r["time"] for r in rows)
    print("\nTOTAL %d nodes %.1fs %s" % (tn, tt, fmt_rate(tn, tt)))
    print("(node total is your fingerprint: same code + same depth = same number)")
    if save:
        os.makedirs(RESULTS_DIR, exist_ok=True)
        label = label or time.strftime("%m%d_%H%M")
        path = os.path.join(RESULTS_DIR, label + ".json")
        with open(path, "w") as f:
            json.dump({"label": label, "depth": depth, "rows": rows,
                       "nodes": tn, "time": tt}, f, indent=1)
        print("saved ->", path)


def load_result(x):
    p = x if os.path.exists(x) else os.path.join(RESULTS_DIR, x + ".json")
    with open(p) as f:
        return json.load(f)


def run_compare(a, b):
    hdr("COMPARE %s vs %s" % (a, b))
    A, B = load_result(a), load_result(b)
    if A["depth"] != B["depth"]:
        print("warning: depths differ (%d vs %d)" % (A["depth"], B["depth"]))
    bm = {r["name"]: r for r in B["rows"]}
    print("%-9s %9s %9s %6s %6s" % ("pos", "nodes A", "nodes B", "time x", "move"))
    for r in A["rows"]:
        o = bm.get(r["name"])
        if not o:
            continue
        tx = (o["time"] / r["time"]) if r["time"] > 0 else 0
        mv = "same" if r["move"] == o["move"] else "%s>%s" % (r["move"], o["move"])
        print("%-9s %9d %9d %6.2f %s" % (r["name"], r["nodes"], o["nodes"], tx, mv))
    print("\nnodes: %d -> %d (%.2fx)" % (A["nodes"], B["nodes"], B["nodes"] / max(1, A["nodes"])))
    print("time : %.1fs -> %.1fs (%.2fx)" % (A["time"], B["time"], B["time"] / max(1e-9, A["time"])))
    print("nps  : %d -> %d" % (A["nodes"] / A["time"], B["nodes"] / B["time"]))
    print("(fewer nodes = better pruning; lower time = faster overall)")


# ----------------------------------------------------------------- speed / profile
def timeit(fn, min_time=0.4):
    n = 1
    while True:
        t = time.perf_counter()
        for _ in range(n):
            fn()
        el = time.perf_counter() - t
        if el >= min_time:
            return el / n
        n *= 4


def run_speed():
    hdr("MICRO-BENCHMARKS (kiwipete)")
    g = new_game(KIWI)
    first = g.legal_moves()[0]
    tests = []
    tests.append(("legal_moves", lambda: g.legal_moves()))
    if hasattr(g, "pseudo_move_generator"):
        tests.append(("pseudo_move_generator", lambda: g.pseudo_move_generator()))

    def mk_undo():
        g.make_move(first)
        g.undo_move()
    tests.append(("make+undo", mk_undo))
    tests.append(("square_attacked", lambda: g.square_attacked(7, 4, "BLACK")))
    tests.append(("is_in_check", lambda: g.is_in_check("WHITE")))
    tests.append(("clone", lambda: g.clone()))
    tests.append(("game_status", lambda: g.game_status()))
    if evaluate_relative is not None:
        tests.append(("evaluate_relative", lambda: evaluate_relative(g)))
    if compute_hash is not None:
        tests.append(("compute_hash", lambda: compute_hash(g)))
    for name, fn in tests:
        try:
            per = timeit(fn)
            print("%-22s %9.1f us  %10s calls/s" % (name, per * 1e6, format(int(1 / per), ",")))
        except Exception as e:
            print("%-22s CRASH %s" % (name, e))
    print("\nFor a search node think: ~1 legal_moves + moves x (make+undo) + 1 evaluate.")


def run_profile(depth=3, fen=None, sort="tottime", lines=20):
    hdr("PROFILE depth %d" % depth)
    if Engine is None:
        print("no Engine")
        return
    g = new_game(fen or KIWI)
    e = Engine(depth=depth)
    pr = cProfile.Profile()
    pr.enable()
    e.get_best_move(g, depth)
    pr.disable()
    s = io.StringIO()
    st = pstats.Stats(pr, stream=s)
    st.strip_dirs().sort_stats(sort).print_stats(lines)
    print("nodes:", e.nodes_searched)
    print(s.getvalue())


# ----------------------------------------------------------------- driver
def run_quick():
    run_perft(3, 20)
    run_integrity(2)
    run_rules()
    run_tactics(3)
    run_search(3, label="quick", save=False)
    run_speed()


def menu(args):
    items = [
        ("perft suite", lambda: run_perft(ask("max depth", 4))),
        ("perft diff vs python-chess", lambda: perft_diff(input("fen: ").strip() or KIWI, ask("depth", 3))),
        ("integrity (make/undo/hash)", lambda: run_integrity(ask("depth", 3))),
        ("rules / draws", run_rules),
        ("tactics", lambda: run_tactics(ask("depth", 3))),
        ("search bench (saves)", lambda: run_search(ask("depth", 4), input("label (enter=auto): ").strip() or None)),
        ("micro-benchmarks", run_speed),
        ("profile a search", lambda: run_profile(ask("depth", 3))),
        ("compare two saved benches", lambda: run_compare(input("A: ").strip(), input("B: ").strip())),
        ("quick: everything small", run_quick),
    ]
    while True:
        print("\n--- GAMBIT BENCH ---")
        for i, (n, _) in enumerate(items, 1):
            print("%d) %s" % (i, n))
        print("q) quit")
        ch = input("> ").strip().lower()
        if ch == "q":
            return
        if ch.isdigit() and 1 <= int(ch) <= len(items):
            try:
                items[int(ch) - 1][1]()
            except Exception:
                traceback.print_exc()


def ask(prompt, default):
    v = input("%s [%s]: " % (prompt, default)).strip()
    return int(v) if v else default


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?")
    ap.add_argument("--depth", type=int)
    ap.add_argument("--dir")
    ap.add_argument("--label")
    ap.add_argument("--other")
    ap.add_argument("--fen")
    args = ap.parse_args()
    if args.cmd != "compare":
        load_engine(args.dir)
    d = args.depth
    c = args.cmd
    if c is None:
        menu(args)
    elif c == "perft":
        run_perft(d or 4)
    elif c == "diff":
        perft_diff(args.fen or KIWI, d or 3)
    elif c == "integrity":
        run_integrity(d or 3)
    elif c == "rules":
        run_rules()
    elif c == "tactics":
        run_tactics(d or 3)
    elif c == "search":
        run_search(d or 4, args.label)
    elif c == "speed":
        run_speed()
    elif c == "profile":
        run_profile(d or 3, args.fen)
    elif c == "compare":
        run_compare(args.label, args.other)
    elif c == "quick":
        run_quick()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
