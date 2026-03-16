from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
from .database import get_db_connection

views = Blueprint('views', __name__)

@views.route('/api/trend/<int:item_id>')
@login_required
def trend_api(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT year, season, popularity
        FROM trend_data
        WHERE clothing_id = :1
        ORDER BY year, season
    """, [item_id])

    rows = cursor.fetchall()

    data = {
        "labels": [f"{r[0]} {r[1]}" for r in rows],
        "popularity": [r[2] for r in rows]
    }

    cursor.close()
    conn.close()

    return jsonify(data)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')
    return render_template("home.html", user=current_user)

@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
            
    return jsonify({})

from collections import defaultdict

from collections import defaultdict

@views.route('/items')
@login_required
def items():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            ci.id,
            ci.name,
            ci.color,
            ci.material,
            ci.price,
            c.name AS category_name
        FROM clothing_item ci
        JOIN categories c
            ON ci.category_id = c.id
        WHERE ci.gender_target IN ('female', 'unisex')
        ORDER BY c.name, ci.name
    """)

    grouped_items = defaultdict(list)

    for row in cursor.fetchall():
        item = {
            "id": row[0],
            "name": row[1],
            "color": row[2],
            "material": row[3],
            "price": row[4],
        }

        category = row[5]
        grouped_items[category].append(item)

    cursor.close()
    conn.close()

    return render_template(
        "items.html",
        grouped_items=grouped_items,
        user=current_user
    )


@views.route('/itemsmen')
@login_required
def itemsmen():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            ci.id,
            ci.name,
            ci.color,
            ci.material,
            ci.price,
            c.name AS category_name
        FROM clothing_item ci
        JOIN categories c
            ON ci.category_id = c.id
        WHERE ci.gender_target IN ('male')
        ORDER BY c.name, ci.name
    """)

    grouped_items = defaultdict(list)

    for row in cursor.fetchall():
        item = {
            "id": row[0],
            "name": row[1],
            "color": row[2],
            "material": row[3],
            "price": row[4],
        }

        category = row[5]
        grouped_items[category].append(item)

    cursor.close()
    conn.close()

    return render_template(
        "itemsmen.html",
        grouped_items=grouped_items,
        user=current_user
    )

@views.route('/item/<int:item_id>')
@login_required
def item_detail(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # --- Item info ---
    cursor.execute("""
        SELECT name, color, material, price
        FROM clothing_item
        WHERE id = :1
    """, [item_id])

    row = cursor.fetchone()

    if not row:
        cursor.close()
        conn.close()
        return "Item not found", 404

    item = {
        "id": item_id,
        "name": row[0],
        "color": row[1],
        "material": row[2],
        "price": row[3]
    }

    # --- Trend data ---
    cursor.execute("""
        SELECT year, season, popularity
        FROM trend_data
        WHERE clothing_id = :1
        ORDER BY year, season
    """, [item_id])

    trends = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "item_detail.html",
        item=item,
        trends=trends,
        user=current_user
    )


@views.route('/trends')
@login_required
def trends():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT year, AVG(trend_score) FROM trend_data GROUP BY year ORDER BY year")
    trend_rows = cursor.fetchall()
    labels = [row[0] for row in trend_rows]
    values = [row[1] for row in trend_rows]
    cursor.execute("""
        SELECT name, color, material, rating 
        FROM clothing_item 
        WHERE rating > 4.0
        FETCH FIRST 3 ROWS ONLY
    """)
    recommendations = [
        {"name": row[0], "color": row[1], "material": row[2], "rating": row[3]} 
        for row in cursor.fetchall()
    ]

    cursor.close()
    conn.close()

    return render_template("trends.html",
                       labels=labels,
                       values=values,
                       recommendations=recommendations,
                       user=current_user)

@views.route('/womentrends')
@login_required
def womentrends():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name
        FROM clothing_item
        WHERE gender_target IN ('female','unisex')
        FETCH FIRST 4 ROWS ONLY
    """)

    items = []
    labels = None

    for row in cursor.fetchall():

        item_id = row[0]
        name = row[1]

        cursor.execute("""
            SELECT year, popularity
            FROM trend_data
            WHERE clothing_id = :1
            ORDER BY year
        """, [item_id])

        trend_rows = cursor.fetchall()

        labels = [r[0] for r in trend_rows]
        values = [r[1] for r in trend_rows]

        items.append({
            "name": name,
            "image": f"{name.lower().replace(' ','_')}.jpg",
            "values": values
        })

    cursor.close()
    conn.close()

    return render_template(
        "womentrends.html",
        items=items,
        labels=labels,
        user=current_user
    )

@views.route('/mentrends')
@login_required
def mentrends():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name
        FROM clothing_item
        WHERE gender_target IN ('male','unisex')
        FETCH FIRST 4 ROWS ONLY
    """)

    items = []
    labels = None

    for row in cursor.fetchall():

        item_id = row[0]
        name = row[1]

        cursor.execute("""
            SELECT year, popularity
            FROM trend_data
            WHERE clothing_id = :1
            ORDER BY year
        """, [item_id])

        trend_rows = cursor.fetchall()

        labels = [r[0] for r in trend_rows]
        values = [r[1] for r in trend_rows]

        items.append({
            "name": name,
            "image": f"{name.lower().replace(' ','_')}.jpg",
            "values": values
        })

    cursor.close()
    conn.close()

    return render_template(
        "mentrends.html",
        items=items,
        labels=labels,
        user=current_user
    )