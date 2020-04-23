import numpy as np
print ("LOL")
def p_diabetes_china(age):
    #diabetes prevalence for china
    #https://jamanetwork.com/journals/jama/fullarticle/1734701
    male = np.array([5.2755905511811, 8.346456692913385, 13.543307086614174, 17.95275590551181, 20.708661417322837, 21.653543307086615])
    female = np.array([4.015748031496061, 5.1181102362204705, 9.05511811023622, 17.401574803149607, 24.488188976377955, 25.196850393700785])
    male = male/100
    female = female/100

    #https://www.statista.com/statistics/282119/china-sex-ratio-by-age-group/
    sex_ratio = np.zeros(101)
    sex_ratio[0:5] = 113.91
    sex_ratio[5:10] = 118.03
    sex_ratio[10:15] = 118.62
    sex_ratio[15:20] = 118.14
    sex_ratio[20:25] = 112.89
    sex_ratio[25:30] = 105.39
    sex_ratio[30:35] = 101.05
    sex_ratio[35:40] = 102.84
    sex_ratio[40:45] = 103.75
    sex_ratio[45:50] = 103.64
    sex_ratio[50:55] = 102.15
    sex_ratio[55:60] = 101.65
    sex_ratio[60:65] = 100.5
    sex_ratio[65:70] = 96.94
    sex_ratio[70:75] = 94.42
    sex_ratio[75:80] = 89.15
    sex_ratio[80:85] = 76.97
    sex_ratio[85:90] = 71.16
    sex_ratio[90:95] = 48.74
    sex_ratio[95:] = 40.07

    #calculate male to female ratio within each age bucket, and use this to combine the male vs female
    #prevalence numbers
    sex_ratio = sex_ratio/(sex_ratio + 100)

    age_distribution = [16113.281,16543.361,16875.302,17118.429,17282.064,17375.527,17408.145,17389.238,17328.13,17234.143,17117.175,16987.122,16850.435,16715.289,16592.73,16484.473,16388.786,16370.261,16460.9,16637.439,16866.861,17182.465,17477.132,17702.896,17928.813,18144.994,18201.129,18841.832,20387.657,22413.391,24308.028,26355.485,27269.657,26400.295,24405.505,22597.72,20719.355,19296.916,18726.536,18750.928,18640.938,18451.511,18716.505,19599.644,20865.548,22101.75,23374.699,24376.638,24907.095,25077.435,25250.357,25414.362,25172.526,24383.003,23225.134,22043.117,20795.729,19608.86,18589.082,17703.703,16743.545,15666.543,14988.213,14917.427,15198.411,15425.124,15749.105,15550.741,14503.063,12921.733,11444.972,9939.85,8651.521,7764.623,7148.723,6478.704,5807.535,5222.027,4729.055,4307.295,3931.038,3608.42,3272.336,2887.659,2481.964,2118.152,1783.88,1480.587,1215.358,983.8,739.561,551.765,453.96,342.463,217.275,145.809,122.178,96.793,69.654,40.759,74.692]
    age_distribution = np.array(age_distribution)
    intervals = [(18, 30), (30, 40), (40, 50), (50, 60), (60, 70), (70, 100)]

    percent_male_intervals = np.zeros(len(intervals))
    for i in range(len(intervals)):
        age_frequency_within_interval = age_distribution[intervals[i][0]:intervals[i][1]]/age_distribution[intervals[i][0]:intervals[i][1]].sum()
        percent_male_intervals[i] = np.dot(age_frequency_within_interval, sex_ratio[intervals[i][0]:intervals[i][1]])

    p_diabetes = male*percent_male_intervals + female*(1-percent_male_intervals)

    p_diabetes_expanded = np.zeros(101)
    p_diabetes_expanded[:intervals[0][0]] = 0
    for i in range(len(intervals)):
        p_diabetes_expanded[intervals[i][0]:intervals[i][1]] = p_diabetes[i]
    p_diabetes_expanded[intervals[-1][1]:] = p_diabetes[-1]

    return p_diabetes_expanded

def p_hypertension_china(age):
    p_hyp_data = np.zeros(101)
    p_hyp_data[:18] = 0
    p_hyp_data[18:25] = 4.0
    p_hyp_data[25:35] = 6.1
    p_hyp_data[35:45] = 15.0
    p_hyp_data[45:55] = 29.6
    p_hyp_data[55:65] = 44.6
    p_hyp_data[65:75] = 55.7
    p_hyp_data[75:] = 60.2

    p_hyp_data = p_hyp_data/100

    return p_hyp_data


def sample_joint(age, p_diabetes, p_hyp):
    #https://www-nature-com.ezp-prod1.hul.harvard.edu/articles/hr201767
    p_hyp_given_diabetes = 0.5
    p_hyp_given_not_diabetes = (p_hyp - p_hyp_given_diabetes*p_diabetes)/(1 - p_diabetes)
    diabetes_status = (np.random.rand(age.shape[0]) < p_diabetes[age]).astype(np.int)
    hyp_status = np.zeros(age.shape[0], dtype=np.int)
    hyp_status[diabetes_status == 1] = np.random.rand((diabetes_status == 1).sum()) < p_hyp_given_diabetes
    hyp_status[diabetes_status == 0] = np.random.rand((diabetes_status == 0).sum()) < p_hyp_given_not_diabetes[age[diabetes_status == 0]]
    return diabetes_status, hyp_status

def sample_joint_comorbidities(age, country='China'):
    """
    Default country is China.
    For other countries pass value for country from {us, Republic of Korea, japan, Spain, italy, uk, France}
    """
    print("LOL2")
    return sample_joint(age, p_comorbidity(country, 'diabetes'), p_comorbidity(country, 'hypertension'))

def p_comorbidity(country, comorbidity, warning=False):

    """
    Input:
        -country: a string input belonging to- {us, Republic of Korea, japan, Spain, italy, uk, France}
        -comorbidity: a string input belonging to- {diabetes, hypertension}
        -warning: optional, If set to True, prints out the underlying assumptions/approximations
    Returns:
        -prevalence, sampled from a prevalence array of size 100, where prevalence[i] is the prevalence rate at age between {i, i+1}
    """

    prevalence = np.zeros(101)
    warning_string= " "

    ######################################  US ################################
    if country=='us':

        warning_string= " 1. Prevalence assumed to be linerly increasing between ages 0-18"

        if comorbidity=='diabetes':
            for i in range(101):
                if i<18:
                    prevalence[i]= 0.042*(i/18.)
                elif i<45:
                    prevalence[i]=0.042
                elif i<65:
                    prevalence[i]=0.175
                else:
                    prevalence[i]=0.268

        elif comorbidity=='hypertension':
            for i in range(101):
                if i<18:
                    prevalence[i]= 0.075*(i/18.)
                elif i<40:
                    prevalence[i]=0.075
                elif i<59:
                    prevalence[i]=0.332
                else:
                    prevalence[i]=0.631

    ######################################  south korea #######################
    if country=='Republic of Korea':

        if comorbidity=='diabetes':
            for i in range(101):
                if i <= 4:
                    prevalence[i] = 0.0002
                elif i <= 9:
                    prevalence[i] = 0.0013
                elif i <= 14:
                    prevalence[i] = 0.0043
                elif i <= 19:
                    prevalence[i] = 0.0085
                elif i <= 24:
                    prevalence[i] = 0.0150
                elif i <= 29:
                    prevalence[i] = 0.0238
                elif i <= 34:
                    prevalence[i] = 0.0347
                elif i <= 39:
                    prevalence[i] = 0.0484
                elif i <= 44:
                    prevalence[i] = 0.0658
                elif i <= 49:
                    prevalence[i] = 0.0893
                elif i <= 54:
                    prevalence[i] = 0.1195
                elif i <= 59:
                    prevalence[i] = 0.1547
                elif i <= 64:
                    prevalence[i] = 0.1933
                elif i <= 69:
                    prevalence[i] = 0.2319
                elif i <= 74:
                    prevalence[i] = 0.2672
                elif i <= 79:
                    prevalence[i] = 0.2945
                elif i <= 84:
                    prevalence[i] = 0.3106
                elif i <= 89:
                    prevalence[i] = 0.3067
                else:
                    prevalence[i] = 0.2855

        elif comorbidity=='hypertension':
            for i in range(101):
                if i<30:
                    prevalence[i]= 0.086*(i/30.)
                elif i<40:
                    prevalence[i]=0.086
                elif i<50:
                    prevalence[i]=0.194
                elif i<60:
                    prevalence[i]=0.34
                elif i< 70:
                    prevalence[i]=0.497
                else:
                    prevalence[i]=0.645
        elif comorbidity=='CVD':
            for i in range(101):
                if i <= 4:
                    prevalence[i] = 0.0004
                elif i <= 9:
                    prevalence[i] = 0.0005
                elif i <= 14:
                    prevalence[i] = 0.0011
                elif i <= 19:
                    prevalence[i] = 0.0028
                elif i <= 24:
                    prevalence[i] = 0.0031
                elif i <= 29:
                    prevalence[i] = 0.0052
                elif i <= 34:
                    prevalence[i] = 0.0092
                elif i <= 39:
                    prevalence[i] = 0.0201
                elif i <= 44:
                    prevalence[i] = 0.0497
                elif i <= 49:
                    prevalence[i] = 0.0607
                elif i <= 54:
                    prevalence[i] = 0.0839
                elif i <= 59:
                    prevalence[i] = 0.1160
                elif i <= 64:
                    prevalence[i] = 0.1552
                elif i <= 69:
                    prevalence[i] = 0.2005
                elif i <= 74:
                    prevalence[i] = 0.2561
                elif i <= 79:
                    prevalence[i] = 0.3128
                elif i <= 84:
                    prevalence[i] = 0.3655
                elif i <= 89:
                    prevalence[i] = 0.4115
                else:
                    prevalence[i] = 0.4356





    ######################################  Japan #############################
    if country=='japan':

        if comorbidity=='diabetes':
            for i in range(101):
                if i<20:
                    prevalence[i]= 0.02*(i/20.)
                elif i<30:
                    prevalence[i]=0.02
                elif i<40:
                    prevalence[i]=0.04
                elif i<50:
                    prevalence[i]=0.07
                elif i<60:
                    prevalence[i]=0.13
                elif i<70:
                    prevalence[i]=0.22
                else:
                    prevalence[i]=0.23

        elif comorbidity=='hypertension':
            for i in range(101):
                if i<20:
                    prevalence[i]= 0.085*(i/20.)
                elif i<35:
                    prevalence[i]=(1*0.15 + 1*0.02)/(1+1) # = 0.085
                elif i<50:
                    prevalence[i]=(1*0.3 + 1*0.1)/(1+1) # = 0.2
                elif i<65:
                    prevalence[i]=(1*0.67 + 1*0.53)/(1+1) # = 0.6
                else:
                    prevalence[i]=0.8

    ######################################  uk ################################
    if country=='uk':

        if comorbidity=='diabetes':
            for i in range(101):
                if i<16:
                    prevalence[i]= 0.003*(i/16.)
                elif i<25:
                    prevalence[i]=0.003
                elif i<44:
                    prevalence[i]=0.015
                elif i<65:
                    prevalence[i]=0.091
                else:
                    prevalence[i]=0.16

        elif comorbidity=='hypertension':
            for i in range(101):
                if i<16:
                    prevalence[i]= 0.02*(i/16.)
                elif i<25:
                    prevalence[i]=0.02
                elif i<44:
                    prevalence[i]=0.09
                elif i<65:
                    prevalence[i]=0.26
                else:
                    prevalence[i]=0.46

    ######################################  France ################################
    if country=='France':

        if comorbidity=='diabetes':
            for i in range(101):
                if i<40:
                    prevalence[i]= 0
                elif i<45:
                    prevalence[i]=0.01
                elif i<50:
                    prevalence[i]=0.025
                elif i<55:
                    prevalence[i]=0.05
                elif i<60:
                    prevalence[i]=0.075
                elif i<65:
                    prevalence[i]=0.12
                elif i<70:
                    prevalence[i]=0.14
                elif i<75:
                    prevalence[i]=0.16
                elif i<80:
                    prevalence[i]=0.18
                elif i<85:
                    prevalence[i]=0.17
                elif i<90:
                    prevalence[i]=0.14
                else:
                    prevalence[i]=0.09

        elif comorbidity=='hypertension':
            for i in range(101):
                if i<35:
                    prevalence[i]= 0.161*(i/35.)
                elif i<45:
                    prevalence[i]=0.161
                elif i<55:
                    prevalence[i]=0.39
                elif i<65:
                    prevalence[i]=0.56
                else:
                    prevalence[i]=0.75


    ######################################  China #############################
    if country=='China':
        #print ("LOL")
        dummy_value_to_work_with_china_function=0
        if comorbidity=='diabetes':
            for i in range(101):
                if i <= 4:
                    prevalence[i] = 0.0000
                elif i <= 9:
                    prevalence[i] = 0.0001
                elif i <= 14:
                    prevalence[i] = 0.0007
                elif i <= 19:
                    prevalence[i] = 0.0069
                elif i <= 24:
                    prevalence[i] = 0.0259
                elif i <= 29:
                    prevalence[i] = 0.0403
                elif i <= 34:
                    prevalence[i] = 0.0499
                elif i <= 39:
                    prevalence[i] = 0.0591
                elif i <= 44:
                    prevalence[i] = 0.0694
                elif i <= 49:
                    prevalence[i] = 0.0834
                elif i <= 54:
                    prevalence[i] = 0.0996
                elif i <= 59:
                    prevalence[i] = 0.1144
                elif i <= 64:
                    prevalence[i] = 0.1249
                elif i <= 69:
                    prevalence[i] = 0.1318
                elif i <= 74:
                    prevalence[i] = 0.1348
                elif i <= 79:
                    prevalence[i] = 0.1357
                elif i <= 84:
                    prevalence[i] = 0.1349
                elif i <= 89:
                    prevalence[i] = 0.1303
                else:
                    prevalence[i] = 0.1226
        elif comorbidity=='hypertension':
            prevalence= p_hypertension_china(dummy_value_to_work_with_china_function)
        elif comorbidity=='CVD':
            for i in range(101):
                if i <= 4:
                    prevalence[i] = 0.0010
                elif i <= 9:
                    prevalence[i] = 0.0039
                elif i <= 14:
                    prevalence[i] = 0.0075
                elif i <= 19:
                    prevalence[i] = 0.0100
                elif i <= 24:
                    prevalence[i] = 0.0108
                elif i <= 29:
                    prevalence[i] = 0.0135
                elif i <= 34:
                    prevalence[i] = 0.0168
                elif i <= 39:
                    prevalence[i] = 0.0232
                elif i <= 44:
                    prevalence[i] = 0.0448
                elif i <= 49:
                    prevalence[i] = 0.0655
                elif i <= 54:
                    prevalence[i] = 0.0946
                elif i <= 59:
                    prevalence[i] = 0.1336
                elif i <= 64:
                    prevalence[i] = 0.1816
                elif i <= 69:
                    prevalence[i] = 0.2370
                elif i <= 74:
                    prevalence[i] = 0.2953
                elif i <= 79:
                    prevalence[i] = 0.3528
                elif i <= 84:
                    prevalence[i] = 0.3999
                elif i <= 89:
                    prevalence[i] = 0.4250
                else:
                    prevalence[i] = 0.4325

    ######################################  Italy #############################
    if country=='Italy':
        
        if comorbidity=='diabetes':
            for i in range(101):
                if i <= 4:
                    prevalence[i] = 0.0001
                elif i <= 9:
                    prevalence[i] = 0.0009
                elif i <= 14:
                    prevalence[i] = 0.0024
                elif i <= 19:
                    prevalence[i] = 0.0091
                elif i <= 24:
                    prevalence[i] = 0.0264
                elif i <= 29:
                    prevalence[i] = 0.0356
                elif i <= 34:
                    prevalence[i] = 0.0392
                elif i <= 39:
                    prevalence[i] = 0.0428
                elif i <= 44:
                    prevalence[i] = 0.0489
                elif i <= 49:
                    prevalence[i] = 0.0638
                elif i <= 54:
                    prevalence[i] = 0.0893
                elif i <= 59:
                    prevalence[i] = 0.1277
                elif i <= 64:
                    prevalence[i] = 0.1783
                elif i <= 69:
                    prevalence[i] = 0.2106
                elif i <= 74:
                    prevalence[i] = 0.2407
                elif i <= 79:
                    prevalence[i] = 0.2851
                elif i <= 84:
                    prevalence[i] = 0.3348
                elif i <= 89:
                    prevalence[i] = 0.3517
                else:
                    prevalence[i] = 0.3354

        elif comorbidity=='hypertension':
            for i in range(101):
                if i<35:
                    prevalence[i]= 0.14*(i/35.)
                elif i<39:
                    prevalence[i]=0.14
                elif i<44:
                    prevalence[i]=0.1
                elif i<49:
                    prevalence[i]=0.16
                elif i<54:
                    prevalence[i]=0.3
                else:
                    prevalence[i]=0.34

        elif comorbidity=='CVD':
            for i in range(101):
                if i <= 4:
                    prevalence[i] = 0.0021
                elif i <= 9:
                    prevalence[i] = 0.0020
                elif i <= 14:
                    prevalence[i] = 0.0015
                elif i <= 19:
                    prevalence[i] = 0.0027
                elif i <= 24:
                    prevalence[i] = 0.0037
                elif i <= 29:
                    prevalence[i] = 0.0074
                elif i <= 34:
                    prevalence[i] = 0.0106
                elif i <= 39:
                    prevalence[i] = 0.0156
                elif i <= 44:
                    prevalence[i] = 0.0390
                elif i <= 49:
                    prevalence[i] = 0.0569
                elif i <= 54:
                    prevalence[i] = 0.0816
                elif i <= 59:
                    prevalence[i] = 0.1249
                elif i <= 64:
                    prevalence[i] = 0.1904
                elif i <= 69:
                    prevalence[i] = 0.2735
                elif i <= 74:
                    prevalence[i] = 0.3618
                elif i <= 79:
                    prevalence[i] = 0.4350
                elif i <= 84:
                    prevalence[i] = 0.4762
                elif i <= 89:
                    prevalence[i] = 0.4916
                else:
                    prevalence[i] = 0.4825

    ######################################  Maharashtra #############################
    if country=='Maharashtra':    
        print("LOL13")
        if comorbidity=='diabetes':
            
            prevalence=np.array([i*1.63/15 for i in range(15)]+[1.63,1.93,2.00,2.49,2.50,1.21,1.82,2.57,
                        2.21,2.42,3.22,2.37,3.52,3.00,4.18,5.12,
                        3.83,4.29,6.82,5.77,7.53,7.83,8.69,8.88,
                        8.03,8.14,8.50,9.97,10.05,14.43,15.29,
                        13.44,16.39,18.65,15.11,17.66,24.05,16.79,
                        18.53,21.46, 21.55, 22.54, 23.56, 24.59, 
                        25.64, 26.71, 27.79, 28.9,  30.02, 31.16, 
                        32.31,33.49, 34.68, 35.88, 37.1,  38.34,
                        39.6,  40.87, 42.15, 43.45, 44.77, 46.1,
                        47.44, 48.8,50.18, 51.56, 52.97, 54.38, 
                        55.81, 57.26, 58.72, 60.19, 61.67, 63.17,
                        64.68, 66.21,67.75, 69.3, 70.86, 72.43, 
                        74.02, 75.62, 77.23, 78.86, 80.5,82.14])
            for i in range(55,101):
                prevalence[i]=0.5*(prevalence[i]-prevalence[54]) + prevalence[54]
            prevalence=np.array(prevalence)
            prevalence=prevalence/100
            
        elif comorbidity=='hypertension':
            
            prevalence=[i*1.23/15 for i in range(15)]+[1.2300e+00,  1.6300e+00,  2.0500e+00,  2.5100e+00,
                        3.0100e+00,  3.5300e+00,  4.0900e+00,  4.6700e+00 , 5.3000e+00,  5.9500e+00,
                        6.6300e+00 , 7.3500e+00,  8.1000e+00,  8.8900e+00 , 9.7000e+00,  1.0550e+01,
                        1.1430e+01,  1.2340e+01,  1.3290e+01,  1.4260e+01 , 1.5270e+01,  1.6310e+01,
                        1.7390e+01,  1.8490e+01,  1.9630e+01,  2.0800e+01 , 2.2010e+01,  2.3240e+01,
                        2.4510e+01,  2.5810e+01,  2.7140e+01,  2.8510e+01 , 2.9900e+01,  3.1330e+01,
                        3.2800e+01,  3.4290e+01 , 3.5820e+01,  3.7380e+01 , 3.8970e+01,  4.0590e+01,
                        4.2250e+01,  4.3940e+01 , 4.5660e+01,  4.7410e+01 , 4.9190e+01,  5.1010e+01,
                        5.2860e+01,  5.4740e+01 , 5.6660e+01,  5.8610e+01 , 6.0590e+01,  6.2600e+01,
                        6.4640e+01,  6.6720e+01 , 6.8830e+01,  7.0970e+01 , 7.3140e+01,  7.5350e+01,
                        7.7590e+01,  7.9860e+01 , 8.2160e+01,  8.4500e+01 , 8.6860e+01,  8.9260e+01,
                        9.1700e+01,  9.4160e+01 , 9.6660e+01,  9.9190e+01 , 1.0175e+02,  1.0434e+02,
                        1.0697e+02,  1.0963e+02 , 1.1232e+02,  1.1504e+02 , 1.1780e+02,  1.2058e+02,
                        1.2341e+02,  1.2626e+02 , 1.2914e+02,  1.3206e+02 , 1.3501e+02,  1.3799e+02,
                        1.4101e+02,  1.4405e+02 , 1.4713e+02,  1.5024e+02]
            for i in range(55,101):
                prevalence[i]=0.2*(prevalence[i]-prevalence[54]) + prevalence[54]
            prevalence=np.array(prevalence)
        
            prevalence=prevalence/100
            
    ######################################  Uttar Pradesh ################################
    if country=='up':

        warning_string= " 1. Prevalence assumed to be linerly increasing between ages 0-18 and 54+"

        if comorbidity=='diabetes':
                for i in range(101):
                    if i<15:
                        prevalence[i]= 0.025*(i/15.)
                    elif i<19:
                        prevalence[i]=0.025
                    elif i<24:
                        prevalence[i]=0.0288
                    elif i<29:
                        prevalence[i]=0.0412
                    elif i<34:
                        prevalence[i]=0.0595
                    elif i<39:
                        prevalence[i]=0.0781
                    elif i<44:
                        prevalence[i]=0.111
                    elif i<49:
                        prevalence[i]=0.139
                    elif i<54:
                        prevalence[i]=0.206
                    else:
                        prevalence[i]=0.206+0.5*((i-54)/46)
                prevalence=np.array(prevalence)
                #prevalence=prevalence/100
                

        elif comorbidity=='hypertension':
                for i in range(101):
                    if i<15:
                        prevalence[i]= 0.0353*(i/15.)
                    elif i<19:
                        prevalence[i]=0.0353
                    elif i<24:
                        prevalence[i]=0.0493
                    elif i<29:
                        prevalence[i]=0.080
                    elif i<34:
                        prevalence[i]=0.121
                    elif i<39:
                        prevalence[i]=0.156
                    elif i<44:
                        prevalence[i]=0.202
                    elif i<49:
                        prevalence[i]=0.240
                    elif i<54:
                        prevalence[i]=0.248
                    else:
                        prevalence[i]=0.248+0.5*((i-54)/46)
                prevalence=np.array(prevalence)
                #prevalence=prevalence/100
    
    ######################################  tamilnadu #############################
    if country=='tamilnadu':

        if comorbidity=='diabetes':
                for i in range(101):
                    if i<15:
                        prevalence[i]= 0.0202*(i/15.)
                    elif i<19:
                        prevalence[i]=0.0202
                    elif i<24:
                        prevalence[i]=0.0361
                    elif i<29:
                        prevalence[i]=0.0490
                    elif i<34:
                        prevalence[i]=0.0838
                    elif i<39:
                        prevalence[i]=0.1228
                    elif i<44:
                        prevalence[i]=0.1832
                    elif i<49:
                        prevalence[i]=0.2168
                    elif i<54:
                        prevalence[i]=0.3208
                    else:
                        prevalence[i]=0.3208+0.5*((i-54)/46)
                prevalence=np.array(prevalence)
                #prevalence=prevalence/100
  
        elif comorbidity=='hypertension':
                for i in range(101):
                    if i<15:
                        prevalence[i]= 0.0301*(i/15.)
                    elif i<19:
                        prevalence[i]=0.0301
                    elif i<24:
                        prevalence[i]=0.0575
                    elif i<29:
                        prevalence[i]=0.092
                    elif i<34:
                        prevalence[i]=0.1272
                    elif i<39:
                        prevalence[i]=0.17
                    elif i<44:
                        prevalence[i]=0.221
                    elif i<49:
                        prevalence[i]=0.2894
                    elif i<54:
                        prevalence[i]=0.3759
                    else:
                        prevalence[i]=0.3759+0.5*((i-54)/46)
                prevalence=np.array(prevalence)
                #prevalence=prevalence/100
  
    if warning:
        print ("Warning: \n", warning_string)


    #status = (np.random.rand(age.shape[0]) < prevalence[age]).astype(np.int)
    return prevalence
