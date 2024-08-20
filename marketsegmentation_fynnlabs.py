# -*- coding: utf-8 -*-
"""marketsegmentation_fynnlabs

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1UFUwihMN74MvQYt_wxuPi1LyqIBA-qqh
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score, confusion_matrix, classification_report, accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from scipy.cluster.hierarchy import dendrogram, linkage
import joblib
from statsmodels.graphics.mosaicplot import mosaic
import warnings

# Ignore warnings
warnings.filterwarnings("ignore")

# Load the dataset
data = pd.read_csv("mcdonalds.csv")

# Data preprocessing
data.replace({'Yes': 1, 'No': 0}, inplace=True)

# Convert 'Like' to numeric
data['Like'] = pd.to_numeric(data['Like'], errors='coerce')

# Drop rows with NaN values in 'VisitFrequency' and 'Like' after conversion
data.dropna(subset=['VisitFrequency', 'Like'], inplace=True)

# Feature and target separation for classification
target_col = 'Gender'
features = data.drop(columns=[target_col])
target = data[target_col]

# One-hot encoding for categorical features
features = pd.get_dummies(features)

# Train-test split for gender prediction
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.25, random_state=0)

# Standardizing the features for clustering and PCA
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

# Dimensionality reduction using PCA
pca = PCA(n_components=2)
pca_result = pca.fit_transform(scaled_features)
pca_df = pd.DataFrame(pca_result, columns=['PC1', 'PC2'])

# Perform K-Means clustering
kmeans = KMeans(n_clusters=4, random_state=42)
kmeans_labels = kmeans.fit_predict(pca_df)

# Perform Gaussian Mixture Model clustering
gmm = GaussianMixture(n_components=4, random_state=42)
gmm_labels = gmm.fit_predict(pca_df)

# Perform Agglomerative (Hierarchical) Clustering
agg_clustering = AgglomerativeClustering(n_clusters=4)
agg_labels = agg_clustering.fit_predict(pca_df)

# Visualize dendrogram for hierarchical clustering
plt.figure(figsize=(10, 7))
linkage_matrix = linkage(pca_df, method='ward')
dendrogram(linkage_matrix)
plt.title('Dendrogram for Hierarchical Clustering')
plt.xlabel('Sample Index')
plt.ylabel('Distance')
plt.show()

# Compare K-Means, GMM, and Hierarchical Clustering results using Silhouette Score
sil_kmeans = silhouette_score(pca_df, kmeans_labels)
sil_gmm = silhouette_score(pca_df, gmm_labels)
sil_agg = silhouette_score(pca_df, agg_labels)

print(f"Silhouette Score for K-Means: {sil_kmeans:.3f}")
print(f"Silhouette Score for GMM: {sil_gmm:.3f}")
print(f"Silhouette Score for Hierarchical Clustering: {sil_agg:.3f}")

# Confusion matrix between KMeans and Agglomerative Clustering
conf_matrix = confusion_matrix(kmeans_labels, agg_labels)
print("Confusion Matrix between K-Means and Agglomerative Clustering:\n", conf_matrix)

# Assign segment labels back to original data for further analysis
data['Segment'] = kmeans_labels

# Mosaic plot for Segment vs Like
plt.figure(figsize=(10, 7))
mosaic(data, ['Segment', 'Like'])
plt.title('Mosaic Plot: Segments vs Like')
plt.show()

# RandomForest Classifier with Hyperparameter Tuning using GridSearchCV
# Define the pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('rf', RandomForestClassifier(random_state=0))
])

# Set up the hyperparameter grid for GridSearchCV
param_grid = {
    'rf__n_estimators': [100, 200, 300],
    'rf__max_depth': [None, 10, 20, 30],
    'rf__min_samples_split': [2, 5, 10],
    'rf__min_samples_leaf': [1, 2, 4]
}

# Perform GridSearchCV with 5-fold cross-validation
grid_search = GridSearchCV(pipeline, param_grid, cv=5, n_jobs=-1, scoring='accuracy')
grid_search.fit(X_train, y_train)

# Best hyperparameters and model performance
print("Best Hyperparameters:", grid_search.best_params_)
best_model = grid_search.best_estimator_

# Make predictions and evaluate the model
y_pred = best_model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred):.3f}")
print("Classification Report:\n", classification_report(y_test, y_pred))

# Save the best model
joblib.dump(best_model, 'best_rf_gender_model.pkl')

# Additional visualization for segment profiling
# Convert 'VisitFrequency' to numeric values
data['VisitFrequency'] = data['VisitFrequency'].replace({
    'Never': 0,
    'Once a year': 1,
    'Every three months': 2,
    'Once a month': 3,
    'Once a week': 4,
    'More than once a week': 5
})

# Now calculate the mean visit frequency by segment
visit_freq_mean = data.groupby('Segment')['VisitFrequency'].mean()
like_mean = data.groupby('Segment')['Like'].mean()
female_ratio = data.groupby('Segment')['Gender'].apply(lambda x: (x == 'Female').mean())

plt.figure(figsize=(10, 7))
plt.scatter(visit_freq_mean, like_mean, c=female_ratio, cmap='coolwarm', s=100)
plt.xlabel('Mean Visit Frequency')
plt.ylabel('Mean Like Score')
plt.title('Customer Segments: Visit Frequency vs Like Score')
plt.colorbar(label='Proportion of Females')
for i, txt in enumerate(visit_freq_mean.index):
    plt.annotate(txt, (visit_freq_mean[i], like_mean[i]))
plt.show()

"""Conclusion:
The data analysis revealed valuable insights into customer preferences and segmentation for McDonald's. Through PCA and clustering techniques, distinct customer segments were identified based on their perceptions. The analysis highlighted key relationships between attributes, such as the positive correlation between visit frequency and liking, and suggested potential gender-based preference patterns.

The comparison of K-means and GMM clustering offered a robust assessment of the stability of the clustering solutions. These insights are actionable for McDonald's, allowing for tailored offerings and services that cater to different customer segments, ultimately enhancing the dining experience and better aligning with customer preferences.
"""