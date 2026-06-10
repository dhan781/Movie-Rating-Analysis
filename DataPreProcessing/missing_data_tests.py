import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# For statistical tests
from scipy import stats
from statsmodels.tools.tools import add_constant
from statsmodels.discrete.discrete_model import Logit

np.random.seed(42)

print("Libraries imported successfully!")

def littles_mcar_test(df, numeric_cols=None):
    """
    Implementation of Little's MCAR test

    Parameters:
    df (pandas.DataFrame): DataFrame with missing values
    numeric_cols (list): List of numeric columns to include in the test

    Returns:
    tuple: (test statistic, p-value, degrees of freedom)
    """
    if numeric_cols is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    # Get only numeric columns
    df_numeric = df[numeric_cols]

    # Get mean and covariance of the data
    means = df_numeric.mean()
    cov_matrix = df_numeric.cov()

    # Create missing data patterns
    missing_patterns = df_numeric.isnull().astype(int)
    pattern_groups = missing_patterns.groupby(numeric_cols).groups
    print(missing_patterns)
    print(pattern_groups)
    # Calculate test statistic
    d2 = 0
    df_test = 0

    for pattern, indices in pattern_groups.items():
        # Get observed columns for this pattern
        observed_cols = [col for col, missing in zip(numeric_cols, pattern) if missing == 0]
        if not observed_cols:  # Skip if all values are missing
            continue

        # Get data for this pattern
        pattern_data = df_numeric.loc[indices, observed_cols]
        n_pattern = len(pattern_data)

        # Calculate mean for this pattern
        pattern_means = pattern_data.mean()

        # Get subset of overall means and covariance for observed columns
        means_subset = means[observed_cols]
        cov_subset = cov_matrix.loc[observed_cols, observed_cols]

        # Calculate Mahalanobis distance
        mean_diff = pattern_means - means_subset
        try:
            cov_inv = np.linalg.inv(cov_subset)
            d2 += n_pattern * mean_diff.dot(cov_inv).dot(mean_diff)
            df_test += len(observed_cols)
        except np.linalg.LinAlgError:
            # Skip if covariance matrix is singular
            continue

    # Calculate p-value
    p_value = 1 - stats.chi2.cdf(d2, df_test)

    return d2, p_value, df_test



def logistic_regression_test(df, var_with_missing, predictors):
    """
    Test if missingness can be predicted by observed variables using logistic regression

    Parameters:
    df (pandas.DataFrame): DataFrame with missing values
    var_with_missing (str): Column name with missing values
    predictors (list): List of predictor variables

    Returns:
    tuple: (model summary, significant predictors)
    """
    # Create missingness indicator for the variable we are testing (e.g., 'rating')
    df['missing_indicator'] = df[var_with_missing].isnull().astype(int)

    # Prepare data for logistic regression
    X = df[predictors].copy()
    y = df['missing_indicator']

    # --- START FIX ---
    # The Logit model fails if PREDICTORS (X) have missing data.
    # We must drop rows where 'year' (or other predictors) are NaN.

    # Convert categorical variables to dummy variables (if any)
    categorical_cols = X.select_dtypes(include=['object']).columns.tolist()
    if categorical_cols:
        X = pd.get_dummies(X, columns=categorical_cols, drop_first=True)

    # Get a list of all final predictor columns
    all_predictor_cols = X.columns.tolist()

    # Combine X and y to drop NaNs safely while keeping them aligned
    temp_df = pd.concat([X, y], axis=1)
    
    # Drop rows where any of the PREDICTORS are missing
    # This is the key step that removes rows with a NaN 'year'
    temp_df = temp_df.dropna(subset=all_predictor_cols) 

    # Re-separate X and y, now free of NaNs in X
    y = temp_df['missing_indicator']
    X = temp_df[all_predictor_cols]
    # --- END FIX ---

    # Add constant
    X = add_constant(X)
    
    # Check if X is empty after dropping NaNs
    if X.empty:
        print("Error: No data left after dropping NaNs from predictors.")
        return None, []

    # Fit logistic regression model
    model = Logit(y, X).fit(disp=0)

    # Get significant predictors (p < 0.05)
    significant_predictors = model.pvalues[model.pvalues < 0.05].index.tolist()
    if 'const' in significant_predictors:
        significant_predictors.remove('const')
    
    return model.summary(), significant_predictors