"""
Script pour remplir la base de données avec des lieux administratifs
Tunisiens (Poste, Banque, Municipalité, etc.)
"""

from database import SessionLocal
from sqlalchemy import text

def populate_database():
    """Remplir la BD avec des lieux administratifs tunisiens"""
    
    db = SessionLocal()
    
    print("🔧 REMPLISSAGE DE LA BASE DE DONNÉES")
    print("="*70 + "\n")
    
    # 🔹 Lieux à SFAX
    sfax_places = [
        ("La Poste Centrale Sfax", "poste", "Avenue Habib Bourguiba, Sfax", "Sfax", 34.7406, 10.7603, "74 211 777", "Lun-Ven: 8h-17h, Sam: 8h-13h"),
        ("Poste Sfax El Ain", "poste", "Route El Ain Km 2.5, Sfax", "Sfax", 34.7520, 10.7410, "74 240 500", "Lun-Ven: 8h-16h"),
        
        ("Banque de Tunisie Sfax", "banque", "Avenue Majida Boulila, Sfax", "Sfax", 34.7415, 10.7595, "74 227 300", "Lun-Ven: 8h-15h"),
        ("STB Sfax Ville", "banque", "Rue Mongi Slim, Sfax", "Sfax", 34.7400, 10.7600, "74 225 100", "Lun-Ven: 8h-15h"),
        ("BIAT Sfax Centre", "banque", "Avenue Hedi Chaker, Sfax", "Sfax", 34.7390, 10.7620, "74 298 700", "Lun-Ven: 8h-15h"),
        
        ("Municipalité de Sfax", "municipalité", "Place de la République, Sfax", "Sfax", 34.7390, 10.7609, "74 298 000", "Lun-Ven: 8h-16h"),
        
        ("Commissariat Sfax Ville", "police", "Rue Mongi Slim, Sfax", "Sfax", 34.7398, 10.7612, "74 211 888", "24h/24"),
        
        ("Hôpital Habib Bourguiba Sfax", "hôpital", "Route El Ain, Sfax", "Sfax", 34.7550, 10.7380, "74 243 411", "24h/24"),
        
        ("Pharmacie Centrale Sfax", "pharmacie", "Avenue Habib Bourguiba, Sfax", "Sfax", 34.7405, 10.7605, "74 211 234", "Lun-Sam: 8h-20h"),
    ]
    
    # 🔹 Lieux à TUNIS
    tunis_places = [
        ("La Poste Centrale Tunis", "poste", "Rue Charles de Gaulle, Tunis", "Tunis", 36.8065, 10.1815, "71 341 111", "Lun-Ven: 8h-18h, Sam: 8h-13h"),
        ("Poste Bab El Khadra", "poste", "Avenue de la Liberté, Tunis", "Tunis", 36.8120, 10.1850, "71 562 300", "Lun-Ven: 8h-17h"),
        
        ("Banque Centrale de Tunisie", "banque", "Avenue Mohamed V, Tunis", "Tunis", 36.8010, 10.1823, "71 340 588", "Lun-Ven: 8h-15h"),
        ("STB Tunis Centre", "banque", "Avenue Habib Bourguiba, Tunis", "Tunis", 36.7995, 10.1815, "71 340 200", "Lun-Ven: 8h-15h"),
        ("BIAT Lafayette", "banque", "Rue de Marseille, Tunis", "Tunis", 36.8005, 10.1830, "71 832 000", "Lun-Ven: 8h-15h"),
        
        ("Municipalité de Tunis", "municipalité", "Place de la Kasbah, Tunis", "Tunis", 36.7989, 10.1708, "71 560 600", "Lun-Ven: 8h-17h"),
        
        ("Commissariat Bab Bhar", "police", "Avenue Habib Bourguiba, Tunis", "Tunis", 36.8000, 10.1820, "71 341 500", "24h/24"),
        
        ("Hôpital Charles Nicolle", "hôpital", "Boulevard du 9 Avril 1938, Tunis", "Tunis", 36.8080, 10.1770, "71 578 000", "24h/24"),
        
        ("Pharmacie Principale Tunis", "pharmacie", "Avenue de France, Tunis", "Tunis", 36.8010, 10.1820, "71 340 678", "Lun-Sam: 8h-20h"),
    ]
    
    # 🔹 Lieux à SOUSSE
    sousse_places = [
        ("La Poste Sousse Ville", "poste", "Avenue Habib Bourguiba, Sousse", "Sousse", 35.8256, 10.6369, "73 226 400", "Lun-Ven: 8h-17h"),
        
        ("Banque de Tunisie Sousse", "banque", "Avenue Léopold Sédar Senghor, Sousse", "Sousse", 35.8270, 10.6410, "73 225 600", "Lun-Ven: 8h-15h"),
        ("STB Sousse Jawhara", "banque", "Rue de Palestine, Sousse", "Sousse", 35.8290, 10.6380, "73 228 300", "Lun-Ven: 8h-15h"),
        
        ("Municipalité de Sousse", "municipalité", "Avenue Mohamed Maarouf, Sousse", "Sousse", 35.8280, 10.6400, "73 221 900", "Lun-Ven: 8h-16h"),
        
        ("Commissariat Sousse Ville", "police", "Avenue de la République, Sousse", "Sousse", 35.8265, 10.6395, "73 225 888", "24h/24"),
        
        ("Hôpital Sahloul Sousse", "hôpital", "Route de la Ceinture, Sousse", "Sousse", 35.8350, 10.5950, "73 367 400", "24h/24"),
    ]
    
    # 🔹 Combiner tous les lieux
    all_places = sfax_places + tunis_places + sousse_places
    
    # 🔹 Insertion dans la BD
    inserted = 0
    duplicates = 0
    
    for place in all_places:
        try:
            # Vérifier si existe déjà
            check_query = text("""
                SELECT COUNT(*) FROM administrative_places 
                WHERE name = :name AND city = :city
            """)
            result = db.execute(check_query, {"name": place[0], "city": place[3]})
            exists = result.scalar() > 0
            
            if exists:
                print(f"⚠️  Déjà existant: {place[0]}")
                duplicates += 1
                continue
            
            # Insérer
            insert_query = text("""
                INSERT INTO administrative_places 
                (name, type, address, city, latitude, longitude, phone, opening_hours)
                VALUES (:name, :type, :address, :city, :lat, :lon, :phone, :hours)
            """)
            
            db.execute(insert_query, {
                "name": place[0],
                "type": place[1],
                "address": place[2],
                "city": place[3],
                "lat": place[4],
                "lon": place[5],
                "phone": place[6],
                "hours": place[7]
            })
            
            print(f"✅ Ajouté: {place[0]} ({place[1]}) - {place[3]}")
            inserted += 1
            
        except Exception as e:
            print(f"❌ Erreur pour {place[0]}: {e}")
    
    # Commit
    db.commit()
    db.close()
    
    # Résumé
    print("\n" + "="*70)
    print("📊 RÉSUMÉ")
    print("="*70)
    print(f"✅ Lieux ajoutés: {inserted}")
    print(f"⚠️  Doublons ignorés: {duplicates}")
    print(f"📍 Total: {inserted + duplicates}")
    print("\n✅ Base de données remplie avec succès!")


if __name__ == "__main__":
    try:
        populate_database()
    except Exception as e:
        print(f"\n❌ ERREUR FATALE: {e}")
        import traceback
        traceback.print_exc()