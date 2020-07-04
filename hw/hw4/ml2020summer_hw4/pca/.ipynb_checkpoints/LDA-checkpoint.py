import numpy as np
from scipy import linalg



def LDA(data, gnd):
    '''
    LDA: Linear Discriminant Analysis for ML Course

        Input:
            data  - Data matrix(numpy array). Each row vector of fea is a data point. It should be centered before.
            gnd   - Colunm vector of the label information for each
                    data point. 

        Output:
            eigvector - Each column is an embedding function, for a new
                      data point (row vector) x,  y = np.matmul(x, eigvector)
                      will be the embedding result of x.
            eigvalue  - The sorted eigvalue of LDA eigen-problem. 

    '''       
    label = np.unique(gnd)
    mylda = myLDA()
    mylda.fit(data, gnd) 
    eigvector = mylda.scalings_
    eigvalue = mylda.scalings
    return eigvector, eigvalue

class myLDA():
    """Linear Discriminant Analysis

    A classifier with a linear decision boundary, generated by fitting class
    conditional densities to the data and using Bayes' rule.

    The model fits a Gaussian density to each class, assuming that all classes
    share the same covariance matrix.

    The fitted model can also be used to reduce the dimensionality of the input
    by projecting it to the most discriminative directions.
    
    This class is partly modified from sklearn.discriminant_analysis.LinearDiscriminantAnalysis
    """
    def __init__(self):
        pass
    
    def fit(self, X, y):
        self.Dim = np.unique(y).shape[0] - 1
        self.svd_solver(X, y)

    def svd_solver(self, X, y, tol=1e-5):
        """SVD solver.

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            Training data.

        y : array-like, shape (n_samples,) or (n_samples, n_targets)
            Target values.
        tol: the tol for floating point error
        """
        n_samples, n_features = X.shape
        classes = np.unique(y)
        n_classes = classes.shape[0]
        _, y_t = np.unique(y, return_inverse=True)  # non-negative ints
        priors_ = np.bincount(y_t) / float(len(y))
        means_ = self.class_means(X, y)
        covariance_ = self.class_cov(X, y, priors_)

        Xc = []
        for idx, group in enumerate(classes):
            Xg = X[y == group, :]
            Xc.append(Xg - means_[idx])

        self.xbar_ = np.dot(priors_, means_)       
        Xc = np.concatenate(Xc, axis=0)

        # 1) within (univariate) scaling by with classes std-dev
        std = Xc.std(axis=0)
        # avoid division by zero in normalization
        std[std == 0] = 1.
        fac = 1. / (n_samples - n_classes)

        # 2) Within variance scaling
        X = np.sqrt(fac) * (Xc / std)
        # SVD of centered (within)scaled data
        U, S, V = linalg.svd(X, full_matrices=False)

        rank = np.sum(S > tol)
        # Scaling of within covariance is: V' 1/S
        self.scalings = (V[:rank] / std).T / S[:rank]
        
        # 3) Between variance scaling
        # Scale weighted centers
        X = np.dot(((np.sqrt((n_samples * priors_) * fac)) *
                    (means_ - self.xbar_).T).T, self.scalings)
        # Centers are living in a space with n_classes-1 dim (maximum)
        # Use SVD to find projection in the space spanned by the
        # (n_classes) centers
        _, S, V = linalg.svd(X, full_matrices=0)

        explained_variance_ratio_ = (S**2 / np.sum(
            S**2))[:self.Dim]
        rank = np.sum(S > tol * S[0])
        self.scalings_ = np.dot(self.scalings, V.T[:, :rank])
        coef = np.dot(means_ - self.xbar_, self.scalings_) 

    def class_means(self, X, y):
        """Compute class means.

        Input
        ----------
        X : array-like, shape (n_samples, n_features)
            Input data.

        y : array-like, shape (n_samples,) or (n_samples, n_targets)
            Target values.

        Returns
        -------
        means : array-like, shape (n_features,)
            Class means.
        """
        means = []
        classes = np.unique(y)
        for group in classes:
            Xg = X[y == group, :]
            means.append(Xg.mean(0))
        return np.asarray(means)

    def class_cov(self, X, y, priors=None, shrinkage=None):
        """Compute class covariance matrix.

        Input
        ----------
        X : array-like, shape (n_samples, n_features)
            Input data.

        y : array-like, shape (n_samples,) or (n_samples, n_targets)
            Target values.

        priors : array-like, shape (n_classes,)
            Class priors.

        shrinkage : string or float, optional
            Shrinkage parameter, possible values:
              - None: no shrinkage (default).
              - 'auto': automatic shrinkage using the Ledoit-Wolf lemma.
              - float between 0 and 1: fixed shrinkage parameter.

        Returns
        -------
        cov : array-like, shape (n_features, n_features)
            Class covariance matrix.
        """
        classes = np.unique(y)
        covs = []
        for group in classes:
            Xg = X[y == group, :]
            covs.append(np.atleast_2d(np.cov(Xg)))
        return np.average(covs, axis=0, weights=priors)
