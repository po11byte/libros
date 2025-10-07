import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title=" Buscador de Autores", page_icon="", layout="wide")


st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .author-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    .book-info {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

LIBROS_BD = {
    "Cien años de soledad": "Gabriel García Márquez",
    "Don Quijote de la Mancha": "Miguel de Cervantes",
    "1984": "George Orwell",
    "Orgullo y prejuicio": "Jane Austen",
    "El principito": "Antoine de Saint-Exupéry",
    "Crimen y castigo": "Fiódor Dostoyevski",
    "El gran Gatsby": "F. Scott Fitzgerald",
    "Matar a un ruiseñor": "Harper Lee",
    "El señor de los anillos": "J.R.R. Tolkien",
    "Harry Potter y la piedra filosofal": "J.K. Rowling",
    "El código Da Vinci": "Dan Brown",
    "Los juegos del hambre": "Suzanne Collins",
    "It": "Stephen King",
    "Juego de tronos": "George R.R. Martin",
    "El alquimista": "Paulo Coelho",
    "La sombra del viento": "Carlos Ruiz Zafón",
    "Rayuela": "Julio Cortázar",
    "Ficciones": "Jorge Luis Borges",
    "La casa de los espíritus": "Isabel Allende",
    "Pedro Páramo": "Juan Rulfo"
}

def buscar_autor_google_books(titulo_libro):
    """Buscar autor usando Google Books API"""
    try:
        url = f"https://www.googleapis.com/books/v1/volumes"
        params = {
            "q": f"intitle:{titulo_libro}",
            "maxResults": 1,
            "langRestrict": "es"
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("items"):
                libro = data["items"][0]
                volume_info = libro["volumeInfo"]
                
                autores = volume_info.get("authors", [])
                titulo_encontrado = volume_info.get("title", "")
                fecha_publicacion = volume_info.get("publishedDate", "")
                
                if autores:
                    return {
                        "autor": ", ".join(autores),
                        "titulo_exacto": titulo_encontrado,
                        "año": fecha_publicacion[:4] if fecha_publicacion else "Desconocido",
                        "fuente": "Google Books API",
                        "encontrado": True
                    }
        
        return {"encontrado": False}
        
    except Exception as e:
        return {"encontrado": False, "error": str(e)}

def buscar_autor_local(titulo_libro):
    """Buscar autor en la base de datos local"""
    titulo_lower = titulo_libro.lower()
    
    for libro_titulo, autor in LIBROS_BD.items():
        if titulo_lower in libro_titulo.lower() or libro_titulo.lower() in titulo_lower:
            return {
                "autor": autor,
                "titulo_exacto": libro_titulo,
                "año": "Desconocido",
                "fuente": "Base de datos local",
                "encontrado": True
            }
    
    return {"encontrado": False}

def buscar_autor_open_library(titulo_libro):
    """Buscar autor usando Open Library API"""
    try:
        url = f"https://openlibrary.org/search.json"
        params = {
            "title": titulo_libro,
            "limit": 1
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("docs") and len(data["docs"]) > 0:
                libro = data["docs"][0]
                autor = libro.get("author_name", [])
                titulo_encontrado = libro.get("title", "")
                año = libro.get("first_publish_year", "")
                
                if autor:
                    return {
                        "autor": ", ".join(autor) if isinstance(autor, list) else autor,
                        "titulo_exacto": titulo_encontrado,
                        "año": str(año) if año else "Desconocido",
                        "fuente": "Open Library API",
                        "encontrado": True
                    }
        
        return {"encontrado": False}
        
    except Exception as e:
        return {"encontrado": False, "error": str(e)}


st.markdown('<h1 class="main-header"> Buscador de Autores de Libros</h1>', unsafe_allow_html=True)
st.markdown("### Encuentra el autor de cualquier libro con solo el título")
# Sidebar
with st.sidebar:
    st.header("⚙ Configuración")
    fuente_busqueda = st.radio(
        "Fuente de búsqueda:",
        ["Automática (Recomendada)", "Solo base local", "Solo Google Books", "Solo Open Library"]
    )
    
    st.markdown("---")
    st.header(" Libros en Base Local")
    st.write(f"{len(LIBROS_BD)}** libros populares disponibles")
    
    if st.checkbox("Ver lista completa"):
        st.dataframe(
            pd.DataFrame(list(LIBROS_BD.items()), columns=["Libro", "Autor"]),
            use_container_width=True
        )


col1, col2 = st.columns([3, 1])

with col1:
    titulo_libro = st.text_input(
        " Escribe el título del libro:",
        placeholder="Ej: Cien años de soledad, 1984, El principito...",
        key="busqueda_principal"
    )

with col2:
    st.write("")  
    st.write("")
    buscar_clicked = st.button(" Buscar Autor", type="primary")


if 'historial' not in st.session_state:
    st.session_state.historial = []


if buscar_clicked and titulo_libro:
    with st.spinner(" Buscando autor..."):
        resultados = []

        if fuente_busqueda == "Automática (Recomendada)":
            
            resultado = buscar_autor_local(titulo_libro)
            if not resultado["encontrado"]:
                resultado = buscar_autor_google_books(titulo_libro)
            if not resultado["encontrado"]:
                resultado = buscar_autor_open_library(titulo_libro)
            resultados.append(resultado)
            
        elif fuente_busqueda == "Solo base local":
            resultado = buscar_autor_local(titulo_libro)
            resultados.append(resultado)
            
        elif fuente_busqueda == "Solo Google Books":
            resultado = buscar_autor_google_books(titulo_libro)
            resultados.append(resultado)
            
        elif fuente_busqueda == "Solo Open Library":
            resultado = buscar_autor_open_library(titulo_libro)
            resultados.append(resultado)
        
       
        busqueda_info = {
            "titulo_buscado": titulo_libro,
            "resultados": resultados,
            "fecha": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.historial.insert(0, busqueda_info)
        
        
        if len(st.session_state.historial) > 10:
            st.session_state.historial = st.session_state.historial[:10]


if buscar_clicked and titulo_libro:
    st.markdown("---")
    st.subheader(" Resultados de la búsqueda")
    encontrado = False
    
    for resultado in st.session_state.historial[0]["resultados"]:
        if resultado.get("encontrado"):
            encontrado = True
            with st.container():
                st.markdown(f'<div class="author-card">', unsafe_allow_html=True)
                
                col_res1, col_res2 = st.columns([3, 1])
                
                with col_res1:
                    st.success(f" Libro encontrado:** {resultado['titulo_exacto']}")
                    st.success(f" Autor:** {resultado['autor']}")
                    
                    if resultado.get('año') and resultado['año'] != "Desconocido":
                        st.info(f" Año de publicación:** {resultado['año']}")
                    
                    st.info(f" Fuente:** {resultado['fuente']}")
                
                with col_res2:
                    st.metric("Estado", " Encontrado")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                
                st.markdown("####  También podrías buscar:")
                palabras_clave = titulo_libro.split()[:3]  
                sugerencias = [f'"{palabra}"' for palabra in palabras_clave if len(palabra) > 3]
                
                if sugerencias:
                    cols_sug = st.columns(len(sugerencias))
                    for i, sugerencia in enumerate(sugerencias):
                        with cols_sug[i]:
                            if st.button(sugerencia, key=f"sug_{i}"):
                                st.session_state.busqueda_principal = sugerencia.replace('"', '')
                                st.rerun()
                
                break  
    
    if not encontrado:
        st.error(" No se pudo encontrar el autor para este libro")
        st.markdown("""
        <div style='background-color: #fff3cd; padding: 1rem; border-radius: 5px; border-left: 5px solid #ffc107;'>
        <h4>💡 Sugerencias para mejorar la búsqueda:</h4>
        <ul>
            <li>Verifica la ortografía del título</li>
            <li>Intenta con el título completo y exacto</li>
            <li>Usa la búsqueda automática para mejores resultados</li>
            <li>Prueba con títulos en inglés si es una traducción</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)


if st.session_state.historial:
    st.markdown("---")
    st.subheader(" Historial de Búsquedas")
    
    for i, busqueda in enumerate(st.session_state.historial[:5]):  # Mostrar últimas 5
        with st.expander(f"🔍 {busqueda['titulo_buscado']} - {busqueda['fecha']}", expanded=i==0):
            encontrado_en_esta = any(r.get('encontrado') for r in busqueda['resultados'])
            
            if encontrado_en_esta:
                for resultado in busqueda['resultados']:
                    if resultado.get('encontrado'):
                        st.write(f"*Autor:* {resultado['autor']}")
                        st.write(f"*Título exacto:* {resultado['titulo_exacto']}")
                        st.write(f"*Fuente:* {resultado['fuente']}")
                        break
            else:
                st.warning("No se encontró el autor en esta búsqueda")


st.markdown("---")
st.subheader(" Libros Populares en la Base de Datos")
libros_populares = list(LIBROS_BD.items())[:9]  

cols_libros = st.columns(3)
for i, (libro, autor) in enumerate(libros_populares):
    with cols_libros[i % 3]:
        with st.container():
            st.markdown(f'<div class="book-info">', unsafe_allow_html=True)
            st.write(f"{libro}")
            st.write(f"{autor}")
            
            if st.button(" Buscar este", key=f"btn_{i}"):
                st.session_state.busqueda_principal = libro
                st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)


st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong> Buscador de Autores</strong> - Encuentra autores de libros fácilmente</p>
    <p><em>Combina base de datos local con APIs gratuitas de Google Books y Open Library</em></p>
</div>
""", unsafe_allow_html=True)




