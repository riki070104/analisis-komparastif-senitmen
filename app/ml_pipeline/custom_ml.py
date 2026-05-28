import math
import random
from collections import Counter

class CustomTfidfVectorizer:
    """Implementasi manual TF-IDF Vectorizer semirip mungkin dengan scikit-learn"""
    def __init__(self, max_features=1500):
        self.max_features = max_features
        self.vocabulary = {}
        self.idf = {}
        
    def _tokenize(self, text):
        # Mengembalikan list kata tanpa duplikasi kosong
        return text.split()
        
    def fit(self, raw_documents):
        # 1. Hitung frekuensi dokumen (DF)
        df_counts = Counter()
        n_docs = len(raw_documents)
        
        for doc in raw_documents:
            words = set(self._tokenize(doc))
            for word in words:
                df_counts[word] += 1
                
        # 2. Ambil kata terbanyak (max_features) dan urutkan secara alfabetikal (agar deterministik)
        top_words = [word for word, count in df_counts.most_common(self.max_features)]
        self.vocabulary = {word: idx for idx, word in enumerate(sorted(top_words))}
        
        # 3. Hitung Smooth IDF (Sesuai dengan sklearn: log((N+1)/(df+1)) + 1)
        for word, df in df_counts.items():
            if word in self.vocabulary:
                self.idf[word] = math.log((n_docs + 1.0) / (df + 1.0)) + 1.0
        
        return self
        
    def transform(self, raw_documents):
        matrix = []
        for doc in raw_documents:
            words = self._tokenize(doc)
            word_counts = Counter(words)
            
            row = [0.0] * len(self.vocabulary)
            
            for word, count in word_counts.items():
                if word in self.vocabulary:
                    # Term frequency biasa (standar sklearn TfidfVectorizer default)
                    tf = float(count)
                    idx = self.vocabulary[word]
                    row[idx] = tf * self.idf[word]
            
            # L2 Normalization (standar sklearn)
            norm = math.sqrt(sum(val ** 2 for val in row))
            if norm > 0:
                row = [val / norm for val in row]
                
            matrix.append(row)
            
        return matrix
        
    def fit_transform(self, raw_documents):
        self.fit(raw_documents)
        return self.transform(raw_documents)


class CustomDecisionTree:
    """Implementasi Decision Tree Classifier berbasis CART (O(N) splitting)"""
    def __init__(self, max_depth=None):
        self.max_depth = max_depth if max_depth is not None else float('inf')
        self.tree = None
        
    class Node:
        def __init__(self, feature_idx=None, threshold=None, left=None, right=None, value=None):
            self.feature_idx = feature_idx
            self.threshold = threshold
            self.left = left
            self.right = right
            self.value = value
            
    def _best_split(self, X, y, n_features):
        best_gini = float('inf')
        best_criteria = None
        
        n_samples = len(y)
        total_features = len(X[0])
        
        # Random subset fitur untuk Random Forest (sqrt(n_features))
        feature_indices = random.sample(range(total_features), n_features)
        
        for feature_idx in feature_indices:
            # Pasangkan fitur dengan label dan simpan nilai asli indeks
            feature_values = [(X[i][feature_idx], y[i], i) for i in range(n_samples)]
            # Urutkan berdasarkan nilai fitur (O(N log N))
            feature_values.sort(key=lambda x: x[0])
            
            # Persiapkan Counter untuk kalkulasi Gini O(N) (Incremental Gini)
            right_counts = Counter(y)
            left_counts = Counter()
            total_right = n_samples
            total_left = 0
            
            for i in range(1, n_samples):
                val, label, orig_idx = feature_values[i-1]
                
                # Pindahkan 1 item dari kanan ke kiri
                left_counts[label] += 1
                right_counts[label] -= 1
                total_left += 1
                total_right -= 1
                
                next_val = feature_values[i][0]
                # Hanya evaluasi threshold jika nilainya berbeda dengan nilai berikutnya
                if val == next_val:
                    continue
                    
                # Hitung gini kiri
                gini_left = 1.0 - sum((c / total_left) ** 2 for c in left_counts.values()) if total_left > 0 else 0.0
                # Hitung gini kanan
                gini_right = 1.0 - sum((c / total_right) ** 2 for c in right_counts.values()) if total_right > 0 else 0.0
                # Gabungan
                gini = (total_left * gini_left + total_right * gini_right) / n_samples
                
                if gini < best_gini:
                    best_gini = gini
                    best_criteria = (feature_idx, (val + next_val) / 2.0)
                    
        # Rekonstruksi best_sets berdasarkan kriteria absolut terbaik
        if best_criteria is None:
            return float('inf'), None, None
            
        best_feature, best_threshold = best_criteria
        left_idx = [i for i in range(n_samples) if X[i][best_feature] <= best_threshold]
        right_idx = [i for i in range(n_samples) if X[i][best_feature] > best_threshold]
        
        return best_gini, best_criteria, (left_idx, right_idx)
        
    def _build_tree(self, X, y, depth=0):
        # Base case 1: Semua label sama
        if len(set(y)) == 1:
            return self.Node(value=y[0])
            
        # Base case 2: Kedalaman maksimum tercapai atau data kosong
        if depth >= self.max_depth or not X:
            most_common = Counter(y).most_common(1)[0][0]
            return self.Node(value=most_common)
            
        n_features = max(1, int(math.sqrt(len(X[0]))))
        best_gini, best_criteria, best_sets = self._best_split(X, y, n_features)
        
        # Base case 3: Tidak ditemukan pemisahan yang valid
        if best_gini == float('inf') or not best_sets or not best_sets[0] or not best_sets[1]:
            most_common = Counter(y).most_common(1)[0][0]
            return self.Node(value=most_common)
            
        left_idx, right_idx = best_sets
        feature_idx, threshold = best_criteria
        
        X_left = [X[i] for i in left_idx]
        y_left = [y[i] for i in left_idx]
        X_right = [X[i] for i in right_idx]
        y_right = [y[i] for i in right_idx]
        
        left_branch = self._build_tree(X_left, y_left, depth + 1)
        right_branch = self._build_tree(X_right, y_right, depth + 1)
        
        return self.Node(feature_idx=feature_idx, threshold=threshold, left=left_branch, right=right_branch)
        
    def fit(self, X, y):
        self.tree = self._build_tree(X, y)
        
    def _predict_single(self, x, tree):
        if tree.value is not None:
            return tree.value
            
        val = x[tree.feature_idx]
        if val <= tree.threshold:
            return self._predict_single(x, tree.left)
        else:
            return self._predict_single(x, tree.right)
            
    def predict(self, X):
        return [self._predict_single(x, self.tree) for x in X]


class CustomRandomForest:
    """Implementasi manual Random Forest dari gabungan Decision Tree kustom"""
    def __init__(self, n_estimators=50, max_depth=None):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.trees = []
        
    def fit(self, X, y):
        self.trees = []
        n_samples = len(X)
        
        for _ in range(self.n_estimators):
            # Menerapkan Konsep Bagging (Bootstrap Aggregating)
            indices = [random.randint(0, n_samples - 1) for _ in range(n_samples)]
            X_sample = [X[i] for i in indices]
            y_sample = [y[i] for i in indices]
            
            tree = CustomDecisionTree(max_depth=self.max_depth)
            tree.fit(X_sample, y_sample)
            self.trees.append(tree)
            
    def predict(self, X):
        predictions = []
        for x in X:
            tree_preds = [tree._predict_single(x, tree.tree) for tree in self.trees]
            most_common = Counter(tree_preds).most_common(1)[0][0]
            predictions.append(most_common)
        return predictions
        
    def predict_proba(self, X):
        probabilities = []
        for x in X:
            tree_preds = [tree._predict_single(x, tree.tree) for tree in self.trees]
            counts = Counter(tree_preds)
            total = len(self.trees)
            
            prob_dict = {
                'positive': counts.get('positive', 0) / total,
                'negative': counts.get('negative', 0) / total,
                'neutral': counts.get('neutral', 0) / total
            }
            
            probabilities.append([prob_dict['positive'], prob_dict['negative'], prob_dict['neutral']])
            
        return probabilities
