import os

# === 1️⃣ Définir le chemin racine du projet ===
base_path = r"C:\Users\lamba\Documents\DEV\Python_formation\Projet_final_formation"

# === 2️⃣ Structure du projet ===
folders = [
    "data",
    "indicators",
    "core",
    "utils",
    "configs",
    "results"
]

# === 3️⃣ Fichiers à créer par défaut ===
files = {
    "main.py": "",
    "requirements.txt": "pandas\nnumpy\nopenai\npyyaml\nrequests\nbeautifulsoup4\n",
    "README.md": "# AI Trading Assistant – Projet de fin de formation Python\n",
    ".gitignore": "__pycache__/\n*.pyc\nresults/\n.env\n",
    "configs/settings.yaml": """
bb_period: 20
bb_std: 2
kc_period: 20
kc_mult: 1.5
killzone:
  start: "03:00"
  end: "06:30"
    """,
    "indicators/__init__.py": "",
    "core/__init__.py": "",
    "utils/__init__.py": "",
}

# === 4️⃣ Création des dossiers ===
for folder in folders:
    path = os.path.join(base_path, folder)
    os.makedirs(path, exist_ok=True)
    print(f"📁 Dossier créé : {path}")

# === 5️⃣ Création des fichiers ===
for file_path, content in files.items():
    full_path = os.path.join(base_path, file_path)
    # Créer les sous-dossiers si nécessaire
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    # Écrire le contenu
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"📄 Fichier créé : {full_path}")

print("\n✅ Arborescence du projet créée avec succès !")
