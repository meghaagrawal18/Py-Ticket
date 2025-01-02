from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64
app = Flask(__name__)


def get_connection():
    """
    Establish a connection to the MySQL database
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='movie_ticket',
            user="root",
            password="megha@12345",
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL Platform: {e}")
        return None


print("Connected successfully")


@app.route('/')
def home():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id, title, genre, price, showtime, description, image_url FROM movie")
    movies = cursor.fetchall()
    connection.close()
    return render_template('page1/index.html', movies=movies)


@app.route('/book-tickets/<int:id>', methods=['GET', 'POST'])
def book_ticket(id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id, title, genre, price, showtime, description, image_url FROM movie WHERE id = %s", (id,))
    movie = cursor.fetchone()
    connection.close()

    if not movie:
        return "Movie not found", 404

    if request.method == 'POST':
        name = request.form['name']
        seats = request.form['seats']
        total_price = movie['price'] * int(request.form.get('seat_count', 1))

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO bookings (movie_id, customer_name, seats, total_price, booking_time) VALUES (%s, %s, %s, %s, %s)",
            (id, name, seats, total_price, datetime.now())
        )
        booking_id = cursor.lastrowid
        connection.commit()
        connection.close()

        # Redirect to confirmation page with booking ID
        return redirect(url_for('booking_confirmation', booking_id=booking_id))

    return render_template('page 2/index.html', movie=movie)


@app.route('/booking-confirmation/<int:booking_id>')
def booking_confirmation(booking_id):
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Get booking details with movie information
        cursor.execute("""
            SELECT 
                b.id as booking_id,
                b.customer_name,
                b.seats,
                b.total_price,
                b.booking_time,
                m.title,
                m.genre,
                m.price,
                m.showtime,
                m.image_url
            FROM bookings b
            JOIN movie m ON b.movie_id = m.id
            WHERE b.id = %s
        """, (booking_id,))

        booking = cursor.fetchone()
        connection.close()

        if not booking:
            return "Booking not found", 404

        # Format the data for the template
        context = {
            'movie': {
                'title': booking['title'],
                'showtime': booking['showtime'] if booking['showtime'] else 'Not specified',
                'price': booking['price']
            },
            'name': booking['customer_name'],
            'seats': booking['seats'],
            'total_price': booking['total_price']
        }

        return render_template('page 3/index.html', **context)

    except Error as e:
        print(f"Error retrieving booking: {e}")
        return "Error processing your request", 500


@app.route('/analytics')
def analytics():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    # Query to count bookings per movie
    cursor.execute("""
        SELECT 
            m.title,
            COUNT(b.id) as booking_count
        FROM movie m
        LEFT JOIN bookings b ON m.id = b.movie_id
        GROUP BY m.id, m.title
        ORDER BY booking_count DESC
    """)

    data = cursor.fetchall()
    connection.close()

    # Extract data for plotting
    movie_titles = [item['title'] for item in data]
    booking_counts = [item['booking_count'] for item in data]

    # Create the bar plot
    plt.figure(figsize=(12, 6))
    plt.bar(movie_titles, booking_counts, color='skyblue')
    plt.title('Movie Bookings Analysis')
    plt.xlabel('Movies')
    plt.ylabel('Number of Bookings')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Save plot to memory
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    # Convert plot to base64 string for HTML
    graph_url = base64.b64encode(img.getvalue()).decode()

    return render_template('analytics.html', graph_url=graph_url)

if __name__ == '__main__':
    app.run(debug=True)