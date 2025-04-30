import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine, text

# Load embedding model once
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Connexion à ta BDD
engine = create_engine("mysql+pymysql://root:password@localhost/novamind")

def get_user_data_from_db(user_id):
    with engine.connect() as conn:
        enterprise_query = text("SELECT * FROM enterprise_info WHERE user_id = :uid")
        product_query = text("SELECT * FROM products WHERE user_id = :uid")
        
        enterprise = conn.execute(enterprise_query, {"uid": user_id}).fetchone()
        products = conn.execute(product_query, {"uid": user_id}).fetchall()
        
        return enterprise, products

def format_user_text(enterprise, products):
    lines = []
    
    if enterprise:
        lines.append(f"Enterprise Name: {enterprise.enterprise_name}")
        lines.append(f"Description: {enterprise.description}")
        lines.append(f"Sector: {enterprise.sector}")
        lines.append(f"Location: {enterprise.location}")
        lines.append(f"Founded Year: {enterprise.founded_year}")
        lines.append(f"Website: {enterprise.website}")
        if enterprise.other_notes:
            lines.append(f"Other Notes: {enterprise.other_notes}")
    
    for p in products:
        lines.append(f"\nProduct: {p.product_name}")
        lines.append(f"Description: {p.product_description}")
        lines.append(f"Price: {p.price}")
        lines.append(f"Category: {p.category}")
        lines.append(f"Launch Date: {p.launch_date}")
    
    return "\n".join(lines)

def index_user_data(user_id):
    enterprise, products = get_user_data_from_db(user_id)
    if not enterprise and not products:
        print("No data found for user.")
        return

    # Format and save user data
    user_folder = f"users/{user_id}"
    os.makedirs(user_folder, exist_ok=True)
    text_data = format_user_text(enterprise, products)
    
    with open(f"{user_folder}/enterprise.txt", "w", encoding="utf-8") as f:
        f.write(text_data)

    # Embed text
    embeddings = embedder.encode([text_data])
    dimension = embeddings.shape[1]

    # Create and save FAISS index
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    os.makedirs(f"{user_folder}/index", exist_ok=True)
    faiss.write_index(index, f"{user_folder}/index/faiss_index")
    
    # Save mapping doc id to text (if needed)
    with open(f"{user_folder}/index/doc.pkl", "wb") as f:
        pickle.dump([text_data], f)

    print(f"✅ User {user_id} data indexed successfully.")

