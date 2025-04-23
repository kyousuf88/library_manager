import streamlit as st
import sqlite3

# Database setup and utility functions
def get_db_connection():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            publication_year INTEGER,
            genre TEXT,
            read_status BOOLEAN
        )
    ''')
    conn.commit()
    conn.close()

def add_book(title, author, publication_year, genre, read_status):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO books (title, author, publication_year, genre, read_status)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, author, publication_year, genre, read_status))
    conn.commit()
    conn.close()

def remove_book(book_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()

def search_books(search_term):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM books
        WHERE title LIKE ? OR author LIKE ?
    ''', (f'%{search_term}%', f'%{search_term}%'))
    books = cursor.fetchall()
    conn.close()
    return books

def get_all_books():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books').fetchall()
    conn.close()
    return books

def get_stats():
    conn = get_db_connection()
    total = conn.execute('SELECT COUNT(*) FROM books').fetchone()[0]
    read = conn.execute('SELECT COUNT(*) FROM books WHERE read_status = 1').fetchone()[0]
    conn.close()
    percentage = (read / total * 100) if total > 0 else 0
    return total, percentage

# Initialize database.;76^YH 
init_db()

# Streamlit UI
st.title("📚 Personal Library Manager")

menu = st.sidebar.selectbox(
    "Menu",
    ["Add a book", "Remove a book", "Search for a book", "Display all books", "Display statistics", "Exit"]
)

if menu == "Add a book":
    st.subheader("Add a New Book")
    with st.form("add_form"):
        title = st.text_input("Title*")
        author = st.text_input("Author*")
        publication_year = st.number_input("Publication Year*", min_value=1800, max_value=2100)
        genre = st.text_input("Genre")
        read_status = st.checkbox("Read Status")
        submitted = st.form_submit_button("Add Book")
        
        if submitted:
            if title and author:
                add_book(title, author, publication_year, genre, read_status)
                st.success("Book added successfully!")
            else:
                st.error("Title and Author are required fields")

elif menu == "Remove a book":
    st.subheader("Remove a Book")
    search_term = st.text_input("Enter book title to search")
    
    if st.button("Search"):
        st.session_state.remove_results = search_books(search_term)
    
    if 'remove_results' in st.session_state:
        books = st.session_state.remove_results
        if books:
            st.write("Found books:")
            for book in books:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"""
                    *{book['title']}* by {book['author']}  
                    Year: {book['publication_year']} | Genre: {book['genre']}  
                    Read: {'✅' if book['read_status'] else '❌'}
                    """)
                with col2:
                    if st.button(f"Delete", key=f"del_{book['id']}"):
                        remove_book(book['id'])
                        st.success("Book deleted!")
                        st.session_state.remove_results = [b for b in books if b['id'] != book['id']]
                        st.experimental_rerun()
        else:
            st.warning("No books found with that title")

elif menu == "Search for a book":
    st.subheader("Search Books")
    search_term = st.text_input("Enter title or author")
    if st.button("Search"):
        books = search_books(search_term)
        if books:
            st.write("Search results:")
            for book in books:
                st.write(f"""
                *{book['title']}* by {book['author']}  
                Year: {book['publication_year']} | Genre: {book['genre']}  
                Read: {'✅' if book['read_status'] else '❌'}
                """)
        else:
            st.info("No matching books found")

elif menu == "Display all books":
    st.subheader("All Books")
    books = get_all_books()
    if books:
        for book in books:
            st.write(f"""
            *{book['title']}* by {book['author']}  
            Year: {book['publication_year']} | Genre: {book['genre']}  
            Read: {'✅' if book['read_status'] else '❌'}
            """)
    else:
        st.info("Your library is empty")

elif menu == "Display statistics":
    st.subheader("Library Statistics")
    total, percentage = get_stats()
    st.metric("Total Books", total)
    st.metric("Percentage Read", f"{percentage:.1f}%")

elif menu == "Exit":
    st.success("Thank you for using the Library Manager!")
    st.stop()