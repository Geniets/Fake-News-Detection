import joblib
import json

# Load feature names
features = joblib.load('feature_names.joblib')
print(f'Number of features in feature_names.joblib: {len(features)}')

# Load model
model = joblib.load('stacking_model.joblib')
print(f'Model expects: {model.n_features_in_} features')

# Load metadata
with open('model_metadata.json', 'r') as f:
    metadata = json.load(f)
print(f'Metadata says: {metadata["num_features"]} features')

print(f'\nFeature mismatch detected!')
print(f'\nFirst 10 features: {features[:10]}')
print(f'\nLast 10 features: {features[-10:]}')
