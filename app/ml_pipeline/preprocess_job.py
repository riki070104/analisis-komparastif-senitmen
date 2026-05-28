import os
from ..extensions import db
from ..models import Dataset
from .preprocessing_utils import preprocess_text

def run_preprocessing_task(app_context_provider, status_callback=None):
    """
    Fungsi untuk melakukan preprocessing pada data yang belum diproses.
    app_context_provider dipanggil untuk memberikan konteks database Flask.
    """
    def update_status(msg, prog):
        print(msg)
        if status_callback:
            status_callback(msg, prog)

    try:
        update_status("Menghitung data yang belum diproses...", 5)
        
        # Harus dipanggil di dalam app_context
        with app_context_provider():
            datasets = Dataset.query.filter(
                (Dataset.cleaned_text == None) | (Dataset.cleaned_text == '')
            ).all()
            
            total = len(datasets)
            if total == 0:
                update_status("Semua data sudah berstatus Preprocessed!", 100)
                return True
                
            update_status(f"Memulai preprocessing untuk {total} data...", 10)
            
            for i, data in enumerate(datasets):
                # Lakukan preprocessing
                data.cleaned_text = preprocess_text(data.text)
                
                # Update progress setiap 100 baris atau di akhir
                if (i + 1) % 100 == 0 or (i + 1) == total:
                    progress = 10 + int((i + 1) / total * 80)
                    update_status(f"Memproses baris {i+1} dari {total}...", progress)
                    # Commit batch kecil agar aman untuk memori
                    db.session.commit()
            
            # Commit sisa
            db.session.commit()
            
        update_status("Selesai! Preprocessing berhasil.", 100)
        return True
        
    except Exception as e:
        update_status(f"Error saat preprocessing: {e}", 0)
        return False
