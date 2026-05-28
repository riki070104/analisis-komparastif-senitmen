from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from .extensions import db
from .models import Dataset
from .sentiment_model import analyze_sentiment
from sqlalchemy import desc

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    app_target = request.args.get('app', None)  # ChatGPT atau Gemini
    
    chart_data = None
    reviews = []
    global_stats = None
    
    if app_target:
        # Ambil data sentimen dari dataset berdasarkan aplikasi yang dipilih
        datasets = Dataset.query.filter_by(app_target=app_target).filter(Dataset.cleaned_text != None).all()
        
        total_pos = sum(1 for d in datasets if d.label == 'positive')
        total_neg = sum(1 for d in datasets if d.label == 'negative')
        total_neu = sum(1 for d in datasets if d.label == 'neutral')
        
        chart_data = {
            'positive': total_pos,
            'negative': total_neg,
            'neutral': total_neu,
            'total': len(datasets)
        }
        
        # Ambil 50 ulasan terbaru untuk ditampilkan
        reviews = Dataset.query.filter_by(app_target=app_target).filter(Dataset.cleaned_text != None).order_by(desc(Dataset.created_at)).limit(50).all()
    else:
        # Tampilkan ringkasan global
        datasets = Dataset.query.filter(Dataset.cleaned_text != None).all()
        
        total_pos = sum(1 for d in datasets if d.label == 'positive')
        total_neg = sum(1 for d in datasets if d.label == 'negative')
        total_neu = sum(1 for d in datasets if d.label == 'neutral')
        
        global_stats = {
            'positive': total_pos,
            'negative': total_neg,
            'neutral': total_neu,
            'total': len(datasets)
        }
        
        # Ambil 50 ulasan terbaru gabungan
        reviews = Dataset.query.filter(Dataset.cleaned_text != None).order_by(desc(Dataset.created_at)).limit(50).all()
    
    return render_template('index.html', app_target=app_target, chart_data=chart_data, reviews=reviews, global_stats=global_stats)

@main_bp.route('/home')
@login_required
def home():
    return redirect(url_for('main.beranda'))

@main_bp.route('/beranda')
@login_required
def beranda():
    # Get statistics for ChatGPT
    chatgpt_pos = Dataset.query.filter_by(user_id=current_user.id, app_target='ChatGPT', label='positive').count()
    chatgpt_neg = Dataset.query.filter_by(user_id=current_user.id, app_target='ChatGPT', label='negative').count()
    chatgpt_neu = Dataset.query.filter_by(user_id=current_user.id, app_target='ChatGPT', label='neutral').count()

    # Get statistics for Gemini
    gemini_pos = Dataset.query.filter_by(user_id=current_user.id, app_target='Gemini', label='positive').count()
    gemini_neg = Dataset.query.filter_by(user_id=current_user.id, app_target='Gemini', label='negative').count()
    gemini_neu = Dataset.query.filter_by(user_id=current_user.id, app_target='Gemini', label='neutral').count()
    
    # Get recent datasets
    recent_histories = Dataset.query.filter_by(user_id=current_user.id)\
        .order_by(desc(Dataset.created_at)).limit(5).all()
        
    total_datasets = Dataset.query.filter_by(user_id=current_user.id).count()
    total_processed = Dataset.query.filter_by(user_id=current_user.id).filter(Dataset.cleaned_text != None).count()
    total_unprocessed = total_datasets - total_processed
    
    return render_template('admin/beranda.html',
                         total_analyses=total_datasets,
                         total_processed=total_processed,
                         total_unprocessed=total_unprocessed,
                         chatgpt_pos=chatgpt_pos, chatgpt_neg=chatgpt_neg, chatgpt_neu=chatgpt_neu,
                         gemini_pos=gemini_pos, gemini_neg=gemini_neg, gemini_neu=gemini_neu,
                         recent_histories=recent_histories)


@main_bp.route('/dataset')
@login_required
def dataset_list():
    page = request.args.get('page', 1, type=int)
    datasets = Dataset.query.filter_by(user_id=current_user.id)\
        .order_by(desc(Dataset.created_at))\
        .paginate(page=page, per_page=10)
        
    # Hitung distribusi sentimen untuk Chart Bias
    total_pos = Dataset.query.filter_by(user_id=current_user.id, label='positive').count()
    total_neg = Dataset.query.filter_by(user_id=current_user.id, label='negative').count()
    total_neu = Dataset.query.filter_by(user_id=current_user.id, label='neutral').count()
    
    return render_template('admin/dataset/index.html', 
                         datasets=datasets,
                         total_pos=total_pos,
                         total_neg=total_neg,
                         total_neu=total_neu)

@main_bp.route('/dataset/import', methods=['GET', 'POST'])
@login_required
def dataset_import():
    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        if not uploaded_file or uploaded_file.filename == '':
            flash('Silakan pilih file CSV atau XLSX terlebih dahulu.', 'warning')
            return redirect(url_for('main.dataset_import'))

        filename = uploaded_file.filename.lower()
        allowed_extensions = ('.csv', '.xlsx', '.xls')
        if not filename.endswith(allowed_extensions):
            flash('Format file tidak didukung. Gunakan CSV, XLSX, atau XLS.', 'danger')
            return redirect(url_for('main.dataset_import'))

        try:
            import pandas as pd
            from io import BytesIO
            file_data = uploaded_file.read()
            if filename.endswith('.csv'):
                df = pd.read_csv(BytesIO(file_data), encoding='utf-8', dtype=str)
            else:
                df = pd.read_excel(BytesIO(file_data), dtype=str)
        except Exception as error:
            flash(f'Gagal membaca file: {error}', 'danger')
            return redirect(url_for('main.dataset_import'))

        if df.empty:
            flash('File kosong atau tidak berisi data valid.', 'warning')
            return redirect(url_for('main.dataset_import'))

        df.columns = [str(col).strip().lower() for col in df.columns]
        text_column = None
        label_column = None

        for candidate in ['text', 'content', 'cleaned_content', 'konten_review', 'ulasan', 'review', 'review_text']:
            if candidate in df.columns:
                text_column = candidate
                break

        for candidate in ['label', 'sentiment_label', 'sentiment']:
            if candidate in df.columns:
                label_column = candidate
                break

        if text_column is None and len(df.columns) >= 2:
            text_column = df.columns[0]
        if label_column is None and len(df.columns) >= 2:
            label_column = df.columns[1]

        if text_column is None or label_column is None:
            flash('File harus berisi kolom teks dan label.', 'danger')
            return redirect(url_for('main.dataset_import'))

        label_map = {
            'positive': 'positive', 'positif': 'positive', 'pos': 'positive', 'p': 'positive',
            'negative': 'negative', 'negatif': 'negative', 'neg': 'negative', 'n': 'negative',
            'neutral': 'neutral', 'netral': 'neutral', 'none': 'neutral', 'mixed': 'neutral'
        }

        def normalize_label(value):
            if value is None:
                return None
            label_text = str(value).strip().lower()
            if label_text in label_map:
                return label_map[label_text]
            try:
                score = float(label_text)
                if score <= 2:
                    return 'negative'
                if score == 3:
                    return 'neutral'
                if score >= 4:
                    return 'positive'
            except ValueError:
                pass
            # fallback if raw value contains one of the keywords
            for key, mapped in label_map.items():
                if key in label_text:
                    return mapped
            return None

        app_target = request.form.get('app_target') or None

        imported = 0
        for _, row in df.iterrows():
            text = str(row.get(text_column, '') or '').strip()
            label = normalize_label(row.get(label_column, ''))
            if not text or not label:
                continue
            dataset = Dataset(user_id=current_user.id, text=text, label=label, app_target=app_target)
            db.session.add(dataset)
            imported += 1

        if imported > 0:
            db.session.commit()
            flash(f'Berhasil mengimpor {imported} baris dataset.', 'success')
        else:
            flash('Tidak ada baris valid untuk diimpor. Pastikan kolom text dan label benar.', 'warning')
        return redirect(url_for('main.dataset_list'))

    return render_template('admin/dataset/import.html')

@main_bp.route('/dataset/add', methods=['GET', 'POST'])
@login_required
def dataset_add():
    if request.method == 'POST':
        text = request.form.get('text', '').strip()
        label = request.form.get('label', '').strip()
        app_target = request.form.get('app_target', '')
        
        if not text or not label:
            flash('Semua field harus diisi.', 'warning')
            return redirect(url_for('main.dataset_add'))
        
        if label not in ['positive', 'negative', 'neutral']:
            flash('Label tidak valid.', 'danger')
            return redirect(url_for('main.dataset_add'))
        
        if len(text) > 5000:
            flash('Teks terlalu panjang.', 'danger')
            return redirect(url_for('main.dataset_add'))
        
        dataset = Dataset(
            user_id=current_user.id,
            text=text,
            label=label,
            app_target=app_target
        )
        db.session.add(dataset)
        db.session.commit()
        
        flash('Data berhasil ditambahkan.', 'success')
        return redirect(url_for('main.dataset_list'))
    
    return render_template('admin/dataset/add.html')

@main_bp.route('/dataset/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def dataset_edit(id):
    dataset = Dataset.query.get_or_404(id)
    
    if dataset.user_id != current_user.id:
        flash('Tidak memiliki akses.', 'danger')
        return redirect(url_for('main.dataset_list'))
    
    if request.method == 'POST':
        text = request.form.get('text', '').strip()
        label = request.form.get('label', '').strip()
        app_target = request.form.get('app_target', '')
        
        if not text or not label:
            flash('Semua field harus diisi.', 'warning')
            return redirect(url_for('main.dataset_edit', id=id))
        
        if label not in ['positive', 'negative', 'neutral']:
            flash('Label tidak valid.', 'danger')
            return redirect(url_for('main.dataset_edit', id=id))
        
        if len(text) > 5000:
            flash('Teks terlalu panjang.', 'danger')
            return redirect(url_for('main.dataset_edit', id=id))
        
        dataset.text = text
        dataset.label = label
        dataset.app_target = app_target
        db.session.commit()
        
        flash('Data berhasil diperbarui.', 'success')
        return redirect(url_for('main.dataset_list'))
    
    return render_template('admin/dataset/edit.html', dataset=dataset)

@main_bp.route('/dataset/delete/<int:id>', methods=['POST'])
@login_required
def dataset_delete(id):
    dataset = Dataset.query.get_or_404(id)
    
    if dataset.user_id != current_user.id:
        flash('Tidak memiliki akses.', 'danger')
        return redirect(url_for('main.dataset_list'))
    
    db.session.delete(dataset)
    db.session.commit()
    
    flash('Data berhasil dihapus.', 'success')
    return redirect(url_for('main.dataset_list'))

@main_bp.route('/dataset/preview_preprocess/<int:id>')
@login_required
def preview_preprocess(id):
    dataset = Dataset.query.get_or_404(id)
    
    if dataset.user_id != current_user.id:
        return jsonify({'error': 'Tidak memiliki akses.'}), 403
    
    from .ml_pipeline.preprocessing_utils import preprocess_text_detailed
    steps = preprocess_text_detailed(dataset.text)
    
    return jsonify(steps)

@main_bp.route('/about')
def about():
    return render_template('admin/about.html')

@main_bp.route('/tentang')
def tentang_user():
    return render_template('tentang.html')

@main_bp.route('/preprocessing')
@login_required
def preprocessing():
    unprocessed_count = Dataset.query.filter(Dataset.cleaned_text == None).count()
    processed_count = Dataset.query.filter(Dataset.cleaned_text != None).count()
    return render_template('admin/preprocessing.html', unprocessed_count=unprocessed_count, processed_count=processed_count)

@main_bp.route('/klasifikasi')
@login_required
def klasifikasi():
    processed_count = Dataset.query.filter(Dataset.cleaned_text != None).count()
    
    # Ambil sample data untuk ditampilkan sebagai "Hasil Klasifikasi" (jika model sudah ada)
    sample_data = Dataset.query.filter(Dataset.cleaned_text != None).order_by(Dataset.id.desc()).limit(10).all()
    classification_results = []
    
    if sample_data:
        try:
            # Cek apakah model bisa digunakan
            # Kita coba prediksi 1 data saja untuk memastikan model sudah dilatih
            analyze_sentiment("test")
            model_ready = True
        except Exception:
            model_ready = False
            
        if model_ready:
            for data in sample_data:
                pred_label, conf = analyze_sentiment(data.text)
                classification_results.append({
                    'text': data.text,
                    'actual': data.label,
                    'predicted': pred_label,
                    'confidence': conf
                })
                               
    return render_template('admin/klasifikasi.html', 
                           processed_count=processed_count,
                           classification_results=classification_results)

import threading

# Status training global sederhana
TRAINING_STATUS = {
    "is_training": False,
    "is_preprocessing": False,
    "progress": 0,
    "message": ""
}

def update_training_status(msg, prog):
    global TRAINING_STATUS
    TRAINING_STATUS["message"] = msg
    TRAINING_STATUS["progress"] = prog

def run_preprocessing_job(app):
    global TRAINING_STATUS
    TRAINING_STATUS["is_preprocessing"] = True
    TRAINING_STATUS["progress"] = 0
    TRAINING_STATUS["message"] = "Menyiapkan data untuk preprocessing..."
    
    from .ml_pipeline.preprocess_job import run_preprocessing_task
    
    # We pass app.app_context as a provider so the thread can access the DB
    success = run_preprocessing_task(app.app_context, status_callback=update_training_status)
    
    TRAINING_STATUS["is_preprocessing"] = False
    if success:
        TRAINING_STATUS["message"] = "Selesai! Teks berhasil dibersihkan."
        TRAINING_STATUS["progress"] = 100
    else:
        TRAINING_STATUS["message"] = "Gagal memproses teks. Periksa log."

def run_training_job(preprocessed_texts, labels):
    global TRAINING_STATUS
    TRAINING_STATUS["is_training"] = True
    TRAINING_STATUS["progress"] = 0
    TRAINING_STATUS["message"] = "Menyiapkan data training..."
    
    from .ml_pipeline.train_model import train_from_data
    success = train_from_data(preprocessed_texts, labels, status_callback=update_training_status)
    
    TRAINING_STATUS["is_training"] = False
    if success:
        TRAINING_STATUS["message"] = "Selesai! Model berhasil dilatih."
        TRAINING_STATUS["progress"] = 100
    else:
        TRAINING_STATUS["message"] = "Gagal melatih model. Periksa log."

@main_bp.route('/dataset/preprocess', methods=['POST'])
@login_required
def preprocess_dataset():
    global TRAINING_STATUS
    if TRAINING_STATUS["is_training"] or TRAINING_STATUS["is_preprocessing"]:
        flash('Proses latar belakang sedang berjalan. Harap tunggu.', 'warning')
        return redirect(url_for('main.preprocessing'))
        
    from flask import current_app
    app = current_app._get_current_object()
    
    thread = threading.Thread(target=run_preprocessing_job, args=(app,))
    thread.daemon = True
    thread.start()
    
    flash('Proses Preprocessing telah dimulai di latar belakang.', 'info')
    return redirect(url_for('main.preprocessing'))

@main_bp.route('/dataset/train', methods=['POST'])
@login_required
def train_model():
    global TRAINING_STATUS
    if TRAINING_STATUS["is_training"] or TRAINING_STATUS["is_preprocessing"]:
        flash('Proses latar belakang sedang berjalan. Harap tunggu.', 'warning')
        return redirect(url_for('main.klasifikasi'))
        
    datasets = Dataset.query.filter(Dataset.cleaned_text != None, Dataset.cleaned_text != '').all()
    if len(datasets) < 10:
        flash('Data yang sudah di-preprocess terlalu sedikit (minimal 10). Jalankan Preprocessing dulu!', 'danger')
        return redirect(url_for('main.klasifikasi'))
        
    texts = [d.cleaned_text for d in datasets]
    labels = [d.label for d in datasets]
    
    # Jalankan training di background agar tidak timeout
    thread = threading.Thread(target=run_training_job, args=(texts, labels))
    thread.daemon = True
    thread.start()
    
    flash('Proses training telah dimulai di latar belakang.', 'info')
    return redirect(url_for('main.klasifikasi'))

@main_bp.route('/dataset/train/status')
@login_required
def train_status():
    global TRAINING_STATUS
    return jsonify(TRAINING_STATUS)

@main_bp.route('/evaluasi')
@login_required
def evaluasi():
    import os, json
    
    # Baca hasil evaluasi dari file JSON
    model_dir = os.path.join(os.path.dirname(__file__), 'model')
    eval_file = os.path.join(model_dir, 'eval_metrics.json')
    
    if os.path.exists(eval_file):
        try:
            with open(eval_file, 'r') as f:
                eval_data = json.load(f)
                
            return render_template('admin/evaluasi.html',
                                 matrix=eval_data['matrix'],
                                 accuracy=eval_data['accuracy'],
                                 metrics=eval_data['metrics'],
                                 total_samples=eval_data['total_samples'],
                                 labels=eval_data['labels'],
                                 train_samples=eval_data.get('train_samples', 0))
        except Exception as e:
            flash(f'Gagal membaca hasil evaluasi: {str(e)}', 'danger')
            
    return render_template('admin/evaluasi.html')

@main_bp.route('/evaluasi/run', methods=['POST'])
@login_required
def evaluasi_run():
    # Evaluasi sekarang sepenuhnya otomatis setelah training.
    # Route ini dipertahankan jika pengguna menekan tombol evaluasi manual,
    # cukup redirect ke halaman evaluasi biasa yang langsung memuat JSON.
    flash('Evaluasi sekarang dilakukan otomatis bersamaan dengan Training. Hasil di bawah adalah hasil Evaluasi terbaru (Rasio 80:20).', 'info')
    return redirect(url_for('main.evaluasi'))

@main_bp.route('/api/predict', methods=['POST'])
@login_required
def api_predict():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Teks tidak ditemukan.'}), 400
        
    text = data['text'].strip()
    if not text:
        return jsonify({'error': 'Teks tidak boleh kosong.'}), 400
        
    try:
        from .sentiment_model import analyze_sentiment
        sentiment, confidence = analyze_sentiment(text)
        return jsonify({
            'sentiment': sentiment,
            'confidence': confidence,
            'text': text
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


