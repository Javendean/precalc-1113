# -*- coding: utf-8 -*-
"""The knowledge-component (KC) graph for GSU MATH 1113 Precalculus.

Two tiers, and the split is the whole point of this app.

TIER 0 -- the algebra substrate. Exponent laws, factoring, fraction arithmetic,
signs, radicals, equation solving. None of this is "precalculus," and none of it
is what a struggling precalc student names as the problem. It is nonetheless
where most of them are actually broken. A student who cannot simplify x^-3 / x^5
will fail every logarithm problem, and will report the problem as "logs."

TIER 1 -- precalculus proper, aligned to OpenStax Precalculus 2e, the text GSU
MATH 1113 uses.

`prereqs` are real dependency edges, not curricular order. They drive the
diagnostic descent: when a Tier-1 anchor fails, the engine walks DOWN the prereq
edges to find the deepest KC that is actually broken, so the report names a root
cause instead of a symptom. That is the difference between telling a tutor "she
is weak on logarithms" and telling him "she is weak on negative exponents, which
is why logarithms look broken."

`anchor: True` marks a diagnostic entry point -- a KC the course currently leans
on. The diagnostic starts at anchors and descends only on failure, which keeps a
whole-course diagnostic near 25 questions instead of 200.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Knowledge components
# ---------------------------------------------------------------------------
# tier 0 = algebra substrate (the silent killers), tier 1 = precalculus core
KCS = [
    # ---------------- TIER 0: arithmetic & sign sense ----------------
    dict(id="frac_arith", name="Fraction arithmetic", tier=0, chapter="prereq",
         prereqs=[], anchor=False,
         blurb="Add, subtract, multiply and divide numeric fractions; find a common denominator."),
    dict(id="signed_numbers", name="Signed numbers & distributing a negative", tier=0,
         chapter="prereq", prereqs=[], anchor=False,
         blurb="Handle subtraction of a quantity: -(a - b) = -a + b."),
    dict(id="order_ops", name="Order of operations & implicit grouping", tier=0, chapter="prereq",
         prereqs=[], anchor=False,
         blurb="Read -3^2 and (-3)^2 differently; treat a fraction bar as grouping."),

    # ---------------- TIER 0: exponents & radicals ----------------
    dict(id="exp_laws", name="Integer exponent laws", tier=0, chapter="prereq",
         prereqs=["order_ops"], anchor=False,
         blurb="Product, quotient and power rules for like bases."),
    dict(id="exp_negative", name="Negative & zero exponents", tier=0, chapter="prereq",
         prereqs=["exp_laws", "frac_arith"], anchor=False,
         blurb="x^-n is a reciprocal, not a sign change; x^0 = 1."),
    dict(id="exp_rational", name="Rational exponents & radical form", tier=0, chapter="prereq",
         prereqs=["exp_negative"], anchor=False,
         blurb="a^(m/n) is the n-th root of a^m; convert in both directions."),
    dict(id="radicals", name="Radical simplification & rationalizing", tier=0, chapter="prereq",
         prereqs=["exp_rational"], anchor=False,
         blurb="Simplify roots, rationalize denominators, and know sqrt(a^2+b^2) is not a+b."),

    # ---------------- TIER 0: polynomial & rational algebra ----------------
    dict(id="distribute", name="Distributing & expanding binomials", tier=0, chapter="prereq",
         prereqs=["signed_numbers"], anchor=False,
         blurb="(a+b)^2 = a^2 + 2ab + b^2 -- the middle term is not optional."),
    dict(id="factor_gcf", name="Factoring: greatest common factor", tier=0, chapter="prereq",
         prereqs=["distribute"], anchor=False,
         blurb="Pull out the common factor first, always."),
    dict(id="factor_trinomial", name="Factoring trinomials", tier=0, chapter="prereq",
         prereqs=["factor_gcf"], anchor=False,
         blurb="Factor ax^2+bx+c, including the case a is not 1."),
    dict(id="factor_special", name="Special factoring forms", tier=0, chapter="prereq",
         prereqs=["factor_gcf"], anchor=False,
         blurb="Difference of squares, sum/difference of cubes, perfect-square trinomials."),
    dict(id="rational_expr", name="Rational expressions & illegal cancellation", tier=0,
         chapter="prereq", prereqs=["factor_trinomial", "frac_arith"], anchor=False,
         blurb="Cancel factors, never addends: (x+3)/3 does not reduce to x."),
    dict(id="complex_frac", name="Complex fractions", tier=0, chapter="prereq",
         prereqs=["rational_expr"], anchor=False,
         blurb="Simplify a fraction whose parts are themselves fractions."),

    # ---------------- TIER 0: equations & inequalities ----------------
    dict(id="linear_eq", name="Solving linear equations", tier=0, chapter="prereq",
         prereqs=["distribute"], anchor=False,
         blurb="Isolate the variable; clear denominators safely."),
    dict(id="quadratic_eq", name="Solving quadratics: factoring, formula, square roots", tier=0,
         chapter="prereq", prereqs=["factor_trinomial", "radicals"], anchor=True,
         blurb="Zero-product property, the quadratic formula, and plus/minus on square roots."),
    dict(id="rational_eq", name="Rational equations & extraneous solutions", tier=0,
         chapter="prereq", prereqs=["rational_expr", "linear_eq"], anchor=False,
         blurb="Clear denominators, then check every root against the original domain."),
    dict(id="radical_eq", name="Radical equations & extraneous solutions", tier=0, chapter="prereq",
         prereqs=["radicals", "quadratic_eq"], anchor=False,
         blurb="Squaring both sides can invent solutions; checking is part of the method."),
    dict(id="inequalities", name="Inequalities, interval notation & sign analysis", tier=0,
         chapter="prereq", prereqs=["linear_eq", "factor_trinomial"], anchor=True,
         blurb="Flip when multiplying or dividing by a negative; solve nonlinear ones by sign chart."),
    dict(id="absolute_value", name="Absolute value equations & inequalities", tier=0,
         chapter="prereq", prereqs=["inequalities"], anchor=False,
         blurb="Split into two cases; |x|<a is an AND, |x|>a is an OR."),

    # ---------------- TIER 1 / Ch.1-2: functions ----------------
    dict(id="fn_notation", name="Function notation & evaluation", tier=1, chapter="1",
         prereqs=["distribute", "order_ops"], anchor=True,
         blurb="f(x) is a name with an input, not multiplication; evaluate f(x+h) correctly."),
    dict(id="fn_domain_range", name="Domain & range from formulas and graphs", tier=1, chapter="1",
         prereqs=["radicals", "rational_expr", "inequalities"], anchor=True,
         blurb="Exclude zero denominators and negative even radicands; write in interval notation."),
    dict(id="fn_graph_reading", name="Reading graphs: intercepts, increase, extrema", tier=1,
         chapter="1", prereqs=["fn_notation"], anchor=False,
         blurb="Extract behavior and key features from a picture."),
    dict(id="fn_vertical_line", name="Function vs relation; one-to-one", tier=1, chapter="1",
         prereqs=["fn_graph_reading"], anchor=False,
         blurb="Vertical-line test for function, horizontal-line test for invertibility."),
    dict(id="fn_composition", name="Composition of functions", tier=1, chapter="1",
         prereqs=["fn_notation"], anchor=True,
         blurb="The composite f of g means f(g(x)); order matters and the domain can shrink."),
    dict(id="fn_inverse", name="Inverse functions", tier=1, chapter="1",
         prereqs=["fn_composition", "fn_vertical_line", "linear_eq"], anchor=True,
         blurb="The inverse undoes f; it is not the reciprocal. Swap x and y, then solve."),
    dict(id="fn_transformations", name="Transformations of graphs", tier=1, chapter="1",
         prereqs=["fn_notation"], anchor=True,
         blurb="Inside affects x and runs backwards; outside affects y and runs forwards."),
    dict(id="fn_piecewise", name="Piecewise-defined functions", tier=1, chapter="1",
         prereqs=["fn_notation", "inequalities"], anchor=False,
         blurb="Pick the branch whose condition the input satisfies."),
    dict(id="fn_even_odd", name="Even & odd symmetry", tier=1, chapter="1",
         prereqs=["fn_notation", "signed_numbers"], anchor=False,
         blurb="Even means f(-x)=f(x). Odd means f(-x)=-f(x)."),
    dict(id="fn_avg_rate", name="Average rate of change & difference quotient", tier=1, chapter="1",
         prereqs=["fn_notation", "rational_expr"], anchor=False,
         blurb="Slope between two points; the difference quotient is the calculus on-ramp."),
    dict(id="linear_models", name="Linear functions, slope & modeling", tier=1, chapter="2",
         prereqs=["linear_eq", "fn_notation"], anchor=False,
         blurb="Slope as a rate; build and interpret a linear model."),

    # ---------------- TIER 1 / Ch.3: polynomial & rational ----------------
    dict(id="quadratic_forms", name="Quadratic functions: vertex form & completing the square",
         tier=1, chapter="3", prereqs=["quadratic_eq", "factor_special"], anchor=True,
         blurb="Convert to a(x-h)^2+k; read off the vertex and the max or min."),
    dict(id="poly_end_behavior", name="Polynomial end behavior & degree", tier=1, chapter="3",
         prereqs=["exp_laws", "fn_graph_reading"], anchor=False,
         blurb="The leading term alone decides both tails."),
    dict(id="poly_zeros", name="Zeros, multiplicity & graph shape", tier=1, chapter="3",
         prereqs=["factor_trinomial", "poly_end_behavior"], anchor=True,
         blurb="Odd multiplicity crosses; even multiplicity touches and turns."),
    dict(id="poly_division", name="Polynomial & synthetic division; remainder theorem", tier=1,
         chapter="3", prereqs=["poly_zeros"], anchor=False,
         blurb="Divide, and use the fact that f(c) equals the remainder to test roots."),
    dict(id="rational_asymptotes", name="Rational functions: asymptotes & holes", tier=1,
         chapter="3", prereqs=["rational_expr", "poly_end_behavior"], anchor=True,
         blurb="Holes come from cancelled factors; end behavior comes from comparing degrees."),

    # ---------------- TIER 1 / Ch.4: exponential & logarithmic ----------------
    dict(id="exp_functions", name="Exponential functions & growth/decay", tier=1, chapter="4",
         prereqs=["exp_negative", "fn_transformations"], anchor=True,
         blurb="Recognize growth versus decay and the horizontal asymptote."),
    dict(id="log_definition", name="Logarithm as an inverse; converting forms", tier=1, chapter="4",
         prereqs=["exp_functions", "fn_inverse"], anchor=True,
         blurb="A log is an exponent. Every log question is an exponent question."),
    dict(id="log_properties", name="Logarithm properties: product, quotient, power", tier=1,
         chapter="4", prereqs=["log_definition", "exp_laws"], anchor=True,
         blurb="The log of a product is a sum. There is no rule for the log of a sum."),
    dict(id="log_solve", name="Solving exponential & logarithmic equations", tier=1, chapter="4",
         prereqs=["log_properties", "rational_eq"], anchor=True,
         blurb="Take a log, or exponentiate; then check the domain of every answer."),
    dict(id="exp_log_models", name="Exponential & logarithmic models", tier=1, chapter="4",
         prereqs=["log_solve"], anchor=False,
         blurb="Half-life, compound interest, continuous growth with e."),

    # ---------------- TIER 1 / Ch.5-6: trigonometric functions ----------------
    dict(id="angles_radians", name="Angles, radian measure & arc length", tier=1, chapter="5",
         prereqs=["frac_arith"], anchor=True,
         blurb="Convert degrees and radians fluently; arc length is r times theta."),
    dict(id="right_triangle_trig", name="Right-triangle trigonometry", tier=1, chapter="5",
         prereqs=["radicals", "angles_radians"], anchor=True,
         blurb="Define the six ratios and solve for a missing side or angle."),
    dict(id="unit_circle", name="Unit circle & exact values", tier=1, chapter="5",
         prereqs=["right_triangle_trig", "radicals"], anchor=True,
         blurb="The coordinates are cosine and sine; know the special angles and quadrant signs."),
    dict(id="trig_reference_angles", name="Reference angles & quadrant signs", tier=1, chapter="5",
         prereqs=["unit_circle"], anchor=False,
         blurb="Reduce any angle to an acute reference, then fix the sign by quadrant."),
    dict(id="trig_graphs", name="Graphs of sine & cosine: amplitude, period, shifts", tier=1,
         chapter="6", prereqs=["unit_circle", "fn_transformations"], anchor=True,
         blurb="For a sin(b(x-c))+d the period is 2 pi over b and the amplitude is the size of a."),
    dict(id="trig_other_graphs", name="Graphs of tangent, cotangent, secant, cosecant", tier=1,
         chapter="6", prereqs=["trig_graphs", "rational_asymptotes"], anchor=False,
         blurb="Asymptotes appear where the defining ratio has a zero denominator."),
    dict(id="inverse_trig", name="Inverse trigonometric functions", tier=1, chapter="6",
         prereqs=["trig_graphs", "fn_inverse"], anchor=True,
         blurb="Arcsine is not the reciprocal of sine; the restricted range is the whole idea."),

    # ---------------- TIER 1 / Ch.7: identities & equations ----------------
    dict(id="trig_identities_basic", name="Pythagorean & reciprocal identities", tier=1,
         chapter="7", prereqs=["unit_circle"], anchor=True,
         blurb="Sine squared plus cosine squared is one, plus its two derived forms."),
    dict(id="trig_sum_diff", name="Sum, difference & double-angle formulas", tier=1, chapter="7",
         prereqs=["trig_identities_basic"], anchor=False,
         blurb="Sine does not distribute over a sum; the formula exists because of that."),
    dict(id="trig_simplify", name="Simplifying & verifying identities", tier=1, chapter="7",
         prereqs=["trig_identities_basic", "rational_expr"], anchor=False,
         blurb="Work one side into the other using identities and algebra."),
    dict(id="trig_equations", name="Solving trigonometric equations", tier=1, chapter="7",
         prereqs=["trig_identities_basic", "quadratic_eq", "trig_reference_angles"], anchor=True,
         blurb="Find every solution in the stated interval, not only the calculator's one."),

    # ---------------- TIER 1 / Ch.8: applications ----------------
    dict(id="law_sines_cosines", name="Law of sines & law of cosines", tier=1, chapter="8",
         prereqs=["right_triangle_trig", "quadratic_eq"], anchor=True,
         blurb="Match the law to the given parts; watch the ambiguous side-side-angle case."),
    dict(id="vectors", name="Vectors: components, magnitude, operations", tier=1, chapter="8",
         prereqs=["right_triangle_trig", "radicals"], anchor=False,
         blurb="Decompose into components; add componentwise."),
    dict(id="polar", name="Polar coordinates & conversion", tier=1, chapter="8",
         prereqs=["unit_circle", "right_triangle_trig"], anchor=False,
         blurb="Convert between rectangular and polar in both directions."),

    # ---------------- TIER 1 / Ch.9-11: systems, conics, sequences ----------------
    dict(id="systems_linear", name="Systems of linear equations", tier=1, chapter="9",
         prereqs=["linear_eq"], anchor=False,
         blurb="Substitution and elimination; recognize the no-solution and infinite cases."),
    dict(id="systems_nonlinear", name="Nonlinear systems", tier=1, chapter="9",
         prereqs=["systems_linear", "quadratic_eq"], anchor=False,
         blurb="A line and a conic can meet zero, one or two times."),
    dict(id="conics", name="Conic sections: circles, parabolas, ellipses, hyperbolas", tier=1,
         chapter="10", prereqs=["quadratic_forms"], anchor=False,
         blurb="Identify the shape from the equation; complete the square to reach standard form."),
    dict(id="sequences_series", name="Sequences & series: arithmetic and geometric", tier=1,
         chapter="11", prereqs=["exp_functions", "linear_models"], anchor=False,
         blurb="A common difference is linear; a common ratio is exponential."),
]

KC_BY_ID = {k["id"]: k for k in KCS}
ANCHORS = [k["id"] for k in KCS if k["anchor"]]


def prereq_closure(kc_id):
    """Every KC that `kc_id` transitively depends on, deepest-first.

    The diagnostic walks this list when an anchor fails, which is how a wrong
    answer about logarithms turns into a finding about negative exponents.
    """
    seen, order = set(), []

    def visit(node):
        for p in KC_BY_ID[node]["prereqs"]:
            if p not in seen:
                seen.add(p)
                visit(p)
                order.append(p)

    visit(kc_id)
    return order


def validate():
    """Fail the build on a malformed graph rather than shipping a broken descent."""
    ids = set(KC_BY_ID)
    assert len(ids) == len(KCS), "duplicate KC id"
    for k in KCS:
        for p in k["prereqs"]:
            assert p in ids, "%s references unknown prereq %s" % (k["id"], p)
        assert k["tier"] in (0, 1), "%s has a bad tier" % k["id"]
        assert k["blurb"], "%s is missing its blurb" % k["id"]
    # A cycle would make prereq_closure recurse forever; catch it at build time.
    colour = {}

    def dfs(n):
        colour[n] = 1
        for p in KC_BY_ID[n]["prereqs"]:
            if colour.get(p) == 1:
                raise AssertionError("prereq cycle through %s" % p)
            if colour.get(p, 0) == 0:
                dfs(p)
        colour[n] = 2

    for k in KCS:
        if colour.get(k["id"], 0) == 0:
            dfs(k["id"])
    assert ANCHORS, "no diagnostic anchors defined"


if __name__ == "__main__":
    validate()
    t0 = sum(1 for k in KCS if k["tier"] == 0)
    print("KCs: %d  (tier0 substrate=%d, tier1 precalc=%d)" % (len(KCS), t0, len(KCS) - t0))
    print("anchors: %d" % len(ANCHORS))
    print("")
    print("deepest descents:")
    for a in ANCHORS:
        c = prereq_closure(a)
        if len(c) >= 4:
            print("  %-22s -> %2d prereqs: %s" % (a, len(c), ", ".join(c[:6])))
