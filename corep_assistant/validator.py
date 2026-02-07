def validate(fields):

    flags = []

    cet1 = next((f["value"] for f in fields if "CET1" in f["description"]), 0)
    at1 = next((f["value"] for f in fields if "AT1" in f["description"]), 0)
    t2 = next((f["value"] for f in fields if "Tier2" in f["description"]), 0)

    total = cet1 + at1 + t2

    reported_total = next(
        (f["value"] for f in fields if "Total Capital" in f["description"]),
        None
    )

    if reported_total and reported_total != total:
        flags.append("Total capital mismatch")

    return flags
