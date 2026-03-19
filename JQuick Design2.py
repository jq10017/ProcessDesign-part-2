from ttg import Truths

num_vars = int(input("How many variables would you like to use (min 2)? "))
if num_vars < 2:
    print("Please use at least 2 variables")
    raise SystemExit(1)

variables = [chr(65 + i) for i in range(num_vars)]
print(f"\nVariables: {', '.join(variables)}")


ops = []
for i in range(num_vars - 1):
    op = input(f"Please choose an operator to use between {variables[i]} and {variables[i+1]} (AND/OR): ").strip().lower()
    if op not in ["and", "or"]:
        print("You have entered an Invalid operator; defaulting to AND")
        op = "and"
    ops.append(op)


expr_parts = []
for i, var in enumerate(variables):
    expr_parts.append(var)
    if i < len(ops):
        expr_parts.append(ops[i])

expression = " ".join(expr_parts)

table = Truths(variables, [expression])
print("\nTruth table for the expression:")
print(expression)
print(str(table))


df = table.as_pandas
output_col = df.columns[-1]


minterms = []
maxterms = []
for _, row in df.iterrows():
    bits = "".join(str(int(row[var])) for var in variables)
    idx = int(bits, 2)
    if int(row[output_col]) == 1:
        minterms.append(idx)
    else:
        maxterms.append(idx)

print("\nMinterms (output=1):", minterms)
print("Maxterms (output=0):", maxterms)

choice = input("\nConvert to expression (SOP/POS/BOTH) or press Enter to skip? ").strip().lower()

if choice in ("sop", "both"):
    sop_terms = []
    for idx in minterms:
        bits = format(idx, f'0{num_vars}b')
        term = " AND ".join(variables[i] if bit == "1" else f"NOT {variables[i]}" for i, bit in enumerate(bits))
        sop_terms.append(f"({term})")
    print("\nSum of Products (SOP):")
    print(" OR ".join(sop_terms) if sop_terms else "0")

if choice in ("pos", "both"):
    pos_terms = []
    for idx in maxterms:
        bits = format(idx, f'0{num_vars}b')
        term = " OR ".join(variables[i] if bit == "0" else f"NOT {variables[i]}" for i, bit in enumerate(bits))
        pos_terms.append(f"({term})")
    print("\nProduct of Sums (POS):")
    print(" AND ".join(pos_terms) if pos_terms else "1")

if 2 <= num_vars <= 4 and choice in ("sop", "pos", "both"):
    def combine_terms(a: str, b: str):
        diff = 0
        out = []
        for x, y in zip(a, b):
            if x == y:
                out.append(x)
            else:
                diff += 1
                out.append("-")
            if diff > 1:
                return None
        return "".join(out)

    def find_prime_implicants(terms):
        groups = {}
        for m in sorted(set(terms)):
            b = format(m, f'0{num_vars}b')
            groups.setdefault(b.count("1"), set()).add(b)

        prime_implicants = set()
        while groups:
            next_groups = {}
            used = set()
            for ones_count in sorted(groups.keys()):
                for t1 in groups[ones_count]:
                    for t2 in groups.get(ones_count + 1, []):
                        combined = combine_terms(t1, t2)
                        if combined:
                            used.add(t1)
                            used.add(t2)
                            next_groups.setdefault(combined.count("1"), set()).add(combined)
            for ones_count, terms_set in groups.items():
                for t in terms_set:
                    if t not in used:
                        prime_implicants.add(t)
            groups = next_groups
        return sorted(prime_implicants)

    def term_covers(term_bin, implicant):
        return all(i == "-" or i == m for i, m in zip(implicant, term_bin))

    def find_essential(prime_implicants, terms):
        term_bins = [format(m, f'0{num_vars}b') for m in terms]
        coverage = {pi: [] for pi in prime_implicants}
        for m in term_bins:
            for pi in prime_implicants:
                if term_covers(m, pi):
                    coverage[pi].append(m)
        essentials = []
        uncovered = set(term_bins)
        while uncovered:
            best = max(coverage.items(), key=lambda kv: len(set(kv[1]) & uncovered))[0]
            essentials.append(best)
            uncovered -= set(coverage[best])
            if not uncovered:
                break
            coverage.pop(best, None)
        return sorted(set(essentials))

    if choice in ("sop", "both"):
        prime_implicants = find_prime_implicants(minterms)
        essential_implicants = find_essential(prime_implicants, minterms)
        
        def implicant_to_sop(implicant):
            parts = []
            for i, bit in enumerate(implicant):
                if bit == "-":
                    continue
                parts.append(variables[i] if bit == "1" else f"NOT {variables[i]}")
            return "(" + " AND ".join(parts) + ")" if parts else "1"
        
        simplified = " OR ".join(implicant_to_sop(pi) for pi in essential_implicants)
        print("\nK-map simplified (SOP) expression:", simplified if simplified else "0")

    if choice in ("pos", "both"):
        prime_implicants = find_prime_implicants(maxterms)
        essential_implicants = find_essential(prime_implicants, maxterms)
        
        def implicant_to_pos(implicant):
            parts = []
            for i, bit in enumerate(implicant):
                if bit == "-":
                    continue
                parts.append(variables[i] if bit == "0" else f"NOT {variables[i]}")
            return "(" + " OR ".join(parts) + ")" if parts else "0"
        
        simplified = " AND ".join(implicant_to_pos(pi) for pi in essential_implicants)
        print("\nK-map simplified (POS) expression:", simplified if simplified else "1")

if choice not in ("sop", "pos", "both", ""):
    print("\nNo conversion selected.")


try:
    to_validate = kmap_expression
except NameError:
    to_validate = expression

py_expr = (
    to_validate.replace("AND", "and")
    .replace("OR", "or")
    .replace("NOT", "not")
)

def _eval(expr, row):
    env = {var: bool(int(row[var])) for var in variables}
    return bool(eval(expr, {}, env))

valid = True
for _, row in df.iterrows():
    expected = bool(int(row[output_col]))
    if _eval(py_expr, row) != expected:
        valid = False
        break

print(f"\nValidation for the expression: {'Pass' if valid else 'Fail'}")