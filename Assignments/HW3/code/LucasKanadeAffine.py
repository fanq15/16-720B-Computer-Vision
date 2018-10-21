#!/usr/bin/python3

'''
16-720B Computer Vision (Fall 2018)
Homework 3 - Lucas-Kanade Tracking and Correlation Filters
'''

__author__ = "Heethesh Vhavle"
__credits__ = ["Simon Lucey", "16-720B TAs"]
__version__ = "1.0.1"
__email__ = "heethesh@cmu.edu"

import numpy as np
from scipy.ndimage import shift, affine_transform, sobel
from scipy.interpolate import RectBivariateSpline

from LucasKanade import crop, disp

def LucasKanadeAffine(It, It1, threshold=0.0005, iters=50):
    '''
    [input]
    * It - Template image
    * It1 - Current image
    * threshold - Threshold for error convergence (default: 0.005)
    * iters - Number of iterations for error convergence (default: 50)
    
    [output]
    * M - Affine warp matrix [2x3 numpy array]
    '''

    # Initial parameters
    M = np.asarray([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    p = np.asarray([0.0]*6)
    I = M

    # Iterate 
    for i in range(iters):
        # Step 1 - Warp image
        M_ = np.asarray([[p[4]+1, p[3], p[5]], [p[1], p[0]+1, p[2]]])
        warp_img = affine_transform(It1, M_)

        # Step 2 - Compute error image with common pixels
        mask = affine_transform(np.ones(It1.shape), M_)
        error_img = (mask * It) - (mask * warp_img)

        # Step 3 - Warp the gradient
        gradient = np.dstack(np.gradient(warp_img)[::-1])
        warp_gradient = gradient.reshape(gradient.shape[0] * gradient.shape[1], 2).T

        # Step 4 - Evaluate jacobian parameters
        H, W = It.shape
        Jx = np.tile(np.linspace(0, W-1, W), (H, 1)).flatten()
        Jy = np.tile(np.linspace(0, H-1, H), (W, 1)).T.flatten()

        # Step 5 - Compute the steepest descent images
        steepest_descent = np.vstack([warp_gradient[0] * Jx,
                                      warp_gradient[0] * Jy,
                                      warp_gradient[0],
                                      warp_gradient[1] * Jx,
                                      warp_gradient[1] * Jy,
                                      warp_gradient[1]]).T

        # Step 6 - Compute the Hessian matrix
        hessian = np.matmul(steepest_descent.T, steepest_descent)

        # Step 7/8 - Compute delta P
        delta_p = np.matmul(np.linalg.inv(hessian), np.matmul(steepest_descent.T, error_img.flatten()))
        
        # Step 9 - Update the parameters
        p = p + delta_p
        M = p.reshape(2, 3) + I

        # Test for convergence
        if np.linalg.norm(delta_p) <= threshold: break

    return M

if __name__ == '__main__':
    carseq = np.load('../data/carseq.npy')
    LucasKanadeAffine(carseq[:, :, 0], carseq[:, :, 1])
