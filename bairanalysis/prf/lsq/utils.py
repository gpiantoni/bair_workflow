from numpy import arange, exp
from scipy.special import gamma
from scipy.integrate import trapz


def double_gamma_hrf(delay, tr, fptr=1.0, integrator=trapz):

    r"""The double gamma hemodynamic reponse function (HRF).
    The user specifies only the delay of the peak and undershoot.
    The delay shifts the peak and undershoot by a variable number of
    seconds. The other parameters are hardcoded. The HRF delay is
    modeled for each voxel independently. The form of the HRF and the
    hardcoded values are based on previous work [1]_.
    Parameters
    ----------
    delay : float
        The delay of the HRF peak and undershoot.
    tr : float
        The length of the repetition time in seconds.
    fptr : float
        The number of stimulus frames per reptition time.  For a
        60 Hz projector and with a 1 s repetition time, the fptr
        would be equal to 60.  It is possible that you will bin all
        the frames in a single TR, in which case fptr equals 1.
    integrator : callable
        The integration function for normalizing the units of the HRF
        so that the area under the curve is the same for differently
        delayed HRFs.  Set integrator to None to turn off normalization.
    Returns
    -------
    hrf : ndarray
        The hemodynamic response function to convolve with the stimulus
        timeseries.
    Reference
    ----------
    .. [1] Glover, GH (1999) Deconvolution of impulse response in event related
    BOLD fMRI. NeuroImage 9, 416-429.

    Taken from popeye
    """

    # add delay to the peak and undershoot params (alpha 1 and 2)
    alpha_1 = 5 / tr + delay / tr
    beta_1 = 1.0
    c = 0.1
    alpha_2 = 15 / tr + delay / tr
    beta_2 = 1.0

    t = arange(0, 32, tr)

    hrf = (((t ** (alpha_1) * beta_1 ** alpha_1 * exp(-beta_1 * t)) / gamma(alpha_1))
           - c * ((t ** (alpha_2) * beta_2 ** alpha_2 * exp(-beta_2 * t)) / gamma(alpha_2)))

    if integrator:
        hrf /= integrator(hrf)

    return hrf
