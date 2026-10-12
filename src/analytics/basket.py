"""
Market Basket Analysis and Product Affinity engine for Flux.
Uses mlxtend (FP-Growth / Apriori) with high performance and memory efficiency.
"""

from typing import Tuple, Optional, List, Dict, Any
import pandas as pd
import numpy as np
from mlxtend.frequent_patterns import fpgrowth, apriori, association_rules

from src.config import DEFAULT_MIN_SUPPORT, DEFAULT_MIN_CONFIDENCE, DEFAULT_MIN_LIFT

# Common non-product codes to filter out of affinity analysis
EXCLUDED_STOCK_CODES = {"POST", "D", "DOT", "AMAZONFEE", "CR", "M", "S", "BANK CHARGES", "PADS"}

def build_basket_matrix(
    sales_df: pd.DataFrame,
    min_product_frequency: int = 15,
) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    Constructs a binary transaction-item indicator matrix for valid sales invoices.

    Returns:
        basket_matrix: Binary DataFrame (invoices as rows, product descriptions as columns)
        item_code_map: Dictionary mapping stock_code to canonical description
    """
    # Exclude non-product administrative records
    df = sales_df[~sales_df["stock_code"].isin(EXCLUDED_STOCK_CODES)].copy()
    df = df[df["description"].notnull() & (df["description"].str.strip() != "")]

    # Map product descriptions (use the most frequent description per stock code)
    code_desc_map = (
        df.groupby("stock_code")["description"]
        .agg(lambda s: s.mode().iloc[0] if not s.mode().empty else s.iloc[0])
        .to_dict()
    )

    # Filter out rarely purchased products to optimize basket computation
    product_counts = df.groupby("description")["invoice_no"].nunique()
    popular_products = product_counts[product_counts >= min_product_frequency].index

    filtered_df = df[df["description"].isin(popular_products)]

    # Pivot to binary one-hot representation
    basket = (
        filtered_df.groupby(["invoice_no", "description"])["quantity"]
        .sum()
        .unstack(fill_value=0)
    )
    basket_matrix = (basket > 0).astype(bool)

    return basket_matrix, code_desc_map

def run_basket_analysis(
    basket_matrix: pd.DataFrame,
    min_support: float = DEFAULT_MIN_SUPPORT,
    min_confidence: float = DEFAULT_MIN_CONFIDENCE,
    min_lift: float = DEFAULT_MIN_LIFT,
    use_fpgrowth: bool = True,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Computes frequent itemsets and association rules using FP-Growth or Apriori.

    Returns:
        frequent_itemsets: DataFrame with itemsets and support
        rules: DataFrame with antecedents, consequents, support, confidence, lift
    """
    if basket_matrix.empty:
        return pd.DataFrame(), pd.DataFrame()

    # Generate frequent itemsets
    algo_func = fpgrowth if use_fpgrowth else apriori
    itemsets = algo_func(basket_matrix, min_support=min_support, use_colnames=True)

    if itemsets.empty:
        return pd.DataFrame(), pd.DataFrame()

    itemsets["length"] = itemsets["itemsets"].apply(len)

    # Generate association rules
    try:
        rules = association_rules(
            itemsets,
            metric="confidence",
            min_threshold=min_confidence,
        )
    except Exception:
        return itemsets, pd.DataFrame()

    if rules.empty:
        return itemsets, pd.DataFrame()

    # Filter by minimum lift
    rules = rules[rules["lift"] >= min_lift].copy()

    if rules.empty:
        return itemsets, pd.DataFrame()

    # Convert frozensets to readable comma-separated strings
    rules["antecedent_str"] = rules["antecedents"].apply(lambda s: ", ".join(list(s)))
    rules["consequent_str"] = rules["consequents"].apply(lambda s: ", ".join(list(s)))
    rules["support"] = rules["support"].round(4)
    rules["confidence"] = rules["confidence"].round(4)
    rules["lift"] = rules["lift"].round(2)
    rules["leverage"] = rules["leverage"].round(4)

    # Sort by lift descending
    rules = rules.sort_values(by="lift", ascending=False).reset_index(drop=True)

    return itemsets, rules

def get_recommendations_for_product(
    product_name: str,
    rules: pd.DataFrame,
    top_n: int = 5,
) -> pd.DataFrame:
    """
    Extracts high-affinity cross-selling recommendations for a selected product.
    """
    if rules.empty or not product_name:
        return pd.DataFrame()

    # Match rules where product_name is in the antecedent
    matched = rules[
        rules["antecedent_str"].str.contains(product_name, regex=False, case=False)
    ].copy()

    if matched.empty:
        # Fallback to reverse association
        matched = rules[
            rules["consequent_str"].str.contains(product_name, regex=False, case=False)
        ].copy()

    if matched.empty:
        return pd.DataFrame()

    return matched.sort_values(by="lift", ascending=False).head(top_n).reset_index(drop=True)
