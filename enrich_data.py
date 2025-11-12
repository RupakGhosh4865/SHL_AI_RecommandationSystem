"""
Data Enrichment Script
Adds realistic descriptions and metadata to your existing data
"""

import pandas as pd
import json

# Load your current data
df = pd.read_csv('data/processed/shl_catalog_clean.csv')

# Enrichment data based on assessment names
enrichments = {
    "account manager solution": {
        "description": "Comprehensive assessment for account management roles, evaluating sales skills, relationship building, and client retention strategies.",
        "test_type": "Personality & Behavior",
        "duration": 45,
        "remote_support": "Yes",
        "adaptive": "No",
        "skills": ["client management", "sales", "communication", "negotiation"]
    },
    "administrative professional - short form": {
        "description": "Quick assessment for administrative professionals measuring organizational skills, attention to detail, and office management capabilities.",
        "test_type": "Knowledge & Skills",
        "duration": 20,
        "remote_support": "Yes",
        "adaptive": "No",
        "skills": ["organization", "data entry", "scheduling", "communication"]
    },
    "agency manager solution": {
        "description": "Assessment for agency management positions evaluating leadership, strategic planning, and team coordination abilities.",
        "test_type": "Management",
        "duration": 50,
        "remote_support": "Yes",
        "adaptive": "No",
        "skills": ["leadership", "planning", "team management", "decision making"]
    },
    "apprentice 8.0 job focused assessment": {
        "description": "Entry-level assessment for apprentice positions measuring foundational skills, learning aptitude, and workplace behaviors.",
        "test_type": "Competencies",
        "duration": 30,
        "remote_support": "Yes",
        "adaptive": "No",
        "skills": ["problem solving", "learning ability", "teamwork", "communication"]
    },
    "bank administrative assistant - short form": {
        "description": "Banking sector administrative assessment focusing on financial document handling, customer service, and regulatory compliance.",
        "test_type": "Knowledge & Skills",
        "duration": 25,
        "remote_support": "Yes",
        "adaptive": "No",
        "skills": ["banking operations", "customer service", "data accuracy", "compliance"]
    },
    "bank collections agent - short form": {
        "description": "Assessment for collections roles evaluating negotiation skills, persistence, communication, and debt recovery strategies.",
        "test_type": "Competencies",
        "duration": 30,
        "remote_support": "Yes",
        "adaptive": "No",
        "skills": ["negotiation", "communication", "persistence", "conflict resolution"]
    },
    "bank operations supervisor - short form": {
        "description": "Supervisory assessment for banking operations measuring leadership, process management, and regulatory knowledge.",
        "test_type": "Management",
        "duration": 40,
        "remote_support": "Yes",
        "adaptive": "No",
        "skills": ["supervision", "operations management", "compliance", "leadership"]
    },
    "bilingual spanish reservation agent solution": {
        "description": "Bilingual assessment for reservation agents testing Spanish language proficiency, customer service, and booking system knowledge.",
        "test_type": "Knowledge & Skills",
        "duration": 35,
        "remote_support": "Yes",
        "adaptive": "No",
        "skills": ["spanish", "customer service", "communication", "booking systems"]
    },
    "bookkeeping, accounting, auditing clerk short form": {
        "description": "Financial assessment evaluating bookkeeping principles, accounting software proficiency, and auditing fundamentals.",
        "test_type": "Knowledge & Skills",
        "duration": 30,
        "remote_support": "Yes",
        "adaptive": "No",
        "skills": ["bookkeeping", "accounting", "excel", "financial reporting"]
    },
    "branch manager - short form": {
        "description": "Branch management assessment measuring leadership, sales management, operational oversight, and customer service excellence.",
        "test_type": "Management",
        "duration": 45,
        "remote_support": "Yes",
        "adaptive": "No",
        "skills": ["leadership", "sales management", "operations", "customer service"]
    },
    "cashier solution": {
        "description": "Retail cashier assessment evaluating transaction accuracy, customer interaction, cash handling, and point-of-sale system proficiency.",
        "test_type": "Competencies",
        "duration": 20,
        "remote_support": "Yes",
        "adaptive": "No",
        "skills": ["cash handling", "customer service", "accuracy", "pos systems"]
    },
    "global skills development report": {
        "description": "Comprehensive skills assessment and development report evaluating global competencies and creating personalized development plans.",
        "test_type": "Knowledge & Skills",
        "duration": 60,
        "remote_support": "Yes",
        "adaptive": "Yes",
        "skills": ["skill assessment", "development planning", "competencies", "career growth"]
    },
    ".net framework 4.5": {
        "description": "Technical assessment measuring .NET Framework 4.5 proficiency including C#, ASP.NET, and framework libraries.",
        "test_type": "Knowledge & Skills",
        "duration": 40,
        "remote_support": "Yes",
        "adaptive": "No",
        "skills": [".net", "c#", "asp.net", "framework development"]
    },
    ".net mvc (new)": {
        "description": "Assessment testing Model-View-Controller pattern implementation in .NET including routing, controllers, and views.",
        "test_type": "Knowledge & Skills",
        "duration": 35,
        "remote_support": "Yes",
        "adaptive": "No",
        "skills": ["mvc", ".net", "web development", "architecture patterns"]
    },
    ".net mvvm (new)": {
        "description": "Evaluation of Model-View-ViewModel pattern expertise for XAML-based applications and data binding.",
        "test_type": "Knowledge & Skills",
        "duration": 35,
        "remote_support": "Yes",
        "adaptive": "No",
        "skills": ["mvvm", ".net", "xaml", "wpf", "data binding"]
    },
    ".net wcf (new)": {
        "description": "Windows Communication Foundation assessment measuring service-oriented architecture and distributed systems development.",
        "test_type": "Knowledge & Skills",
        "duration": 40,
        "remote_support": "Yes",
        "adaptive": "No",
        "skills": ["wcf", "web services", "soa", ".net"]
    },
    ".net wpf (new)": {
        "description": "Windows Presentation Foundation assessment evaluating desktop application development with XAML and rich UI capabilities.",
        "test_type": "Knowledge & Skills",
        "duration": 40,
        "remote_support": "Yes",
        "adaptive": "No",
        "skills": ["wpf", "xaml", ".net", "desktop development"]
    },
    ".net xaml (new)": {
        "description": "XAML proficiency assessment measuring UI design, data binding, and declarative programming in .NET applications.",
        "test_type": "Knowledge & Skills",
        "duration": 30,
        "remote_support": "Yes",
        "adaptive": "No",
        "skills": ["xaml", "ui design", ".net", "data binding"]
    },
    "accounts payable (new)": {
        "description": "Accounts payable assessment evaluating invoice processing, vendor management, payment processing, and AP best practices.",
        "test_type": "Knowledge & Skills",
        "duration": 30,
        "remote_support": "Yes",
        "adaptive": "No",
        "skills": ["accounts payable", "invoice processing", "vendor management", "accounting"]
    },
    "accounts payable simulation (new)": {
        "description": "Interactive simulation of accounts payable scenarios including invoice matching, approval workflows, and payment scheduling.",
        "test_type": "Simulations",
        "duration": 45,
        "remote_support": "Yes",
        "adaptive": "No",
        "skills": ["accounts payable", "simulation", "workflow management", "problem solving"]
    },
    "accounts receivable (new)": {
        "description": "Accounts receivable assessment measuring collections, credit management, customer billing, and AR reconciliation skills.",
        "test_type": "Knowledge & Skills",
        "duration": 30,
        "remote_support": "Yes",
        "adaptive": "No",
        "skills": ["accounts receivable", "collections", "billing", "credit management"]
    },
    "accounts receivable simulation (new)": {
        "description": "Practical simulation of AR processes including customer communications, aging reports, and payment application scenarios.",
        "test_type": "Simulations",
        "duration": 45,
        "remote_support": "Yes",
        "adaptive": "No",
        "skills": ["accounts receivable", "simulation", "customer communication", "reconciliation"]
    },
    "ado.net (new)": {
        "description": "ADO.NET assessment testing data access proficiency including DataSets, DataReaders, connection management, and database operations.",
        "test_type": "Knowledge & Skills",
        "duration": 35,
        "remote_support": "Yes",
        "adaptive": "No",
        "skills": ["ado.net", "database", "data access", ".net"]
    }
}

# Apply enrichments
for idx, row in df.iterrows():
    name = row['name'].lower().strip()
    
    if name in enrichments:
        enrichment = enrichments[name]
        df.at[idx, 'description'] = enrichment['description']
        df.at[idx, 'test_type'] = enrichment['test_type']
        df.at[idx, 'duration'] = enrichment['duration']
        df.at[idx, 'duration_minutes'] = enrichment['duration']
        df.at[idx, 'remote_testing'] = enrichment['remote_support']
        df.at[idx, 'adaptive'] = enrichment['adaptive']
        df.at[idx, 'skills'] = str(enrichment['skills'])
        df.at[idx, 'category_final'] = enrichment['test_type']
        df.at[idx, 'has_description'] = True
        df.at[idx, 'skill_count'] = len(enrichment['skills'])
        
        # Update combined_text
        combined = f"Assessment: {row['name']} | "
        combined += f"Description: {enrichment['description']} | "
        combined += f"Category: {enrichment['test_type']} | "
        combined += f"Duration: {enrichment['duration']} minutes | "
        combined += f"Skills: {', '.join(enrichment['skills'])}"
        
        df.at[idx, 'combined_text'] = combined
        df.at[idx, 'text_length'] = len(combined)
        df.at[idx, 'word_count'] = len(combined.split())

# Save enriched data
df.to_csv('data/processed/shl_catalog_enriched.csv', index=False)
df.to_json('data/processed/shl_catalog_enriched.json', orient='records', indent=2)

print("="*70)
print("✅ Data Enrichment Complete!")
print("="*70)
print(f"Total assessments: {len(df)}")
print(f"Enriched with descriptions: {df['has_description'].sum()}")
print(f"\nSaved to:")
print("  - data/processed/shl_catalog_enriched.csv")
print("  - data/processed/shl_catalog_enriched.json")
print("\n📝 Next step: Update DATA_PATH in api/config.py to use enriched file")
print("="*70)