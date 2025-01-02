from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error
from datetime import datetime

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


if __name__ == '__main__':
    app.run(debug=True)