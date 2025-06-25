"""
Script para importar múltiples archivos JSON de scraping
Uso: python scripts/import_multiple_files.py data/
"""

import json
import sys
import os
import glob
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.api.repositories.lead_repository import LeadRepository


def import_multiple_json_files(directory_path: str, file_pattern: str = "*.json"):
    if not os.path.exists(directory_path):
        print(f"❌ Error: Directory {directory_path} not found")
        return
    
    json_files = glob.glob(os.path.join(directory_path, file_pattern))
    
    if not json_files:
        print(f"❌ No JSON files found in {directory_path}")
        return
    
    print(f"📁 Found {len(json_files)} JSON files:")
    for file in json_files:
        print(f"   📄 {os.path.basename(file)}")
    
    db: Session = SessionLocal()
    lead_repo = LeadRepository(db)
    
    total_imported = 0
    total_skipped = 0
    total_errors = 0
    
    try:
        for json_file in json_files:
            print(f"\n🔄 Processing {os.path.basename(json_file)}...")
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    leads_data = json.load(f)
                
                if not isinstance(leads_data, list):
                    print(f"⚠️  Skipping {json_file}: Not a list of leads")
                    continue
                
                file_imported = 0
                file_skipped = 0
                file_errors = 0
                
                for i, lead_data in enumerate(leads_data, 1):
                    try:
                        clean_data = clean_lead_data(lead_data)
                        
                        if not clean_data.get('company_name') or not clean_data.get('activity'):
                            file_errors += 1
                            continue
                        
                        if is_duplicate(lead_repo, clean_data):
                            file_skipped += 1
                            continue
                        
                        lead_repo.create(clean_data)
                        file_imported += 1
                        
                    except Exception as e:
                        file_errors += 1
                        continue
                
                print(f"   ✅ {file_imported} imported, 🔄 {file_skipped} skipped, ❌ {file_errors} errors")
                
                total_imported += file_imported
                total_skipped += file_skipped
                total_errors += file_errors
                
            except Exception as e:
                print(f"❌ Error processing {json_file}: {str(e)}")
                continue
    
    finally:
        db.close()
    
    print(f"\n📊 FINAL SUMMARY:")
    print(f"   ✅ Total imported: {total_imported}")
    print(f"   🔄 Total skipped: {total_skipped}")
    print(f"   ❌ Total errors: {total_errors}")
    print(f"   📁 Files processed: {len(json_files)}")


def clean_lead_data(lead_data: dict) -> dict:
    clean_data = {
        'company_name': str(lead_data.get('company_name', '')).strip(),
        'activity': str(lead_data.get('activity', '')).strip(),
        'email': lead_data.get('email'),
        'phone': lead_data.get('phone'),
        'company_website': lead_data.get('company_website') or lead_data.get('website'),
        'address': lead_data.get('address'),
        'state': lead_data.get('state') or lead_data.get('provincia'),
        'country': lead_data.get('country', 'España'),
        'description': lead_data.get('description'),
        'category': lead_data.get('category') or lead_data.get('sector'),
        'verified_email': validate_email(lead_data.get('email')),
        'verified_phone': validate_phone(lead_data.get('phone')),
        'verified_website': validate_website(lead_data.get('company_website') or lead_data.get('website'))
    }
    return {k: v for k, v in clean_data.items() if v is not None and str(v).strip() != ''}


def validate_email(email: str) -> bool:
    """Simple email validation"""
    if not email:
        return False
    return "@" in email and "." in email.split("@")[-1]


def validate_phone(phone: str) -> bool:
    if not phone:
        return False
    clean_phone = ''.join(filter(str.isdigit, str(phone)))
    return len(clean_phone) >= 9


def validate_website(website: str) -> bool:
    if not website:
        return False
    return any(website.startswith(p) for p in ["http://", "https://", "www."])


def is_duplicate(lead_repo: LeadRepository, clean_data: dict) -> bool:
    if clean_data.get('email'):
        existing = lead_repo.get_by_field('email', clean_data['email'])
        if existing:
            return True

    if clean_data.get('state'):
        similar_leads = lead_repo.search_leads(
            search_term=clean_data['company_name'],
            states=[clean_data['state']],
            limit=1
        )
        if similar_leads:
            return True
    
    return False


def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python scripts/import_multiple_files.py <directory_path>")
        print("Example: python scripts/import_multiple_files.py data/scraped/")
        sys.exit(1)
    
    directory_path = sys.argv[1]
    
    print("🚀 Starting bulk import process...")
    import_multiple_json_files(directory_path)
    print("🎉 Bulk import completed!")


if __name__ == "__main__":
    main()