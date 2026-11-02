import pandas as pd
df = pd.read_csv("data.csv", encoding = "ISO-8859-1")
print("Dataset loaded  successfully!")
print("Dateset shape :",df.shape)

print(("\nColumn names :"))
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate rows:")
print(df.duplicated().sum())


print("\n--- DATA QUALITY INVESTIGATION ---")

print("\nQuantity statistics:")
print(df["Quantity"].describe())

print("\nUnitPrice statistics:")
print(df["UnitPrice"].describe())

print("\nUnique invoice numbers:")
print(df["InvoiceNo"].nunique())

print("\nUnique products:")
print(df["StockCode"].nunique())

print("\nUnique customers (excluding missing IDs):")
print(df["CustomerID"].nunique())

print("\nInvoice numbers starting with C:")
print(
    df["InvoiceNo"]
    .astype(str)
    .str.startswith("C")
    .sum()
)


print("\nZero or negative quantities:")
print((df["Quantity"] <= 0).sum())

print("\nZero or negative prices:")
print((df["UnitPrice"] <= 0).sum())

print("\nMissing descriptions with product codes:")
print(
    df.loc[df["Description"].isna(), ["StockCode", "Quantity", "UnitPrice"]]
    .head(10)
)


print("\n--- TRANSACTION INVESTIGATION ---")

# 1. Sample of cancellation-style invoices
cancel_rows = df[
    df["InvoiceNo"].astype(str).str.startswith("C")
]

print("\nCancellation-style invoice rows:")
print(cancel_rows.shape[0])

print("\nSample cancellation records:")
print(
    cancel_rows[
        ["InvoiceNo", "StockCode", "Description",
         "Quantity", "UnitPrice", "CustomerID"]
    ].head(10).to_string(index=False)
)

# 2. Negative quantities
negative_qty = df[df["Quantity"] < 0]

print("\nNegative quantity rows:", len(negative_qty))

print("\nNegative quantity invoice prefixes:")
print(
    negative_qty["InvoiceNo"]
    .astype(str)
    .str.startswith("C")
    .value_counts()
)

# 3. Zero-price records
zero_price = df[df["UnitPrice"] == 0]

print("\nZero-price rows:", len(zero_price))

print("\nSample zero-price records:")
print(
    zero_price[
        ["InvoiceNo", "StockCode", "Description",
         "Quantity", "UnitPrice", "Country"]
    ].head(10).to_string(index=False)
)

# 4. Negative-price records
negative_price = df[df["UnitPrice"] < 0]

print("\nNegative-price rows:", len(negative_price))

print("\nSample negative-price records:")
print(
    negative_price[
        ["InvoiceNo", "StockCode", "Description",
         "Quantity", "UnitPrice", "Country"]
    ].head(10).to_string(index=False)
)

print("\n--- REVENUE VALIDATION ---")

# Calculate a provisional line amount
df["LineAmount"] = df["Quantity"] * df["UnitPrice"]

print("\nTotal line amount (raw dataset):")
print(round(df["LineAmount"].sum(), 2))

# Compare invoice categories
is_cancel = df["InvoiceNo"].astype(str).str.startswith("C")
is_adjustment = df["InvoiceNo"].astype(str).str.startswith("A")

print("\nRows by invoice category:")
print("C-prefix rows:", is_cancel.sum())
print("A-prefix rows:", is_adjustment.sum())
print("Other rows:", (~is_cancel & ~is_adjustment).sum())

print("\nLine amount by invoice category:")
print(
    df.assign(
        InvoiceCategory=[
            "Cancellation" if c
            else "Adjustment" if a
            else "Other"
            for c, a in zip(is_cancel, is_adjustment)
        ]
    )
    .groupby("InvoiceCategory")["LineAmount"]
    .agg(["count", "sum"])
    .round(2)
)

# Check unusual large positive and negative line amounts
print("\nLargest positive line amounts:")
print(
    df.nlargest(5, "LineAmount")[
        ["InvoiceNo", "Description", "Quantity",
         "UnitPrice", "LineAmount"]
    ].to_string(index=False)
)

print("\nSmallest (most negative) line amounts:")
print(
    df.nsmallest(5, "LineAmount")[
        ["InvoiceNo", "Description", "Quantity",
         "UnitPrice", "LineAmount"]
    ].to_string(index=False)
)

print("\n--- SALE AND CANCELLATION CHECK ---")

check_codes = ["85123A", "23843", "22834"]

for code in check_codes:
    print(f"\n--- StockCode: {code} ---")

    cols = [
        "InvoiceNo", "StockCode", "Description",
        "Quantity", "InvoiceDate", "UnitPrice", "CustomerID"
    ]

    sample = df[df["StockCode"] == code][cols]

    print(
        sample.sort_values("InvoiceDate")
        .tail(15)
        .to_string(index=False)
    )

print("\n--- EXACT EXTREME-QUANTITY RECORDS ---")

extreme = df[df["Quantity"].abs() >= 70000]

print(
    extreme[
        ["InvoiceNo", "StockCode", "Description",
         "Quantity", "InvoiceDate", "UnitPrice", "CustomerID"]
    ].sort_values(["StockCode", "InvoiceDate"])
    .to_string(index=False)
)

print("\n--- DATE CONVERSION CHECK ---")

df["InvoiceDate"] = pd.to_datetime(
    df["InvoiceDate"],
    format="%m/%d/%Y %H:%M",
    errors="coerce"
)

print("InvoiceDate data type:")
print(df["InvoiceDate"].dtype)

print("\nInvalid dates:")
print(df["InvoiceDate"].isna().sum())

print("\nDate range:")
print("First date:", df["InvoiceDate"].min())
print("Last date:", df["InvoiceDate"].max())

print("\n--- DATASET STATUS ---")
print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\n--- CUSTOMER ID INVESTIGATION ---")

missing_customer = df[df["CustomerID"].isna()]

print("Rows with missing CustomerID:")
print(len(missing_customer))

print("\nMissing CustomerID by country:")
print(missing_customer["Country"].value_counts().head(10))

print("\nMissing CustomerID transaction types:")
print(missing_customer["InvoiceNo"].astype(str).str.startswith("C").value_counts())

print("\nLineAmount summary for missing CustomerID:")
print(missing_customer["LineAmount"].describe())

print("\nSample rows with missing CustomerID:")
print(
    missing_customer[
        ["InvoiceNo", "StockCode", "Description",
         "Quantity", "UnitPrice", "LineAmount", "Country"]
    ].head(10).to_string(index=False)
)
print("\n--- MISSING CUSTOMERID: CANCELLATION ANALYSIS ---")

missing_customer = df[df["CustomerID"].isna()]

cancellation_rows = missing_customer[
    missing_customer["InvoiceNo"].astype(str).str.startswith("C")
]

normal_prefix_rows = missing_customer[
    ~missing_customer["InvoiceNo"].astype(str).str.startswith("C")
]

print("Cancellation-like rows:", len(cancellation_rows))
print("Cancellation-like LineAmount total:",
      round(cancellation_rows["LineAmount"].sum(), 2))

print("\nOther-prefix rows:", len(normal_prefix_rows))
print("Other-prefix LineAmount total:",
      round(normal_prefix_rows["LineAmount"].sum(), 2))

print("\nCancellation-like sample:")
print(
    cancellation_rows[
        ["InvoiceNo", "Description", "Quantity",
         "UnitPrice", "LineAmount", "Country"]
    ].head(10).to_string(index=False)
)

print("\n--- CUSTOMER ID: PRESENT VS MISSING ---")

missing_id = df[df["CustomerID"].isna()]
present_id = df[df["CustomerID"].notna()]

print("Rows with CustomerID:", len(present_id))
print("Rows without CustomerID:", len(missing_id))

print("\nLineAmount comparison:")

print("\nCustomerID present:")
print(present_id["LineAmount"].describe())

print("\nCustomerID missing:")
print(missing_id["LineAmount"].describe())

print("\nNegative-quantity rows:")
print("CustomerID present:",
      (present_id["Quantity"] < 0).sum())
print("CustomerID missing:",
      (missing_id["Quantity"] < 0).sum())

print("\nZero-price rows:")
print("CustomerID present:",
      (present_id["UnitPrice"] == 0).sum())
print("CustomerID missing:",
      (missing_id["UnitPrice"] == 0).sum())

print("\n--- ZERO-PRICE TRANSACTION INVESTIGATION ---")

zero_price = df[df["UnitPrice"] == 0]

print("Total zero-price rows:", len(zero_price))

print("\nCustomerID status:")
print(
    zero_price["CustomerID"]
    .isna()
    .value_counts()
    .rename(index={True: "Missing", False: "Present"})
)

print("\nMost common descriptions:")
print(zero_price["Description"].value_counts().head(15))

print("\nInvoice prefix distribution:")
print(
    zero_price["InvoiceNo"]
    .astype(str)
    .str.startswith("C")
    .value_counts()
)

print("\nQuantity summary:")
print(zero_price["Quantity"].describe())

print("\nSample zero-price rows:")
print(
    zero_price[
        ["InvoiceNo", "StockCode", "Description",
         "Quantity", "UnitPrice", "CustomerID", "Country"]
    ].head(20).to_string(index=False)
)


print("\n--- EXTREME ZERO-PRICE QUANTITIES ---")

zero_price = df[df["UnitPrice"] == 0].copy()

print("\nLargest positive quantities:")
print(
    zero_price.sort_values("Quantity", ascending=False)[
        ["InvoiceNo", "StockCode", "Description",
         "Quantity", "UnitPrice", "CustomerID", "Country"]
    ].head(10).to_string(index=False)
)

print("\nLargest negative quantities:")
print(
    zero_price.sort_values("Quantity")[
        ["InvoiceNo", "StockCode", "Description",
         "Quantity", "UnitPrice", "CustomerID", "Country"]
    ].head(10).to_string(index=False)
)

print("\nZero-price rows grouped by description:")
print(
    zero_price.groupby("Description", dropna=False)
    .agg(
        Rows=("InvoiceNo", "size"),
        TotalQuantity=("Quantity", "sum")
    )
    .sort_values("Rows", ascending=False)
    .head(15)
)



print("\n--- ZERO-PRICE BUSINESS CATEGORIES ---")

zero_price = df[df["UnitPrice"] == 0].copy()

description = (
    zero_price["Description"]
    .fillna("")
    .str.lower()
    .str.strip()
)

conditions = [
    description.str.contains(
        r"damag|thrown away|throw away|destroyed|unsaleable|smudges",
        regex=True
    ),
    description.str.contains(
        r"incorrect|wrongly|wrong|adjustment|credit",
        regex=True
    ),
    description.str.contains(
        r"check|\?",
        regex=True
    ),
    description.eq("")
]

labels = [
    "Damage / disposal",
    "Correction / adjustment",
    "Check / uncertain",
    "Missing description"
]

zero_price["InvestigationCategory"] = "Other / review"

for condition, label in zip(conditions, labels):
    zero_price.loc[
        condition & zero_price["InvestigationCategory"].eq("Other / review"),
        "InvestigationCategory"
    ] = label

print("\nRows per investigation category:")
print(
    zero_price["InvestigationCategory"]
    .value_counts()
)

print("\nCategory summary:")
print(
    zero_price.groupby("InvestigationCategory")
    .agg(
        Rows=("InvoiceNo", "size"),
        TotalQuantity=("Quantity", "sum"),
        UniqueInvoices=("InvoiceNo", "nunique")
    )
    .sort_values("Rows", ascending=False)
)

print("\nSample rows per category:")
print(
    zero_price[
        ["InvoiceNo", "Description", "Quantity",
         "UnitPrice", "InvestigationCategory"]
    ]
    .sort_values("InvestigationCategory")
    .groupby("InvestigationCategory")
    .head(3)
    .to_string(index=False)
)

print("\n--- ZERO-PRICE CATEGORY VALIDATION ---")

zero_price = df[df["UnitPrice"] == 0].copy()

description = (
    zero_price["Description"]
    .fillna("")
    .str.lower()
    .str.strip()
)

print("Total zero-price rows:", len(zero_price))

print("\nRows containing damage-related words:")
damage_rows = zero_price[
    description.str.contains(
        r"damag|thrown away|throw away|destroyed|unsaleable|smudges",
        regex=True
    )
]
print("Count:", len(damage_rows))
print(
    damage_rows[
        ["InvoiceNo", "Description", "Quantity", "UnitPrice"]
    ].head(10).to_string(index=False)
)

print("\nRows containing correction-related words:")
correction_rows = zero_price[
    description.str.contains(
        r"incorrect|wrongly|wrong|adjustment|credit",
        regex=True
    )
]
print("Count:", len(correction_rows))
print(
    correction_rows[
        ["InvoiceNo", "Description", "Quantity", "UnitPrice"]
    ].head(10).to_string(index=False)
)

print("\nRows with missing descriptions:")
missing_desc = zero_price[zero_price["Description"].isna()]
print("Count:", len(missing_desc))



print("\n--- ZERO-PRICE CATEGORY OVERLAP CHECK ---")

zero_price = df[df["UnitPrice"] == 0].copy()

description = (
    zero_price["Description"]
    .fillna("")
    .str.lower()
    .str.strip()
)

damage_mask = description.str.contains(
    r"damag|thrown away|throw away|destroyed|unsaleable|smudges",
    regex=True
)

correction_mask = description.str.contains(
    r"incorrect|wrongly|wrong|adjustment|credit",
    regex=True
)

overlap = zero_price[damage_mask & correction_mask]

print("Damage-related rows:", damage_mask.sum())
print("Correction-related rows:", correction_mask.sum())
print("Rows matching BOTH categories:", len(overlap))

print("\nOverlapping descriptions:")
print(
    overlap[
        ["InvoiceNo", "Description", "Quantity", "UnitPrice"]
    ].to_string(index=False)
)

print("\nRows matching neither category:")
neither = zero_price[~damage_mask & ~correction_mask]
print("Count:", len(neither))
print(
    neither[
        ["InvoiceNo", "Description", "Quantity", "UnitPrice"]
    ].head(10).to_string(index=False)
)


print("\n--- EXACT DUPLICATE ROW INVESTIGATION ---")

duplicate_mask = df.duplicated(keep=False)
duplicate_rows = df[duplicate_mask]

print("Rows belonging to duplicate groups:", len(duplicate_rows))

print("\nNumber of repeated copies beyond first occurrence:")
print(df.duplicated().sum())

print("\nSample duplicate rows:")
print(
    duplicate_rows.sort_values(
        by=["InvoiceNo", "StockCode", "Quantity"]
    )[
        ["InvoiceNo", "StockCode", "Description",
         "Quantity", "InvoiceDate", "UnitPrice", "CustomerID"]
    ].head(20).to_string(index=False)
)

print("\nMost frequent duplicated row patterns:")
print(
    duplicate_rows.groupby(
        ["InvoiceNo", "StockCode", "Description",
         "Quantity", "InvoiceDate", "UnitPrice", "CustomerID"],
        dropna=False
    ).size().sort_values(ascending=False).head(10)
)


print("\n--- VERIFIED EXACT DUPLICATE GROUPS ---")

# Har column ko use karke complete-row duplicates count karo
all_columns = df.columns.tolist()

exact_duplicate_counts = (
    df.groupby(all_columns, dropna=False)
    .size()
)

exact_duplicate_groups = exact_duplicate_counts[
    exact_duplicate_counts > 1
]

print(
    "Distinct exact duplicate groups:",
    len(exact_duplicate_groups)
)

print(
    "Rows belonging to exact duplicate groups:",
    int(exact_duplicate_groups.sum())
)

print(
    "Extra duplicate copies:",
    int((exact_duplicate_groups - 1).sum())
)

print(
    "Maximum copies of one identical row:",
    int(exact_duplicate_groups.max())
)

print("\nTop 10 exact duplicate groups:")
print(
    exact_duplicate_groups
    .sort_values(ascending=False)
    .head(10)
    .to_string()
)

print("\n--- DUPLICATE FINANCIAL IMPACT ---")

# Har complete row ki extra copies identify karo
duplicate_extra_mask = df.duplicated(keep="first")
extra_duplicate_rows = df[duplicate_extra_mask]

print("Extra duplicate rows:", len(extra_duplicate_rows))

print(
    "LineAmount from extra duplicate copies:",
    round(extra_duplicate_rows["LineAmount"].sum(), 2)
)

print(
    "Original raw LineAmount total:",
    round(df["LineAmount"].sum(), 2)
)

print(
    "LineAmount total if exact extra copies were removed:",
    round(
        df["LineAmount"].sum()
        - extra_duplicate_rows["LineAmount"].sum(),
        2
    )
)

print("\n--- DUPLICATE REPETITION DISTRIBUTION ---")

# Har complete row kitni baar appear hui?
row_counts = df.groupby(
    df.columns.tolist(),
    dropna=False
).size()

# Sirf repeated rows ke counts
repeated_counts = row_counts[row_counts > 1]

print("\nNumber of groups by repetition count:")
print(
    repeated_counts.value_counts()
    .sort_index()
    .to_string()
)

print("\nTotal duplicate groups:", len(repeated_counts))
print(
    "Maximum repetitions:",
    int(repeated_counts.max())
)


print("\n--- DUPLICATE IMPACT: SALES VS CANCELLATIONS ---")

# Sirf extra copies, har group ki first occurrence retain karke
extra_rows = df[df.duplicated(keep="first")].copy()

# Cancellation invoice number C se start hota hai
extra_rows["InvoiceType"] = extra_rows["InvoiceNo"].astype(str).str.startswith("C").map({
    True: "Cancellation",
    False: "Other invoice"
})

print(
    extra_rows.groupby("InvoiceType")
    .agg(
        ExtraDuplicateRows=("InvoiceNo", "size"),
        NetLineAmount=("LineAmount", "sum")
    )
    .round(2)
    .to_string()
)

print("\n--- STEP 1: REMOVE EXACT DUPLICATES SAFELY ---")

# Original df ko change nahi karna
df_clean = df.drop_duplicates().copy()

print("Original rows:", len(df))
print("Cleaned rows:", len(df_clean))
print("Rows removed:", len(df) - len(df_clean))

print(
    "Remaining exact duplicates:",
    df_clean.duplicated().sum()
)

print(
    "Original LineAmount total:",
    round(df["LineAmount"].sum(), 2)
)

print(
    "Cleaned LineAmount total:",
    round(df_clean["LineAmount"].sum(), 2)
)

print(
    "Original df unchanged:",
    len(df) == 541909
)


print("\n--- STEP 2: MISSING VALUES AFTER DEDUPLICATION ---")

print("\nMissing values in cleaned dataset:")
print(
    df_clean.isnull()
    .sum()
    .sort_values(ascending=False)
)

print("\nCustomerID missing vs available:")

print(
    df_clean["CustomerID"]
    .isnull()
    .value_counts()
    .rename(index={
        True: "Missing CustomerID",
        False: "CustomerID available"
    })
)

print("\nDescription missing vs available:")

print(
    df_clean["Description"]
    .isnull()
    .value_counts()
    .rename(index={
        True: "Missing Description",
        False: "Description available"
    })
)


print("\n--- STEP 3: MISSING CUSTOMERID INVESTIGATION ---")

missing_id = df_clean[df_clean["CustomerID"].isna()]
available_id = df_clean[df_clean["CustomerID"].notna()]

for label, group in [
    ("Missing CustomerID", missing_id),
    ("CustomerID available", available_id)
]:
    print(f"\n{label}")
    print("Rows:", len(group))
    print(
        "Cancellation invoices:",
        group["InvoiceNo"].astype(str).str.startswith("C").sum()
    )
    print("Zero-price rows:", (group["UnitPrice"] == 0).sum())
    print(
        "Net LineAmount:",
        round(group["LineAmount"].sum(), 2)
    )
    print(
        "Median LineAmount:",
        round(group["LineAmount"].median(), 2)
    )


print("\n--- STEP 4: MISSING DESCRIPTION INVESTIGATION ---")

missing_desc = df_clean[df_clean["Description"].isna()].copy()

print("Rows with missing Description:", len(missing_desc))

print(
    "Unique StockCodes:",
    missing_desc["StockCode"].nunique()
)

print(
    "Zero-price rows:",
    (missing_desc["UnitPrice"] == 0).sum()
)

print(
    "Negative-quantity rows:",
    (missing_desc["Quantity"] < 0).sum()
)

print(
    "Cancellation invoices:",
    missing_desc["InvoiceNo"].astype(str).str.startswith("C").sum()
)

print(
    "Net LineAmount:",
    round(missing_desc["LineAmount"].sum(), 2)
)

print("\nMost frequent StockCodes:")
print(missing_desc["StockCode"].value_counts().head(10))

print("\nSample missing-description rows:")
print(
    missing_desc[
        ["InvoiceNo", "StockCode", "Quantity",
         "InvoiceDate", "UnitPrice", "CustomerID",
         "Country", "LineAmount"]
    ].head(15).to_string(index=False)
)


print("\n--- STEP 5: CAN WE RECOVER MISSING DESCRIPTIONS? ---")

# Missing descriptions ke StockCodes
missing_codes = df_clean.loc[
    df_clean["Description"].isna(), "StockCode"
].unique()

# Un codes ki rows jahan Description available hai
known_descriptions = df_clean[
    df_clean["StockCode"].isin(missing_codes)
    & df_clean["Description"].notna()
]

# Har StockCode ke saath available descriptions
description_lookup = (
    known_descriptions.groupby("StockCode")["Description"]
    .agg(lambda values: sorted(set(values)))
)

print("Missing-description StockCodes:", len(missing_codes))
print(
    "Codes with a known description:",
    len(description_lookup)
)

print("\nSample available descriptions:")
print(description_lookup.head(20).to_string())

print("\nMissing codes with no known description:")
codes_without_description = set(missing_codes) - set(description_lookup.index)

print("Count:", len(codes_without_description))
print(sorted(codes_without_description)[:30])


print("\n--- STEP 6: CHECK DESCRIPTION AMBIGUITY ---")

# Har StockCode ki unique available descriptions count karo
description_counts = description_lookup.apply(len)

# Missing descriptions wale codes mein classification
unique_candidate_codes = description_counts[description_counts == 1]
multiple_candidate_codes = description_counts[description_counts > 1]

# Missing-description rows ko code level par classify karo
missing_description_rows = df_clean[df_clean["Description"].isna()]

unique_candidate_rows = missing_description_rows[
    missing_description_rows["StockCode"].isin(unique_candidate_codes.index)
]

multiple_candidate_rows = missing_description_rows[
    missing_description_rows["StockCode"].isin(multiple_candidate_codes.index)
]

no_candidate_rows = missing_description_rows[
    missing_description_rows["StockCode"].isin(codes_without_description)
]

print("Codes with exactly one description:", len(unique_candidate_codes))
print("Codes with multiple descriptions:", len(multiple_candidate_codes))
print("Codes with no description:", len(codes_without_description))

print("\nMissing rows with one candidate:", len(unique_candidate_rows))
print("Missing rows with multiple candidates:", len(multiple_candidate_rows))
print("Missing rows with no candidate:", len(no_candidate_rows))

print("\nExamples of ambiguous StockCodes:")
print(
    description_lookup.loc[multiple_candidate_codes.index]
    .head(15)
    .to_string()
)

print("\nSample rows with exactly one candidate:")
print(
    unique_candidate_rows[["StockCode", "Description", "UnitPrice", "Quantity"]]
    .head(10)
    .to_string(index=False)
)

print("\n--- STEP 7: REVIEW UNIQUE DESCRIPTION CANDIDATES ---")

# Har missing row ke StockCode ke liye ek known description
unique_description_map = {
    code: descriptions[0]
    for code, descriptions in description_lookup.items()
    if len(descriptions) == 1
}

# Missing rows jinke codes ka unique candidate hai
review_candidates = unique_candidate_rows.copy()

review_candidates["CandidateDescription"] = (
    review_candidates["StockCode"].map(unique_description_map)
)

# Distinct StockCodes aur proposed descriptions ka sample
candidate_review = (
    review_candidates[
        ["StockCode", "CandidateDescription"]
    ]
    .drop_duplicates()
    .sort_values("StockCode")
)

print("Unique candidate codes:", len(candidate_review))

print("\nFirst 30 candidate descriptions:")
print(candidate_review.head(30).to_string(index=False))

print("\nLast 20 candidate descriptions:")
print(candidate_review.tail(20).to_string(index=False))

print("\nOriginal missing descriptions still missing:",
      df_clean["Description"].isna().sum())

print("\n--- STEP 8: VALIDATE DESCRIPTION CANDIDATES ---")

# Candidate description blank ya whitespace-only to nahi?
candidate_text = candidate_review["CandidateDescription"].astype("string")

blank_candidates = (
    candidate_text.isna()
    | candidate_text.str.strip().eq("")
)

print("Total candidate codes:", len(candidate_review))
print("Blank candidate descriptions:", int(blank_candidates.sum()))

# Missing-description rows mein kitni rows ke liye candidate hai?
candidate_row_count = len(unique_candidate_rows)

print("Rows with a unique candidate:", candidate_row_count)
print("Rows still missing before recovery:", int(df_clean["Description"].isna().sum()))

# Verify mapping consistency
print(
    "Candidate mapping covers all unique-candidate rows:",
    review_candidates["CandidateDescription"].notna().all()
)

print("\nSample candidate descriptions after trimming spaces:")
print(
    candidate_review.assign(
        CandidateDescription=candidate_review["CandidateDescription"].str.strip()
    ).head(15).to_string(index=False)
)

print("\nOriginal df unchanged:", int(df["Description"].isna().sum()) == 1454)


print("\n--- STEP 9: RECOVER VALIDATED CANDIDATE DESCRIPTIONS ---")

# Recovery se pehle missing values count
missing_before = int(df_clean["Description"].isna().sum())

# Sirf missing descriptions ko unique candidate se fill karo
recovered_mask = (
    df_clean["Description"].isna()
    & df_clean["StockCode"].isin(unique_description_map.keys())
)

df_clean.loc[recovered_mask, "Description"] = (
    df_clean.loc[recovered_mask, "StockCode"]
    .map(unique_description_map)
)

# Recovery ke baad validation
missing_after = int(df_clean["Description"].isna().sum())

print("Missing descriptions before:", missing_before)
print("Descriptions recovered:", int(recovered_mask.sum()))
print("Missing descriptions after:", missing_after)

print(
    "Original df still unchanged:",
    int(df["Description"].isna().sum()) == 1454
)

print(
    "Remaining missing descriptions are ambiguous or unknown:",
    missing_after == 421
)

print("\n--- STEP 10: DATA QUALITY AUDIT ---")

# 1. Dataset size
print("\n1. Dataset shape:", df_clean.shape)

# 2. Remaining exact duplicates
print("2. Remaining exact duplicates:", df_clean.duplicated().sum())

# 3. Missing values in each column
print("\n3. Missing values by column:")
print(df_clean.isna().sum().to_string())

# 4. Quantity checks
print("\n4. Quantity checks:")
print("Zero quantity rows:", (df_clean["Quantity"] == 0).sum())
print("Negative quantity rows:", (df_clean["Quantity"] < 0).sum())

# 5. UnitPrice checks
print("\n5. UnitPrice checks:")
print("Zero UnitPrice rows:", (df_clean["UnitPrice"] == 0).sum())
print("Negative UnitPrice rows:", (df_clean["UnitPrice"] < 0).sum())

# 6. Verify LineAmount calculation
expected_amount = df_clean["Quantity"] * df_clean["UnitPrice"]

amount_mismatch = ~(
    df_clean["LineAmount"].eq(expected_amount)
    | (
        df_clean["LineAmount"].isna()
        & expected_amount.isna()
    )
)

print("\n6. LineAmount mismatches:", amount_mismatch.sum())

# 7. Confirm original data is still unchanged
print("\n7. Original dataset rows:", len(df))
print("Original missing descriptions:", df["Description"].isna().sum())
print("Original missing CustomerIDs:", df["CustomerID"].isna().sum())

print("\n--- STEP 11: INVESTIGATE NEGATIVE QUANTITIES ---")

# Negative quantity rows
negative_qty = df_clean[df_clean["Quantity"] < 0].copy()

# InvoiceNo ka C-prefix cancellation indicator hai
negative_qty["InvoiceType"] = negative_qty["InvoiceNo"].astype(str).str.startswith("C")

print("Total negative-quantity rows:", len(negative_qty))

print("\nNegative quantities by invoice type:")
print(
    negative_qty["InvoiceType"]
    .map({True: "C-prefix invoice", False: "Other invoice"})
    .value_counts()
    .to_string()
)

print("\nQuantity and LineAmount summary:")
print(
    negative_qty[["Quantity", "UnitPrice", "LineAmount"]]
    .describe()
    .round(2)
    .to_string()
)

print("\nLargest negative quantities:")
print(
    negative_qty.nsmallest(10, "Quantity")[
        ["InvoiceNo", "StockCode", "Description",
         "Quantity", "UnitPrice", "LineAmount", "CustomerID"]
    ].to_string(index=False)
)

print("\nNegative quantities in non-C-prefix invoices:")
print(
    negative_qty[~negative_qty["InvoiceType"]][
        ["InvoiceNo", "StockCode", "Description",
         "Quantity", "UnitPrice", "LineAmount"]
    ].head(15).to_string(index=False)
)

print("\n--- STEP 12: CLASSIFY NEGATIVE-QUANTITY ROWS ---")

negative_qty = df_clean[df_clean["Quantity"] < 0].copy()

# Invoice prefix
negative_qty["IsCancellationInvoice"] = (
    negative_qty["InvoiceNo"].astype(str).str.startswith("C")
)

# Price category
negative_qty["PriceCategory"] = "Positive price"
negative_qty.loc[
    negative_qty["UnitPrice"] == 0, "PriceCategory"
] = "Zero price"
negative_qty.loc[
    negative_qty["UnitPrice"] < 0, "PriceCategory"
] = "Negative price"

# Dono indicators ka combination
classification = (
    negative_qty.groupby(
        ["IsCancellationInvoice", "PriceCategory"],
        dropna=False
    )
    .agg(
        Rows=("InvoiceNo", "size"),
        TotalQuantity=("Quantity", "sum"),
        TotalLineAmount=("LineAmount", "sum")
    )
    .reset_index()
)

classification["InvoiceType"] = classification[
    "IsCancellationInvoice"
].map({True: "C-prefix", False: "Other invoice"})

print(
    classification[
        ["InvoiceType", "PriceCategory", "Rows",
         "TotalQuantity", "TotalLineAmount"]
    ].to_string(index=False)
)

print("\nNegative-quantity rows with zero price:")
print(
    negative_qty.loc[
        negative_qty["UnitPrice"] == 0,
        ["InvoiceNo", "StockCode", "Description",
         "Quantity", "UnitPrice", "LineAmount"]
    ].head(10).to_string(index=False)
)

print("\n--- STEP 13: INVESTIGATE ZERO-PRICE TRANSACTIONS ---")

zero_price = df_clean[df_clean["UnitPrice"] == 0].copy()

print("Total zero-price rows:", len(zero_price))

print("\nQuantity sign:")
print(
    zero_price["Quantity"]
    .apply(lambda q: "Negative" if q < 0 else "Positive" if q > 0 else "Zero")
    .value_counts()
    .to_string()
)

print("\nInvoice prefix:")
print(
    zero_price["InvoiceNo"]
    .astype(str)
    .str.startswith("C")
    .map({True: "C-prefix", False: "Other invoice"})
    .value_counts()
    .to_string()
)

print("\nMost common descriptions:")
print(
    zero_price["Description"]
    .fillna("[Missing description]")
    .value_counts()
    .head(20)
    .to_string()
)

print("\nZero-price rows with positive quantity:")
print(
    zero_price.loc[
        zero_price["Quantity"] > 0,
        ["InvoiceNo", "StockCode", "Description",
         "Quantity", "UnitPrice", "CustomerID"]
    ].head(15).to_string(index=False)
)

print("\nZero-price rows with negative quantity:")
print(
    zero_price.loc[
        zero_price["Quantity"] < 0,
        ["InvoiceNo", "StockCode", "Description",
         "Quantity", "UnitPrice", "CustomerID"]
    ].head(15).to_string(index=False)
)

print("\n--- STEP 14: CLASSIFY ZERO-PRICE DESCRIPTIONS ---")

zero_price = df_clean[df_clean["UnitPrice"] == 0].copy()

# Description ko lowercase text mein convert karo
desc = zero_price["Description"].fillna("").str.lower().str.strip()

# Default category
zero_price["ReviewCategory"] = "Product / other - review"

# Missing description
zero_price.loc[desc.eq(""), "ReviewCategory"] = "Missing description"

# Operational clues ke liye keyword groups
damage_pattern = (
    r"damage|damaged|throw.?away|thrown away|"
    r"destroyed|unsaleable|smudg|broken"
)

adjustment_pattern = r"adjustment|bad debt|incorrectly|credit"

uncertain_pattern = r"^check$|^\?$|^found$|^amazon$"

zero_price.loc[
    desc.str.contains(damage_pattern, regex=True, na=False),
    "ReviewCategory"
] = "Damage / disposal clue"

zero_price.loc[
    desc.str.contains(adjustment_pattern, regex=True, na=False),
    "ReviewCategory"
] = "Adjustment / correction clue"

zero_price.loc[
    desc.str.contains(uncertain_pattern, regex=True, na=False),
    "ReviewCategory"
] = "Uncertain / needs review"

print("\nRows per review category:")
print(zero_price["ReviewCategory"].value_counts().to_string())

print("\nCategory summary:")
print(
    zero_price.groupby("ReviewCategory")
    .agg(
        Rows=("InvoiceNo", "size"),
        NegativeQuantityRows=("Quantity", lambda s: (s < 0).sum()),
        PositiveQuantityRows=("Quantity", lambda s: (s > 0).sum()),
        TotalQuantity=("Quantity", "sum"),
        TotalLineAmount=("LineAmount", "sum")
    )
    .sort_values("Rows", ascending=False)
    .to_string()
)

print("\nOriginal df_clean zero-price rows:", (df_clean["UnitPrice"] == 0).sum())
print("Original df unchanged:", len(df) == 541909)

print("\n--- STEP 15: VALIDATE KEYWORD OVERLAPS ---")

# Har description ko normalized text mein rakho
desc = zero_price["Description"].fillna("").str.lower().str.strip()

# Har rule ka independent match
missing_match = desc.eq("")
damage_match = desc.str.contains(
    r"damage|damaged|throw.?away|thrown away|destroyed|unsaleable|smudg|broken",
    regex=True,
    na=False
)
adjustment_match = desc.str.contains(
    r"adjustment|bad debt|incorrectly|credit",
    regex=True,
    na=False
)
uncertain_match = desc.str.contains(
    r"^check$|^\?$|^found$|^amazon$",
    regex=True,
    na=False
)

matches = pd.DataFrame({
    "Missing": missing_match,
    "Damage/disposal": damage_match,
    "Adjustment/correction": adjustment_match,
    "Uncertain/review": uncertain_match
}, index=zero_price.index)

print("Rows matching each rule independently:")
print(matches.sum().to_string())

# Ek row kitne rules match karti hai?
matches_per_row = matches.sum(axis=1)

print("\nRows matching more than one rule:", int((matches_per_row > 1).sum()))
print("Rows matching no special rule:", int((matches_per_row == 0).sum()))

print("\nExamples matching multiple rules:")
overlap_index = matches.index[matches_per_row > 1]

print(
    zero_price.loc[
        overlap_index, ["StockCode", "Description", "Quantity", "UnitPrice"]
    ].head(20).to_string(index=False)
)

print("\nOriginal data unchanged:", len(df) == 541909)



print("\n--- STEP 16: PRESERVE ZERO-PRICE REVIEW CLUES ---")

zero_price["ReviewClues"] = ""

zero_price.loc[missing_match, "ReviewClues"] = (
    zero_price.loc[missing_match, "ReviewClues"] + "Missing description; "
)

zero_price.loc[damage_match, "ReviewClues"] = (
    zero_price.loc[damage_match, "ReviewClues"] + "Damage/disposal keyword; "
)

zero_price.loc[adjustment_match, "ReviewClues"] = (
    zero_price.loc[adjustment_match, "ReviewClues"] + "Adjustment/correction keyword; "
)

zero_price.loc[uncertain_match, "ReviewClues"] = (
    zero_price.loc[uncertain_match, "ReviewClues"] + "Uncertain/review keyword; "
)

zero_price.loc[
    zero_price["ReviewClues"].eq(""), "ReviewClues"
] = "No special keyword matched; review"

print("Rows with multiple clues:",
      int((zero_price["ReviewClues"].str.count(";") > 1).sum()))

print("\nRows with multiple clues:")
print(
    zero_price.loc[
        zero_price["ReviewClues"].str.count(";") > 1,
        ["Description", "Quantity", "ReviewCategory", "ReviewClues"]
    ].to_string(index=False)
)

print("\nReview clue counts:")
print(zero_price["ReviewClues"].value_counts().to_string())

print("\nZero-price rows:", len(zero_price))
print("Original df_clean zero-price rows:",
      (df_clean["UnitPrice"] == 0).sum())
print("Original data row count unchanged:", len(df) == 541909)


print("\n--- STEP 17: INVESTIGATE NEGATIVE UNIT PRICE ---")

negative_price = df_clean[df_clean["UnitPrice"] < 0].copy()

print("Negative UnitPrice rows:", len(negative_price))

print("\nNegative-price records:")
print(
    negative_price[
        [
            "InvoiceNo",
            "StockCode",
            "Description",
            "Quantity",
            "InvoiceDate",
            "UnitPrice",
            "CustomerID",
            "Country",
            "LineAmount"
        ]
    ].to_string(index=False)
)

print("\nNegative-price summary:")
print(
    negative_price[
        ["Quantity", "UnitPrice", "LineAmount"]
    ].describe().to_string()
)

print("\nOriginal df_clean negative-price rows:",
      (df_clean["UnitPrice"] < 0).sum())

print("Original data row count unchanged:", len(df) == 541909)


print("\n--- STEP 18: INVESTIGATE BAD-DEBT ADJUSTMENTS ---")

bad_debt = df_clean[
    df_clean["Description"]
    .fillna("")
    .str.lower()
    .str.contains("bad debt", regex=False)
].copy()

print("Rows with 'bad debt' in Description:", len(bad_debt))

print("\nAll bad-debt records:")
print(
    bad_debt[
        [
            "InvoiceNo",
            "StockCode",
            "Description",
            "Quantity",
            "InvoiceDate",
            "UnitPrice",
            "CustomerID",
            "Country",
            "LineAmount"
        ]
    ].sort_values("InvoiceDate").to_string(index=False)
)

print("\nBad-debt summary:")
print(
    bad_debt.groupby("InvoiceNo")
    .agg(
        Rows=("InvoiceNo", "size"),
        TotalQuantity=("Quantity", "sum"),
        TotalLineAmount=("LineAmount", "sum")
    )
    .to_string()
)

print("\nExact duplicate rows within bad-debt records:",
      int(bad_debt.duplicated().sum()))

print("Original data row count unchanged:", len(df) == 541909)



print("\n--- STEP 19: FLAG ACCOUNTING ADJUSTMENTS ---")

df_analysis = df_clean.copy()

description_lower = (
    df_analysis["Description"]
    .fillna("")
    .str.lower()
    .str.strip()
)

df_analysis["TransactionFlag"] = "Review transaction type"

df_analysis.loc[
    description_lower.str.contains("bad debt", regex=False),
    "TransactionFlag"
] = "Bad-debt adjustment"

print("Transaction flag counts:")
print(df_analysis["TransactionFlag"].value_counts().to_string())

print("\nBad-debt adjustment summary:")
print(
    df_analysis.loc[
        df_analysis["TransactionFlag"] == "Bad-debt adjustment"
    ]
    .groupby("TransactionFlag")
    .agg(
        Rows=("InvoiceNo", "size"),
        TotalLineAmount=("LineAmount", "sum")
    )
    .to_string()
)

print("\nAnalysis dataset shape:", df_analysis.shape)
print("Clean dataset shape:", df_clean.shape)
print("Original dataset shape:", df.shape)
print("Bad-debt rows retained:",
      (df_analysis["TransactionFlag"] == "Bad-debt adjustment").sum())



print("\n--- STEP 20: FLAG C-PREFIX INVOICES ---")

invoice_text = df_analysis["InvoiceNo"].astype("string").str.strip()

c_prefix = invoice_text.str.upper().str.startswith(
    "C", na=False
)

df_analysis["InvoiceFlag"] = "Other invoice prefix"

df_analysis.loc[
    c_prefix, "InvoiceFlag"
] = "C-prefix invoice - investigate"

print("Invoice flag counts:")
print(df_analysis["InvoiceFlag"].value_counts().to_string())

print("\nC-prefix invoice summary:")
print(
    df_analysis.loc[c_prefix]
    .groupby("InvoiceFlag")
    .agg(
        Rows=("InvoiceNo", "size"),
        NegativeQuantityRows=("Quantity", lambda s: (s < 0).sum()),
        PositiveQuantityRows=("Quantity", lambda s: (s > 0).sum()),
        TotalLineAmount=("LineAmount", "sum")
    )
    .to_string()
)

print("\nAnalysis dataset shape:", df_analysis.shape)
print("Original dataset shape:", df.shape)


print("\n--- STEP 21: CREATE COMBINED REVIEW FLAG ---")

df_analysis["ReviewStatus"] = "Standard review"

# Accounting adjustments ko specific label do
bad_debt_mask = (
    df_analysis["TransactionFlag"] == "Bad-debt adjustment"
)

df_analysis.loc[
    bad_debt_mask, "ReviewStatus"
] = "Accounting adjustment"

# C-prefix invoices ko flag karo, lekin accounting label preserve rakho
c_prefix_mask = (
    df_analysis["InvoiceFlag"] == "C-prefix invoice - investigate"
)

df_analysis.loc[
    c_prefix_mask & ~bad_debt_mask, "ReviewStatus"
] = "C-prefix transaction - investigate"

print("Combined review status:")
print(df_analysis["ReviewStatus"].value_counts().to_string())

print("\nReview status summary:")
print(
    df_analysis.groupby("ReviewStatus")
    .agg(
        Rows=("InvoiceNo", "size"),
        NegativeQuantityRows=("Quantity", lambda s: (s < 0).sum()),
        TotalLineAmount=("LineAmount", "sum")
    )
    .sort_values("Rows", ascending=False)
    .to_string()
)

print("\nAnalysis dataset shape:", df_analysis.shape)
print("Original dataset shape:", df.shape)


print("\n--- STEP 22: INVESTIGATE NON-C NEGATIVE QUANTITIES ---")

non_c_negative = df_analysis[
    (df_analysis["Quantity"] < 0)
    & (df_analysis["InvoiceFlag"] == "Other invoice prefix")
].copy()

print("Non-C negative-quantity rows:", len(non_c_negative))

print("\nUnitPrice breakdown:")
print(
    non_c_negative["UnitPrice"]
    .value_counts(dropna=False)
    .head(10)
    .to_string()
)

print("\nCustomerID missing rows:",
      int(non_c_negative["CustomerID"].isna().sum()))

print("\nMost common descriptions:")
print(
    non_c_negative["Description"]
    .fillna("[Missing description]")
    .value_counts()
    .head(25)
    .to_string()
)

print("\nSample records:")
print(
    non_c_negative[
        [
            "InvoiceNo",
            "StockCode",
            "Description",
            "Quantity",
            "InvoiceDate",
            "UnitPrice",
            "CustomerID",
            "LineAmount"
        ]
    ].head(20).to_string(index=False)
)

print("\nOriginal data row count unchanged:", len(df) == 541909)


print("\n--- STEP 23: CLASSIFY NON-C NEGATIVE-QUANTITY CLUES ---")

# Normalize descriptions for consistent keyword matching
desc = (
    non_c_negative["Description"]
    .fillna("")
    .str.lower()
    .str.strip()
)

# Independent clues — a row can match multiple clues
clue_flags = pd.DataFrame({
    "Missing description": desc.eq(""),

    "Damage / disposal clue": desc.str.contains(
        r"damage|damaged|unsaleable|destroyed|"
        r"thrown away|throw.?away|smashed|broken|wet pallet",
        regex=True,
        na=False
    ),

    "Uncertain note": desc.str.fullmatch(
        r"check+|\?+|missing",
        na=False
    ),

    "Marketplace / channel clue": desc.str.contains(
        r"amazon|ebay|dotcom",
        regex=True,
        na=False
    )
}, index=non_c_negative.index)

# Count each clue independently
print("\nRows matching each clue:")
print(clue_flags.sum().sort_values(ascending=False).to_string())

# Count rows with multiple clues
clues_per_row = clue_flags.sum(axis=1)

print("\nRows matching multiple clues:",
      int((clues_per_row > 1).sum()))

# Rows with no identified clue
no_clue = clues_per_row.eq(0)

print("Rows with no identified clue:",
      int(no_clue.sum()))

print("\nExamples with multiple clues:")
print(
    non_c_negative.loc[
        clues_per_row > 1,
        ["InvoiceNo", "Description", "Quantity", "UnitPrice"]
    ].head(15).to_string(index=False)
)

print("\nExamples with no identified clue:")
print(
    non_c_negative.loc[
        no_clue,
        ["InvoiceNo", "Description", "Quantity", "UnitPrice"]
    ].head(15).to_string(index=False)
)

print("\nRows investigated:", len(non_c_negative))
print("Original df_clean rows:", len(df_clean))
print("Original df rows:", len(df))



print("\n--- STEP 24: CHECK INVOICE CLUSTERS ---")

invoice_summary = (
    non_c_negative.groupby("InvoiceNo")
    .agg(
        Rows=("InvoiceNo", "size"),
        TotalNegativeQuantity=("Quantity", "sum"),
        UniqueStockCodes=("StockCode", "nunique"),
        FirstDate=("InvoiceDate", "min"),
        LastDate=("InvoiceDate", "max")
    )
    .sort_values("Rows", ascending=False)
)

print("Unique invoices:", len(invoice_summary))

print("\nLargest invoice groups:")
print(invoice_summary.head(15).to_string())

print("\nInvoice groups with multiple rows:",
      int((invoice_summary["Rows"] > 1).sum()))

print("\nMaximum rows in one invoice:",
      int(invoice_summary["Rows"].max()))

print("\nTotal rows across invoice groups:",
      int(invoice_summary["Rows"].sum()))

print("\nOriginal dataset row count:", len(df))


# STEP 25: Document negative quantity review decisions

# Negative quantity wali rows identify karo
negative_qty_mask = df_analysis["Quantity"] < 0

# Invoice number C se start hota hai ya nahi
c_prefix_mask = (
    df_analysis["InvoiceNo"]
    .astype(str)
    .str.startswith("C")
)

# Negative quantity rows ko review categories do
df_analysis["NegativeQuantityReview"] = "No negative quantity"

df_analysis.loc[
    negative_qty_mask,
    "NegativeQuantityReview"
] = "Negative quantity - investigate"

df_analysis.loc[
    negative_qty_mask & c_prefix_mask,
    "NegativeQuantityReview"
] = "C-prefix negative quantity - investigate"

df_analysis.loc[
    negative_qty_mask
    & ~c_prefix_mask
    & (df_analysis["UnitPrice"] == 0)
    & (df_analysis["CustomerID"].isna()),
    "NegativeQuantityReview"
] = "Non-C negative qty, zero price, missing CustomerID - investigate"

# Results check karo
print("\nSTEP 25: Negative Quantity Review Summary")

print(
    df_analysis["NegativeQuantityReview"]
    .value_counts(dropna=False)
)

print("\nCategory-wise row counts and amounts:")

print(
    df_analysis.groupby("NegativeQuantityReview")
    .agg(
        Rows=("Quantity", "size"),
        TotalQuantity=("Quantity", "sum"),
        TotalLineAmount=("LineAmount", "sum")
    )
    .round(2)
)

# Confirm original and cleaned row counts are unchanged
print("\nOriginal df rows:", len(df))
print("Cleaned df rows:", len(df_clean))
print("Analysis df rows:", len(df_analysis))


# STEP 26: Validate negative quantity review labels

negative_qty_mask = df_analysis["Quantity"] < 0

print("\nSTEP 26: Negative Quantity Audit")

# 1. Total negative quantity rows
print(
    "Actual negative quantity rows:",
    negative_qty_mask.sum()
)

# 2. Negative quantity rows assigned to a review category
print(
    "Rows labelled for investigation:",
    (
        df_analysis["NegativeQuantityReview"]
        != "No negative quantity"
    ).sum()
)

# 3. Check for negative quantity rows incorrectly labelled
# as having no negative quantity
incorrectly_labelled = df_analysis[
    negative_qty_mask
    & (
        df_analysis["NegativeQuantityReview"]
        == "No negative quantity"
    )
]

print(
    "Negative quantity rows with incorrect label:",
    len(incorrectly_labelled)
)

# 4. Check for non-negative rows incorrectly flagged
incorrectly_flagged = df_analysis[
    (~negative_qty_mask)
    & (
        df_analysis["NegativeQuantityReview"]
        != "No negative quantity"
    )
]

print(
    "Non-negative rows incorrectly flagged:",
    len(incorrectly_flagged)
)

# 5. Check whether every row belongs to exactly one category
print(
    "\nReview category totals:",
    df_analysis["NegativeQuantityReview"].value_counts().sum()
)


# STEP 27: Validate specific negative quantity categories

negative_qty = df_analysis["Quantity"] < 0

c_prefix = (
    df_analysis["InvoiceNo"]
    .astype(str)
    .str.startswith("C")
)

zero_price = df_analysis["UnitPrice"] == 0
missing_customer = df_analysis["CustomerID"].isna()

review = df_analysis["NegativeQuantityReview"]

# Expected conditions for each category
expected_c_prefix = negative_qty & c_prefix

expected_non_c = (
    negative_qty
    & ~c_prefix
    & zero_price
    & missing_customer
)

# Check actual category assignments
actual_c_prefix = (
    review == "C-prefix negative quantity - investigate"
)

actual_non_c = (
    review
    == "Non-C negative qty, zero price, missing CustomerID - investigate"
)

print("\nSTEP 27: Category-wise Validation")

print(
    "C-prefix category mismatches:",
    (actual_c_prefix != expected_c_prefix).sum()
)

print(
    "Non-C category mismatches:",
    (actual_non_c != expected_non_c).sum()
)

print(
    "Negative quantity rows outside both specific categories:",
    (
        negative_qty
        & ~actual_c_prefix
        & ~actual_non_c
    ).sum()
)



# STEP 28: Final Cleaning Policy and Decision Log

cleaning_decisions = [
    {
        "Issue": "Exact duplicate rows",
        "Decision": "Remove exact duplicates from cleaned dataset",
        "Reason": "Exact duplicate records were identified"
    },
    {
        "Issue": "Missing Description",
        "Decision": "Recover only unique known descriptions",
        "Reason": "Avoid guessing when multiple or no candidates exist"
    },
    {
        "Issue": "Missing CustomerID",
        "Decision": "Retain",
        "Reason": "Customer identity cannot be safely inferred"
    },
    {
        "Issue": "Negative Quantity",
        "Decision": "Retain and flag",
        "Reason": "May represent returns, cancellations, or other activity"
    },
    {
        "Issue": "Zero UnitPrice",
        "Decision": "Retain and review",
        "Reason": "May represent operational or non-sales records"
    },
    {
        "Issue": "Negative UnitPrice / bad debt",
        "Decision": "Retain and investigate",
        "Reason": "May represent accounting adjustments"
    },
    {
        "Issue": "C-prefix invoices",
        "Decision": "Flag for review",
        "Reason": "Invoice prefix alone does not prove transaction meaning"
    }
]

cleaning_decisions_df = pd.DataFrame(cleaning_decisions)

print("\nSTEP 28: Cleaning Decision Log")
print(cleaning_decisions_df.to_string(index=False))

print("\nDataset row-count checkpoint")
print("Original df:", len(df))
print("Cleaned df:", len(df_clean))
print("Analysis df:", len(df_analysis))

print("\nMissing values in analysis dataset")
print(df_analysis.isna().sum())

print("\nExact duplicates remaining in cleaned dataset")
print(df_clean.duplicated().sum())


# STEP 29: Final Data Validation

print("\nSTEP 29: Final Data Validation")

# 1. Row and column counts
print("\n1. Dataset shapes")
print("Original df:", df.shape)
print("Cleaned df:", df_clean.shape)
print("Analysis df:", df_analysis.shape)

# 2. Duplicate check
print("\n2. Exact duplicate rows in df_clean:")
print(df_clean.duplicated().sum())

# 3. Verify LineAmount = Quantity * UnitPrice
expected_amount = (
    df_analysis["Quantity"] * df_analysis["UnitPrice"]
)

amount_mismatch = (
    (df_analysis["LineAmount"] - expected_amount).abs() > 0.000001
)

print("\n3. LineAmount calculation check")
print("Mismatched rows:", amount_mismatch.sum())

# 4. Data types
print("\n4. Data types")
print(df_analysis.dtypes)

# 5. Date range
print("\n5. InvoiceDate range")
print("Earliest:", df_analysis["InvoiceDate"].min())
print("Latest:", df_analysis["InvoiceDate"].max())

# 6. Unusual quantity and price values
print("\n6. Quantity and UnitPrice checks")
print("Zero quantity rows:", (df_analysis["Quantity"] == 0).sum())
print("Negative quantity rows:", (df_analysis["Quantity"] < 0).sum())
print("Zero UnitPrice rows:", (df_analysis["UnitPrice"] == 0).sum())
print("Negative UnitPrice rows:", (df_analysis["UnitPrice"] < 0).sum())

# 7. Missing-value summary
print("\n7. Missing values")
print(df_analysis.isna().sum())

# 8. Check whether row counts remain unchanged
print("\n8. Row-count integrity")
print("Original row count unchanged:", len(df) == 541909)
print("Cleaned row count expected:", len(df_clean) == 536641)
print("Analysis row count matches cleaned:", len(df_analysis) == len(df_clean))






# STEP 30: Audit derived review flags

print("\nSTEP 30: Derived Flags Audit")

# 1. Validate InvoiceFlag against InvoiceNo prefix
is_c_prefix = (
    df_analysis["InvoiceNo"]
    .astype(str)
    .str.startswith("C")
)

expected_invoice_flag = is_c_prefix.map({
    True: "C-prefix invoice - investigate",
    False: "Other invoice prefix"
})

print(
    "\nInvoiceFlag mismatches:",
    (
        df_analysis["InvoiceFlag"] != expected_invoice_flag
    ).sum()
)

# 2. Validate TransactionFlag using the known bad-debt description
is_bad_debt = (
    df_analysis["Description"]
    .astype("string")
    .str.contains("bad debt", case=False, na=False)
)

expected_transaction_flag = is_bad_debt.map({
    True: "Bad-debt adjustment",
    False: "Review transaction type"
})

print(
    "TransactionFlag mismatches:",
    (
        df_analysis["TransactionFlag"]
        != expected_transaction_flag
    ).sum()
)

# 3. Validate ReviewStatus priority
expected_review_status = pd.Series(
    "Standard review",
    index=df_analysis.index
)

expected_review_status.loc[is_c_prefix] = (
    "C-prefix transaction - investigate"
)

expected_review_status.loc[is_bad_debt] = (
    "Accounting adjustment"
)

print(
    "ReviewStatus mismatches:",
    (
        df_analysis["ReviewStatus"]
        != expected_review_status
    ).sum()
)

# 4. Print category counts for final inspection
print("\nInvoiceFlag counts:")
print(df_analysis["InvoiceFlag"].value_counts())

print("\nTransactionFlag counts:")
print(df_analysis["TransactionFlag"].value_counts())

print("\nReviewStatus counts:")
print(df_analysis["ReviewStatus"].value_counts())



# STEP 31: EDA Readiness Check

print("\nSTEP 31: EDA Readiness Check")

# 1. Check required analysis columns
required_columns = [
    "InvoiceNo",
    "StockCode",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
    "LineAmount"
]

missing_columns = [
    col for col in required_columns
    if col not in df_analysis.columns
]

print("\n1. Required columns missing:", missing_columns)

# 2. Check infinite numeric values
numeric_cols = ["Quantity", "UnitPrice", "LineAmount"]

print("\n2. Infinite values in numeric columns:")
for col in numeric_cols:
    print(
        col,
        pd.Series(
            df_analysis[col].isin([float("inf"), float("-inf")])
        ).sum()
    )

# 3. Check date validity
print("\n3. Invalid or missing dates:")
print(df_analysis["InvoiceDate"].isna().sum())

# 4. Summarize known data-quality issues
print("\n4. Known issues to remember")
print("Missing descriptions:", df_analysis["Description"].isna().sum())
print("Missing CustomerID:", df_analysis["CustomerID"].isna().sum())
print("Negative quantities:", (df_analysis["Quantity"] < 0).sum())
print("Zero prices:", (df_analysis["UnitPrice"] == 0).sum())
print("Negative prices:", (df_analysis["UnitPrice"] < 0).sum())

# 5. Confirm dataset remains unchanged in row count
print("\n5. EDA dataset checkpoint")
print("Analysis rows:", len(df_analysis))
print("Analysis columns:", len(df_analysis.columns))















# STEP 32: Monthly Business Activity Analysis

df_analysis["Month"] = (
    df_analysis["InvoiceDate"].dt.to_period("M")
)

monthly_activity = (
    df_analysis.groupby("Month")
    .agg(
        TransactionRows=("InvoiceNo", "size"),
        UniqueInvoices=("InvoiceNo", "nunique"),
        TotalLineAmount=("LineAmount", "sum")
    )
    .reset_index()
)

c_prefix_rows = df_analysis[
    df_analysis["InvoiceNo"].astype(str).str.startswith("C")
]

monthly_c_activity = (
    c_prefix_rows.groupby("Month")
    .agg(
        C_Prefix_Rows=("InvoiceNo", "size"),
        C_Prefix_Invoices=("InvoiceNo", "nunique"),
        C_Prefix_LineAmount=("LineAmount", "sum")
    )
    .reset_index()
)

monthly_activity = monthly_activity.merge(
    monthly_c_activity,
    on="Month",
    how="left"
)

monthly_activity[
    ["C_Prefix_Rows", "C_Prefix_Invoices", "C_Prefix_LineAmount"]
] = monthly_activity[
    ["C_Prefix_Rows", "C_Prefix_Invoices", "C_Prefix_LineAmount"]
].fillna(0)

print("\nSTEP 32: Monthly Business Activity")
print(monthly_activity.to_string(index=False))

print("\nTotal months:", len(monthly_activity))
print("Earliest month:", monthly_activity["Month"].min())
print("Latest month:", monthly_activity["Month"].max())



# STEP 33: Monthly Activity - Daily Average Comparison

monthly_daily = (
    df_analysis.groupby("Month")
    .agg(
        TransactionRows=("InvoiceNo", "size"),
        UniqueInvoices=("InvoiceNo", "nunique"),
        TotalLineAmount=("LineAmount", "sum"),
        ObservedDays=("InvoiceDate", lambda x: x.dt.date.nunique())
    )
    .reset_index()
)

monthly_daily["AvgRowsPerDay"] = (
    monthly_daily["TransactionRows"] / monthly_daily["ObservedDays"]
)

monthly_daily["AvgInvoicesPerDay"] = (
    monthly_daily["UniqueInvoices"] / monthly_daily["ObservedDays"]
)

monthly_daily["AvgLineAmountPerDay"] = (
    monthly_daily["TotalLineAmount"] / monthly_daily["ObservedDays"]
)

print("\nSTEP 33: Monthly Daily Average Comparison")
print(monthly_daily.round(2).to_string(index=False))



# STEP 34: Visualize Average Daily Invoice Activity

# import matplotlib.pyplot as plt

# plt.figure(figsize=(12, 6))

# plt.plot(
#     monthly_daily["Month"].astype(str),
#     monthly_daily["AvgInvoicesPerDay"],
#     marker="o"
# )

# plt.title("Average Daily Invoice Activity by Month")
# plt.xlabel("Month")
# plt.ylabel("Average Unique Invoices per Recorded Day")
# plt.xticks(rotation=45)
# plt.grid(True, alpha=0.3)
# plt.tight_layout()
# plt.show()
# print("df_clean columns:", df_clean.columns.tolist())
# print("monthly_daily columns:", monthly_daily.columns.tolist())

# monthly_revenue = (
#     df_clean.groupby(
#         df_clean["InvoiceDate"].dt.to_period("M")
#     )["LineAmount"]
#     .sum()
#     .reset_index(name="TotalLineAmount")
# )

# monthly_revenue = monthly_revenue.rename(
#     columns={"InvoiceDate": "Month"}
# )

# print(monthly_revenue)






print("STEP 35 STARTED")

print(df_clean["Description"].dropna().unique()[:30])



# STEP 36: Product-Level Activity Analysis

# Missing product descriptions ko filhal exclude karo
product_data = df_clean[df_clean["Description"].notna()].copy()

# Har product description ki activity summarize karo
product_summary = (
    product_data
    .groupby(["StockCode", "Description"])
    .agg(
        Frequency=("InvoiceNo", "size"),
        UniqueInvoices=("InvoiceNo", "nunique"),
        NetQuantity=("Quantity", "sum"),
        TotalLineAmount=("LineAmount", "sum")
    )
    .reset_index()
)

# Sab se zyada rows mein aane wale 15 products
top_products = product_summary.sort_values(
    "Frequency",
    ascending=False
).head(15)

print("\nSTEP 36: Top 15 Products by Frequency")
print(top_products.to_string(index=False))

print("\nTotal product groups:", len(product_summary))
print("Rows used:", len(product_data))
print("Rows excluded due to missing Description:",
      df_clean["Description"].isna().sum())




# STEP 37: Top 15 Products by Total Line Amount

top_amount_products = product_summary.sort_values(
    "TotalLineAmount",
    ascending=False
).head(15)

print("\nSTEP 37: Top 15 Products by Total Line Amount")

print(
    top_amount_products.to_string(index=False)
)


# STEP 38: Investigate Unusual High-Amount Product

target_stockcode = "22502"

picnic_rows = df_clean[
    df_clean["StockCode"].astype(str) == target_stockcode
].copy()

print("\nSTEP 38: Picnic Basket Transaction Details")

print(
    picnic_rows[
        [
            "InvoiceNo",
            "InvoiceDate",
            "StockCode",
            "Description",
            "Quantity",
            "UnitPrice",
            "LineAmount",
            "CustomerID",
            "Country"
        ]
    ].to_string(index=False)
)

print("\nTotal rows:", len(picnic_rows))
print("Total quantity:", picnic_rows["Quantity"].sum())
print("Total LineAmount:", picnic_rows["LineAmount"].sum())





# STEP 39: Verify Product Summary Against Raw Cleaned Data

target_stockcode = "22502"

direct_rows = df_clean[
    df_clean["StockCode"].astype(str) == target_stockcode
].copy()

summary_rows = product_summary[
    product_summary["StockCode"].astype(str) == target_stockcode
].copy()

print("\nSTEP 39: Direct Data Check")
print("Direct rows:", len(direct_rows))
print("Direct quantity:", direct_rows["Quantity"].sum())
print("Direct LineAmount:", direct_rows["LineAmount"].sum())

print("\nProduct Summary Check")
print(summary_rows.to_string(index=False))

print("\nProduct Summary total groups:", len(product_summary))





# STEP 40: Investigate Missing Rows in Product Summary

target_stockcode = "22502"

direct_rows = df_clean[
    df_clean["StockCode"].astype(str) == target_stockcode
].copy()

summary_count = product_summary.loc[
    product_summary["StockCode"].astype(str) == target_stockcode,
    "Frequency"
].sum()

print("\nSTEP 40: Row Count Reconciliation")
print("Direct data rows:", len(direct_rows))
print("Summary frequency total:", summary_count)
print("Difference:", len(direct_rows) - summary_count)

print("\nDescription-wise direct row counts:")
print(
    direct_rows.groupby("Description", dropna=False)
    .size()
    .sort_values(ascending=False)
    .to_string()
)

print("\nMissing descriptions:", direct_rows["Description"].isna().sum())





# STEP 41: Inspect Missing-Description Rows for StockCode 22502

missing_desc_rows = df_clean[
    (df_clean["StockCode"].astype(str) == "22502")
    & (df_clean["Description"].isna())
].copy()

print("\nSTEP 41: Missing Description Row Details")

print(
    missing_desc_rows[
        [
            "InvoiceNo",
            "InvoiceDate",
            "StockCode",
            "Quantity",
            "UnitPrice",
            "LineAmount",
            "CustomerID",
            "Country"
        ]
    ].to_string(index=False)
)

print("\nMissing-description row count:", len(missing_desc_rows))
print("Total quantity:", missing_desc_rows["Quantity"].sum())
print("Total LineAmount:", missing_desc_rows["LineAmount"].sum())






# STEP 42: Validate Product Summary Totals

print("\nSTEP 42: Product Summary Validation")

print("Clean dataset rows:", len(df_clean))
print("Rows used for product analysis:", len(product_data))
print("Product summary frequency total:", product_summary["Frequency"].sum())

print("\nClean dataset LineAmount:", df_clean["LineAmount"].sum())
print("Product summary LineAmount:", product_summary["TotalLineAmount"].sum())

print("\nMissing descriptions in clean data:",
      df_clean["Description"].isna().sum())

print("Missing descriptions excluded:",
      len(df_clean) - len(product_data))






# STEP 43: Monthly Product Variety

monthly_products = (
    product_data
    .groupby(product_data["InvoiceDate"].dt.to_period("M"))
    .agg(
        UniqueProducts=("StockCode", "nunique"),
        TransactionRows=("InvoiceNo", "size"),
        UniqueInvoices=("InvoiceNo", "nunique")
    )
    .reset_index()
)

monthly_products = monthly_products.rename(
    columns={"InvoiceDate": "Month"}
)

print("\nSTEP 43: Monthly Product Variety")
print(monthly_products.to_string(index=False))




# STEP 44: Visualize Monthly Product Variety

# import matplotlib.pyplot as plt

# plt.figure(figsize=(12, 6))

# plt.plot(
#         monthly_products["Month"].astype(str),
#         monthly_products["UniqueProducts"],
#         marker="o"
#     )

# plt.title("Monthly Product Variety")
# plt.xlabel("Month")
# plt.ylabel("Number of Unique StockCodes")
# plt.xticks(rotation=45)
# plt.grid(True, alpha=0.3)
# plt.tight_layout()
# plt.show()





# STEP 45: Compare Product Variety with Transaction Activity

monthly_products["ProductsPer1000Rows"] = (
    monthly_products["UniqueProducts"]
    / monthly_products["TransactionRows"]
    * 1000
)

print("\nSTEP 45: Product Variety vs Activity")

print(
    monthly_products[
        [
            "Month",
            "UniqueProducts",
            "TransactionRows",
            "UniqueInvoices",
            "ProductsPer1000Rows"
        ]
    ].to_string(index=False)
)

print("\nDecember Comparison")

december_data = monthly_products[
    monthly_products["Month"].astype(str).str.endswith("-12")
]

print(december_data.to_string(index=False))







# # STEP 46: Visualize Monthly Transaction Activity

# import matplotlib.pyplot as plt

# plt.figure(figsize=(12, 6))

# plt.plot(
#     monthly_products["Month"].astype(str),
#     monthly_products["TransactionRows"],
#     marker="o"
# )

# plt.title("Monthly Transaction Activity")
# plt.xlabel("Month")
# plt.ylabel("Transaction Rows")
# plt.xticks(rotation=45)
# plt.grid(True, alpha=0.3)
# plt.tight_layout()
# plt.show()




# # STEP 47: Visualize Monthly Unique Invoices

# import matplotlib.pyplot as plt

# plt.figure(figsize=(12, 6))

# plt.plot(
#     monthly_products["Month"].astype(str),
#     monthly_products["UniqueInvoices"],
#     marker="o"
# )

# plt.title("Monthly Unique Invoice Activity")
# plt.xlabel("Month")
# plt.ylabel("Number of Unique Invoices")
# plt.xticks(rotation=45)
# plt.grid(True, alpha=0.3)
# plt.tight_layout()
# plt.show()




# # STEP 48: Visualize Monthly Net Line Amount

# import matplotlib.pyplot as plt

# plt.figure(figsize=(12, 6))

# plt.plot(
#     monthly_revenue["Month"].astype(str),
#     monthly_revenue["TotalLineAmount"],
#     marker="o"
# )

# plt.title("Monthly Net Line Amount")
# plt.xlabel("Month")
# plt.ylabel("Net Line Amount (£)")
# plt.xticks(rotation=45)
# plt.grid(True, alpha=0.3)
# plt.tight_layout()
# plt.show()





# # STEP 49: Visualize Monthly Net Line Amount Using Bar Chart

# import matplotlib.pyplot as plt

# plt.figure(figsize=(12, 6))

# plt.bar(
#     monthly_revenue["Month"].astype(str),
#     monthly_revenue["TotalLineAmount"]
# )

# plt.title("Monthly Net Line Amount")
# plt.xlabel("Month")
# plt.ylabel("Net Line Amount (£)")
# plt.xticks(rotation=45)
# plt.grid(axis="y", alpha=0.3)
# plt.tight_layout()
# plt.show()




# STEP 50: Compare Monthly Transaction Rows and Unique Invoices

# import matplotlib.pyplot as plt

# plt.figure(figsize=(12, 6))

# plt.plot(
#     monthly_products["Month"].astype(str),
#     monthly_products["TransactionRows"],
#     marker="o",
#     label="Transaction Rows"
# )

# plt.plot(
#     monthly_products["Month"].astype(str),
#     monthly_products["UniqueInvoices"],
#     marker="o",
#     label="Unique Invoices"
# )

# plt.title("Monthly Transaction Rows vs Unique Invoices")
# plt.xlabel("Month")
# plt.ylabel("Count")
# plt.xticks(rotation=45)
# plt.legend()
# plt.grid(True, alpha=0.3)
# plt.tight_layout()
# plt.show()




# # STEP 51: Compare Monthly Rows and Invoices with Separate Axes

# fig, ax1 = plt.subplots(figsize=(12, 6))

# months = monthly_products["Month"].astype(str)

# ax1.plot(
#     months,
#     monthly_products["TransactionRows"],
#     marker="o",
#     label="Transaction Rows"
# )

# ax1.set_xlabel("Month")
# ax1.set_ylabel("Transaction Rows")
# ax1.tick_params(axis="y")

# ax2 = ax1.twinx()

# ax2.plot(
#     months,
#     monthly_products["UniqueInvoices"],
#     marker="s",
#     label="Unique Invoices"
# )

# ax2.set_ylabel("Unique Invoices")
# ax1.set_title("Monthly Transaction Rows vs Unique Invoices")

# ax1.tick_params(axis="x", rotation=45)
# ax1.grid(True, alpha=0.3)

# fig.tight_layout()
# plt.show()



# STEP 52: Calculate Monthly Average Line Amount per Transaction Row

monthly_average = (
    df_clean
    .groupby(df_clean["InvoiceDate"].dt.to_period("M"))
    .agg(
        TransactionRows=("InvoiceNo", "size"),
        TotalLineAmount=("LineAmount", "sum")
    )
    .reset_index()
)

monthly_average = monthly_average.rename(
    columns={"InvoiceDate": "Month"}
)

monthly_average["AverageLineAmountPerRow"] = (
    monthly_average["TotalLineAmount"]
    / monthly_average["TransactionRows"]
)

print("\nSTEP 52: Monthly Average Line Amount per Transaction Row")
print(monthly_average.to_string(index=False))



# STEP 53: Visualize Monthly Average Line Amount

# import matplotlib.pyplot as plt

# plt.figure(figsize=(12, 6))

# plt.plot(
#     monthly_average["Month"].astype(str),
#     monthly_average["AverageLineAmountPerRow"],
#     marker="o"
# )

# plt.title("Monthly Average Line Amount per Transaction Row")
# plt.xlabel("Month")
# plt.ylabel("Average Line Amount (£)")
# plt.xticks(rotation=45)
# plt.grid(True, alpha=0.3)
# plt.tight_layout()
# plt.show()



# # STEP 54: Monthly Average Line Amount Bar Chart

# import matplotlib.pyplot as plt

# plt.figure(figsize=(12, 6))

# plt.bar(
#     monthly_average["Month"].astype(str),
#     monthly_average["AverageLineAmountPerRow"]
# )

# plt.title("Monthly Average Line Amount per Transaction Row")
# plt.xlabel("Month")
# plt.ylabel("Average Line Amount (£)")
# plt.xticks(rotation=45)
# plt.grid(axis="y", alpha=0.3)
# plt.tight_layout()
# plt.show()




# STEP 55: Calculate Monthly Average Quantity per Invoice

monthly_quantity = (
    df_clean
    .groupby(df_clean["InvoiceDate"].dt.to_period("M"))
    .agg(
        TotalQuantity=("Quantity", "sum"),
        UniqueInvoices=("InvoiceNo", "nunique")
    )
    .reset_index()
)

monthly_quantity = monthly_quantity.rename(
    columns={"InvoiceDate": "Month"}
)

monthly_quantity["AverageQuantityPerInvoice"] = (
    monthly_quantity["TotalQuantity"]
    / monthly_quantity["UniqueInvoices"]
)

print("\nSTEP 55: Monthly Average Quantity per Invoice")
print(monthly_quantity.to_string(index=False))




# STEP 56: Visualize Monthly Average Quantity per Invoice

# import matplotlib.pyplot as plt

# plt.figure(figsize=(12, 6))

# plt.plot(
#     monthly_quantity["Month"].astype(str),
#     monthly_quantity["AverageQuantityPerInvoice"],
#     marker="o"
# )

# plt.title("Monthly Average Quantity per Invoice")
# plt.xlabel("Month")
# plt.ylabel("Average Quantity per Invoice")
# plt.xticks(rotation=45)
# plt.grid(True, alpha=0.3)
# plt.tight_layout()
# plt.show()




# # STEP 57: Visualize Monthly Total Quantity

# import matplotlib.pyplot as plt

# plt.figure(figsize=(12, 6))

# plt.bar(
#     monthly_quantity["Month"].astype(str),
#     monthly_quantity["TotalQuantity"]
# )

# plt.title("Monthly Total Quantity")
# plt.xlabel("Month")
# plt.ylabel("Total Quantity")
# plt.xticks(rotation=45)
# plt.grid(axis="y", alpha=0.3)
# plt.tight_layout()
# plt.show()





# STEP 58: Visualize Monthly Total Quantity Trend

# import matplotlib.pyplot as plt

# plt.figure(figsize=(12, 6))

# plt.plot(
#     monthly_quantity["Month"].astype(str),
#     monthly_quantity["TotalQuantity"],
#     marker="o"
# )

# plt.title("Monthly Total Quantity Trend")
# plt.xlabel("Month")
# plt.ylabel("Total Quantity")
# plt.xticks(rotation=45)
# plt.grid(True, alpha=0.3)
# plt.tight_layout()
# plt.show()




# STEP 59: Calculate Monthly Average Unit Price

monthly_price = (
    df_clean
    .groupby(df_clean["InvoiceDate"].dt.to_period("M"))
    .agg(
        AverageUnitPrice=("UnitPrice", "mean"),
        TransactionRows=("InvoiceNo", "size")
    )
    .reset_index()
)

monthly_price = monthly_price.rename(
    columns={"InvoiceDate": "Month"}
)

print("\nSTEP 59: Monthly Average Unit Price")
print(monthly_price.to_string(index=False))



# STEP 60: Visualize Monthly Average Unit Price

# import matplotlib.pyplot as plt

# plt.figure(figsize=(12, 6))

# plt.plot(
#     monthly_price["Month"].astype(str),
#     monthly_price["AverageUnitPrice"],
#     marker="o"
# )

# plt.title("Monthly Average Unit Price")
# plt.xlabel("Month")
# plt.ylabel("Average Unit Price (£)")
# plt.xticks(rotation=45)
# plt.grid(True, alpha=0.3)
# plt.tight_layout()
# plt.show()



# STEP 61: Visualize Monthly Average Unit Price Using Bar Chart

# import matplotlib.pyplot as plt

# plt.figure(figsize=(12, 6))

# plt.bar(
#     monthly_price["Month"].astype(str),
#     monthly_price["AverageUnitPrice"]
# )

# plt.title("Monthly Average Unit Price")
# plt.xlabel("Month")
# plt.ylabel("Average Unit Price (£)")
# plt.xticks(rotation=45)
# plt.grid(axis="y", alpha=0.3)
# plt.tight_layout()
# plt.show()






# STEP 62: Monthly Unit Price Statistics

monthly_price_stats = (
    df_clean
    .groupby(df_clean["InvoiceDate"].dt.to_period("M"))
    .agg(
        MinimumPrice=("UnitPrice", "min"),
        MaximumPrice=("UnitPrice", "max"),
        MedianPrice=("UnitPrice", "median"),
        AveragePrice=("UnitPrice", "mean")
    )
    .reset_index()
)

monthly_price_stats = monthly_price_stats.rename(
    columns={"InvoiceDate": "Month"}
)

print("\nSTEP 62: Monthly Unit Price Statistics")
print(monthly_price_stats.to_string(index=False))





# STEP 63: Visualize Monthly Median Unit Price

# import matplotlib.pyplot as plt

# plt.figure(figsize=(12, 6))

# plt.plot(
#     monthly_price_stats["Month"].astype(str),
#     monthly_price_stats["MedianPrice"],
#     marker="o"
# )

# plt.title("Monthly Median Unit Price")
# plt.xlabel("Month")
# plt.ylabel("Median Unit Price (£)")
# plt.xticks(rotation=45)
# plt.grid(True, alpha=0.3)
# plt.tight_layout()
# plt.show()





# STEP 64: Calculate Monthly Unit Price Range

monthly_price_stats["PriceRange"] = (
    monthly_price_stats["MaximumPrice"]
    - monthly_price_stats["MinimumPrice"]
)

print("\nSTEP 64: Monthly Unit Price Range")

print(
    monthly_price_stats[
        ["Month", "MinimumPrice", "MaximumPrice", "PriceRange"]
    ].to_string(index=False)
)



# STEP 65: Visualize Monthly Unit Price Range

# import matplotlib.pyplot as plt

# plt.figure(figsize=(12, 6))

# plt.bar(
#     monthly_price_stats["Month"].astype(str),
#     monthly_price_stats["PriceRange"]
# )

# plt.title("Monthly Unit Price Range")
# plt.xlabel("Month")
# plt.ylabel("Price Range (£)")
# plt.xticks(rotation=45)
# plt.grid(axis="y", alpha=0.3)
# plt.tight_layout()
# plt.show()


# STEP 66: Investigate Highest Unit Price Transactions


print("STEP 66 STARTED")

highest_prices = (
    df_clean
    .sort_values("UnitPrice", ascending=False)
    [["InvoiceNo", "StockCode", "Description",
      "Quantity", "InvoiceDate", "UnitPrice", "CustomerID"]]
    .head(20)
)   

print(highest_prices.to_string(index=False))

print("STEP 66 COMPLETED")




# STEP 67: Investigate Manual Transactions

print("STEP 67 STARTED")

manual_transactions = df_clean[
    df_clean["Description"].str.contains(
        "Manual",
        case=False,
        na=False
    )
]

print("Total Manual Transactions:", len(manual_transactions))

print("\nManual Transaction Details:")

print(
    manual_transactions[
        ["InvoiceNo", "StockCode", "Description",
         "Quantity", "InvoiceDate", "UnitPrice", "CustomerID"]
    ].to_string(index=False)
)


# STEP 68: Manual Transactions Summary

print("STEP 68 STARTED")

manual_summary = manual_transactions.agg(
    TotalTransactions=("InvoiceNo", "count"),
    UniqueInvoices=("InvoiceNo", "nunique"),
    MinimumPrice=("UnitPrice", "min"),
    MaximumPrice=("UnitPrice", "max"),
    AveragePrice=("UnitPrice", "mean"),
    MedianPrice=("UnitPrice", "median"),
    TotalQuantity=("Quantity", "sum")
)

print(manual_summary)

print("\nSTEP 68 COMPLETED")



# STEP 69: Manual Transactions Price Distribution

print("STEP 69 STARTED")

print("\nManual Transaction Price Distribution:")

print(
    manual_transactions["UnitPrice"].describe()
)

print("\nTransactions Above £100:")

high_price_manual = manual_transactions[
    manual_transactions["UnitPrice"] > 100
]

print("Count:", len(high_price_manual))

print(
    high_price_manual[
        ["InvoiceNo", "Description", "Quantity",
         "UnitPrice", "InvoiceDate", "CustomerID"]
    ].to_string(index=False)
)

print("\nSTEP 69 COMPLETED")




# STEP 70: Manual Transactions Quantity Analysis

print("STEP 70 STARTED")

positive_manual = manual_transactions[
    manual_transactions["Quantity"] > 0
]

negative_manual = manual_transactions[
    manual_transactions["Quantity"] < 0
]

zero_manual = manual_transactions[
    manual_transactions["Quantity"] == 0
]

print("\nManual Transaction Quantity Summary:")

print("Positive Quantity Transactions:", len(positive_manual))
print("Negative Quantity Transactions:", len(negative_manual))
print("Zero Quantity Transactions:", len(zero_manual))

print("\nPositive Quantity LineAmount:",
      positive_manual["LineAmount"].sum())

print("Negative Quantity LineAmount:",
      negative_manual["LineAmount"].sum())

print("\nSTEP 70 COMPLETED")



# STEP 71: Monthly Manual Transaction Analysis

print("STEP 71 STARTED")

manual_transactions["Month"] = (
    manual_transactions["InvoiceDate"].dt.to_period("M")
)

monthly_manual = manual_transactions.groupby("Month").agg(
    TotalTransactions=("InvoiceNo", "count"),
    PositiveTransactions=("Quantity", lambda x: (x > 0).sum()),
    NegativeTransactions=("Quantity", lambda x: (x < 0).sum()),
    NetLineAmount=("LineAmount", "sum")
).reset_index()

print("\nMonthly Manual Transaction Summary:")

print(monthly_manual.to_string(index=False))

print("\nSTEP 71 COMPLETED")









# ============================================================
# PROJECT ECOM FIRST — FINAL ANALYSIS & REPORT
# ============================================================

import os
import pandas as pd
import matplotlib.pyplot as plt

print("\n" + "=" * 60)
print("PROJECT ECOM FIRST — FINAL ANALYSIS STARTED")
print("=" * 60)


# STEP 72: Create Safe Manual Transactions Copy

manual_final = manual_transactions.copy()

manual_final["Month"] = (
    manual_final["InvoiceDate"].dt.to_period("M")
)

print("\nSTEP 72 COMPLETED")


# STEP 73: Monthly Manual Transaction Analysis

monthly_manual_final = manual_final.groupby("Month").agg(
    TotalTransactions=("InvoiceNo", "count"),
    UniqueInvoices=("InvoiceNo", "nunique"),
    PositiveTransactions=("Quantity", lambda x: (x > 0).sum()),
    NegativeTransactions=("Quantity", lambda x: (x < 0).sum()),
    NetLineAmount=("LineAmount", "sum")
).reset_index()

print("\nSTEP 73: MONTHLY MANUAL ANALYSIS")
print(monthly_manual_final.to_string(index=False))


# STEP 74: Identify Highest and Lowest Manual Months

highest_manual_month = monthly_manual_final.loc[
    monthly_manual_final["NetLineAmount"].idxmax()
]

lowest_manual_month = monthly_manual_final.loc[
    monthly_manual_final["NetLineAmount"].idxmin()
]

print("\nSTEP 74: MONTHLY EXTREMES")

print(
    "Highest Net LineAmount Month:",
    highest_manual_month["Month"],
    "Amount:",
    round(highest_manual_month["NetLineAmount"], 2)
)

print(
    "Lowest Net LineAmount Month:",
    lowest_manual_month["Month"],
    "Amount:",
    round(lowest_manual_month["NetLineAmount"], 2)
)


# STEP 75: Manual Transactions Monthly Chart

# plt.figure(figsize=(13, 6))

# plt.bar(
#     monthly_manual_final["Month"].astype(str),
#     monthly_manual_final["NetLineAmount"]
# )

# plt.axhline(y=0, linewidth=1)

# plt.title("Monthly Net LineAmount — Manual Transactions")
# plt.xlabel("Month")
# plt.ylabel("Net LineAmount (£)")
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()

print("\nSTEP 75 COMPLETED")


# STEP 76: Overall Dataset KPIs

total_rows = len(df_clean)

unique_invoices = df_clean["InvoiceNo"].nunique()

unique_products = df_clean["StockCode"].nunique()

unique_countries = df_clean["Country"].nunique()

net_line_amount = df_clean["LineAmount"].sum()

negative_quantity_rows = (
    df_clean["Quantity"] < 0
).sum()

positive_quantity_rows = (
    df_clean["Quantity"] > 0
).sum()

cancelled_invoice_rows = (
    df_clean["InvoiceNo"].astype(str).str.startswith("C")
).sum()

missing_customer_ids = df_clean["CustomerID"].isna().sum()

print("\nSTEP 76: OVERALL DATASET KPIs")

print("Total Rows:", total_rows)
print("Unique Invoices:", unique_invoices)
print("Unique Products:", unique_products)
print("Unique Countries:", unique_countries)
print("Net LineAmount (£):", round(net_line_amount, 2))
print("Negative Quantity Rows:", negative_quantity_rows)
print("Positive Quantity Rows:", positive_quantity_rows)
print("Cancellation-like Invoice Rows:", cancelled_invoice_rows)
print("Missing Customer IDs:", missing_customer_ids)


# STEP 77: Monthly Overall Dataset Analysis

df_final = df_clean.copy()

df_final["Month"] = (
    df_final["InvoiceDate"].dt.to_period("M")
)

monthly_overall = df_final.groupby("Month").agg(
    TransactionRows=("InvoiceNo", "count"),
    UniqueInvoices=("InvoiceNo", "nunique"),
    UniqueProducts=("StockCode", "nunique"),
    NetLineAmount=("LineAmount", "sum")
).reset_index()

print("\nSTEP 77: MONTHLY OVERALL ANALYSIS")
print(monthly_overall.to_string(index=False))


# STEP 78: Country-Level Analysis

country_analysis = df_final.groupby("Country").agg(
    TransactionRows=("InvoiceNo", "count"),
    UniqueInvoices=("InvoiceNo", "nunique"),
    NetLineAmount=("LineAmount", "sum")
).reset_index()

country_analysis = country_analysis.sort_values(
    "NetLineAmount",
    ascending=False
)

print("\nSTEP 78: TOP 10 COUNTRIES BY NET LINE AMOUNT")

print(
    country_analysis.head(10).to_string(index=False)
)


# STEP 79: Top 10 Products by Net LineAmount

product_analysis = df_final.groupby(
    ["StockCode", "Description"]
).agg(
    TotalQuantity=("Quantity", "sum"),
    NetLineAmount=("LineAmount", "sum")
).reset_index()

product_analysis = product_analysis.sort_values(
    "NetLineAmount",
    ascending=False
)

print("\nSTEP 79: TOP 10 PRODUCTS BY NET LINE AMOUNT")

print(
    product_analysis.head(10).to_string(index=False)
)


# STEP 80: Create Final Output Folder

output_folder = "Ecom_First_Outputs"

os.makedirs(output_folder, exist_ok=True)

print("\nSTEP 80: EXPORTING PROJECT OUTPUTS")

df_clean.to_csv(
    os.path.join(output_folder, "cleaned_online_retail.csv"),
    index=False
)

monthly_manual_final.to_csv(
    os.path.join(output_folder, "monthly_manual_analysis.csv"),
    index=False
)

monthly_overall.to_csv(
    os.path.join(output_folder, "monthly_overall_analysis.csv"),
    index=False
)

country_analysis.to_csv(
    os.path.join(output_folder, "country_analysis.csv"),
    index=False
)

product_analysis.to_csv(
    os.path.join(output_folder, "product_analysis.csv"),
    index=False
)

print("Cleaned Dataset Exported")
print("Monthly Manual Analysis Exported")
print("Monthly Overall Analysis Exported")
print("Country Analysis Exported")
print("Product Analysis Exported")


# STEP 81: Final Project Completion Message

print("\n" + "=" * 60)
print("PROJECT ECOM FIRST — FINAL ANALYSIS COMPLETED")
print("=" * 60)

print("\nOutput Folder:", os.path.abspath(output_folder))

print("\nAll final analysis files have been exported.")

print("\nIMPORTANT:")
print("Net LineAmount is not confirmed revenue or profit.")
print("December 2011 contains only partial-month data.")
print("Negative transactions and adjustments require business context.")

print("\nPROJECT ECOM FIRST — DONE!")






# ============================================================
# PROJECT ECOM FIRST — FINAL INVESTIGATION
# STEPS 82–85
# ============================================================

import os
import pandas as pd
import matplotlib.pyplot as plt

print("\n" + "=" * 60)
print("FINAL INVESTIGATION STARTED")
print("=" * 60)


# STEP 82: Monthly Manual Analysis Without June

manual_final = manual_transactions.copy()

manual_final["Month"] = (
    manual_final["InvoiceDate"].dt.to_period("M")
)

monthly_manual_final = manual_final.groupby("Month").agg(
    TotalTransactions=("InvoiceNo", "count"),
    NetLineAmount=("LineAmount", "sum")
).reset_index()

monthly_manual_no_june = monthly_manual_final[
    monthly_manual_final["Month"].astype(str) != "2011-06"
]

# plt.figure(figsize=(13, 6))

# plt.bar(
#     monthly_manual_no_june["Month"].astype(str),
#     monthly_manual_no_june["NetLineAmount"]
# )

# plt.axhline(y=0, linewidth=1)

# plt.title("Monthly Manual Net LineAmount (June Excluded)")
# plt.xlabel("Month")
# plt.ylabel("Net LineAmount (£)")
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()

print("\nSTEP 82 COMPLETED")


# STEP 83: Investigate June 2011 Manual Transactions

june_manual = manual_final[
    manual_final["Month"].astype(str) == "2011-06"
].copy()

print("\nSTEP 83: JUNE 2011 INVESTIGATION")

print("June Transactions:", len(june_manual))

print(
    "June Net LineAmount:",
    round(june_manual["LineAmount"].sum(), 2)
)

print("\nJune Manual Transaction Details:")

print(
    june_manual[
        ["InvoiceNo", "Description", "Quantity",
         "UnitPrice", "LineAmount", "InvoiceDate", "CustomerID"]
    ].sort_values(
        "LineAmount"
    ).to_string(index=False)
)

print("\nSTEP 83 COMPLETED")


# STEP 84: Identify Largest Manual Transaction Impacts

manual_final["AbsoluteLineAmount"] = (
    manual_final["LineAmount"].abs()
)

top_manual_transactions = manual_final.sort_values(
    "AbsoluteLineAmount",
    ascending=False
).head(20)

print("\nSTEP 84: TOP 20 MANUAL TRANSACTIONS BY ABSOLUTE IMPACT")

print(
    top_manual_transactions[
        ["InvoiceNo", "Description", "Quantity",
         "UnitPrice", "LineAmount", "InvoiceDate", "CustomerID"]
    ].to_string(index=False)
)

print("\nSTEP 84 COMPLETED")


# STEP 85: Final Data Quality Checks and Export

print("\nSTEP 85: FINAL DATA QUALITY CHECKS")

print("Total cleaned rows:", len(df_clean))
print("Remaining exact duplicates:", df_clean.duplicated().sum())
print("Missing Customer IDs:", df_clean["CustomerID"].isna().sum())
print("Missing Descriptions:", df_clean["Description"].isna().sum())
print("Invalid Invoice Dates:", df_clean["InvoiceDate"].isna().sum())
print("Negative Quantity Rows:", (df_clean["Quantity"] < 0).sum())
print("Zero UnitPrice Rows:", (df_clean["UnitPrice"] == 0).sum())

output_folder = "Ecom_First_Outputs"

os.makedirs(output_folder, exist_ok=True)

monthly_manual_final.to_csv(
    os.path.join(output_folder, "monthly_manual_final.csv"),
    index=False
)

june_manual.to_csv(
    os.path.join(output_folder, "june_2011_manual_investigation.csv"),
    index=False
)

top_manual_transactions.to_csv(
    os.path.join(output_folder, "top_manual_transactions.csv"),
    index=False
)

print("\nFinal investigation files exported successfully.")

print("\n" + "=" * 60)
print("PROJECT ECOM FIRST — INVESTIGATION COMPLETED")
print("=" * 60)

print("Output Folder:", os.path.abspath(output_folder))







# PHASE 4 — BUSINESS INSIGHTS & STORYTELLING

# STEP 86: INVESTIGATE MAY 2011 MANUAL TRANSACTIONS

may_transactions = manual_final[
    manual_final["Month"] == "2011-05"
].copy()

print("\nSTEP 86: MAY 2011 INVESTIGATION")

print("\nTotal Manual Transactions:", len(may_transactions))

print(
    "Net LineAmount:",
    round(may_transactions["LineAmount"].sum(), 2)
)

print(
    "Positive Transactions:",
    (may_transactions["Quantity"] > 0).sum()
)

print(
    "Negative Transactions:",
    (may_transactions["Quantity"] < 0).sum()
)

print("\nMay Manual Transaction Details:")

may_transactions["AbsoluteImpact"] = (
    may_transactions["LineAmount"].abs()
)

may_details = may_transactions.sort_values(
    "AbsoluteImpact",
    ascending=False
)

print(
    may_details[
        [
            "InvoiceNo",
            "Description",
            "Quantity",
            "UnitPrice",
            "LineAmount",
            "InvoiceDate",
            "CustomerID"
        ]
    ].to_string(index=False)
)

print("\nSTEP 86 COMPLETED")










# STEP 87: INVESTIGATE CUSTOMER 12757

customer_12757 = may_transactions[
    (may_transactions["CustomerID"] == 12757) &
    (may_transactions["InvoiceDate"].dt.date ==
     pd.Timestamp("2011-05-23").date())
].copy()

customer_12757 = customer_12757.sort_values("InvoiceDate")

print("\nSTEP 87: CUSTOMER 12757 INVESTIGATION")

print("\nTotal Transactions:", len(customer_12757))

print(
    "Net LineAmount:",
    round(customer_12757["LineAmount"].sum(), 2)
)

print("\nTransaction Details:")

print(
    customer_12757[
        [
            "InvoiceNo",
            "Description",
            "Quantity",
            "UnitPrice",
            "LineAmount",
            "InvoiceDate",
            "CustomerID"
        ]
    ].to_string(index=False)
)

print("\nSTEP 87 COMPLETED")











# ============================================================
# PHASE 4 — BUSINESS INSIGHTS & STORYTELLING
# STEPS 88–95 — COMPLETE ANALYSIS
# ============================================================

import pandas as pd

print("\n" + "=" * 65)
print("PROJECT ECOM FIRST — PHASE 4")
print("BUSINESS INSIGHTS & STORYTELLING")
print("=" * 65)


# STEP 88: MAY MAJOR TRANSACTIONS

print("\nSTEP 88: MAY MAJOR TRANSACTIONS")

may_major = may_transactions.copy()
may_major["AbsoluteImpact"] = may_major["LineAmount"].abs()

may_top = may_major.sort_values(
    "AbsoluteImpact", ascending=False
).head(10)

print(may_top[
    ["InvoiceNo", "Description", "Quantity",
     "UnitPrice", "LineAmount", "CustomerID"]
].to_string(index=False))


# STEP 89: MAY VS JUNE COMPARISON


# STEP 89: MAY VS JUNE COMPARISON — FIXED

print("\nSTEP 89: MAY VS JUNE COMPARISON")

manual_final["Month"] = (
    manual_final["InvoiceDate"].dt.strftime("%Y-%m")
)

may_june = manual_final[
    manual_final["Month"].isin(["2011-05", "2011-06"])
].groupby("Month").agg(
    TotalTransactions=("InvoiceNo", "count"),
    PositiveTransactions=("Quantity", lambda x: (x > 0).sum()),
    NegativeTransactions=("Quantity", lambda x: (x < 0).sum()),
    NetLineAmount=("LineAmount", "sum")
).round(2)

print(may_june)

print("\nSTEP 89 COMPLETED")

print(may_june)


# STEP 90: MONTHLY BUSINESS TRENDS


# STEP 90: MONTHLY BUSINESS TRENDS

print("\nSTEP 90: MONTHLY BUSINESS TRENDS")

monthly_trends = monthly_overall.copy()

monthly_trends["NetLineAmount"] = (
    monthly_trends["NetLineAmount"].round(2)
)

print("\nHighest monthly Net LineAmount:")
print(
    monthly_trends.loc[
        monthly_trends["NetLineAmount"].idxmax()
    ].to_string()
)

print("\nLowest monthly Net LineAmount:")
print(
    monthly_trends.loc[
        monthly_trends["NetLineAmount"].idxmin()
    ].to_string()
)

print("\nMonthly overview:")
print(monthly_trends.to_string(index=False))

print("\nSTEP 90 COMPLETED")


# STEP 91: COUNTRY-WISE BUSINESS INSIGHTS

print("\nSTEP 91: COUNTRY-WISE BUSINESS INSIGHTS")

country_insights = country_analysis.sort_values(
    "NetLineAmount", ascending=False
)

print("\nTop 10 countries by Net LineAmount:")
print(country_insights.head(10).to_string(index=False))


# STEP 92: PRODUCT-WISE BUSINESS INSIGHTS

print("\nSTEP 92: PRODUCT-WISE BUSINESS INSIGHTS")

product_insights = product_analysis.sort_values(
    "NetLineAmount", ascending=False
)

print("\nTop 10 products by Net LineAmount:")
print(product_insights.head(10).to_string(index=False))


# STEP 93: KEY BUSINESS FINDINGS

print("\nSTEP 93: KEY BUSINESS FINDINGS")

print("Total cleaned rows:", len(df_clean))

print("Unique invoices:", df_clean["InvoiceNo"].nunique())

print("Unique products:", df_clean["StockCode"].nunique())

print("Unique countries:", df_clean["Country"].nunique())

print(
    "Overall Net LineAmount:",
    round(df_clean["LineAmount"].sum(), 2)
)

print(
    "Missing Customer IDs:",
    df_clean["CustomerID"].isna().sum()
)

print(
    "Negative quantity rows:",
    (df_clean["Quantity"] < 0).sum()
)

print(
    "Zero UnitPrice rows:",
    (df_clean["UnitPrice"] == 0).sum()
)


# STEP 94: BUSINESS RECOMMENDATIONS

print("\nSTEP 94: BUSINESS RECOMMENDATIONS")

recommendations = [
    "Investigate high-impact Manual transactions individually.",
    "Separate cancellation and adjustment records from ordinary sales analysis.",
    "Investigate missing CustomerID records before customer-level analysis.",
    "Monitor monthly transaction and product trends.",
    "Review country-wise business performance.",
    "Investigate high-value products and unusual price entries.",
    "Treat December 2011 as a partial month in monthly comparisons."
]

for number, recommendation in enumerate(recommendations, start=1):
    print(f"{number}. {recommendation}")


# STEP 95: EXPORT FINAL PHASE 4 REPORTS

print("\nSTEP 95: EXPORT FINAL PHASE 4 REPORTS")

monthly_trends.to_csv(
    "phase4_monthly_business_trends.csv", index=False
)

country_insights.to_csv(
    "phase4_country_business_insights.csv", index=False
)

product_insights.to_csv(
    "phase4_product_business_insights.csv", index=False
)

may_top.to_csv(
    "phase4_may_major_transactions.csv", index=False
)

may_june.to_csv(
    "phase4_may_june_comparison.csv"
)

print("\nPhase 4 report files exported successfully!")

print("\n" + "=" * 65)
print("PHASE 4 — BUSINESS INSIGHTS COMPLETED")
print("=" * 65)







