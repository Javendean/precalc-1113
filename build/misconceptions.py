# -*- coding: utf-8 -*-
"""Named misconceptions -- the registry that turns a wrong answer into a diagnosis.

Every distractor in the item bank carries a misconception id. A wrong answer is
therefore not "she got it wrong"; it is "she applied THIS specific rule, and here
is the rule she over-generalized to get there."

The `family` layer is the part that actually changes a tutoring session. Most
students do not have twelve unrelated problems. They have two or three bad
generalizations that surface in a dozen places. A student who writes
(a+b)^2 = a^2+b^2, log(a+b) = log a + log b, and sin(A+B) = sin A + sin B does
not have an algebra problem, a logarithm problem and a trigonometry problem --
she has ONE belief, that every function distributes over addition, and it is
costing her marks in three chapters. Reporting that as one finding lets a tutor
fix it in one conversation instead of three.

Fields:
  signature -- the illegal move, written the way the student writes it
  root      -- the generalization being over-applied (the WHY)
  fix       -- the intervention that works, phrased for a tutor at a whiteboard
  probe     -- a fast question that exposes the bug in isolation
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Error families -- the tutoring-agenda layer
# ---------------------------------------------------------------------------
FAMILIES = {
    "LINEARITY_ILLUSION": dict(
        name="Everything distributes over addition",
        summary=(
            "Treats every operation as if f(a+b) = f(a) + f(b). This single belief "
            "produces errors in exponents, radicals, logarithms, trigonometry and "
            "rational expressions, which makes it look like five separate weaknesses."),
        fix=(
            "Attack it once, numerically, and let the arithmetic do the arguing. "
            "(3+4)^2 = 49 but 3^2+4^2 = 25. sqrt(9+16) = 5 but 3+4 = 7. Then name the "
            "rule out loud: only multiplication distributes over addition. Return to "
            "the same counterexample every time it resurfaces in a new chapter so she "
            "sees it is one bug, not a new topic."),
    ),
    "INVERSE_AS_RECIPROCAL": dict(
        name="The -1 exponent always means reciprocal",
        summary=(
            "Reads f inverse, arcsine and similar notation as one over the function. "
            "Blocks inverse functions, logarithms and inverse trig simultaneously."),
        fix=(
            "Separate the two meanings explicitly: on a NUMBER the -1 exponent means "
            "reciprocal, on a FUNCTION NAME it means undo. Verify with composition -- "
            "if it is really the inverse then f(f inverse (x)) returns x, and one over "
            "f will not do that. Make her run that check herself."),
    ),
    "RULE_OVERGENERALIZATION": dict(
        name="Right rule, wrong operation",
        summary=(
            "Knows the exponent and logarithm rules exist but reaches for the wrong one "
            "-- multiplying exponents when adding is called for, and so on. Typically "
            "memorized as symbol patterns without the meaning underneath."),
        fix=(
            "Re-derive from the definition rather than drilling the rule. Expand "
            "x^2 times x^3 as x x times x x x and count. Once she has counted it twice "
            "she stops needing to remember which rule it was."),
    ),
    "SIGN_MANAGEMENT": dict(
        name="Signs get lost under distribution or negation",
        summary=(
            "Drops or mishandles a negative, especially when subtracting a quantity or "
            "squaring a negative. Low-glamour and high-cost: it turns correct method "
            "into a wrong answer, which hides the fact that the method was right."),
        fix=(
            "Have her write the subtraction as adding the opposite, every time, for a "
            "week. Also separate -3^2 from (-3)^2 early. Score her work for METHOD and "
            "for ARITHMETIC separately so she can see the method was right."),
    ),
    "NOTATION_LITERALISM": dict(
        name="Notation read as literal arithmetic",
        summary=(
            "Reads f(x) as f times x, or sine squared theta as sine of theta squared. "
            "The mathematics may be fine; the parsing is not."),
        fix=(
            "Read the notation aloud together in words before any manipulation. "
            "Convention, not logic, so it has to be taught as convention -- but once "
            "named it usually resolves quickly."),
    ),
    "DIRECTION_INVERSION": dict(
        name="Inside-the-function changes run backwards",
        summary=(
            "Expects f(x-2) to move a graph left, or reads the period and phase shift "
            "off the wrong part of a sine formula."),
        fix=(
            "Do not teach the rule; test one point. In f(x-2), what input now gives the "
            "old output at 0? x = 2. So the point that was at 0 is now at 2: right. One "
            "point beats any mnemonic, and it survives into the trig chapter."),
    ),
    "INCOMPLETE_SOLUTION_SET": dict(
        name="Stops at the first solution",
        summary=(
            "Drops the negative square root, reports only the calculator's angle, or "
            "skips the extraneous-solution check. Method correct, answer incomplete -- "
            "which is the most frustrating way to lose marks."),
        fix=(
            "Make the last step of every solve explicit: how many solutions SHOULD "
            "this have, and have I got them all? For trig, sketch the unit circle and "
            "mark every crossing before writing anything down."),
    ),
    "PROCEDURAL_NO_DOMAIN": dict(
        name="Procedure runs without checking whether it is legal",
        summary=(
            "Cancels across a sum, ignores a zero denominator, or accepts the log of a "
            "negative number. The steps are fluent and the constraints are invisible."),
        fix=(
            "Add a standing habit: before solving, write down what x is not allowed to "
            "be; after solving, check every answer against that line. Two extra lines "
            "of work, and it removes a whole category of lost marks."),
    ),
}

# ---------------------------------------------------------------------------
# The registry
# ---------------------------------------------------------------------------
MISCONCEPTIONS = [
    # ---- LINEARITY_ILLUSION ----
    dict(id="LIN_SQUARE_SUM", family="LINEARITY_ILLUSION",
         name="Squares a sum term by term",
         signature="(a+b)^2 -> a^2 + b^2",
         kcs=["distribute", "factor_special", "quadratic_forms"],
         root="Applies the distributive law to an exponent, which it does not govern.",
         fix="Expand it as (a+b)(a+b) once by hand; the middle term appears and cannot be unseen.",
         probe="Expand (x+3)^2."),
    dict(id="LIN_SQRT_SUM", family="LINEARITY_ILLUSION",
         name="Splits a radical over a sum",
         signature="sqrt(a^2+b^2) -> a + b",
         kcs=["radicals", "right_triangle_trig", "vectors"],
         root="Extends the true rule for products to sums.",
         fix="Numbers settle it: sqrt(9+16)=5, not 7. Radicals split over times and divide, never plus.",
         probe="Simplify sqrt(9+16)."),
    dict(id="LIN_LOG_SUM", family="LINEARITY_ILLUSION",
         name="Splits a log over a sum",
         signature="log(a+b) -> log a + log b",
         kcs=["log_properties", "log_solve"],
         root="Runs the product rule backwards onto an addition.",
         fix="The rule turns a PRODUCT into a sum. There is no rule for a sum -- it must be factored first.",
         probe="Can log(x+5) be expanded?"),
    dict(id="LIN_FRAC_SPLIT_DEN", family="LINEARITY_ILLUSION",
         name="Splits a fraction over a denominator sum",
         signature="c/(a+b) -> c/a + c/b",
         kcs=["rational_expr", "complex_frac"],
         root="Mirrors the legal split over a NUMERATOR sum onto the denominator.",
         fix="Test with numbers: 1/(1+1)=0.5 but 1/1+1/1=2. Splitting works on top, never on the bottom.",
         probe="Does 1/(2+3) equal 1/2 + 1/3?"),
    dict(id="LIN_SIN_SUM", family="LINEARITY_ILLUSION",
         name="Distributes sine over a sum",
         signature="sin(A+B) -> sin A + sin B",
         kcs=["trig_sum_diff", "trig_identities_basic"],
         root="Reads sin as a multiplier rather than a function name.",
         fix="Check at A=B=90 degrees: sin(180)=0 but sin90+sin90=2. That is why the sum formula exists.",
         probe="Does sin(90+90) equal sin90 + sin90?"),
    dict(id="LIN_FN_ADD", family="LINEARITY_ILLUSION",
         name="Distributes a function over its input sum",
         signature="f(x+h) -> f(x) + f(h)",
         kcs=["fn_notation", "fn_avg_rate"],
         root="Same belief as above, at the level of a general function.",
         fix="Substitute the whole quantity into every x, with brackets. Do it slowly once.",
         probe="For f(x)=x^2, find f(x+h)."),

    # ---- INVERSE_AS_RECIPROCAL ----
    dict(id="INV_FN_RECIPROCAL", family="INVERSE_AS_RECIPROCAL",
         name="Reads the inverse function as one over the function",
         signature="f^-1(x) -> 1/f(x)",
         kcs=["fn_inverse"],
         root="Carries the numeric meaning of a -1 exponent onto a function name.",
         fix="Verify by composition: the inverse must send f(x) back to x; the reciprocal will not.",
         probe="If f(x)=x+3, what is f inverse of x?"),
    dict(id="INV_TRIG_RECIPROCAL", family="INVERSE_AS_RECIPROCAL",
         name="Confuses arcsine with cosecant",
         signature="sin^-1(x) -> 1/sin(x)",
         kcs=["inverse_trig"],
         root="Same notation collision, made worse because cosecant genuinely is 1/sin.",
         fix="Name them apart: arcsin returns an ANGLE, csc returns a RATIO. Ask which one the answer should be.",
         probe="Is arcsin(0.5) an angle or a ratio?"),
    dict(id="INV_LOG_AS_DIV", family="INVERSE_AS_RECIPROCAL",
         name="Turns a log quotient into a quotient of logs",
         signature="log(a/b) -> (log a)/(log b)",
         kcs=["log_properties"],
         root="Blends the quotient rule with the change-of-base formula.",
         fix="Quotient rule gives a DIFFERENCE. A quotient of logs is change of base, a different tool.",
         probe="Expand log(x/5)."),

    # ---- RULE_OVERGENERALIZATION ----
    dict(id="EXP_PROD_MULTIPLY", family="RULE_OVERGENERALIZATION",
         name="Multiplies exponents when multiplying like bases",
         signature="x^a * x^b -> x^(ab)",
         kcs=["exp_laws"],
         root="Confuses the product rule with the power rule.",
         fix="Count it: x^2 x^3 written out is five x's. Adding, not multiplying.",
         probe="Simplify x^2 times x^3."),
    dict(id="EXP_QUOT_REVERSED", family="RULE_OVERGENERALIZATION",
         name="Subtracts exponents in the wrong order",
         signature="x^a / x^b -> x^(b-a)",
         kcs=["exp_laws", "exp_negative"],
         root="Remembers 'subtract' without anchoring which one leads.",
         fix="Top minus bottom, always. Sanity-check with x^5/x^2 = x^3.",
         probe="Simplify x^3 / x^5."),
    dict(id="EXP_POWER_ADD", family="RULE_OVERGENERALIZATION",
         name="Adds exponents when raising a power to a power",
         signature="(x^a)^b -> x^(a+b)",
         kcs=["exp_laws"],
         root="The mirror image of the product-rule confusion.",
         fix="Expand (x^2)^3 as x^2 x^2 x^2 and count to six.",
         probe="Simplify (x^2)^3."),
    dict(id="EXP_NEG_AS_SIGN", family="RULE_OVERGENERALIZATION",
         name="Reads a negative exponent as a negative value",
         signature="x^-2 -> -x^2",
         kcs=["exp_negative", "exp_functions"],
         root="Transfers the minus sign from the exponent to the base.",
         fix="2^-1 is 0.5, not -2. A negative exponent flips; it never changes the sign.",
         probe="Evaluate 2^-3."),
    dict(id="EXP_RATIONAL_INVERTED", family="RULE_OVERGENERALIZATION",
         name="Swaps root and power in a rational exponent",
         signature="a^(2/3) -> the square root of a cubed",
         kcs=["exp_rational", "radicals"],
         root="Knows both numbers matter but not which does which.",
         fix="Denominator is the root, numerator is the power. Test on 8^(1/3)=2.",
         probe="Evaluate 8^(2/3)."),
    dict(id="LOG_POWER_OUTSIDE", family="RULE_OVERGENERALIZATION",
         name="Moves an exponent out of the wrong position",
         signature="(log a)^n <-> log(a^n)",
         kcs=["log_properties"],
         root="Loses track of what the exponent is attached to.",
         fix="Only an exponent ON THE ARGUMENT comes down. Bracket the argument first.",
         probe="Is (log x)^2 the same as log(x^2)?"),
    dict(id="LOG_BASE_DROPPED", family="RULE_OVERGENERALIZATION",
         name="Ignores the base when converting to exponential form",
         signature="log_b(x)=y -> 10^y = x",
         kcs=["log_definition"],
         root="Defaults to base 10 because that is the calculator button.",
         fix="Say it as a sentence: the base, raised to the answer, gives the argument.",
         probe="Rewrite log_3(9)=2 in exponential form."),

    # ---- SIGN_MANAGEMENT ----
    dict(id="SIGN_DISTRIB_NEG", family="SIGN_MANAGEMENT",
         name="Distributes a negative to only the first term",
         signature="-(a-b) -> -a - b",
         kcs=["signed_numbers", "distribute", "linear_eq"],
         root="Applies the sign once and moves on.",
         fix="Rewrite as (-1) times the bracket and distribute explicitly.",
         probe="Simplify -(x-4)."),
    dict(id="SIGN_SQUARE_NEG", family="SIGN_MANAGEMENT",
         name="Confuses -3^2 with (-3)^2",
         signature="-3^2 -> 9",
         kcs=["order_ops", "signed_numbers"],
         root="Treats the minus as part of the base when no bracket says so.",
         fix="Without brackets the exponent binds tighter, so it is minus (three squared).",
         probe="Evaluate -3^2 and (-3)^2."),
    dict(id="SIGN_QUADFORM_B", family="SIGN_MANAGEMENT",
         name="Drops the sign of b in the quadratic formula",
         signature="uses b instead of -b",
         kcs=["quadratic_eq"],
         root="Copies the formula shape without tracking the sign of the coefficient.",
         fix="Write a, b, c on their own line with signs before substituting. Always.",
         probe="Solve x^2 - 5x + 6 = 0 with the formula."),

    # ---- NOTATION_LITERALISM ----
    dict(id="NOT_FN_AS_MULT", family="NOTATION_LITERALISM",
         name="Reads f(x) as f times x",
         signature="f(x+2) -> f*x + f*2",
         kcs=["fn_notation", "fn_composition"],
         root="Brackets after a letter usually do mean multiplication -- until they name a function.",
         fix="Read it aloud as 'f of x'. Rename the function to something non-algebraic for a session.",
         probe="For f(x)=3x, what is f(2)?"),
    dict(id="NOT_TRIG_SQUARED", family="NOTATION_LITERALISM",
         name="Confuses sine squared with sine of a square",
         signature="sin^2(x) -> sin(x^2)",
         kcs=["trig_identities_basic", "trig_simplify"],
         root="Ambiguous historical notation, genuinely badly designed.",
         fix="Rewrite sin^2(x) as (sin x)^2 in her own work until the parse is automatic.",
         probe="Is sin^2(x) equal to sin(x^2)?"),
    dict(id="NOT_COMPOSITION_MULT", family="NOTATION_LITERALISM",
         name="Reads composition as multiplication",
         signature="(f o g)(x) -> f(x) * g(x)",
         kcs=["fn_composition"],
         root="The composition ring is unfamiliar and looks like an operator.",
         fix="Feed a number through both machines in order and watch the output differ from the product.",
         probe="If f(x)=x+1 and g(x)=2x, find f(g(3))."),

    # ---- DIRECTION_INVERSION ----
    dict(id="DIR_SHIFT_BACKWARDS", family="DIRECTION_INVERSION",
         name="Shifts horizontally the wrong way",
         signature="f(x-2) -> graph moves left",
         kcs=["fn_transformations", "trig_graphs"],
         root="Reads the minus sign as a direction rather than as an input adjustment.",
         fix="Test one point: which x makes the bracket zero? That is where the old zero went.",
         probe="Which way does y=(x-3)^2 move?"),
    dict(id="DIR_PERIOD_MULTIPLIED", family="DIRECTION_INVERSION",
         name="Multiplies by b instead of dividing to get the period",
         signature="period of sin(bx) -> 2*pi*b",
         kcs=["trig_graphs"],
         root="Assumes a bigger coefficient means a bigger period.",
         fix="A bigger b means faster, so shorter. Period is 2 pi divided by b. Sketch sin(2x) once.",
         probe="What is the period of sin(2x)?"),
    dict(id="DIR_TRANSFORM_ORDER", family="DIRECTION_INVERSION",
         name="Applies stretches and shifts in the wrong order",
         signature="ignores factoring before reading the shift",
         kcs=["fn_transformations", "trig_graphs"],
         root="Reads the constants off in written order rather than operation order.",
         fix="Factor the inside completely first: b(x-c). The shift is only readable after factoring.",
         probe="Find the phase shift of sin(2x - pi)."),
    dict(id="DIR_INSIDE_OUTSIDE", family="DIRECTION_INVERSION",
         name="Swaps vertical and horizontal effects",
         signature="f(x)+2 -> moves right",
         kcs=["fn_transformations"],
         root="Has not separated changes to the input from changes to the output.",
         fix="Outside the function touches y and behaves normally; inside touches x and reverses.",
         probe="Which way does y=x^2+4 move?"),

    # ---- INCOMPLETE_SOLUTION_SET ----
    dict(id="INC_SQRT_POSITIVE_ONLY", family="INCOMPLETE_SOLUTION_SET",
         name="Takes only the positive square root",
         signature="x^2=9 -> x=3",
         kcs=["quadratic_eq", "radicals"],
         root="Confuses the square-root operation, which is positive by definition, with solving.",
         fix="Solving an equation is not applying a function. Both signs square to 9.",
         probe="Solve x^2 = 16."),
    dict(id="INC_TRIG_ONE_SOLUTION", family="INCOMPLETE_SOLUTION_SET",
         name="Reports only the calculator angle",
         signature="sin(x)=0.5 on [0,2pi) -> x=pi/6 only",
         kcs=["trig_equations", "trig_reference_angles"],
         root="Inverse trig returns one value; the equation has more.",
         fix="Sketch the unit circle, draw the horizontal line, count the crossings BEFORE writing.",
         probe="Solve sin(x)=1/2 on [0,2pi)."),
    dict(id="INC_ZERO_PRODUCT_MISUSE", family="INCOMPLETE_SOLUTION_SET",
         name="Applies the zero-product rule to a non-zero product",
         signature="(x-2)(x-3)=6 -> x-2=6 or x-3=6",
         kcs=["quadratic_eq"],
         root="Uses the factored shortcut without the zero that licenses it.",
         fix="The rule needs zero on one side. Expand, move everything over, then factor.",
         probe="Solve (x-2)(x-3)=6."),
    dict(id="INC_EXTRANEOUS_UNCHECKED", family="INCOMPLETE_SOLUTION_SET",
         name="Does not check for extraneous solutions",
         signature="accepts every root after squaring or clearing denominators",
         kcs=["radical_eq", "rational_eq", "log_solve"],
         root="Squaring and clearing denominators are not reversible, so they can invent roots.",
         fix="Any solve that squared or cleared a denominator is unfinished until each root is checked.",
         probe="Solve sqrt(x+6)=x and check both roots."),
    dict(id="INC_ABS_ONE_CASE", family="INCOMPLETE_SOLUTION_SET",
         name="Solves only the positive case of an absolute value",
         signature="|x-1|=5 -> x=6 only",
         kcs=["absolute_value"],
         root="Reads the bars as decoration rather than as two cases.",
         fix="Absolute value always splits into two equations. Write both before solving either.",
         probe="Solve |x-1|=5."),

    # ---- PROCEDURAL_NO_DOMAIN ----
    dict(id="DOM_CANCEL_ADDEND", family="PROCEDURAL_NO_DOMAIN",
         name="Cancels a term across a sum",
         signature="(x+3)/3 -> x",
         kcs=["rational_expr", "complex_frac", "rational_asymptotes"],
         root="Cancellation is a factor operation applied to an addend.",
         fix="Only whole factors cancel. Factor first; if it will not factor, nothing cancels.",
         probe="Simplify (x+3)/3."),
    dict(id="DOM_IGNORE_RESTRICTION", family="PROCEDURAL_NO_DOMAIN",
         name="Ignores values excluded from the domain",
         signature="reports a root that makes a denominator zero",
         kcs=["fn_domain_range", "rational_eq", "rational_asymptotes"],
         root="Solves the equation without ever asking what x is allowed to be.",
         fix="Write the excluded values down before solving, and check the answers against that line.",
         probe="Solve x/(x-2) = 2/(x-2)."),
    dict(id="DOM_LOG_NEGATIVE", family="PROCEDURAL_NO_DOMAIN",
         name="Accepts the log of a negative or zero",
         signature="keeps a root that makes a log argument non-positive",
         kcs=["log_solve", "log_definition"],
         root="Treats the algebra as complete when the domain still rules a root out.",
         fix="Every log argument must be strictly positive. Substitute each root back in and confirm.",
         probe="Solve log(x)+log(x-3)=1 and check both roots."),
    dict(id="DOM_HOLE_AS_ASYMPTOTE", family="PROCEDURAL_NO_DOMAIN",
         name="Calls a hole a vertical asymptote",
         signature="reports an asymptote at a cancelled factor",
         kcs=["rational_asymptotes"],
         root="Reads the original denominator without simplifying first.",
         fix="Factor and cancel first. A cancelled factor leaves a hole; a surviving one gives an asymptote.",
         probe="Where are the asymptotes and holes of (x^2-4)/(x-2)?"),
    dict(id="DOM_INEQ_NO_FLIP", family="PROCEDURAL_NO_DOMAIN",
         name="Does not flip the inequality on a negative multiplier",
         signature="-2x > 6 -> x > -3",
         kcs=["inequalities"],
         root="Applies equation moves to an inequality without the extra rule.",
         fix="Test a number from the answer set. -4 satisfies -2x>6; -2 does not. The sign must flip.",
         probe="Solve -2x > 6."),
    dict(id="DOM_INEQ_CROSS_MULT", family="PROCEDURAL_NO_DOMAIN",
         name="Cross-multiplies a rational inequality",
         signature="multiplies by a variable of unknown sign",
         kcs=["inequalities", "rational_expr"],
         root="Multiplying by a variable is only legal once its sign is known.",
         fix="Move everything to one side, combine, and use a sign chart instead.",
         probe="Solve 1/x < 2."),

    # ---- topic-specific, cross-family ----
    dict(id="TRIG_DEGREE_RADIAN_MODE", family="RULE_OVERGENERALIZATION",
         name="Mixes degrees and radians",
         signature="evaluates sin(pi/6) in degree mode",
         kcs=["angles_radians", "unit_circle", "trig_equations"],
         root="Treats the calculator mode as a setting rather than as part of the question.",
         fix="If the angle contains pi, the mode is radians. Check the mode before every trig session.",
         probe="Evaluate sin(pi/6) exactly."),
    dict(id="TRIG_COORD_SWAP", family="NOTATION_LITERALISM",
         name="Swaps sine and cosine on the unit circle",
         signature="cos(theta) read as the y-coordinate",
         kcs=["unit_circle", "trig_reference_angles"],
         root="Memorized the pairs without anchoring which coordinate is which.",
         fix="Alphabetical: cosine goes with x, sine goes with y. Confirm at theta=0, the point (1,0).",
         probe="What are the coordinates at theta=0?"),
    dict(id="TRIG_QUADRANT_SIGN", family="SIGN_MANAGEMENT",
         name="Uses the reference angle without fixing the quadrant sign",
         signature="cos(2pi/3) -> +1/2",
         kcs=["trig_reference_angles", "unit_circle"],
         root="Finds the right magnitude and stops before the sign step.",
         fix="Reference angle gives the size; the quadrant gives the sign. Two steps, never one.",
         probe="Evaluate cos(2pi/3)."),
    dict(id="TRIG_LAW_CHOICE", family="RULE_OVERGENERALIZATION",
         name="Picks the wrong law for the given parts",
         signature="uses law of sines on side-angle-side",
         kcs=["law_sines_cosines"],
         root="Selects by familiarity instead of by which parts are known.",
         fix="Law of sines needs a matched angle-side PAIR. No pair means law of cosines.",
         probe="Given two sides and the included angle, which law applies?"),
    dict(id="POLY_MULTIPLICITY_IGNORED", family="RULE_OVERGENERALIZATION",
         name="Treats every zero as a crossing",
         signature="graphs (x-2)^2 as crossing the axis",
         kcs=["poly_zeros"],
         root="Finds the zeros correctly and ignores their multiplicity.",
         fix="Odd multiplicity crosses, even multiplicity bounces. Sketch (x-2)^2 next to (x-2).",
         probe="Does y=(x-1)^2(x+3) cross or touch at x=1?"),
    dict(id="RAT_ASYMPTOTE_DEGREE", family="RULE_OVERGENERALIZATION",
         name="Gets the horizontal asymptote rule backwards",
         signature="top degree larger -> y=0",
         kcs=["rational_asymptotes", "poly_end_behavior"],
         root="Remembers three cases and mismatches them.",
         fix="Bottom bigger wins, giving y=0. Equal degrees give the leading-coefficient ratio. Top bigger has none.",
         probe="Find the horizontal asymptote of (2x^2+1)/(x^2-3)."),
    dict(id="FN_DOMAIN_RANGE_SWAP", family="NOTATION_LITERALISM",
         name="Reports the range when asked for the domain",
         signature="domain and range interchanged",
         kcs=["fn_domain_range"],
         root="Knows both sets and has not fixed which name belongs to which axis.",
         fix="Domain is the inputs, the x's, read left to right. Range is the outputs, read bottom to top.",
         probe="State the domain and range of y=sqrt(x)."),
    dict(id="COMP_ORDER_SWAPPED", family="NOTATION_LITERALISM",
         name="Composes in the wrong order",
         signature="f(g(x)) computed as g(f(x))",
         kcs=["fn_composition"],
         root="Reads left to right, but the inner function acts first.",
         fix="Work outward from the innermost bracket, exactly as with arithmetic.",
         probe="If f(x)=x^2 and g(x)=x+1, find f(g(2)) and g(f(2))."),
]

MISCONCEPTION_BY_ID = {m["id"]: m for m in MISCONCEPTIONS}


def validate(kc_ids):
    """Every misconception must attach to real KCs and a real family."""
    seen = set()
    for m in MISCONCEPTIONS:
        assert m["id"] not in seen, "duplicate misconception id %s" % m["id"]
        seen.add(m["id"])
        assert m["family"] in FAMILIES, "%s has unknown family %s" % (m["id"], m["family"])
        assert m["kcs"], "%s attaches to no KC" % m["id"]
        for k in m["kcs"]:
            assert k in kc_ids, "%s references unknown KC %s" % (m["id"], k)
        for field in ("name", "signature", "root", "fix", "probe"):
            assert m.get(field), "%s missing %s" % (m["id"], field)


if __name__ == "__main__":
    from kc_graph import KC_BY_ID

    validate(set(KC_BY_ID))
    print("misconceptions: %d across %d families" % (len(MISCONCEPTIONS), len(FAMILIES)))
    for fam in FAMILIES:
        members = [m["id"] for m in MISCONCEPTIONS if m["family"] == fam]
        print("  %-26s %2d  %s" % (fam, len(members), ", ".join(members[:4])))
    covered = set()
    for m in MISCONCEPTIONS:
        covered.update(m["kcs"])
    missing = sorted(set(KC_BY_ID) - covered)
    print("")
    print("KCs with no named misconception (%d): %s" % (len(missing), ", ".join(missing)))
