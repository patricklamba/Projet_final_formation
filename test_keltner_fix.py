# test_keltner_fixed.py
def test_keltner_alignment_with_missing_dates():
    """
    Test robuste de l'alignement temporel avec données manquantes.
    Version corrigée du bug d'indexation.
    """
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    from indicators.keltner_channel import KeltnerChannel

    print("🧪 TEST ALIGNEMENT TEMPOREL AVEC DONNÉES MANQUANTES (CORRIGÉ)")
    print("=" * 70)
    
    # --- 1️⃣ Création de données avec trous temporels réalistes ---
    dates = [datetime(2023, 1, 1) + timedelta(days=i) for i in range(30)]
    dates.pop(5)   # Simule un weekend
    dates.pop(10)  # Simule un jour férié  
    dates.pop(15)  # Simule des données manquantes
    
    np.random.seed(42)
    df = pd.DataFrame({
        "open": 100 + np.cumsum(np.random.randn(len(dates)) * 0.5),
        "high": 100 + np.cumsum(np.random.randn(len(dates)) * 0.5) + 1.0,
        "low": 100 + np.cumsum(np.random.randn(len(dates)) * 0.5) - 1.0,
        "close": 100 + np.cumsum(np.random.randn(len(dates)) * 0.5),
    }, index=pd.to_datetime(dates))
    
    print(f"📊 Données d'entrée: {len(df)} bougies avec {30 - len(df)} jours manquants")
    print(f"📅 Période: {df.index.min()} à {df.index.max()}")
    print(f"🔍 Type d'index: {type(df.index)}")
    print(f"🔍 Exemple d'index: {df.index[:3].tolist()}")
    
    # --- 2️⃣ Test avec fill_missing=True ---
    print("\n🔧 TEST 1: Mode fill_missing=True")
    kc_fill = KeltnerChannel(ema_period=10, atr_period=5, verbose=True, fill_missing=True)
    
    try:
        out_fill = kc_fill.calculate(df)
        print("✅ Calcul réussi sans erreur d'indexation")
        
        # Vérifications de base
        assert "kc_middle" in out_fill.columns, "❌ Colonne kc_middle manquante"
        assert len(out_fill) == len(df), f"❌ Taille différente: {len(out_fill)} vs {len(df)}"
        assert out_fill.index.is_monotonic_increasing, "❌ Index non monotone"
        
        calculated_values = out_fill["kc_middle"].notna().sum()
        print(f"✅ {calculated_values}/{len(out_fill)} valeurs calculées")
        
    except Exception as e:
        print(f"❌ Erreur lors du calcul: {e}")
        return False
    
    # --- 3️⃣ Test avec fill_missing=False ---
    print("\n🔧 TEST 2: Mode fill_missing=False")
    kc_no_fill = KeltnerChannel(ema_period=10, atr_period=5, verbose=True, fill_missing=False)
    
    try:
        out_no_fill = kc_no_fill.calculate(df)
        print("✅ Calcul réussi sans erreur d'indexation")
        
        assert len(out_no_fill) <= len(df), "❌ Taille inattendue"
        assert out_no_fill["kc_middle"].notna().all(), "❌ NaN résiduels"
        assert out_no_fill.index.is_monotonic_increasing, "❌ Index non monotone"
        
        print(f"✅ Mode no-fill: {len(out_no_fill)} lignes après nettoyage")
        
    except Exception as e:
        print(f"❌ Erreur lors du calcul: {e}")
        return False
    
    # --- 4️⃣ Vérification de la cohérence ---
    print("\n🔧 TEST 3: Cohérence des résultats")
    
    common_dates = out_fill.index.intersection(out_no_fill.index)
    if len(common_dates) > 0:
        fill_common = out_fill.loc[common_dates, "kc_middle"]
        no_fill_common = out_no_fill.loc[common_dates, "kc_middle"]
        
        # Vérifier l'égalité des valeurs (tolérance pour les erreurs d'arrondi)
        diff = (fill_common - no_fill_common).abs().max()
        assert diff < 1e-10, f"❌ Différence trop grande: {diff}"
        print(f"✅ {len(common_dates)} dates communes - valeurs identiques")
    
    # --- 5️⃣ Vérifications finales ---
    print("\n🔧 TEST 4: Vérifications finales")
    
    # Relations mathématiques
    assert (out_no_fill["kc_upper"] > out_no_fill["kc_lower"]).all(), "❌ Canal inversé"
    assert (out_no_fill["kc_position"] >= 0).all() and (out_no_fill["kc_position"] <= 1).all(), "❌ kc_position hors limites"
    
    print("✅ Toutes les vérifications passées")
    
    # --- 6️⃣ Résumé ---
    print("\n📊 RÉSULTATS FINAUX:")
    print(f"   • Données d'entrée: {len(df)} bougies")
    print(f"   • Mode fill_missing=True: {len(out_fill)} bougies, {out_fill['kc_middle'].notna().sum()} calculées")
    print(f"   • Mode fill_missing=False: {len(out_no_fill)} bougies, {out_no_fill['kc_middle'].notna().sum()} calculées")
    print(f"   • Dates communes: {len(common_dates)}")
    
    print("\n🔍 ÉCHANTILLON FINAL:")
    print(out_no_fill[['close', 'kc_middle', 'kc_upper', 'kc_lower', 'kc_position']].tail())
    
    print("\n🎉 TEST D'ALIGNEMENT RÉUSSI !")
    return True

# Exécution du test
if __name__ == "__main__":
    test_keltner_alignment_with_missing_dates()