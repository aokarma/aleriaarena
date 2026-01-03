import pandas as pd
import json
import re
from pathlib import Path

def remove_empty_columns(df):
    """Usuwa całkowicie puste kolumny"""
    return df.dropna(axis=1, how='all')

def process_description_json(desc):
    """
    Przetwarza opis oferty z formatu JSON na format kompatybilny z Prestashop.
    Ekstrahuje tekst ze sekcji i formatuje jako zwykły tekst HTML.
    """
    if pd.isna(desc):
        return ""
    
    try:
        # Jeśli jest to string, spróbuj sparsować jako JSON
        if isinstance(desc, str):
            data = json.loads(desc)
        else:
            data = desc
        
        # Jeśli jest to lista sekcji (typowy format Allegro)
        if isinstance(data, list):
            sections = data
        elif isinstance(data, dict) and 'sections' in data:
            sections = data['sections']
        else:
            return str(desc)
        
        # Ekstrakcja tekstu
        texts = []
        for section in sections:
            if isinstance(section, dict):
                if 'content' in section:
                    texts.append(section['content'])
                elif 'text' in section:
                    texts.append(section['text'])
            elif isinstance(section, str):
                texts.append(section)
        
        # Połączenie tekstów z separatorem
        result = "<br />\n".join([str(t).strip() for t in texts if t])
        return result
    
    except (json.JSONDecodeError, TypeError):
        # Jeśli nie jest JSON, zwróć oryginalną wartość
        return str(desc)

def split_subcategories(subcategory):
    """
    Dzieli podkategorię po znaku '>' na osobne elementy
    Zwraca dict z kluczami 'Podkategoria_1', 'Podkategoria_2', itd.
    """
    result = {}
    
    if pd.isna(subcategory):
        return result
    
    # Podziel po znaku '>'
    parts = [part.strip() for part in str(subcategory).split('>')]
    
    # Utwórz nowe kolumny
    for i, part in enumerate(parts, 1):
        col_name = f'Podkategoria_{i}'
        result[col_name] = part
    
    return result

def clean_last_subcategory(text):
    """Usuwa nawiasy i cyfry z ostatniej podkategorii"""
    if pd.isna(text):
        return text
    
    # Usuń wszystko w nawiasach (zarówno () jak i [])
    text = re.sub(r'[\(\[].*?[\)\]]', '', str(text))
    # Usuń cyfry na końcu
    text = re.sub(r'\d+\s*$', '', text)
    # Usuń zbędne spacje
    text = text.strip()
    
    return text

def process_allegro_excel(input_file, output_file=None):
    """
    Główna funkcja przetwarzająca plik Excel z ofertami Allegro
    
    Args:
        input_file: Ścieżka do pliku wejściowego (xlsx)
        output_file: Ścieżka do pliku wyjściowego (jeśli None, nazwa będzie input_file_processed.xlsx)
    """
    
    # Odczytaj plik Excel
    print(f"📂 Czytam plik: {input_file}")
    df = pd.read_excel(input_file)
    print(f"✓ Wczytano {len(df)} wierszy i {len(df.columns)} kolumn")
    
    # 1. Usuń puste kolumny
    print("\n🗑️  Usuwam puste kolumny...")
    initial_cols = len(df.columns)
    df = remove_empty_columns(df)
    removed = initial_cols - len(df.columns)
    print(f"✓ Usunięto {removed} pustych kolumn")
    
    # 2. Przetwórz opisy ofert (kolumna "Opis oferty")
    if 'Opis oferty' in df.columns:
        print("\n📝 Przetwarzam opisy ofert (JSON → Prestashop)...")
        df['Opis oferty'] = df['Opis oferty'].apply(process_description_json)
        print("✓ Opisy przetworzono")
    
    # 3. Podziel podkategorię
    if 'Podkategoria' in df.columns:
        print("\n📂 Dzielę podkategorię...")
        subcategory_dfs = df['Podkategoria'].apply(split_subcategories).apply(pd.Series)
        
        # Połącz z głównym dataframe
        df = pd.concat([df, subcategory_dfs], axis=1)
        print(f"✓ Utworzono {len(subcategory_dfs.columns)} nowych kolumn podkategorii")
        
        # 4. Oczyść ostatnią kolumnę podkategorii
        last_subcat_col = None
        for col in sorted(df.columns):
            if col.startswith('Podkategoria_'):
                last_subcat_col = col
        
        if last_subcat_col:
            print(f"\n🧹 Czyszczę ostatnią podkategorię ({last_subcat_col})...")
            df[last_subcat_col] = df[last_subcat_col].apply(clean_last_subcategory)
            print("✓ Ostatnia podkategoria wyczyszczona")
    
    # Zapisz plik wyjściowy
    if output_file is None:
        output_file = input_file.replace('.xlsx', '_processed.xlsx')
    
    print(f"\n💾 Zapisuję plik: {output_file}")
    df.to_excel(output_file, index=False, engine='openpyxl')
    print(f"✓ Plik zapisany pomyślnie!")
    print(f"   Ostateczna liczba kolumn: {len(df.columns)}")
    
    return df

if __name__ == "__main__":
    # Użycie
    input_file = "data/offers_2026-01-03.xlsm"  # Zmień na swoją nazwę pliku
    
    # Sprawdź czy plik istnieje
    if not Path(input_file).exists():
        print(f"❌ Plik '{input_file}' nie znaleziony!")
        print("\nUżycie:")
        print("  process_allegro_excel('nazwa_twojego_pliku.xlsx')")
    else:
        df = process_allegro_excel(input_file)
        print("\n" + "="*50)
        print("Podgląd pierwszych wierszy:")
        print("="*50)
        print(df.head())
