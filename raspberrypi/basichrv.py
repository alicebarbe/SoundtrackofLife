from hrvanalysis import remove_outliers, remove_ectopic_beats, interpolate_nan_values
from hrvanalysis import get_time_domain_features

from random import seed
from random import randint

def samplegen():
    ##replace this part with actual RR values
    # seed random number generator
    seed(520)
    # generate some integers
    rr = []
    for _ in range(500):
        value = randint(972, 1265)
        print(value)
        rr.append(value)
    return rr



def gethrv(rr):
    # rr_intervals_list contains integer values of RR-interval
    # rr_intervals_list = [1000, 1050, 1020, 1080, ..., 1100, 1110, 1060]

    rr_intervals_list = rr


    # This remove outliers from signal
    rr_intervals_without_outliers = remove_outliers(rr_intervals=rr_intervals_list,
                                                    low_rri=300, high_rri=2000)
    # This replace outliers nan values with linear interpolation
    interpolated_rr_intervals = interpolate_nan_values(rr_intervals=rr_intervals_without_outliers,
                                                    interpolation_method="linear")

    interpolated_rr_intervals = rr # this is hacky

    # This remove ectopic beats from signal
    nn_intervals_list, ocount = remove_ectopic_beats(rr_intervals=interpolated_rr_intervals, method="malik")
    # This replace ectopic beats nan values with linear interpolation
    interpolated_nn_intervals = interpolate_nan_values(rr_intervals=nn_intervals_list)

    #print (ocount)

    # time_domain_features = get_time_domain_features(nn_intervals_list)

    time_domain_features = get_time_domain_features(interpolated_nn_intervals)


    #print (time_domain_features)

    return time_domain_features, ocount



##testing

#rr = samplegen()

#tdf, oc = gethrv(rr)
