import streamlit as st
import pandas as pd
import joblib
import json
import time

# Charger le modèle et les encodeurs
model = joblib.load("modele_voiture.pkl")
scaler_annee = joblib.load("annee_scaler.pkl")
marque_encoder = joblib.load("marque_encoder.pkl")
modele_encoder = joblib.load("modele_encoder.pkl")
scaler_kilometrage = joblib.load("kilometrage_scaler.pkl")
price_scaler = joblib.load("price_scaler.pkl")
# @st.cache_data
def load_marques_modeles():
    with open("marques_modeles.json", "r", encoding="utf-8") as f:
        return json.load(f)

marques_modeles = load_marques_modeles()

def input_construction(annee, marque, modele, kilometrage, papiers, boite, energie):
    
    annee_scaled = scaler_annee.transform([[annee]])[0, 0]
    kilometrage_scaled = scaler_kilometrage.transform([[kilometrage]])[0, 0]

    try:
        marque_encoded = marque_encoder.transform([marque])[0]
    except ValueError:
        marque_encoded = -1  # Valeur par défaut si la marque n'est pas connue

    try:
        modele_encoded = modele_encoder.transform([modele])[0]
    except ValueError:
        modele_encoded = -1 

    categories = [
        "Papiers_Carte jaune",
        "Papiers_Licence / Délai",
        "Boite_Manuelle",
        "Boite_Semi Automatique",
        "Energie_Essence",
        "Energie_GPL"
    ]

    # Initialiser un dictionnaire avec toutes les catégories à 0
    input_dict = {cat: 0 for cat in categories}
    
    # Gérer les cas où la catégorie supprimée est la valeur actuelle
    if papiers == "Carte jaune" or papiers == "Licence / Délai":
        papiers_col = f"Papiers_{papiers}"
        if papiers_col in input_dict:
            input_dict[papiers_col] = 1



    if boite == "Manuelle" or boite == "Semi Automatique":
        boite_col = f"Boite_{boite}"
        if boite_col in input_dict:
            input_dict[boite_col] = 1

    if energie == "Essence" or energie == "GPL":
        energie_col = f"Energie_{energie}"
        if energie_col in input_dict:
            input_dict[energie_col] = 1

    # Convertir en DataFrame
    input_df = pd.DataFrame([{
        "Année": annee_scaled,
        "Marque": marque_encoded,
        "Modèle": modele_encoded,
        "Kilométrage": kilometrage_scaled,
        **input_dict
    }])

    return input_df


# Page configuration
st.set_page_config(
    page_title="CarPrice Estimator - Voiture d'occasion",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("style.css")  # Create a style.css file in the same directory

# Load model and encoders
@st.cache_resource
def load_assets():
    return {
        "model": joblib.load("modele_voiture.pkl"),
        "scaler_annee": joblib.load("annee_scaler.pkl"),
        "marque_encoder": joblib.load("marque_encoder.pkl"),
        "modele_encoder": joblib.load("modele_encoder.pkl"),
        "scaler_kilometrage": joblib.load("kilometrage_scaler.pkl"),
        "price_scaler": joblib.load("price_scaler.pkl"),
        "marques_modeles": json.load(open("marques_modeles.json", "r", encoding="utf-8"))
    }

assets = load_assets()


# Header Section
col1, col2 = st.columns([1, 3])
with col1:
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <div style='font-size: 48px; color: #1976d2;'>🚙</div>
    </div>
    """, unsafe_allow_html=True)
    
with col2:
    st.markdown("<h1 style='color: #1a237e; margin-bottom: 0;'>Estimation des prix des voitures d'occasion</h1>", unsafe_allow_html=True)
    st.markdown("<div style='color: #1976d2; font-size: 18px; margin-top: -10px;'>Entrez les informations de votre voiture et obtenez une estimation de son prix selon le marché</div>", unsafe_allow_html=True)

# Main Content
with st.container():
    st.markdown("""
        <style>
            .main-container {
                max-width: 1000px;
                margin: auto;
                padding: 50px;
            }
            .st-emotion-cache-1v0mbdj {
                margin: 0 0.5rem;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    cols = st.columns([3, 4])
    
    with cols[0]:
        with st.expander("📋 Informations du Véhicule", expanded=True):
            st.markdown("### Caractéristiques de base")
            annee = st.slider(
                "Année du véhicule",
                min_value=1970,
                max_value=2025,
                value=2013,
                help="Sélectionnez l'année du véhicule"
            )
            
            marque = st.selectbox(
                "Marque du véhicule",
                options=list(assets["marques_modeles"].keys()),
                index=5,
                help="Sélectionnez la marque du véhicule"
            )
            
            modeles_disponibles = assets["marques_modeles"].get(marque, [])
            modele = st.selectbox(
                "Modèle du véhicule",
                options=modeles_disponibles,
                index=min(5, len(modeles_disponibles)-1) if modeles_disponibles else 0,
                help="Sélectionnez le modèle spécifique"
            )
            
            kilometrage = st.number_input(
                "Kilométrage (km)",
                min_value=0,
                max_value=600000,
                value=100000,
                step=1000,
                format="%d",
                help="Entrez le kilométrage actuel du véhicule"
            )

    with cols[1]:
        with st.expander("⚙️ Détails Techniques", expanded=True):
            st.markdown("### Configuration technique")
            
            papiers = st.radio(
                "Type de papiers",
                options=["Carte grise / safia", "Carte jaune", "Licence / Délai"],
                horizontal=True,
                help="Sélectionnez le type de documents disponibles"
            )
            
            boite = st.selectbox(
                "Type de boîte de vitesse",
                options=["Manuelle", "Automatique", "Semi Automatique"],
                index=0,
                help="Sélectionnez le type de transmission"
            )
            
            energie = st.selectbox(
                "Type de carburant",
                options=["Essence", "Diesel", "GPL"],
                index=0,
                help="Sélectionnez le type de carburant utilisé"
            )
    st.markdown('</div>', unsafe_allow_html=True)
# Prediction Button
st.markdown("---")
col_btn = st.columns([1, 2, 1])
with col_btn[1]:
    predict_btn = st.button(
        "🎯 Calculer le Prix Estimé",
        use_container_width=True,
        type="primary"
    )

# Prediction Logic
if predict_btn:
    try:
        input_df = input_construction(annee, marque, modele, kilometrage, papiers, boite, energie)
        prediction = assets["model"].predict(input_df)
        price = assets["price_scaler"].inverse_transform(prediction.reshape(-1, 1))
        
        # Display result with animation
        with st.spinner("Analyse en cours..."):
            time.sleep(1.5)
            
        st.markdown("---")
        st.markdown(f"""
<div class="result-box">
    <h2 style='text-align: center; color: #1a237e; margin-bottom: 20px;'>
        Estimation de Prix
    </h2>
    <p style='text-align: center; font-size: 32px; font-weight: bold; color: #1976d2;'>
        {float(price[0][0]):,.0f} MILLIONS
    </p>
    <p style='text-align: center; color: #2c3e50;'>
        Prix estimé pour un {marque} {modele} de {annee}
    </p>
</div>
""", unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Une erreur est survenue : {str(e)}")

# Footer
st.markdown("---")
footer = """<div style="text-align: center; color: #7f8c8d; padding: 20px;">
    <p>📌 Note : Cette estimation est basée sur les tendances du marché et peut varier selon l'état du véhicule</p>
    <p>© 2025 CarPrice Estimator - Tous droits réservés</p>
</div>"""
st.markdown(footer, unsafe_allow_html=True)