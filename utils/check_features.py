import joblib

# Load features
features = joblib.load('feature_names.joblib')
model = joblib.load('stacking_model.joblib')

# Get first 67 features (what model uses)
model_features = features[:model.n_features_in_]

print("=" * 80)
print("FEATURES THE MODEL WAS TRAINED ON (67 total):")
print("=" * 80)

# Group by category
categorical = []
numerical = []

for feat in model_features:
    if '_' in feat and not feat.endswith('_years') and not feat.endswith('_sec') and not feat.endswith('_score') and not feat.endswith('_count') and not feat.endswith('_code'):
        categorical.append(feat)
    else:
        numerical.append(feat)

print(f"\nNUMERICAL FEATURES ({len(numerical)}):")
for feat in numerical:
    print(f"  - {feat}")

print(f"\nCATEGORICAL FEATURES (one-hot encoded) ({len(categorical)}):")

# Group by base feature
from collections import defaultdict
grouped = defaultdict(list)
for feat in categorical:
    base = feat.rsplit('_', 1)[0]
    grouped[base].append(feat)

for base, feats in sorted(grouped.items()):
    print(f"\n  {base}:")
    for feat in feats:
        suffix = feat.split('_')[-1]
        print(f"    - {suffix}")
