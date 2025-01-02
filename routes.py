# from flask import render_template, request, redirect, url_for
# from app import app
# from app.db_config import get_connection
#
# @app.route('/')
# def index():
#     conn = get_connection()
#     cursor = conn.cursor(dictionary=True)
#     # Query from the 'movie' table
#     cursor.execute("SELECT * FROM movie")
#     movies = cursor.fetchall()
#     conn.close()
#     return render_template('index.html', movies=movies)  # Pass the variable as 'movies'
#
# @app.route('/book/<int:movie_id>', methods=['GET', 'POST'])
# def book_ticket(movie_id):
#     conn = get_connection()
#     cursor = conn.cursor(dictionary=True)
#     # Query a specific movie from the 'movie' table
#     cursor.execute("SELECT * FROM movie WHERE id = %s", (movie_id,))
#     movie = cursor.fetchone()
#
#     if request.method == 'POST':
#         customer_name = request.form['name']
#         seats = int(request.form['seats'])
#         total_price = movie['price'] * seats  # Calculate total price
#
#         # Insert booking details into 'bookings' table
#         cursor.execute(
#             "INSERT INTO bookings (movie_id, customer_name, seats, total_price) "
#             "VALUES (%s, %s, %s, %s)",
#             (movie_id, customer_name, seats, total_price)
#         )
#         conn.commit()
#         conn.close()
#         return redirect(url_for('index'))  # Redirect to the home page
#
#     conn.close()
#     return render_template('book_tickets.html', movie=movie)
#
# @app.route('/analytics')
# def analytics():
#     conn = get_connection()
#     cursor = conn.cursor(dictionary=True)
#
#     # Most Booked Movies (from 'movie' table)
#     cursor.execute(
#         "SELECT m.title, SUM(b.seats) AS total_seats "
#         "FROM bookings b JOIN movie m ON b.movie_id = m.id "
#         "GROUP BY m.id ORDER BY total_seats DESC"
#     )
#     most_booked_movies = cursor.fetchall()
#
#     # Peak Booking Times
#     cursor.execute(
#         "SELECT HOUR(booking_time) AS booking_hour, COUNT(*) AS total_bookings "
#         "FROM bookings GROUP BY booking_hour ORDER BY total_bookings DESC"
#     )
#     peak_booking_times = cursor.fetchall()
#
#     # Revenue Trends
#     cursor.execute(
#         "SELECT DATE(booking_time) AS booking_date, SUM(total_price) AS total_revenue "
#         "FROM bookings GROUP BY booking_date ORDER BY booking_date"
#     )
#     revenue_trends = cursor.fetchall()
#
#     conn.close()
#     return render_template(
#         'analytics.html',
#         most_booked_movies=most_booked_movies,
#         peak_booking_times=peak_booking_times,
#         revenue_trends=revenue_trends
#     )


from flask import render_template, request, redirect, url_for
from app import app
from db_config import get_connection

@app.route('/')
def index():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    # Query from the 'movie' table
    cursor.execute("SELECT * FROM movie")
    movies = cursor.fetchall()
    conn.close()
    return render_template('index.html', movies=movies)

@app.route('/book/<int:movie_id>', methods=['GET', 'POST'])
def book_ticket(movie_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    # Query a specific movie from the 'movie' table
    cursor.execute("SELECT * FROM movie WHERE id = %s", (movie_id,))
    movie = cursor.fetchone()

    if request.method == 'POST':
        customer_name = request.form['name']
        seats = int(request.form['seats'])
        total_price = movie['price'] * seats  # Calculate total price

        # Insert booking details into 'bookings' table
        cursor.execute(
            "INSERT INTO bookings (movie_id, customer_name, seats, total_price) "
            "VALUES (%s, %s, %s, %s)",
            (movie_id, customer_name, seats, total_price)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))  # Redirect to the home page

    conn.close()
    return render_template('book_tickets.html', movie=movie)

@app.route('/analytics')
def analytics():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Most Booked Movies (from 'movie' table)
    cursor.execute(
        "SELECT m.title, SUM(b.seats) AS total_seats "
        "FROM bookings b JOIN movie m ON b.movie_id = m.id "
        "GROUP BY m.id ORDER BY total_seats DESC"
    )
    most_booked_movies = cursor.fetchall()

    # Peak Booking Times
    cursor.execute(
        "SELECT HOUR(booking_time) AS booking_hour, COUNT(*) AS total_bookings "
        "FROM bookings GROUP BY booking_hour ORDER BY total_bookings DESC"
    )
    peak_booking_times = cursor.fetchall()

    # Revenue Trends
    cursor.execute(
        "SELECT DATE(booking_time) AS booking_date, SUM(total_price) AS total_revenue "
        "FROM bookings GROUP BY booking_date ORDER BY booking_date"
    )
    revenue_trends = cursor.fetchall()

    conn.close()
    return render_template(
        'analytics.html',
        most_booked_movies=most_booked_movies,
        peak_booking_times=peak_booking_times,
        revenue_trends=revenue_trends
    )