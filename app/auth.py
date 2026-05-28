from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from .extensions import db
from .models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # Validate
        if not username or not email or not password:
            flash('Semua field harus diisi.', 'danger')
            return redirect(url_for('auth.register'))
        
        if password != password_confirm:
            flash('Password tidak sama.', 'danger')
            return redirect(url_for('auth.register'))
        
        if len(password) < 6:
            flash('Password minimal 6 karakter.', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username sudah terdaftar.', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email sudah terdaftar.', 'danger')
            return redirect(url_for('auth.register'))
        
        # Create user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.beranda'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login berhasil!', 'success')
            return redirect(url_for('main.beranda'))
        else:
            flash('Username atau password salah.', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('main.index'))
