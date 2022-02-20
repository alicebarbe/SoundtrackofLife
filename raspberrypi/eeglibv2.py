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

        #TODO: verify that these are correct
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
        
        valence = 0.0
        arousal = 0.0
        
        gmul1 = 1.0 ##change this to scale
        gmul2 = 1.0 ##change this to scale
        gmul3 = 1.0 ##change this to scale
        gmul4 = 1.0 ##change this to scale
        
        
        arousal += (gmul1*gamma)-delta
        arousal += (gmul2*gamma)-theta
        arousal += (gmul3*gamma)-alpha
        arousal += (gmul4*gamma)-beta
        
        
        
        tmul = 0.5 ##change this to scale
        amul = 2.5 ##change this to scale
        bmul = 1.5 ##change this to scale
        
        valence += (amul *alpha) - (delta +(gmul3 *gamma)) 
        valence += (bmul *beta) - (delta +(gmul4 *gamma))
        valence += (tmul *theta) - (delta + (gmul2*gamma))
        
        
        data['arousal'] = arousal
        data['valence'] = valence

        return data


