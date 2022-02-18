import numpy as np

def getbrainwaves(eegraw, samplerate):
        amplitude = np.array(eegraw)

        fourierTransform = np.fft.fft(amplitude)/len(amplitude)           # Normalize amplitude

        fourierTransform = fourierTransform[range(int(len(amplitude)/2))] # Exclude sampling frequency



        tpCount     = len(amplitude)

        values      = np.arange(int(tpCount/2))

        timePeriod  = tpCount/samplerate

        frequencies = values/timePeriod

        alpha = 0
        beta = 0
        gamma = 0
        delta = 0
        theta = 0

        for x,y in np.c_[frequencies,abs(fourierTransform)]:
            if x>0.1 and x<3.6:
                delta = delta + y
            if x>=3.6 and x <7.6:
                theta = theta + y
            if x>=7.6 and x <12:
                alpha = alpha + y
            if x>=12 and x <30:
                beta = beta + y
            if x>=30:
                gamma = gamma + y

        data = {}

        data['alpha'] = alpha
        data['beta'] = beta
        data['theta'] = theta
        data['delta'] = delta
        data['gamma'] = gamma

        return data


