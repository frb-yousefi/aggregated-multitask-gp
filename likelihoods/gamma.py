# Copyright (c) 2018 Pablo Moreno-Munoz
# Universidad Carlos III de Madrid and University of Sheffield

import sys
import numpy as np
from GPy.likelihoods import link_functions
from GPy.likelihoods import Likelihood
from GPy.util.misc import safe_exp, safe_square
from scipy.special import beta, betaln, psi, zeta, gamma, gammaln
from functools import reduce


class Gamma(Likelihood):
    """
    Gamma likelihood with a latent function over its parameter

    """

    def __init__(self, gp_link=None):
        if gp_link is None:
            gp_link = link_functions.Identity()

        super(Gamma, self).__init__(gp_link, name='Gamma')

    def pdf(self, F, y, Y_metadata=None):
        eF = safe_exp(F)
        a = eF[:,0,None]
        b = eF[:,1,None]
        a = np.clip(a, 1e-9, 1e9)  # numerical stability
        b = np.clip(b, 1e-9, 1e9)  # numerical stability
        pdf = (b**a) * (y**(a-1)) * safe_exp(-b*y) / gamma(a)
        return pdf

    def logpdf(self, F, y, Y_metadata=None):
        eF = safe_exp(F)
        a = eF[:,0,None]
        b = eF[:,1,None]
        a = np.clip(a, 1e-9, 1e9)  # numerical stability
        b = np.clip(b, 1e-9, 1e9)  # numerical stability
        logpdf = - gammaln(a) + (a*np.log(b)) + ((a-1)*np.log(y)) - (b*y)
        return logpdf

    def logpdf_sampling(self, F, y, Y_metadata=None):
        eF = safe_exp(F)
        a = eF[:,0,:]
        b = eF[:,1,:]
        a = np.clip(a, 1e-9, 1e9)  # numerical stability
        b = np.clip(b, 1e-9, 1e9)  # numerical stability
        ym = np.tile(y, (1, F.shape[2]))
        logpdf = - gammaln(a) + (a*np.log(b)) + ((a-1)*np.log(ym)) - (b*ym)
        return logpdf

    def samples(self, F ,num_samples, Y_metadata=None):
        eF = safe_exp(F)
        a = eF[:,0,None]
        b = eF[:,1,None]
        a = np.clip(a, 1e-9, 1e9)  # numerical stability
        b = np.clip(b, 1e-9, 1e9)  # numerical stability
        samples = np.random.gamma(shape=a, scale=1/b)
        return samples

    def mean(self, F, Y_metadata=None):
        eF = safe_exp(F)
        a = eF[:,0, None]
        b = eF[:,1, None]
        a = np.clip(a, 1e-9, 1e9)  # numerical stability
        b = np.clip(b, 1e-9, 1e9)  # numerical stability
        mean = a / b
        return mean

    def mean_sq(self, F, Y_metadata=None):
        eF = safe_exp(F)
        a = eF[:,0, None]
        b = eF[:,1, None]
        a = np.clip(a, 1e-9, 1e9)  # numerical stability
        b = np.clip(b, 1e-9, 1e9)  # numerical stability
        mean = a / b
        mean_sq = np.square(mean)
        return mean_sq

    def variance(self, F, Y_metadata=None):
        eF = safe_exp(F)
        a = eF[:,0, None]
        b = eF[:,1, None]
        a = np.clip(a, 1e-9, 1e9)  # numerical stability
        b = np.clip(b, 1e-9, 1e9)  # numerical stability
        var = a / (b**2)
        return var

    def dlogp_df(self, F, y, Y_metadata=None):
        eF = safe_exp(F)
        a = eF[:,0, None]
        b = eF[:,1, None]
        a = np.clip(a, 1e-9, 1e9)  # numerical stability
        b = np.clip(b, 1e-9, 1e9)  # numerical stability
        psi_a = psi(a)
        dlogp_dfa = (-psi_a + np.log(b) + np.log(y)) * a
        dlogp_dfb = a - (b*y)
        return dlogp_dfa, dlogp_dfb

    def d2logp_df2(self, F, y, Y_metadata=None):
        eF = safe_exp(F)
        a = eF[:,0, None]
        b = eF[:,1, None]
        a = np.clip(a, 1e-9, 1e9)  # numerical stability
        b = np.clip(b, 1e-9, 1e9)  # numerical stability
        psi_a = psi(a)
        zeta_a = zeta(2,a)
        d2logp_dfa2 = (- psi_a - (a*zeta_a) + np.log(b) + np.log(y)) * a
        d2logp_dfb2 = - y*b
        return d2logp_dfa2, d2logp_dfb2

    def var_exp(self, y, M, V, gh_points=None, Y_metadata=None):
        # Variational Expectation
        # gh: Gaussian-Hermite quadrature
        if gh_points is None:
            gh_f, gh_w = self._gh_points(T=16)
        else:
            gh_f, gh_w = gh_points
        gh_w = gh_w / np.sqrt(np.pi)
        D = M.shape[1]
        expanded_F_tuples = []
        grid_tuple = [M.shape[0]]
        for d in range(D):
            grid_tuple.append(gh_f.shape[0])
            expanded_fd_tuple = [1] * (D + 1)
            expanded_fd_tuple[d + 1] = gh_f.shape[0]
            expanded_F_tuples.append(tuple(expanded_fd_tuple))

        # mean-variance tuple
        mv_tuple = [1] * (D + 1)
        mv_tuple[0] = M.shape[0]
        mv_tuple = tuple(mv_tuple)

        # building, normalizing and reshaping the grids
        F = np.zeros((reduce(lambda x, y: x * y, grid_tuple), D))
        for d in range(D):
            fd = np.zeros(tuple(grid_tuple))
            fd[:] = np.reshape(gh_f, expanded_F_tuples[d]) * np.sqrt(2 * np.reshape(V[:, d], mv_tuple)) \
                    + np.reshape(M[:, d], mv_tuple)
            F[:, d, None] = fd.reshape(reduce(lambda x, y: x * y, grid_tuple), -1, order='C')

        # function evaluation
        Y_full = np.repeat(y, gh_f.shape[0] ** D, axis=0)
        logp = self.logpdf(F, Y_full)
        logp = logp.reshape(tuple(grid_tuple))

        # calculating quadrature
        var_exp = logp.dot(gh_w)# / np.sqrt(np.pi)
        for d in range(D - 1):
            var_exp = var_exp.dot(gh_w)# / np.sqrt(np.pi)

        return var_exp[:, None]

    def var_exp_derivatives(self, y, M, V, gh_points=None, Y_metadata=None):
        # Variational Expectation
        # gh: Gaussian-Hermite quadrature
        if gh_points is None:
            gh_f, gh_w = self._gh_points(T=16)
        else:
            gh_f, gh_w = gh_points
        gh_w = gh_w / np.sqrt(np.pi)
        D = M.shape[1]
        expanded_F_tuples = []
        grid_tuple = [M.shape[0]]
        for d in range(D):
            grid_tuple.append(gh_f.shape[0])
            expanded_fd_tuple = [1] * (D + 1)
            expanded_fd_tuple[d + 1] = gh_f.shape[0]
            expanded_F_tuples.append(tuple(expanded_fd_tuple))

        # mean-variance tuple
        mv_tuple = [1] * (D + 1)
        mv_tuple[0] = M.shape[0]
        mv_tuple = tuple(mv_tuple)

        # building, normalizing and reshaping the grids
        F = np.zeros((reduce(lambda x, y: x * y, grid_tuple), D))
        for d in range(D):
            fd = np.zeros(tuple(grid_tuple))
            fd[:] = np.reshape(gh_f, expanded_F_tuples[d]) * np.sqrt(2 * np.reshape(V[:, d], mv_tuple)) \
                    + np.reshape(M[:, d], mv_tuple)
            F[:, d, None] = fd.reshape(reduce(lambda x, y: x * y, grid_tuple), -1, order='C')

        # function evaluation
        Y_full = np.repeat(y, gh_f.shape[0] ** D, axis=0)

        dlogp_a, dlogp_b = self.dlogp_df(F, Y_full)
        d2logp_a, d2logp_b = self.d2logp_df2(F, Y_full)

        dlogp_a = dlogp_a.reshape(tuple(grid_tuple))
        dlogp_b = dlogp_b.reshape(tuple(grid_tuple))
        d2logp_a = d2logp_a.reshape(tuple(grid_tuple))
        d2logp_b = d2logp_b.reshape(tuple(grid_tuple))

        ve_dm_fa = dlogp_a.dot(gh_w).dot(gh_w)# / np.square(np.sqrt(np.pi))
        ve_dm_fb = dlogp_b.dot(gh_w).dot(gh_w) #/ np.square(np.sqrt(np.pi))
        ve_dv_fa = d2logp_a.dot(gh_w).dot(gh_w) #/ np.square(np.sqrt(np.pi))
        ve_dv_fb = d2logp_b.dot(gh_w).dot(gh_w) #/ np.square(np.sqrt(np.pi))

        var_exp_dm = np.hstack((ve_dm_fa[:,None], ve_dm_fb[:,None]))
        var_exp_dv = 0.5*np.hstack((ve_dv_fa[:,None], ve_dv_fb[:,None]))

        return var_exp_dm, var_exp_dv

    def predictive(self, M, V, gh_points=None, Y_metadata=None):
        # Variational Expectation
        # gh: Gaussian-Hermite quadrature
        if gh_points is None:
            gh_f, gh_w = self._gh_points(T=20)
        else:
            gh_f, gh_w = gh_points
        gh_w = gh_w / np.sqrt(np.pi)
        D = M.shape[1]
        expanded_F_tuples = []
        grid_tuple = [M.shape[0]]
        for d in range(D):
            grid_tuple.append(gh_f.shape[0])
            expanded_fd_tuple = [1] * (D + 1)
            expanded_fd_tuple[d + 1] = gh_f.shape[0]
            expanded_F_tuples.append(tuple(expanded_fd_tuple))

        # mean-variance tuple
        mv_tuple = [1] * (D + 1)
        mv_tuple[0] = M.shape[0]
        mv_tuple = tuple(mv_tuple)

        # building, normalizing and reshaping the grids
        F = np.zeros((reduce(lambda x, y: x * y, grid_tuple), D))
        for d in range(D):
            fd = np.zeros(tuple(grid_tuple))
            fd[:] = np.reshape(gh_f, expanded_F_tuples[d]) * np.sqrt(2 * np.reshape(V[:, d], mv_tuple)) \
                    + np.reshape(M[:, d], mv_tuple)
            F[:, d, None] = fd.reshape(reduce(lambda x, y: x * y, grid_tuple), -1, order='C')

        mean = self.mean(F)
        mean = mean.reshape(tuple(grid_tuple))
        mean_pred = mean.dot(gh_w).dot(gh_w) #/ np.square(np.sqrt(np.pi))

        var = self.variance(F)
        var = var.reshape(tuple(grid_tuple))
        var_int = var.dot(gh_w).dot(gh_w) #/ np.square(np.sqrt(np.pi))
        mean_sq = self.mean_sq(F)
        mean_sq = mean_sq.reshape(tuple(grid_tuple))
        mean_sq_int = mean_sq.dot(gh_w).dot(gh_w) #/ np.square(np.sqrt(np.pi))

        var_pred = var_int + mean_sq_int - safe_square(mean_pred)
        return mean_pred[:,None] , var_pred[:,None]

    def log_predictive(self, Ytest, mu_F_star, v_F_star, num_samples):
        Ntest, D = mu_F_star.shape
        F_samples = np.empty((Ntest, D, num_samples))
        # function samples:
        for d in range(D):
            mu_fd_star = mu_F_star[:, d][:, None]
            var_fd_star = v_F_star[:, d][:, None]
            F_samples[:, d, :] = np.random.normal(mu_fd_star, np.sqrt(var_fd_star), size=(Ntest, num_samples))

         # monte-carlo:
        log_pred = -np.log(num_samples) + logsumexp(self.logpdf_sampling(F_samples, Ytest), axis=-1)
        log_pred = np.array(log_pred).reshape(*Ytest.shape)
        "I just changed this to have the log_predictive of each data point and not a mean values"
        #log_predictive = (1/num_samples)*log_pred.sum()
        
        return log_pred
        
    def get_metadata(self):
        dim_y = 1
        dim_f = 2
        dim_p = 1
        return dim_y, dim_f, dim_p

    def ismulti(self):
        # Returns if the distribution is multivariate
        return False
