import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA


# import matplotlib.pyplot as plt
# import io
# import base64

class GTM:
    def __init__(self, latent_dim=2, num_nodes=100, rbf_width=1.0):
        self.latent_dim = latent_dim
        self.num_nodes = num_nodes
        self.rbf_width = rbf_width
        self.nodes = None
        self.weights = None

    def _initialize_nodes(self):
        # Initialize latent space nodes in a grid
        grid_size = int(np.sqrt(self.num_nodes))
        x = np.linspace(-1, 1, grid_size)
        y = np.linspace(-1, 1, grid_size)
        xx, yy = np.meshgrid(x, y)
        self.nodes = np.column_stack([xx.ravel(), yy.ravel()])[:self.num_nodes]

    def _rbf_kernel(self, X, centers):
        distances = np.sum((X[:, np.newaxis] - centers[np.newaxis, :]) ** 2, axis=2)
        return np.exp(-distances / (2 * self.rbf_width ** 2))

    def fit(self, X, max_iter=100):
        self._initialize_nodes()
        n_samples, n_features = X.shape
        self.weights = np.random.randn(n_features, self.num_nodes)

        for _ in range(max_iter):
            # E-step: compute responsibilities
            phi = self._rbf_kernel(self.nodes, self.nodes)
            Y = phi @ self.weights.T
            distances = np.sum((X[:, np.newaxis] - Y[np.newaxis, :]) ** 2, axis=2)
            responsibilities = np.exp(-distances / 2)
            responsibilities /= responsibilities.sum(axis=1, keepdims=True)

            # M-step: update weights
            for k in range(self.num_nodes):
                R_k = np.diag(responsibilities[:, k])
                self.weights[:, k] = np.linalg.pinv(phi.T @ R_k @ phi) @ phi.T @ R_k @ X

    def transform(self, X):
        phi = self._rbf_kernel(X, self.nodes)
        return phi @ self.weights.T

    def generate_map(self, patents_data, output_dim=2):
        # patents_data: list of dicts with 'title', 'abstract', etc.
        # Extract features (simplified: use TF-IDF or embeddings)
        # For demo, use PCA on dummy features
        features = np.random.randn(len(patents_data), 100)  # Placeholder
        pca = PCA(n_components=50)
        reduced_features = pca.fit_transform(features)

        self.fit(reduced_features)
        map_coords = self.transform(reduced_features)

        # Cluster for visualization
        kmeans = KMeans(n_clusters=5)
        clusters = kmeans.fit_predict(map_coords)

        return map_coords, clusters


def create_patent_map_image(patents_data):
    gtm = GTM()
    coords, clusters = gtm.generate_map(patents_data)

    # Return coordinates and clusters instead of image
    return {
        'coordinates': coords.tolist(),
        'clusters': clusters.tolist(),
        'patents': [{'id': p.get('id'), 'title': p.get('title')} for p in patents_data]
    }
