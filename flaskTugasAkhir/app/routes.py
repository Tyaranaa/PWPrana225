from flask import Blueprint, jsonify, request, render_template, flash, session, redirect, url_for
from . import db
from .models import User
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Anda harus login terlebih dahulu.', 'danger')
        return redirect(url_for('main.login'))
    
    users = User.query.all()
    
    current_user_role = session.get('role', None)
    
    return render_template('dashboard.html', users=users, current_user_role=current_user_role)

def dashboard_():
    # Pastikan pengguna telah login
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu.', 'danger')
        return redirect(url_for('main.login'))

    # Dapatkan semua pengguna untuk ditampilkan di dashboard (hanya admin)
    if session.get('role') == 'admin':
        users = User.query.all()  # Admin melihat semua pengguna
    else:
        users = [User.query.get(session['user_id'])]  # User hanya melihat dirinya sendiri
    
    return render_template('dashboard.html', users=users, current_user_role=session.get('role'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Validasi input
        if not username or not email or not password:
            flash('All fields are required!', 'danger')
            return redirect(url_for('main.register'))

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return redirect(url_for('main.register'))

        # Periksa apakah email sudah terdaftar
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email is already registered. Please use a different email.', 'danger')
            return redirect(url_for('main.register'))

        # Tambahkan pengguna baru
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password, role='user')
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('main.login'))
        except IntegrityError:
            db.session.rollback()
            flash('An unexpected error occurred. Please try again.', 'danger')
            return redirect(url_for('main.register'))

    return render_template('register.html')

   # Endpoint untuk login dan menghasilkan JWT
@main.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role

            flash('Login berhasil!', 'success')
            return redirect(url_for('main.dashboard'))
        
        flash('Username atau password salah', 'danger')
        return redirect(url_for('main.login'))

    return render_template('login.html')

@main.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout.', 'success')
    return redirect(url_for('main.home'))

@main.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    # Hanya admin yang bisa mengakses
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Anda tidak memiliki izin untuk mengakses halaman ini.', 'danger')
        return redirect(url_for('main.dashboard'))

    # Ambil data pengguna
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        # Update data pengguna
        user.username = request.form['username']
        user.email = request.form['email']
        user.role = request.form['role']

        db.session.commit()
        flash('User berhasil diupdate!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('edit_user.html', user=user)


@main.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    # Hanya admin yang bisa menghapus pengguna
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Anda tidak memiliki izin untuk mengakses halaman ini.', 'danger')
        return redirect(url_for('main.dashboard'))

    # Hapus pengguna
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User berhasil dihapus!', 'success')
    return redirect(url_for('main.dashboard'))