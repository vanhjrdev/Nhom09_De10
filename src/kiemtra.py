import sys
from scp_core import SCPInstance


def main():
    if len(sys.argv) < 3:
        print("Cu phap: python kiemtra.py <tep_vao> <tep_loi_giai>")
        sys.exit(1)

    inst = SCPInstance()
    if not inst.load_from_file(sys.argv[1]):
        print("KHONG HOP LE (Khong mo duoc tep vao)")
        sys.exit(1)

    try:
        with open(sys.argv[2], 'r', encoding='utf-8') as f:
            tokens = f.read().split()
    except OSError:
        print("KHONG HOP LE (Khong mo duoc tep loi giai)")
        sys.exit(0)

    if not tokens:
        print("KHONG HOP LE (Tep loi giai rong)")
        sys.exit(0)

    try:
        reported_cost = int(tokens[0])
        selected = [int(x) for x in tokens[1:]]
    except ValueError:
        print("KHONG HOP LE (Sai dinh dang so)")
        sys.exit(0)

    used = set()
    covered = set()
    actual_cost = 0

    for c in selected:
        if c < 1 or c > inst.n:
            print(f"KHONG HOP LE (Chi so cot nam ngoai pham vi: {c})")
            sys.exit(0)
        if c in used:
            print(f"KHONG HOP LE (Cot bi chon lap lai: {c})")
            sys.exit(0)
        used.add(c)
        actual_cost += inst.cost[c]
        covered.update(inst.col_rows[c])

    uncovered = [i for i in range(1, inst.m + 1) if i not in covered]
    if uncovered:
        print(f"KHONG HOP LE (Cac hang chua duoc phu: {' '.join(map(str, uncovered))}) | Chi phi tinh duoc: {actual_cost}")
        sys.exit(0)

    if actual_cost != reported_cost:
        print(f"KHONG HOP LE (Sai lech chi phi: bao cao={reported_cost}, thuc te={actual_cost})")
        sys.exit(0)

    print(f"HOP LE | Tong chi phi: {actual_cost}")


if __name__ == "__main__":
    main()