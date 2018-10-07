# @Author: Sharib Ali <shariba>
# @Date:   2018-05-09T11:52:47+01:00
# @Email:  sharib.ali@eng.ox.ac.uk
# @Project: BRC: VideoEndoscopy
# @Filename: videoQualityMetrics.py
# @Last modified by:   shariba
# @Last modified time: 2018-08-07T14:43:24+01:00
# @Copyright: 2018-2020, sharib ali

import numpy
import math
import scipy.signal
import scipy.ndimage

def psnr(img1, img2):
    # PSNR, Peak Signal to Noise Ratio: implemented
    mse = numpy.mean( (img1 - img2) ** 2 )
    if mse == 0:
        return 100
    PIXEL_MAX = 255.0
    return 20 * math.log10(PIXEL_MAX / math.sqrt(mse))

def MSE(img1, img2):
    # PSNR, Peak Signal to Noise Ratio: implemented
    mse = numpy.mean( (img1 - img2) ** 2 )
    return mse

def vifp_mscale(ref, dist):
    # Visual Information Fidelity: implemented
    '''This software release consists of a MULTISCALE PIXEL DOMAIN, SCALAR GSM implementation of the algorithm described in the paper:
    H. R. Sheikh and A. C. Bovik, "Image Information and Visual Quality"., IEEE Transactions on Image Processing, (to appear).
    Download manuscript draft from http://live.ece.utexas.edu in the Publications link.
    Input : (1) img1: The reference image as a matrix
            (2) img2: The distorted image (order is important)
    Output: (1) VIF the visual information fidelity measure between the two images
    Default Usage:
        Given 2 test images img1 and img2, whose dynamic range is 0-255
        vif = vifvec(img1, img2);
    '''
    sigma_nsq=2
    eps = 1e-10

    num = 0.0
    den = 0.0
    for scale in range(1, 5):

        N = 2**(4-scale+1) + 1
        sd = N/5.0

        if (scale > 1):
            ref = scipy.ndimage.gaussian_filter(ref, sd)
            dist = scipy.ndimage.gaussian_filter(dist, sd)
            ref = ref[::2, ::2]
            dist = dist[::2, ::2]

        mu1 = scipy.ndimage.gaussian_filter(ref, sd)
        mu2 = scipy.ndimage.gaussian_filter(dist, sd)
        mu1_sq = mu1 * mu1
        mu2_sq = mu2 * mu2
        mu1_mu2 = mu1 * mu2
        sigma1_sq = scipy.ndimage.gaussian_filter(ref * ref, sd) - mu1_sq
        sigma2_sq = scipy.ndimage.gaussian_filter(dist * dist, sd) - mu2_sq
        sigma12 = scipy.ndimage.gaussian_filter(ref * dist, sd) - mu1_mu2

        sigma1_sq[sigma1_sq<0] = 0
        sigma2_sq[sigma2_sq<0] = 0

        g = sigma12 / (sigma1_sq + eps)
        sv_sq = sigma2_sq - g * sigma12

        g[sigma1_sq<eps] = 0
        sv_sq[sigma1_sq<eps] = sigma2_sq[sigma1_sq<eps]
        sigma1_sq[sigma1_sq<eps] = 0

        g[sigma2_sq<eps] = 0
        sv_sq[sigma2_sq<eps] = 0

        sv_sq[g<0] = sigma2_sq[g<0]
        g[g<0] = 0
        sv_sq[sv_sq<=eps] = eps

        num += numpy.sum(numpy.log10(1 + g * g * sigma1_sq / (sv_sq + sigma_nsq)))
        den += numpy.sum(numpy.log10(1 + sigma1_sq / sigma_nsq))

    vifp = num/den

    return vifp

from numpy import sqrt, pi
import scipy.ndimage.filters

"""
RECO: Relative Polar Edge Coherence
An excellent reduced-reference metric (need just one number from the source image to compare with).
This implementation follows closely the notation and terminology in the original paper, except that some of the kernels are reflected
(probably due to y axis pointing down rather than up in images).
Cite:
Baroncini, V., Capodiferro, L., Di Claudio, E. D., & Jacovitti, G. (2009). The polar edge coherence:
a quasi blind metric for video quality assessment. EUSIPCO 2009, Glasgow, 564-568.
"""

def Laguerre_Gauss_Circular_Harmonic_3_0(size, sigma):
    x = numpy.linspace(-size/2.0, size/2.0, size)
    y = numpy.linspace(-size/2.0, size/2.0, size)
    xx, yy = numpy.meshgrid(x, y)

    r = numpy.sqrt(xx*xx + yy*yy)
    gamma = numpy.arctan2(yy, xx)
    l30 = - (1/6.0) * (1 / (sigma * sqrt(pi))) * numpy.exp( -r*r / (2*sigma*sigma)) * (sqrt(r*r/(sigma*sigma)) ** 3) * numpy.exp( -1j * 3 * gamma )
    return l30

def Laguerre_Gauss_Circular_Harmonic_1_0(size, sigma):
    x = numpy.linspace(-size/2.0, size/2.0, size)
    y = numpy.linspace(-size/2.0, size/2.0, size)
    xx, yy = numpy.meshgrid(x, y)

    r = numpy.sqrt(xx*xx + yy*yy)
    gamma = numpy.arctan2(yy, xx)
    l10 = - (1 / (sigma * sqrt(pi))) * numpy.exp( -r*r / (2*sigma*sigma)) * sqrt(r*r/(sigma*sigma)) * numpy.exp( -1j * gamma )
    return l10

"""
Polar edge coherence map
Same size as source image
"""
def pec(img):
    # TODO scale parameter should depend on resolution
    l10 = Laguerre_Gauss_Circular_Harmonic_1_0(17, 2)
    l30 = Laguerre_Gauss_Circular_Harmonic_3_0(17, 2)
    y10 = scipy.ndimage.filters.convolve(img, numpy.real(l10)) + 1j * scipy.ndimage.filters.convolve(img, numpy.imag(l10))
    y30 = scipy.ndimage.filters.convolve(img, numpy.real(l30)) + 1j * scipy.ndimage.filters.convolve(img, numpy.imag(l30))
    pec_map = - (numpy.absolute(y30) / numpy.absolute(y10)) * numpy.cos( numpy.angle(y30) - 3 * numpy.angle(y10) )
    return pec_map

"""
Edge coherence metric
Just one number summarizing typical edge coherence in this image.
"""
def eco(img):
    l10 = Laguerre_Gauss_Circular_Harmonic_1_0(17, 2)
    l30 = Laguerre_Gauss_Circular_Harmonic_3_0(17, 2)
    # print(l10.shape)
    # print(l30.shape)
    # print(img.shape)
    y10 = scipy.ndimage.filters.convolve(img, numpy.real(l10)) + 1j * scipy.ndimage.filters.convolve(img, numpy.imag(l10))
    y30 = scipy.ndimage.filters.convolve(img, numpy.real(l30)) + 1j * scipy.ndimage.filters.convolve(img, numpy.imag(l30))
    eco = numpy.sum( - (numpy.absolute(y30) * numpy.absolute(y10)) * numpy.cos( numpy.angle(y30) - 3 * numpy.angle(y10) ) )
    return eco

"""
Relative edge coherence
Ratio of ECO
"""
def reco(img1, img2):
    C = 1 # TODO what is a good value?
    return (eco(img2) + C) / (eco(img1) + C)
