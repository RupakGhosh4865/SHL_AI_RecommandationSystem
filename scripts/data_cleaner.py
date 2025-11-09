"""
Simple Data Cleaner - Guaranteed to work on Windows
No complex array handling, just straightforward cleaning
"""

import pandas as pd
import json
import re
import os
from datetime import datetime
from pathlib import Path

print("="*60)
print("Starting Data Cleaning Pipeline")
print("="*60)

# Load data
print("\n[1/10] Loading data...")
input_file = 'data/raw/shl_catalog_raw.json'

with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

df = pd.DataFrame(data)
print(f"[OK] Loaded {len(df)} records")

# Remove duplicates
print("\n[2/10] Removing duplicates...")
before = len(df)
df = df.drop_duplicates(subset=['name', 'url'], keep='first')
df = df.drop_duplicates(subset=['name'], keep='first')
after = len(df)
print(f"[OK] Removed {before - after} duplicates ({after} records remaining)")

# Clean text function
def clean_text(text):
    if pd.isna(text) or text is None:
        return ""
    text = str(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,;:()\-/&]', '', text)
    text = re.sub(r'\.{2,}', '.', text)
    return text.strip().lower()

# Clean all text columns
print("\n[3/10] Cleaning text fields...")
text_columns = ['name', 'description', 'category', 'test_type', 
               'duration', 'remote_testing', 'adaptive']

for col in text_columns:
    if col in df.columns:
        df[col] = df[col].apply(clean_text)
        print(f"  [OK] Cleaned: {col}")

# Clean skills column - SIMPLE VERSION THAT ALWAYS WORKS
print("\n[4/10] Cleaning skills column...")
if 'skills' in df.columns:
    # Convert everything to string first, then to list
    df['skills_temp'] = df['skills'].astype(str)
    
    def parse_skills_simple(skill_str):
        if skill_str == 'nan' or skill_str == '' or skill_str == '[]':
            return []
        try:
            # Try to evaluate if it looks like a list
            if skill_str.startswith('['):
                skills = eval(skill_str)
                if isinstance(skills, list):
                    return [clean_text(s) for s in skills if s]
        except:
            pass
        # If not a list, treat as single skill
        cleaned = clean_text(skill_str)
        return [cleaned] if cleaned else []
    
    df['skills'] = df['skills_temp'].apply(parse_skills_simple)
    df = df.drop('skills_temp', axis=1)
    print("[OK] Skills cleaned")

# Standardize categories
print("\n[5/10] Standardizing categories...")
category_mapping = {
    'ability & aptitude': 'Ability & Aptitude',
    'cognitive': 'Ability & Aptitude',
    'personality & behavior': 'Personality & Behavior',
    'personality': 'Personality & Behavior',
    'knowledge & skills': 'Knowledge & Skills',
    'technical': 'Knowledge & Skills',
    'simulations': 'Simulations',
    'simulation': 'Simulations',
    'biodata': 'Biodata & SJT',
    'sjt': 'Biodata & SJT'
}

if 'category' in df.columns:
    df['category_standardized'] = df['category'].apply(
        lambda x: category_mapping.get(x if x else '', 'Other')
    )
print("[OK] Categories standardized")

# Infer missing categories
print("\n[6/10] Inferring missing categories...")
def infer_category(row):
    if row.get('category_standardized') and row['category_standardized'] != 'Other':
        return row['category_standardized']
    
    combined = f"{row.get('test_type', '')} {row.get('description', '')} {row.get('name', '')}".lower()
    
    if any(word in combined for word in ['cognitive', 'ability', 'aptitude', 'reasoning', 'numerical', 'verbal']):
        return 'Ability & Aptitude'
    elif any(word in combined for word in ['personality', 'behavior', 'opq']):
        return 'Personality & Behavior'
    elif any(word in combined for word in ['simulation', 'exercise']):
        return 'Simulations'
    elif any(word in combined for word in ['knowledge', 'technical', 'skill', 'programming']):
        return 'Knowledge & Skills'
    elif any(word in combined for word in ['biodata', 'situational', 'judgment']):
        return 'Biodata & SJT'
    else:
        return 'Other'

df['category_final'] = df.apply(infer_category, axis=1)
print("[OK] Categories inferred")

# Extract duration
print("\n[7/10] Extracting duration values...")
def parse_duration(duration_str):
    if pd.isna(duration_str) or not duration_str:
        return None
    duration_str = str(duration_str).lower()
    
    minutes_match = re.search(r'(\d+)\s*(?:min|minute)', duration_str)
    if minutes_match:
        return int(minutes_match.group(1))
    
    hours_match = re.search(r'(\d+)\s*(?:hr|hour)', duration_str)
    if hours_match:
        return int(hours_match.group(1)) * 60
    
    number_match = re.search(r'(\d+)', duration_str)
    if number_match:
        num = int(number_match.group(1))
        return num if num < 300 else None
    
    return None

if 'duration' in df.columns:
    df['duration_minutes'] = df['duration'].apply(parse_duration)
print("[OK] Duration extracted")

# Create combined text
print("\n[8/10] Creating combined text field...")
def combine_fields(row):
    parts = []
    
    if row.get('name'):
        parts.append(f"Assessment: {row['name']}")
    if row.get('description') and len(row['description']) > 10:
        parts.append(f"Description: {row['description']}")
    if row.get('category_final'):
        parts.append(f"Category: {row['category_final']}")
    if row.get('test_type'):
        parts.append(f"Type: {row['test_type']}")
    if row.get('duration'):
        parts.append(f"Duration: {row['duration']}")
    if row.get('remote_testing'):
        parts.append(f"Remote Testing: {row['remote_testing']}")
    if row.get('adaptive'):
        parts.append(f"Adaptive: {row['adaptive']}")
    if row.get('skills') and isinstance(row['skills'], list) and len(row['skills']) > 0:
        skills_text = ", ".join([s for s in row['skills'] if s])
        if skills_text:
            parts.append(f"Skills Assessed: {skills_text}")
    
    return " | ".join(parts)

df['combined_text'] = df.apply(combine_fields, axis=1)
df['text_length'] = df['combined_text'].str.len()
df['word_count'] = df['combined_text'].str.split().str.len()
print("[OK] Combined text created")

# Add metadata
print("\n[9/10] Adding metadata features...")
if 'skills' in df.columns:
    df['skill_count'] = df['skills'].apply(lambda x: len(x) if isinstance(x, list) else 0)

df['has_description'] = df['description'].apply(lambda x: len(str(x)) > 20)

if 'adaptive' in df.columns:
    df['is_adaptive'] = df['adaptive'].apply(lambda x: 'yes' in str(x).lower())

if 'remote_testing' in df.columns:
    df['is_remote'] = df['remote_testing'].apply(lambda x: 'yes' in str(x).lower())

required_fields = ['name', 'description', 'category_final', 'test_type']
df['completeness_score'] = df[required_fields].notna().sum(axis=1) / len(required_fields)
print("[OK] Metadata added")

# Save results
print("\n[10/10] Saving cleaned data...")
Path('data/processed').mkdir(parents=True, exist_ok=True)

# Save CSV
csv_file = 'data/processed/shl_catalog_clean.csv'
df.to_csv(csv_file, index=False, encoding='utf-8')
print(f"[OK] Saved: {csv_file}")

# Save JSON
json_file = 'data/processed/shl_catalog_clean.json'
df.to_json(json_file, orient='records', indent=2, force_ascii=False)
print(f"[OK] Saved: {json_file}")

# Save embeddings file
embeddings_df = df[['name', 'combined_text', 'url', 'category_final']].copy()
embeddings_file = 'data/processed/shl_catalog_for_embeddings.csv'
embeddings_df.to_csv(embeddings_file, index=False, encoding='utf-8')
print(f"[OK] Saved: {embeddings_file}")

# Save statistics
stats = {
    'total_records': len(df),
    'processing_date': datetime.now().isoformat(),
    'categories': df['category_final'].value_counts().to_dict(),
    'avg_text_length': int(df['text_length'].mean()),
    'avg_word_count': int(df['word_count'].mean()),
    'completeness_avg': float(df['completeness_score'].mean())
}

stats_file = 'data/processed/data_summary.json'
with open(stats_file, 'w', encoding='utf-8') as f:
    json.dump(stats, f, indent=2)
print(f"[OK] Saved: {stats_file}")

# Print summary
print("\n" + "="*60)
print("DATA CLEANING COMPLETE!")
print("="*60)
print(f"Total records:        {len(df)}")
print(f"Average text length:  {int(df['text_length'].mean())} chars")
print(f"Average word count:   {int(df['word_count'].mean())} words")
print(f"\nCategory Distribution:")
print(df['category_final'].value_counts())
print(f"\nFiles saved to: data/processed/")
print("  - shl_catalog_clean.csv")
print("  - shl_catalog_clean.json")
print("  - shl_catalog_for_embeddings.csv")
print("  - data_summary.json")
print("="*60)