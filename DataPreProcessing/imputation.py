def regression_imputation(df, missing_col, group_cols):
    """
    Imputes a missing numerical column using a hierarchical/multi-stage approach.

    It imputes in the following order:
    1. By the mean of the first group (e.g., 'movieId')
    2. By the mean of the second group (e.g., 'userId')
    3. By the global mean of the entire column

    Parameters:
    df (pd.DataFrame): The DataFrame to impute.
    missing_col (str): The name of the column with missing values (e.g., 'rating').
    group_cols (list): A list of 2 column names to group by, in order of priority 
                         (e.g., ['movieId', 'userId']).

    Returns:
    pd.DataFrame: A new DataFrame with the missing values imputed.
    """
    
    # Create a copy to avoid modifying the original DataFrame
    df_imputed = df.copy()
    
    print(f"--- Starting hierarchical imputation for '{missing_col}' ---")
    original_nans = df_imputed[missing_col].isna().sum()
    print(f"Missing values BEFORE imputation: {original_nans}")

    if original_nans == 0:
        print("No missing values to impute.")
        return df_imputed

    # --- STEP 1: Impute with First Group (e.g., 'movieId') ---
    group1_col = group_cols[0]
    print(f"\nStep 1: Calculating {group1_col} level average...")
    group1_means = df_imputed.groupby(group1_col)[missing_col].transform('mean')
    df_imputed[missing_col] = df_imputed[missing_col].fillna(group1_means)
    
    nans_after_step1 = df_imputed[missing_col].isna().sum()
    print(f"Missing values after Step 1 ({group1_col}): {nans_after_step1}")

    # --- STEP 2: Impute remaining with Second Group (e.g., 'userId') ---
    if nans_after_step1 > 0:
        group2_col = group_cols[1]
        print(f"\nStep 2: Calculating {group2_col} level average...")
        group2_means = df_imputed.groupby(group2_col)[missing_col].transform('mean')
        df_imputed[missing_col] = df_imputed[missing_col].fillna(group2_means)
        
        nans_after_step2 = df_imputed[missing_col].isna().sum()
        print(f"Missing values after Step 2 ({group2_col}): {nans_after_step2}")
    
        # --- STEP 3: Impute remaining with Global Average ---
        if nans_after_step2 > 0:
            print("\nStep 3: Calculating global average...")
            global_mean = df_imputed[missing_col].mean()
            df_imputed[missing_col] = df_imputed[missing_col].fillna(global_mean)
            print(f"Missing values after Step 3 (Global): {df_imputed[missing_col].isna().sum()}")

    # --- 4. Final Check ---
    final_nans = df_imputed[missing_col].isna().sum()
    print("\n--- Imputation Complete ---")
    print(f"Original missing: {original_nans}")
    print(f"Final missing:    {final_nans}")
    
    return df_imputed