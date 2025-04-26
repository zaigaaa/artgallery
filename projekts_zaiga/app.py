from flask import Flask, render_template, url_for, request  # <- PIEVIENOTS "request"
import sqlite3
from pathlib import Path

app = Flask(__name__)

def get_db_connection():
    db = Path(__file__).parent / "baze"
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    conn = get_db_connection()
    artworks = conn.execute("""
        SELECT artworks.id, artworks.nosaukums, artists.vards AS artist, 
               art_styles.stils AS style, countries.nosaukums AS country, artworks.gads
        FROM artworks
        JOIN artists ON artworks.artist_id = artists.id
        JOIN art_styles ON artworks.style_id = art_styles.id
        JOIN countries ON artworks.country_id = countries.id
    """).fetchall()
    conn.close()
    return render_template("index.html", artworks=artworks)

@app.route("/artworks/<int:artwork_id>")
def artwork_detail(artwork_id):
    conn = get_db_connection()
    artwork = conn.execute("""
        SELECT artworks.*, artists.vards AS artist, 
               art_styles.stils AS style, art_styles.apraksts AS style_desc, 
               countries.nosaukums AS country
        FROM artworks
        JOIN artists ON artworks.artist_id = artists.id
        JOIN art_styles ON artworks.style_id = art_styles.id
        JOIN countries ON artworks.country_id = countries.id
        WHERE artworks.id = ?
    """, (artwork_id,)).fetchone()
    conn.close()
    return render_template("artwork_detail.html", artwork=artwork)

@app.route("/db-tabulas")
def db_info():
    conn = get_db_connection()
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    struktura = {}
    for t in tables:
        table_name = t['name']
        rows = conn.execute(f"PRAGMA table_info({table_name});").fetchall()
        struktura[table_name] = rows
    conn.close()
    return render_template("db_info.html", struktura=struktura)

@app.route("/Par-mums")
def about():
    return render_template("about.html")

@app.route("/makslas-darbi")
def artworks():
    conn = get_db_connection()
    artworks = conn.execute("""
        SELECT artworks.id, artworks.nosaukums, artists.vards AS artist,
               art_styles.stils AS style, countries.nosaukums AS country, 
               artworks.gads, artworks.foto
        FROM artworks
        JOIN artists ON artworks.artist_id = artists.id
        JOIN art_styles ON artworks.style_id = art_styles.id
        JOIN countries ON artworks.country_id = countries.id
    """).fetchall()
    conn.close()
    return render_template("artworks.html", artworks=artworks)

@app.route("/izstades") 
def exhibitions():
    # Also fetch feedback data here
    conn = get_db_connection()
    atsauksmes = conn.execute("SELECT * FROM feedback ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("exhibitions.html", atsauksmes=atsauksmes)

@app.route("/atsauksmes", methods=["GET", "POST"]) 
def feedback():
    conn = get_db_connection()
    
    if request.method == "POST":
        teksts = request.form.get("feedback")
        if teksts:
            # Pievienojam jaunu atsauksmi
            conn.execute("INSERT INTO feedback (teksts) VALUES (?)", (teksts,))
            conn.commit()
    
    # Nolasām visas atsauksmes pēc pievienošanas
    atsauksmes = conn.execute("SELECT * FROM feedback ORDER BY id DESC").fetchall()
    conn.close()
    
    # Redirect back to exhibitions page to display all feedback
    return render_template("exhibitions.html", atsauksmes=atsauksmes)


if __name__ == "__main__":
    app.run(debug=True)
