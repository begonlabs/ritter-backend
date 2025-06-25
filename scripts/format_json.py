"""
Script para convertir JSONs de scraping al formato esperado por la API
Uso: uv run scripts/format_json.py input.json output.json
"""

import json
import sys
import os
from pathlib import Path
import polars as pl


def clean_company_name(nombre: str) -> str:
    if not nombre or nombre == "N/A":
        return nombre
    return nombre.split('\n')[0].strip()


def clean_website(website: str) -> str:
    if not website or website == "N/A":
        return None
    if '?' in website:
        return website.split('?')[0]
    return website


def extract_state_from_address(direccion: str) -> str:
    if not direccion or direccion == "N/A":
        return "N/A"
    
    parts = direccion.split(', ')
    if len(parts) >= 3:
        city = parts[-1].strip()
        provincias = [
            'Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Zaragoza',
            'Málaga', 'Murcia', 'Palma', 'Las Palmas', 'Bilbao',
            'Alicante', 'Córdoba', 'Valladolid', 'Vigo', 'Gijón',
            'Alcorcón', 'Getafe', 'Móstoles', 'Fuenlabrada', 'Leganés'
        ]
        for provincia in provincias:
            if provincia.lower() in city.lower():
                return provincia
        return city
    return "N/A"


def convert_json_format(input_file: str, output_file: str):
    with open(input_file, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    df = pl.DataFrame(original_data)
    converted_data = []
    
    for row in df.iter_rows(named=True):
        company_name = clean_company_name(row.get('nombre', 'N/A'))
        clean_web = clean_website(row.get('website', 'N/A'))
        state = extract_state_from_address(row.get('direccion', 'N/A'))
        
        converted_lead = {
            "company_name": company_name,
            "activity": row.get('actividades', 'N/A'),
            "description": row.get('descripcion', 'N/A'),
            "email": "N/A",
            "phone": row.get('telefono', 'N/A'),
            "company_website": clean_web,
            "address": row.get('direccion', 'N/A'),
            "state": state,
            "country": "España",
            "category": row.get('actividades', 'N/A'),
            "source_url": row.get('url', 'N/A'),
            "verified_email": False,
            "verified_phone": True if row.get('telefono') and row.get('telefono') != 'N/A' else False,
            "verified_website": True if clean_web else False
        }
        
        if converted_lead["company_website"] in [None, "N/A"]:
            del converted_lead["company_website"]
        if converted_lead["email"] == "N/A":
            del converted_lead["email"]
        if converted_lead["phone"] == "N/A":
            del converted_lead["phone"]
        if converted_lead["description"] == "N/A":
            del converted_lead["description"]
        
        converted_data.append(converted_lead)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(converted_data, f, indent=2, ensure_ascii=False)


def convert_multiple_files(input_directory: str, output_directory: str):
    input_path = Path(input_directory)
    output_path = Path(output_directory)
    output_path.mkdir(parents=True, exist_ok=True)
    
    json_files = list(input_path.glob("*.json"))
    
    for json_file in json_files:
        output_file = output_path / f"converted_{json_file.name}"
        convert_json_format(str(json_file), str(output_file))


def main():
    if len(sys.argv) < 3:
        print("Uso:")
        print("  Archivo único: uv run scripts/format_json.py input.json output.json")
        print("  Múltiples archivos: uv run scripts/format_json.py input_dir/ output_dir/")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    if os.path.isdir(input_path):
        convert_multiple_files(input_path, output_path)
    else:
        convert_json_format(input_path, output_path)


if __name__ == "__main__":
    main()