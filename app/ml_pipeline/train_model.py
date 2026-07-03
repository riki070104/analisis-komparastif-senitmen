import os
import pickle
import json
import random
import pandas as pd

# Karena file ini sekarang berada di dalam folder ml_pipeline,
# import preprocessing dan model menggunakan path lokal.
from .preprocessing_utils import preprocess_text
from .custom_ml import CustomTfidfVectorizer, CustomRandomForest

def train_from_data(preprocessed_texts, labels, app_targets=None, status_callback=None):
    """
    Melatih model menggunakan list of texts yang sudah di-preprocess dan labels.
    Termasuk melakukan split 80:20 dan menyimpan hasil evaluasi test set.
    """
    # Mengunci seed agar hasil Random Forest konsisten (reproducible) untuk skripsi
    random.seed(42)
    
    def update_status(msg, prog):
        print(msg)
        if status_callback:
            status_callback(msg, prog)

    try:
        update_status("Memvalidasi data...", 5)
        if not preprocessed_texts or not labels or len(preprocessed_texts) != len(labels):
            update_status("Error: Data teks dan label kosong atau tidak seimbang.", 0)
            return False
            
        df = pd.DataFrame({'cleaned_text': preprocessed_texts, 'label': labels})
        if app_targets and len(app_targets) == len(labels):
            df['app_target'] = app_targets
        else:
            df['app_target'] = 'Unknown'
            
        update_status("Tahap 1: Membersihkan baris kosong...", 10)
        df = df[df['cleaned_text'].str.strip() != ""]
        df = df.dropna(subset=['cleaned_text', 'label'])
        
        if len(df) == 0:
            update_status("Error: Tidak ada data valid tersisa untuk dilatih.", 0)
            return False
            
        # Shuffle dataset
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        splits = [0.8, 0.75, 0.7]
        eval_results_dict = {}
        
        saved_vectorizer = None
        saved_model = None
        saved_test_df = None

        for idx, train_ratio in enumerate(splits):
            ratio_key = str(int(train_ratio * 100))
            
            update_status(f"Tahap {2 + idx*3}: Memisahkan {ratio_key}% Data Latih...", 15 + idx*25)
            split_idx = int(len(df) * train_ratio)
            train_df = df.iloc[:split_idx]
            test_df = df.iloc[split_idx:].copy()
            
            update_status(f"Tahap {3 + idx*3}: Ekstraksi Fitur TF-IDF ({ratio_key}%)...", 20 + idx*25)
            vectorizer = CustomTfidfVectorizer(max_features=1500)
            X_train = vectorizer.fit_transform(train_df['cleaned_text'].tolist())
            y_train = train_df['label'].tolist()
            
            update_status(f"Tahap {4 + idx*3}: Melatih Random Forest ({ratio_key}%)...", 25 + idx*25)
            rf_model = CustomRandomForest(n_estimators=50, max_depth=None)
            rf_model.fit(X_train, y_train)
            
            if train_ratio == 0.8:
                saved_vectorizer = vectorizer
                saved_model = rf_model
                
            update_status(f"Mengevaluasi Model ({ratio_key}%)...", 30 + idx*25)
            X_test = vectorizer.transform(test_df['cleaned_text'].tolist())
            y_test = test_df['label'].tolist()
            y_pred = rf_model.predict(X_test)
            
            # Simpan prediksi untuk kalkulasi komparasi pada testing data
            test_df['predicted_label'] = y_pred
            
            if train_ratio == 0.8:
                saved_test_df = test_df.copy()
            
            # Kalkulasi Metrik (Confusion Matrix & Precision/Recall/F1)
            labels_order = ['positive', 'negative', 'neutral']
            matrix = {actual: {pred: 0 for pred in labels_order} for actual in labels_order}
            correct_predictions = 0
            total_samples = len(y_test)
            
            for actual, pred in zip(y_test, y_pred):
                if actual in labels_order and pred in labels_order:
                    matrix[actual][pred] += 1
                    if actual == pred:
                        correct_predictions += 1
                        
            accuracy = (correct_predictions / total_samples) * 100 if total_samples > 0 else 0
            
            metrics = {}
            for label in labels_order:
                tp = matrix[label][label]
                fp = sum(matrix[actual][label] for actual in labels_order) - tp
                fn = sum(matrix[label][pred] for pred in labels_order) - tp
                
                precision = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else 0
                recall = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else 0
                f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                
                metrics[label] = {
                    'precision': round(precision, 2),
                    'recall': round(recall, 2),
                    'f1': round(f1, 2),
                    'support': tp + fn
                }
                
            # Kalkulasi Komparasi di Data Testing
            chatgpt_test = test_df[test_df['app_target'] == 'ChatGPT']
            gemini_test = test_df[test_df['app_target'] == 'Gemini']
            
            test_comparison_stats = {
                'chatgpt_pos': len(chatgpt_test[chatgpt_test['predicted_label'] == 'positive']),
                'chatgpt_neg': len(chatgpt_test[chatgpt_test['predicted_label'] == 'negative']),
                'chatgpt_neu': len(chatgpt_test[chatgpt_test['predicted_label'] == 'neutral']),
                'gemini_pos': len(gemini_test[gemini_test['predicted_label'] == 'positive']),
                'gemini_neg': len(gemini_test[gemini_test['predicted_label'] == 'negative']),
                'gemini_neu': len(gemini_test[gemini_test['predicted_label'] == 'neutral'])
            }
                
            eval_results_dict[ratio_key] = {
                'accuracy': round(accuracy, 2),
                'matrix': matrix,
                'metrics': metrics,
                'total_samples': total_samples,
                'labels': labels_order,
                'train_samples': len(train_df),
                'test_comparison_stats': test_comparison_stats
            }
        
        update_status("Menyimpan model & hasil evaluasi...", 90)
        model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'model')
        os.makedirs(model_dir, exist_ok=True)
        
        with open(os.path.join(model_dir, 'vectorizer.pkl'), 'wb') as f:
            pickle.dump(saved_vectorizer, f)
            
        with open(os.path.join(model_dir, 'rf_model.pkl'), 'wb') as f:
            pickle.dump(saved_model, f)
            
        with open(os.path.join(model_dir, 'eval_metrics.json'), 'w') as f:
            json.dump(eval_results_dict, f, indent=4)
            
        if saved_test_df is not None:
            # Format: [{"text": "...", "app_target": "ChatGPT", "predicted_label": "positive"}, ...]
            test_predictions = saved_test_df[['cleaned_text', 'app_target', 'predicted_label']].rename(columns={'cleaned_text': 'text'}).to_dict('records')
            with open(os.path.join(model_dir, 'test_predictions.json'), 'w') as f:
                json.dump(test_predictions, f, indent=4)
        
        update_status("Selesai! Model berhasil dilatih pada berbagai skenario.", 100)
        return True
    except Exception as e:
        update_status(f"Error saat training: {e}", 0)
        return False
