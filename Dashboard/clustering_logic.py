import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def perform_clustering(data):
    # Select relevant columns
    features = data[['calculate_education_score',
                     'calculate_overall_physical_wellbeing', 'calculate_behavior_score']]

    # Data scaling (often recommended)
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    # Determine optimal number of clusters
    num_clusters = 3  # You'll need experiment with this

    # Create a K-Means model
    kmeans = KMeans(n_clusters=num_clusters, random_state=0)

    # Fit the model
    kmeans.fit(scaled_features)

    # Get cluster assignments
    labels = kmeans.labels_

    # Add cluster assignments as a new column
    data['cluster'] = labels

    return data
