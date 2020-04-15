import numpy as np
import csv
import math

def get_family_p(country):
    with open('Houseshold.csv',encoding='latin-1') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        flag=False
        for row in csv_reader:
            if flag==False:
                if row[0]==country and len(row[0])==len(country):
                    family_vector=np.array(row)
                    flag=True
            else:
                if row[0]==country and len(row[0])==len(country):
                    family_vector=np.array(row)
                else:
                    break
    family_vector[family_vector=='..']='0.0'
    average_household_size=float(family_vector[4])
    one_person_p=float(family_vector[30])/100
    couple_only_p=float(family_vector[31])/100
    couple_with_children_p=float(family_vector[32])/100
    single_parent_with_children_p=float(family_vector[33])/100
    average_household_size-1*one_person_p-2*couple_only_p
    Extended_family_p=float(family_vector[36])/100
    Non_relative_p=float(family_vector[37])/100
    return np.array([one_person_p,couple_only_p,couple_with_children_p,single_parent_with_children_p])

def get_age_distribution(country):
    age_distribution=[]
    with open('World_Age_2019.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if row[0]==country:
                for i in range(101):
                    age_distribution.append(float(row[i+1]))
                break
    return np.array(age_distribution)

def get_mean_child_number(country):
    with open('TotalFertility.csv',encoding='latin-1') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if row[0]==country:
                child_number=float(row[1])
                break
    return child_number

def get_mother_birth_age_distribution(country):
    mother_birth_age_distribution=[]
    with open('AgeSpecificFertility.csv',encoding='latin-1') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if row[0]==country:
                #15-19	20-24	25-29	30-34	35-39	40-44	45-49
                for i in range(7):
                    mother_birth_age_distribution.append(float(row[i+1]))
                break
    return np.array(mother_birth_age_distribution)

def sample_households_un(n,country):
    max_household_size = 8
    households = np.zeros((n, max_household_size), dtype=np.int)
    households[:] = -1
    age = np.zeros(n, dtype=np.int)
    n_ages = 101
    
    age_distribution = get_age_distribution(country)
    age_distribution = np.array(age_distribution)
    age_distribution = age_distribution/age_distribution.sum()
        
    household_probs = get_family_p(country)
    household_probs /= household_probs.sum()
    num_generated = 0
    #All from UN data
    mean_child_number=get_mean_child_number(country)
    mother_birth_age_distribution=get_mother_birth_age_distribution(country)
    child_to_adult=25
    while num_generated < n:
        if n - num_generated < 5:
            i = 0
        else:
            i = np.random.choice(household_probs.shape[0], p=household_probs)
        #single person household
        #sample from age distribution
        if i == 0:
        #The couple will become couple with children once mother give birth and back to couple when children leave house
            renormalized = mother_birth_age_distribution/mother_birth_age_distribution.sum() 
            mother_age_at_birth = (np.random.choice(7, p=renormalized) + 3)*5+np.random.randint(5)
            if mother_age_at_birth>child_to_adult:
                renormalized = np.append(age_distribution[child_to_adult:mother_age_at_birth],age_distribution[(mother_age_at_birth+child_to_adult):])
                age_vec=np.append(range(child_to_adult,mother_age_at_birth) ,range((mother_age_at_birth+child_to_adult),n_ages))
            else:
                renormalized =age_distribution[mother_age_at_birth+child_to_adult:]
                age_vec=range((mother_age_at_birth+child_to_adult),n_ages)
            renormalized = renormalized/renormalized.sum()
            age[num_generated]=age_vec[np.random.choice(len(age_vec), p=renormalized)]
#            renormalized = age_distribution[child_to_adult:]
#            renormalized = renormalized/renormalized.sum()
#            age[num_generated] = np.random.choice(n_ages-child_to_adult, p=renormalized)+child_to_adult
            generated_this_step = 1
        #couple, sample from age distribution conditioned on age >= 22
        elif i == 1:
            renormalized = mother_birth_age_distribution/mother_birth_age_distribution.sum() 
            mother_age_at_birth = (np.random.choice(7, p=renormalized) + 3)*5+np.random.randint(5)
            if mother_age_at_birth>child_to_adult:
                renormalized = np.append(age_distribution[child_to_adult:mother_age_at_birth],age_distribution[(mother_age_at_birth+child_to_adult):])
                age_vec=np.append(range(child_to_adult,mother_age_at_birth) ,range((mother_age_at_birth+child_to_adult),n_ages))
            else:
                renormalized =age_distribution[mother_age_at_birth+child_to_adult:]
                age_vec=range((mother_age_at_birth+child_to_adult),n_ages)
            renormalized = renormalized/renormalized.sum()
            age[num_generated]=age_vec[np.random.choice(len(age_vec), p=renormalized)]
            age[num_generated+1]=age_vec[np.random.choice(len(age_vec), p=renormalized)]
#            renormalized = age_distribution[(child_to_adult):]
#            renormalized = renormalized/renormalized.sum()
#            age[num_generated] = np.random.choice(n_ages-(child_to_adult), p=renormalized) + (child_to_adult)
#            age[num_generated+1] = np.random.choice(n_ages-(child_to_adult), p=renormalized) + (child_to_adult)
            generated_this_step = 2
        #couple with children
        elif i == 2:           
            child_number=min(2,np.random.poisson(mean_child_number-1))
            child_number+=1
            child_ages=[]
            for j in range(child_number):
                renormalized = age_distribution[:child_to_adult]
                renormalized = renormalized/renormalized.sum()
                child_age = np.random.choice(child_to_adult, p=renormalized)
                age[num_generated+j] = child_age
                child_ages.append(child_age)
            renormalized = mother_birth_age_distribution/mother_birth_age_distribution.sum() 
            mother_age_at_birth = (np.random.choice(7, p=renormalized) + 3)*5+np.random.randint(5)
            mother_current_age = mother_age_at_birth + max(child_ages)
            age[num_generated+child_number] = mother_current_age
            age[num_generated+child_number + 1] = mother_current_age
            generated_this_step = 2+child_number
        #single parent with children_p
        elif i == 3:
            child_number=min(2,np.random.poisson(mean_child_number-1))
            child_number+=1
            child_ages=[]
            for j in range(child_number):
                renormalized = age_distribution[:child_to_adult]
                renormalized = renormalized/renormalized.sum()
                child_age = np.random.choice(child_to_adult, p=renormalized)
                age[num_generated+j] = child_age
                child_ages.append(child_age)
            renormalized = mother_birth_age_distribution/mother_birth_age_distribution.sum()
            mother_age_at_birth = (np.random.choice(7, p=renormalized) + 3)*5+np.random.randint(5)
            mother_current_age = mother_age_at_birth + max(child_ages)
            age[num_generated+child_number] = mother_current_age
            generated_this_step = 1+child_number
        #update list of household contacts
        for i in range(num_generated, num_generated+generated_this_step):
            curr_pos = 0
            for j in range(num_generated, num_generated+generated_this_step):
                if i != j:
                    households[i, curr_pos] = j
                    curr_pos += 1
        num_generated += generated_this_step
    return households, age
    
    

def sample_households_china(n):
    max_household_size = 4

    households = np.zeros((n, max_household_size), dtype=np.int)
    households[:] = -1
    age = np.zeros(n, dtype=np.int)
    n_ages = 101
    #estimates for china from 2020
    #from https://population.un.org/wpp/Download/Standard/Interpolated/
    age_distribution = [16113.281,16543.361,16875.302,17118.429,17282.064,17375.527,17408.145,17389.238,17328.13,17234.143,17117.175,16987.122,16850.435,16715.289,16592.73,16484.473,16388.786,16370.261,16460.9,16637.439,16866.861,17182.465,17477.132,17702.896,17928.813,18144.994,18201.129,18841.832,20387.657,22413.391,24308.028,26355.485,27269.657,26400.295,24405.505,22597.72,20719.355,19296.916,18726.536,18750.928,18640.938,18451.511,18716.505,19599.644,20865.548,22101.75,23374.699,24376.638,24907.095,25077.435,25250.357,25414.362,25172.526,24383.003,23225.134,22043.117,20795.729,19608.86,18589.082,17703.703,16743.545,15666.543,14988.213,14917.427,15198.411,15425.124,15749.105,15550.741,14503.063,12921.733,11444.972,9939.85,8651.521,7764.623,7148.723,6478.704,5807.535,5222.027,4729.055,4307.295,3931.038,3608.42,3272.336,2887.659,2481.964,2118.152,1783.88,1480.587,1215.358,983.8,739.561,551.765,453.96,342.463,217.275,145.809,122.178,96.793,69.654,40.759,74.692]
    age_distribution = np.array(age_distribution)
    age_distribution = age_distribution/age_distribution.sum()
    
    #single person, couple only, parents and unmarried children, 3-generation
    #from https://link.springer.com/article/10.1186/s40711-015-0011-0/tables/2
    #(2010 census, urban populations)
    household_probs = np.array([0.1703, .2117, 0.3557, 0.1126])
    household_probs /= household_probs.sum()
    num_generated = 0
    while num_generated < n:
        if n - num_generated < 5:
            i = 0
        else:
            i = np.random.choice(household_probs.shape[0], p=household_probs)
        #single person household
        #sample from age distribution
        if i == 0:
            age[num_generated] = np.random.choice(n_ages, p=age_distribution)
            generated_this_step = 1
        #couple, sample from age distribution conditioned on age >= 22
        elif i == 1:
            renormalized = age_distribution[22:]
            renormalized = renormalized/renormalized.sum()
            age[num_generated] = np.random.choice(n_ages-22, p=renormalized) + 22
            age[num_generated+1] = np.random.choice(n_ages-22, p=renormalized) + 22
            generated_this_step = 2
        #some information about mother's age at birth of first child
        #https://link.springer.com/article/10.1007/s42379-019-00022-9
        elif i == 2:
            renormalized = age_distribution[:22]
            renormalized = renormalized/renormalized.sum()
            child_age = np.random.choice(22, p=renormalized)
            age[num_generated] = child_age
            #super rough approximation, women have child at a uniformly random age between 23 and 33
            renormalized = age_distribution[23:34]
            renormalized = renormalized/renormalized.sum()
            mother_age_at_birth = np.random.choice(11, p=renormalized) + 23
            mother_current_age = mother_age_at_birth + child_age
            age[num_generated + 1] = mother_current_age
            age[num_generated + 2] = mother_current_age
            generated_this_step = 3
        elif i == 3:
            #start by generating parents/unmarried child
            renormalized = age_distribution[:22]
            renormalized = renormalized/renormalized.sum()
            child_age = np.random.choice(22, p=renormalized)
            age[num_generated] = child_age
            #super rough approximation, women have child at a uniformly random age between 23 and 33
            renormalized = age_distribution[23:34]
            renormalized = renormalized/renormalized.sum()
            mother_age_at_birth = np.random.choice(11, p=renormalized) + 23
            mother_current_age = mother_age_at_birth + child_age
            age[num_generated + 1] = mother_current_age
            age[num_generated + 2] = mother_current_age
            #add grandparents
            renormalized = age_distribution[23:34]
            renormalized = renormalized/renormalized.sum()
            grandmother_age_at_birth = np.random.choice(11, p=renormalized) + 23
            grandmother_current_age = grandmother_age_at_birth + mother_current_age
            age[num_generated + 3] = grandmother_current_age
            age[num_generated + 4] = grandmother_current_age
            generated_this_step = 5
        
        #update list of household contacts
        for i in range(num_generated, num_generated+generated_this_step):
            curr_pos = 0
            for j in range(num_generated, num_generated+generated_this_step):
                if i != j:
                    households[i, curr_pos] = j
                    curr_pos += 1
        num_generated += generated_this_step
    return households, age

def sample_households_italy(n):
    max_household_size = 6
    
    households = np.zeros((n, max_household_size), dtype=np.int)
    households[:] = -1
    age = np.zeros(n, dtype=np.int)    
    n_ages = 101
        
    age_distribution = get_age_distribution("Italy")
    age_distribution = np.array(age_distribution)
    age_distribution = age_distribution/age_distribution.sum()
        
    # List of household types: single household, couple without children, single parent +1/2/3 children, couple +1/2/3 children,
    # family without a nucleus, nucleus with other persons, households with two or more nuclei (a and b)
    household_probs = np.array([0.308179, 0.191000, 0.0694283, 0.0273065, 0.00450268, 0.152655, 0.132429, 0.0340969, 
                       0.043821, 0.033, 0.0150])
    household_probs /= household_probs.sum()
    
    num_generated = 0
    
    # from fertility data
    mother_birth_age_distribution=get_mother_birth_age_distribution("Italy")    
    renormalized_mother = mother_birth_age_distribution/mother_birth_age_distribution.sum()
    renormalized_adult = age_distribution[18:]
    renormalized_adult = renormalized_adult/renormalized_adult.sum()
    # 18 considered as majority age, maybe should consider that children may still live with parents until 30 or so
    renormalized_child = age_distribution[:30]
    renormalized_child = renormalized_child/renormalized_child.sum()
    
    renormalized_adult_older = age_distribution[30:]
    renormalized_adult_older /= renormalized_adult_older.sum()
    # 60 considered as retirement threshold, maybe should be larger, but reasonable for first pass
    renormalized_grandparent = age_distribution[60:]
    renormalized_grandparent = renormalized_grandparent/renormalized_grandparent.sum()
    
    while num_generated < n:
        if n - num_generated < (max_household_size+1):
            i = 0
        else:
            i = np.random.choice(household_probs.shape[0], p=household_probs)
        #single person household
        #sample from age distribution
        if i == 0:
            age[num_generated] = np.random.choice(n_ages-30, p=renormalized_adult_older) + 30
            generated_this_step = 1
        # couple, sample from age distribution conditioned on age >= 18
        elif i == 1:  
            age_adult = np.random.choice(n_ages-30, p=renormalized_adult_older) + 30
            age[num_generated] = age_adult
            age[num_generated+1] = min(n_ages-1,age_adult+3) # man three years older on average
            generated_this_step = 2
        # single parent, 1 child
        elif i == 2:            
            child_age = np.random.choice(30, p=renormalized_child)
            age[num_generated] = child_age
            #super rough approximation
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = min(n_ages-1,mother_age_at_birth + child_age)
            age[num_generated + 1] = mother_current_age
            generated_this_step = 2
        # single parent, 2 children
        elif i == 3:
            for j in range(2):                
                child_age = np.random.choice(30, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = min(n_ages-1,mother_age_at_birth + max(age[num_generated:(num_generated+2)]))
            age[num_generated + 2] = mother_current_age
            generated_this_step = 3
        # single parent, 3 children
        elif i == 4:
            for j in range(3):                
                child_age = np.random.choice(30, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = min(n_ages-1,mother_age_at_birth + max(age[num_generated:(num_generated+3)]))
            age[num_generated + 3] = mother_current_age
            generated_this_step = 4
            
        # couple, 1 child
        elif i == 5: 
            child_age = np.random.choice(30, p=renormalized_child)
            age[num_generated] = child_age
            #super rough approximation
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = min(n_ages-1,mother_age_at_birth + child_age)
            age[num_generated + 1] = mother_current_age
            age[num_generated + 2] = min(n_ages-1,mother_current_age+3)
            generated_this_step = 3
        
        # couple, 2 children
        elif i == 6:
            for j in range(2):                
                child_age = np.random.choice(30, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = min(n_ages-1,mother_age_at_birth + max(age[num_generated:(num_generated+2)]))
            age[num_generated + 2] = mother_current_age
            age[num_generated + 3] = min(n_ages-1,mother_current_age+3)
            generated_this_step = 4            
        
        # couple, 3 children
        elif i == 7:
            for j in range(3):                
                child_age = np.random.choice(30, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = min(n_ages-1,mother_age_at_birth + max(age[num_generated:(num_generated+3)]))
            age[num_generated + 3] = mother_current_age
            age[num_generated + 4] = min(n_ages-1,mother_current_age+3)
            generated_this_step = 5
        
        # family without nucleus
        elif i == 8:
            age[num_generated] = np.random.choice(n_ages-30, p=renormalized_adult_older) + 30
            age[num_generated+1] = np.random.choice(n_ages-30, p=renormalized_adult_older) + 30
            generated_this_step = 2         
                
        # nucleus with other persons (couple, 2 children, adult >= 60)
        elif i == 9:
            for j in range(2):                
                child_age = np.random.choice(30, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = min(n_ages-1,mother_age_at_birth + max(age[num_generated:(num_generated+2)]))
            age[num_generated + 2] = mother_current_age
            age[num_generated + 3] = min(n_ages-1,mother_current_age+3)
            age[num_generated + 4] = np.random.choice(n_ages-60, p=renormalized_grandparent) + 60
            generated_this_step = 5
            
        # households with 2 or more nuclei
        # a - couple with same age for mother/father sampled from > 18 + 2 children <= 18 + 2 grand-parents
        # b - couple with same age for mother/father sampled from > 18 + 2 children <= 18 + 2 children from other marriage <= 18
        # scenario b removed for now 
        
        elif i == 10:
            for j in range(2):                
                child_age = np.random.choice(30, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = min(n_ages-1,mother_age_at_birth + max(age[num_generated:(num_generated+2)]))
            age[num_generated + 2] = mother_current_age
            age[num_generated + 3] = min(n_ages-1,mother_current_age+3)
            #grandparent_age =  np.random.choice(n_ages-60, p=renormalized_grandparent) + 60
            grandmother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            grandmother_current_age = min(n_ages-1,grandmother_age_at_birth + mother_current_age)
            #age[num_generated + 4] = grandparent_age
            #age[num_generated + 5] = grandparent_age+3   
            age[num_generated + 4] = grandmother_current_age
            age[num_generated + 5] = min(n_ages-1,grandmother_current_age+3)   
            generated_this_step = 6
            
        #elif i == 11:
            #for j in range(4):                
                #child_age = np.random.choice(30, p=renormalized_child)
                #age[num_generated+j] = child_age
            #mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            #mother_current_age = min(n_ages-1,mother_age_at_birth + max(age[num_generated:(num_generated+4)]))
            #age[num_generated + 4] = mother_current_age
            #age[num_generated + 5] = min(n_ages-1,mother_current_age+3)          
            #generated_this_step = 6
            
        #update list of household contacts
        for i in range(num_generated, num_generated+generated_this_step):
            curr_pos = 0
            for j in range(num_generated, num_generated+generated_this_step):
                if i != j:
                    households[i, curr_pos] = j
                    curr_pos += 1
        num_generated += generated_this_step
        
    return households, age

def sample_households_lombardy(n):
    max_household_size = 6
    
    households = np.zeros((n, max_household_size), dtype=np.int)
    households[:] = -1
    age = np.zeros(n, dtype=np.int)    
    n_ages = 101
        
    age_distribution = [0.00786667, 0.00786667, 0.00786667, 0.0087, 0.0087,
       0.0087    , 0.00963333, 0.00963333, 0.00963333, 0.00963333,
       0.00963333, 0.00963333, 0.0095    , 0.0095    , 0.0095    ,
       0.0095    , 0.0095    , 0.0095    , 0.00945714, 0.00945714,
       0.00945714, 0.00945714, 0.00945714, 0.00945714, 0.00945714,
       0.01058   , 0.01058   , 0.01058   , 0.01058   , 0.01058   ,
       0.01058   , 0.01058   , 0.01058   , 0.01058   , 0.01058   ,
       0.01381   , 0.01381   , 0.01381   , 0.01381   , 0.01381   ,
       0.01381   , 0.01381   , 0.01381   , 0.01381   , 0.01381   ,
       0.01664   , 0.01664   , 0.01664   , 0.01664   , 0.01664   ,
       0.01664   , 0.01664   , 0.01664   , 0.01664   , 0.01664   ,
       0.0133    , 0.0133    , 0.0133    , 0.0133    , 0.0133    ,
       0.0133    , 0.0133    , 0.0133    , 0.0133    , 0.0133    ,
       0.01091   , 0.01091   , 0.01091   , 0.01091   , 0.01091   ,
       0.01091   , 0.01091   , 0.01091   , 0.01091   , 0.01091   ,
       0.00894924, 0.00859131, 0.00823338, 0.00787545, 0.00751752,
       0.00715959, 0.00680166, 0.00644373, 0.0060858 , 0.00572787,
       0.00536994, 0.00501201, 0.00465408, 0.00429615, 0.00393822,
       0.0035803 , 0.00322237, 0.00286444, 0.00250651, 0.00214858,
       0.00179065, 0.00143272, 0.00107479, 0.00071686, 0.00035893,
       0.00054791]
    age_distribution = np.array(age_distribution)
    age_distribution = age_distribution/age_distribution.sum()
        
    # List of household types: single household, couple without children, single parent +1/2/3 children, couple +1/2/3 children,
    # family without a nucleus, nucleus with other persons, households with two or more nuclei (a and b)
    household_probs = np.array([0.308179, 0.191000, 0.0694283, 0.0273065, 0.00450268, 0.152655, 0.132429, 0.0340969, 
                       0.043821, 0.033, 0.0150])
    household_probs /= household_probs.sum()
    
    num_generated = 0
    
    # from fertility data
    mother_birth_age_distribution=get_mother_birth_age_distribution("Italy")    
    renormalized_mother = mother_birth_age_distribution/mother_birth_age_distribution.sum()
    renormalized_adult = age_distribution[18:]
    renormalized_adult = renormalized_adult/renormalized_adult.sum()
    # 18 considered as majority age, maybe should consider that children may still live with parents until 30 or so
    renormalized_child = age_distribution[:30]
    renormalized_child = renormalized_child/renormalized_child.sum()
    
    renormalized_adult_older = age_distribution[30:]
    renormalized_adult_older /= renormalized_adult_older.sum()
    # 60 considered as retirement threshold, maybe should be larger, but reasonable for first pass
    renormalized_grandparent = age_distribution[60:]
    renormalized_grandparent = renormalized_grandparent/renormalized_grandparent.sum()
    
    while num_generated < n:
        if n - num_generated < (max_household_size+1):
            i = 0
        else:
            i = np.random.choice(household_probs.shape[0], p=household_probs)
        #single person household
        #sample from age distribution
        if i == 0:
            age[num_generated] = np.random.choice(n_ages-30, p=renormalized_adult_older) + 30
            generated_this_step = 1
        # couple, sample from age distribution conditioned on age >= 18
        elif i == 1:  
            age_adult = np.random.choice(n_ages-30, p=renormalized_adult_older) + 30
            age[num_generated] = age_adult
            age[num_generated+1] = min(n_ages-1,age_adult+3) # man three years older on average
            generated_this_step = 2
        # single parent, 1 child
        elif i == 2:            
            child_age = np.random.choice(30, p=renormalized_child)
            age[num_generated] = child_age
            #super rough approximation
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = min(n_ages-1,mother_age_at_birth + child_age)
            age[num_generated + 1] = mother_current_age
            generated_this_step = 2
        # single parent, 2 children
        elif i == 3:
            for j in range(2):                
                child_age = np.random.choice(30, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = min(n_ages-1,mother_age_at_birth + max(age[num_generated:(num_generated+2)]))
            age[num_generated + 2] = mother_current_age
            generated_this_step = 3
        # single parent, 3 children
        elif i == 4:
            for j in range(3):                
                child_age = np.random.choice(30, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = min(n_ages-1,mother_age_at_birth + max(age[num_generated:(num_generated+3)]))
            age[num_generated + 3] = mother_current_age
            generated_this_step = 4
            
        # couple, 1 child
        elif i == 5: 
            child_age = np.random.choice(30, p=renormalized_child)
            age[num_generated] = child_age
            #super rough approximation
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = min(n_ages-1,mother_age_at_birth + child_age)
            age[num_generated + 1] = mother_current_age
            age[num_generated + 2] = min(n_ages-1,mother_current_age+3)
            generated_this_step = 3
        
        # couple, 2 children
        elif i == 6:
            for j in range(2):                
                child_age = np.random.choice(30, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = min(n_ages-1,mother_age_at_birth + max(age[num_generated:(num_generated+2)]))
            age[num_generated + 2] = mother_current_age
            age[num_generated + 3] = min(n_ages-1,mother_current_age+3)
            generated_this_step = 4            
        
        # couple, 3 children
        elif i == 7:
            for j in range(3):                
                child_age = np.random.choice(30, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = min(n_ages-1,mother_age_at_birth + max(age[num_generated:(num_generated+3)]))
            age[num_generated + 3] = mother_current_age
            age[num_generated + 4] = min(n_ages-1,mother_current_age+3)
            generated_this_step = 5
        
        # family without nucleus
        elif i == 8:
            age[num_generated] = np.random.choice(n_ages-30, p=renormalized_adult_older) + 30
            age[num_generated+1] = np.random.choice(n_ages-30, p=renormalized_adult_older) + 30
            generated_this_step = 2         
                
        # nucleus with other persons (couple, 2 children, adult >= 60)
        elif i == 9:
            for j in range(2):                
                child_age = np.random.choice(30, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = min(n_ages-1,mother_age_at_birth + max(age[num_generated:(num_generated+2)]))
            age[num_generated + 2] = mother_current_age
            age[num_generated + 3] = min(n_ages-1,mother_current_age+3)
            age[num_generated + 4] = np.random.choice(n_ages-60, p=renormalized_grandparent) + 60
            generated_this_step = 5
            
        # households with 2 or more nuclei
        # a - couple with same age for mother/father sampled from > 18 + 2 children <= 18 + 2 grand-parents
        # b - couple with same age for mother/father sampled from > 18 + 2 children <= 18 + 2 children from other marriage <= 18
        # scenario b removed for now 
        
        elif i == 10:
            for j in range(2):                
                child_age = np.random.choice(30, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = min(n_ages-1,mother_age_at_birth + max(age[num_generated:(num_generated+2)]))
            age[num_generated + 2] = mother_current_age
            age[num_generated + 3] = min(n_ages-1,mother_current_age+3)
            #grandparent_age =  np.random.choice(n_ages-60, p=renormalized_grandparent) + 60
            grandmother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            grandmother_current_age = min(n_ages-1,grandmother_age_at_birth + mother_current_age)
            #age[num_generated + 4] = grandparent_age
            #age[num_generated + 5] = grandparent_age+3   
            age[num_generated + 4] = grandmother_current_age
            age[num_generated + 5] = min(n_ages-1,grandmother_current_age+3)   
            generated_this_step = 6
            
        #elif i == 11:
            #for j in range(4):                
                #child_age = np.random.choice(30, p=renormalized_child)
                #age[num_generated+j] = child_age
            #mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            #mother_current_age = min(n_ages-1,mother_age_at_birth + max(age[num_generated:(num_generated+4)]))
            #age[num_generated + 4] = mother_current_age
            #age[num_generated + 5] = min(n_ages-1,mother_current_age+3)          
            #generated_this_step = 6
            
        #update list of household contacts
        for i in range(num_generated, num_generated+generated_this_step):
            curr_pos = 0
            for j in range(num_generated, num_generated+generated_this_step):
                if i != j:
                    households[i, curr_pos] = j
                    curr_pos += 1
        num_generated += generated_this_step
        
    return households, age

def sample_households_uk(n):    
    
    max_household_size = 6
    
    households = np.zeros((n, max_household_size), dtype=np.int)
    households[:] = -1
    age = np.zeros(n, dtype=np.int)    
    n_ages = 101
        
    age_distribution = get_age_distribution("United Kingdom")
    age_distribution = np.array(age_distribution)
    age_distribution = age_distribution/age_distribution.sum()
    
    # Source: https://www.statista.com/statistics/813647/share-of-households-uk/        
    # List of household types: 1 retired adult, 2 retired adults, 1 adult without children, 2 adults without children, 
    # 3 or more adults without children (taken equal to 3, possibly different ages),
    # 2 adults with one child, 2 adults with 2 children, 2 adults with 3 or more children (taken equal to 3), 
    # 3 or more adults (a: couple, one age grand parent b: couple, two grand parents) with children (taken equal to 2)
    
    household_probs = np.array([0.14, 0.135, 0.134, 0.212, 0.079, 0.048, 0.083, 0.099, 0.028, 0.021, 0.021])
    household_probs /= household_probs.sum()
    
    num_generated = 0
    
    # from fertility data
    mother_birth_age_distribution=get_mother_birth_age_distribution("UnitedKingdom")    
    renormalized_mother = mother_birth_age_distribution/mother_birth_age_distribution.sum()
    renormalized_adult = age_distribution[18:]
    renormalized_adult = renormalized_adult/renormalized_adult.sum()
    # 18 considered as majority age, maybe should consider that children may still live with parents until 30 or so
    renormalized_child = age_distribution[:18]
    renormalized_child = renormalized_child/renormalized_child.sum()
    # 60 considered as retirement threshold, maybe should be larger, but reasonable for first pass
    renormalized_grandparent = age_distribution[60:]
    renormalized_grandparent = renormalized_grandparent/renormalized_grandparent.sum()
    
    while num_generated < n:
        if n - num_generated < (max_household_size+1):
            i = 0
        else:
            i = np.random.choice(household_probs.shape[0], p=household_probs)
        # retired adult
        if i == 0:
            age[num_generated] = np.random.choice(n_ages-60, p=renormalized_grandparent) + 60
            generated_this_step = 1
        # 2 retired adults
        elif i == 1:  
            age_adult = np.random.choice(n_ages-60, p=renormalized_grandparent) + 60
            age[num_generated] = age_adult
            age[num_generated+1] = min(n_ages-1,age_adult+3) # man three years older on average
            generated_this_step = 2
        # 1 adult without children
        elif i == 2:            
            age[num_generated] = np.random.choice(n_ages-18, p=renormalized_adult) + 18
            generated_this_step = 1      
        # 2 adults without chidren
        elif i == 3:
            age_adult = np.random.choice(n_ages-18, p=renormalized_adult) + 18
            age[num_generated] = age_adult
            age[num_generated+1] = min(n_ages-1,age_adult+3)
            generated_this_step = 2
        # 3 adults without children
        elif i == 4:
            age[num_generated] = np.random.choice(n_ages-18, p=renormalized_adult) + 18
            age[num_generated+1] = np.random.choice(n_ages-18, p=renormalized_adult) + 18
            age[num_generated+2] = np.random.choice(n_ages-18, p=renormalized_adult) + 18
            generated_this_step = 3
        # 1 adult with children (taken equal to 1)        
        elif i == 5:
            child_age = np.random.choice(18, p=renormalized_child)
            age[num_generated] = child_age
            #super rough approximation
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = mother_age_at_birth + child_age
            age[num_generated + 1] = mother_current_age
            generated_this_step = 2
        # 2 adults with one child
        elif i == 6:
            child_age = np.random.choice(18, p=renormalized_child)
            age[num_generated] = child_age
            #super rough approximation
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = mother_age_at_birth + child_age
            age[num_generated + 1] = mother_current_age
            age[num_generated + 2] = min(n_ages-1,mother_current_age+3)
            generated_this_step = 3
        # 2 adults with 2 children
        elif i == 7:
            for j in range(2):                
                child_age = np.random.choice(18, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = mother_age_at_birth + max(age[num_generated:(num_generated+2)])
            age[num_generated + 2] = mother_current_age
            age[num_generated + 3] = min(n_ages-1,mother_current_age+3)
            generated_this_step = 4   
        # 2 adults with 3 children
        elif i == 8:
            for j in range(3):                
                child_age = np.random.choice(18, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = mother_age_at_birth + max(age[num_generated:(num_generated+3)])
            age[num_generated + 3] = mother_current_age
            age[num_generated + 4] = min(n_ages-1,mother_current_age+3)
            generated_this_step = 5
        # 3 adults + children - a
        elif i == 9:
            for j in range(2):                
                child_age = np.random.choice(18, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = mother_age_at_birth + max(age[num_generated:(num_generated+2)])
            age[num_generated + 2] = mother_current_age
            age[num_generated + 3] = min(n_ages-1,mother_current_age+3)
            grandparent_age =  np.random.choice(n_ages-60, p=renormalized_grandparent) + 60
            age[num_generated + 4] = grandparent_age  
            generated_this_step = 5
        # 3 adults + children - b
        elif i == 10:
            for j in range(2):                
                child_age = np.random.choice(18, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = mother_age_at_birth + max(age[num_generated:(num_generated+2)])
            age[num_generated + 2] = mother_current_age
            age[num_generated + 3] = min(n_ages-1,mother_current_age+3)
            #grandparent_age =  np.random.choice(n_ages-60, p=renormalized_grandparent) + 60
            grandmother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            grandmother_current_age = grandmother_age_at_birth + mother_current_age
            #age[num_generated + 4] = grandparent_age
            #age[num_generated + 5] = grandparent_age+3   
            age[num_generated + 4] = grandmother_current_age
            age[num_generated + 5] = min(n_ages-1,grandmother_current_age+3) 
            generated_this_step = 6
            
        #update list of household contacts
        for i in range(num_generated, num_generated+generated_this_step):
            curr_pos = 0
            for j in range(num_generated, num_generated+generated_this_step):
                if i != j:
                    households[i, curr_pos] = j
                    curr_pos += 1
        num_generated += generated_this_step
        
    return households, age

def sample_households_spain(n):
    
    max_household_size = 6
    
    households = np.zeros((n, max_household_size), dtype=np.int)
    households[:] = -1
    age = np.zeros(n, dtype=np.int)    
    n_ages = 101
        
    age_distribution = get_age_distribution("Spain")
    age_distribution = np.array(age_distribution)
    age_distribution = age_distribution/age_distribution.sum()
    
    # Source: https://www.ine.es/en/prensa/np837_en.pdf
    # List of household types: single person, couple without children living in the household, couple with 1 child, couple with 2 children,
    # couple with 3 children or more (taken equal to 3), one adult with children (with 1, 2, 3),
    # couple or father/mother with children and other persons (couple with 2 children, person aged >= 60)
    # more than one family nucleus, others (approximated by family without nucleus - 2 adult ages)
    household_probs = np.array([0.242, 0.216, 0.164, 0.153, 0.032, 0.047, 0.0282, 0.0188, 0.026, 0.021, 0.052])
    household_probs /= household_probs.sum()
    
    num_generated = 0
    
    # from fertility data
    mother_birth_age_distribution=get_mother_birth_age_distribution("Spain")    
    renormalized_mother = mother_birth_age_distribution/mother_birth_age_distribution.sum()
    renormalized_adult = age_distribution[18:]
    renormalized_adult = renormalized_adult/renormalized_adult.sum()
    # 18 considered as majority age, maybe should consider that children may still live with parents until 30 or so
    renormalized_child = age_distribution[:18]
    renormalized_child = renormalized_child/renormalized_child.sum()
    # 60 considered as retirement threshold, maybe should be larger, but reasonable for first pass
    renormalized_grandparent = age_distribution[60:]
    renormalized_grandparent = renormalized_grandparent/renormalized_grandparent.sum()
    
    while num_generated < n:
        if n - num_generated < (max_household_size+1):
            i = 0
        else:
            i = np.random.choice(household_probs.shape[0], p=household_probs) 
            
        # single person
        if i == 0:
            age[num_generated] = np.random.choice(n_ages-18, p=renormalized_adult) + 18
            generated_this_step = 1            
        # couple without children
        elif i == 1:
            age_adult = np.random.choice(n_ages-18, p=renormalized_adult) + 18
            age[num_generated] = age_adult
            age[num_generated+1] = min(n_ages-1,age_adult+3)
            generated_this_step = 2            
        # couple with 1 child
        elif i == 2:
            child_age = np.random.choice(18, p=renormalized_child)
            age[num_generated] = child_age
            #super rough approximation
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = mother_age_at_birth + child_age
            age[num_generated + 1] = mother_current_age
            age[num_generated + 2] = min(n_ages-1,mother_current_age+3)
            generated_this_step = 3            
        # couple with 2 children
        elif i == 3:
            for j in range(2):                
                child_age = np.random.choice(18, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = mother_age_at_birth + max(age[num_generated:(num_generated+2)])
            age[num_generated + 2] = mother_current_age
            age[num_generated + 3] = min(n_ages-1,mother_current_age+3)
            generated_this_step = 4              
        # couple with 3 children or more 
        elif i == 4:
            for j in range(3):                
                child_age = np.random.choice(18, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = mother_age_at_birth + max(age[num_generated:(num_generated+3)])
            age[num_generated + 3] = mother_current_age
            age[num_generated + 4] = min(n_ages-1,mother_current_age+3)
            generated_this_step = 5
        # one adult with children
        # 1 child (50%)
        elif i == 5:
            child_age = np.random.choice(18, p=renormalized_child)
            age[num_generated] = child_age
            #super rough approximation
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = mother_age_at_birth + child_age
            age[num_generated + 1] = mother_current_age
            generated_this_step = 2
        # 2 children (30%)
        elif i == 6:
            for j in range(2):                
                child_age = np.random.choice(18, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = mother_age_at_birth + max(age[num_generated:(num_generated+2)])
            age[num_generated + 2] = mother_current_age
            generated_this_step = 3
        # 3 children (20%)
        elif i == 7:
            for j in range(3):                
                child_age = np.random.choice(18, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = mother_age_at_birth + max(age[num_generated:(num_generated+3)])
            age[num_generated + 3] = mother_current_age
            generated_this_step = 4
    
        # couple or father/mother with children and other persons
        elif i == 8:
            for j in range(2):                
                child_age = np.random.choice(18, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = mother_age_at_birth + max(age[num_generated:(num_generated+2)])
            age[num_generated + 2] = mother_current_age
            age[num_generated + 3] = min(n_ages-1,mother_current_age+3)
            age[num_generated + 4] = np.random.choice(n_ages-60, p=renormalized_grandparent) + 60
            generated_this_step = 5
    
        # similar to "more than one family nucleus" in Italy
        # approximated by: a - couple with same age for mother/father sampled from > 18 + 2 children <= 18 + 2 grand-parents
        elif i == 9:
            for j in range(2):                
                child_age = np.random.choice(18, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = mother_age_at_birth + max(age[num_generated:(num_generated+2)])
            age[num_generated + 2] = mother_current_age
            age[num_generated + 3] = min(n_ages-1,mother_current_age+3)
            #grandparent_age =  np.random.choice(n_ages-60, p=renormalized_grandparent) + 60
            grandmother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            grandmother_current_age = grandmother_age_at_birth + mother_current_age
            #age[num_generated + 4] = grandparent_age
            #age[num_generated + 5] = grandparent_age+3   
            age[num_generated + 4] = grandmother_current_age
            age[num_generated + 5] = min(n_ages-1,grandmother_current_age+3)  
            generated_this_step = 6

        # others
        elif i == 10:
            age[num_generated] = np.random.choice(n_ages-18, p=renormalized_adult) + 18
            age[num_generated+1] = np.random.choice(n_ages-18, p=renormalized_adult) + 18
            generated_this_step = 2   
            
        #update list of household contacts
        for i in range(num_generated, num_generated+generated_this_step):
            curr_pos = 0
            for j in range(num_generated, num_generated+generated_this_step):
                if i != j:
                    households[i, curr_pos] = j
                    curr_pos += 1
        num_generated += generated_this_step
        
    return households, age

def sample_households_germany(n): 
        
    max_household_size = 6
    
    households = np.zeros((n, max_household_size), dtype=np.int)
    households[:] = -1
    age = np.zeros(n, dtype=np.int)    
    n_ages = 101
    
    age_distribution = get_age_distribution("Germany")
    age_distribution = np.array(age_distribution)
    age_distribution = age_distribution/age_distribution.sum()
    
    # Source 1: https://www.statista.com/statistics/464187/households-by-size-germany/
    # Source 2 (3 tables): https://www.destatis.de/EN/Themes/Society-Environment/Population/Households-Families/Tables/couples.html, 
    # https://www.destatis.de/EN/Themes/Society-Environment/Population/Households-Families/Tables/families.html,
    # https://www.destatis.de/EN/Themes/Society-Environment/Population/Households-Families/Tables/unattached-people.html
    
    age_18_24 = age_distribution[18:25]
    age_18_24 /= age_18_24.sum()
    age_25_44 = age_distribution[25:45]
    age_25_44 /= age_25_44.sum()
    age_45_64 = age_distribution[45:65]
    age_45_64 /= age_45_64.sum()
    age_65_84 = age_distribution[65:85]
    age_65_84 /= age_65_84.sum()
    age_85 = age_distribution[85:]
    age_85 /= age_85.sum()
    
    age_one_person_scaling = np.array([0.0761527, 0.280135, 0.297618, 0.282802, 0.0632923])
    age_one_person_scaling *= 0.4189042
    
    two_person_scaling = np.array([0.862261, 0.106558, 0.031181])
    two_person_scaling *= 0.337941
    
    age_child_0_17 = age_distribution[:18]
    age_child_0_17 /= age_child_0_17.sum()
    age_child_0_17_final = np.zeros(30)
    age_child_0_17_final[:18] = age_child_0_17
    age_child_18_30 = age_distribution[18:30]
    age_child_18_30 /= age_child_18_30.sum()
    age_child_18_30_final = np.zeros(30)
    age_child_18_30_final[18:] = age_child_18_30
    
    renormalized_child = 0.741 * age_child_0_17_final + 0.259 * age_child_18_30_final
    
    renormalized_adult = age_distribution[18:]
    renormalized_adult /= renormalized_adult.sum()
    renormalized_grandparent = age_distribution[60:]
    renormalized_grandparent /= renormalized_grandparent.sum()
    
    # from fertility data
    mother_birth_age_distribution=get_mother_birth_age_distribution("Germany")    
    renormalized_mother = mother_birth_age_distribution/mother_birth_age_distribution.sum()
    
    # 5 scenarios, 3 scenarios, 2 scenarios, 3 scenarios
    household_probs = np.concatenate([age_one_person_scaling, age_two_person_scaling,0.118979,0.0905817,
                                      0.0167968,0.00839838,0.00839838])
    household_probs /= household_probs.sum()
 
    num_generated = 0
    
    
    while num_generated < n:
        if n - num_generated < (max_household_size+1):
            i = 0
        else:
            i = np.random.choice(household_probs.shape[0], p=household_probs) 
            
        # single person - 18-24
        if i == 0:
            age[num_generated] = np.random.choice(24-18+1, p=age_18_24) + 18
            generated_this_step = 1            
        # single person - 25-44
        elif i == 1:
            age[num_generated] = np.random.choice(44-25+1, p=age_25_44) + 25
            generated_this_step = 1       
        # single person - 45-64
        elif i == 2:
            age[num_generated] = np.random.choice(64-45+1, p=age_45_64) + 45
            generated_this_step = 1             
        # single person - 65-84
        elif i == 3:
            age[num_generated] = np.random.choice(84-65+1, p=age_65_84) + 65
            generated_this_step = 1            
        # single person - >= 85
        elif i == 4:
            age[num_generated] = np.random.choice(n_ages-85, p=age_85) + 85
            generated_this_step = 1  
            
        # couple without children
        elif i == 5:
            age_adult = np.random.choice(n_ages-18, p=renormalized_adult) + 18
            age[num_generated] = age_adult
            age[num_generated+1] = min(n_ages-1,age_adult+3)
            generated_this_step = 2  
            
        # lone parent + one child
        elif i == 6:
            child_age = np.random.choice(18, p=renormalized_child)
            age[num_generated] = child_age
            #super rough approximation
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = mother_age_at_birth + child_age
            age[num_generated + 1] = mother_current_age
            generated_this_step = 2
            
        # other - 2 random ages
        elif i == 7:
            age[num_generated] = np.random.choice(n_ages-18, p=renormalized_adult) + 18
            age[num_generated+1] = np.random.choice(n_ages-18, p=renormalized_adult) + 18
            generated_this_step = 2
            
        # couple with 1 child
        elif i == 8:
            child_age = np.random.choice(18, p=renormalized_child)
            age[num_generated] = child_age
            #super rough approximation
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = mother_age_at_birth + child_age
            age[num_generated + 1] = mother_current_age
            age[num_generated + 2] = min(n_ages-1,mother_current_age+3)
            generated_this_step = 3   
            
        # couple + 2 children
        elif i == 9:
            for j in range(2):                
                child_age = np.random.choice(30, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = mother_age_at_birth + max(age[num_generated:(num_generated+2)])
            age[num_generated + 2] = mother_current_age
            age[num_generated + 3] = min(n_ages-1,mother_current_age+3)
            generated_this_step = 4          
        
        # couple + 3 children
        elif i == 10:
            for j in range(3):                
                child_age = np.random.choice(18, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = mother_age_at_birth + max(age[num_generated:(num_generated+3)])
            age[num_generated + 3] = mother_current_age
            age[num_generated + 4] = min(n_ages-1,mother_current_age+3)
            generated_this_step = 5
        
        # couple + 4 children
        elif i == 11:
            for j in range(4):                
                child_age = np.random.choice(18, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = mother_age_at_birth + max(age[num_generated:(num_generated+4)])
            age[num_generated + 4] = mother_current_age
            age[num_generated + 5] = min(n_ages-1,mother_current_age+3)
            generated_this_step = 6
        
        # couple + 2 children + grand-mother      
        elif i == 12:
            for j in range(2):                
                child_age = np.random.choice(18, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = mother_age_at_birth + max(age[num_generated:(num_generated+2)])
            age[num_generated + 2] = mother_current_age
            age[num_generated + 3] = min(n_ages-1,mother_current_age+3)
            #grandparent_age =  np.random.choice(n_ages-60, p=renormalized_grandparent) + 60
            grandmother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            grandmother_current_age = grandmother_age_at_birth + mother_current_age
            #age[num_generated + 4] = grandparent_age
            #age[num_generated + 5] = grandparent_age+3   
            age[num_generated + 4] = grandmother_current_age
            generated_this_step = 5
            
        #update list of household contacts
        for i in range(num_generated, num_generated+generated_this_step):
            curr_pos = 0
            for j in range(num_generated, num_generated+generated_this_step):
                if i != j:
                    households[i, curr_pos] = j
                    curr_pos += 1
        num_generated += generated_this_step
        
    return households, age


def sample_households_maharashtra(n):
    print("LOL3")
    max_household_size = 10
    son_lives_with_parents_till_age=30
    
    households = np.zeros((n, max_household_size), dtype=np.int)
    households[:] = -1
    age = np.zeros(n, dtype=np.int)    
    n_ages = 101
    age_distribution= [1.63, 1.54, 1.73, 1.67, 1.68, 1.50, 1.60, 1.58, 1.67, 1.54, 1.67, 1.59, 1.78, 1.65, 2.01, 1.76,
                       1.65, 1.76, 1.93, 1.68, 1.98, 1.84, 2.14, 1.83, 1.95, 2.29, 1.91, 1.71, 1.91, 1.50, 2.23, 1.20,
                       1.78, 1.14, 1.24, 2.20, 1.19, 1.17, 1.37, 1.18, 2.01 ,0.94, 1.38, 1.03, 0.91 ,1.86, 0.95, 0.92,
                       0.99, 0.76, 1.78, 0.79, 1.05, 0.66, 0.73, 1.66, 0.70, 0.66, 0.71, 0.50, 1.74, 0.44, 0.70, 0.45,
                       0.45, 1.84, 0.44, 0.51, 0.41, 0.36, 1.12, 0.22, 0.37, 0.18, 0.20, 0.64, 0.12, 0.12 ,0.14, 0.07,
                       0.38, 0.06, 0.10, 0.05, 0.07, 0.15, 0.03, 0.03, 0.02, 0.03, 0.10, 0.00,0.01, 0.01, 0.01, 0.07,0.02, 0,0,0,0]    
    age_distribution = np.array(age_distribution)
    age_distribution = age_distribution/age_distribution.sum()
        
    # List of household types: single household, couple without children, single parent +1/2/3 children, couple +1/2/3 children,
    # family without a nucleus, nucleus with other persons, households with two or more nuclei (a and b)
    #household_probs = np.array([0.308179, 0.191000, 0.0694283, 0.0273065, 0.00450268, 0.152655, 0.132429, 0.0340969, 
    #                  0.043821, 0.033, 0.0150])
    
    household_probs= np.array([0.0594284038, 0.1135717199, 0.02265637467 ,0.02265637467, 0.006669284629,0.1135717199 ,0.2117641302 ,0.2117641302 ,
                               0.009533560241, 0.003714170745, 0.224670131])
    
    household_probs /= household_probs.sum()
    
    num_generated = 0
    
    # from fertility data
    mother_birth_age_distribution=get_mother_birth_age_distribution("India")    
    renormalized_mother = mother_birth_age_distribution/mother_birth_age_distribution.sum()
    renormalized_adult = age_distribution[18:]
    renormalized_adult = renormalized_adult/renormalized_adult.sum()
    # 18 considered as majority age, maybe should consider that children may still live with parents until 30 or so
    renormalized_child = age_distribution[:30]
    renormalized_child = renormalized_child/renormalized_child.sum()
    
    renormalized_adult_older = age_distribution[30:]
    renormalized_adult_older /= renormalized_adult_older.sum()
    # 60 considered as retirement threshold, maybe should be larger, but reasonable for first pass
    renormalized_grandparent = age_distribution[60:]
    renormalized_grandparent = renormalized_grandparent/renormalized_grandparent.sum()
    
    while num_generated < n:
        if n - num_generated < (max_household_size+1):
            i = 0
        else:
            i = np.random.choice(household_probs.shape[0], p=household_probs)
        #single person household
        #sample from age distribution
        if i == 0:
            age[num_generated] = np.random.choice(n_ages-30, p=renormalized_adult_older) + 30
            generated_this_step = 1
        # couple, sample from age distribution conditioned on age >= 18
        elif i == 1:  
            age_adult = np.random.choice(n_ages-30, p=renormalized_adult_older) + 30
            age[num_generated] = age_adult
            age[num_generated+1] = min(n_ages-1,age_adult+3) # man three years older on average
            generated_this_step = 2
        # single parent, 1 child
        elif i == 2:            
            child_age = np.random.choice(30, p=renormalized_child)
            age[num_generated] = child_age
            #super rough approximation
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = min(n_ages-1,mother_age_at_birth + child_age)
            age[num_generated + 1] = mother_current_age
            generated_this_step = 2
        # single parent, 2 children
        elif i == 3:
            for j in range(2):                
                child_age = np.random.choice(30, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = min(n_ages-1,mother_age_at_birth + max(age[num_generated:(num_generated+2)]))
            age[num_generated + 2] = mother_current_age
            generated_this_step = 3
        # single parent, 3 children
        elif i == 4:
            for j in range(3):                
                child_age = np.random.choice(30, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = min(n_ages-1,mother_age_at_birth + max(age[num_generated:(num_generated+3)]))
            age[num_generated + 3] = mother_current_age
            generated_this_step = 4
            
        # couple, 1 child
        elif i == 5: 
            child_age = np.random.choice(30, p=renormalized_child)
            age[num_generated] = child_age
            #super rough approximation
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = min(n_ages-1,mother_age_at_birth + child_age)
            age[num_generated + 1] = mother_current_age
            age[num_generated + 2] = min(n_ages-1,mother_current_age+3)
            generated_this_step = 3
        
        # couple, 2 children
        elif i == 6:
            for j in range(2):                
                child_age = np.random.choice(30, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = min(n_ages-1,mother_age_at_birth + max(age[num_generated:(num_generated+2)]))
            age[num_generated + 2] = mother_current_age
            age[num_generated + 3] = min(n_ages-1,mother_current_age+3)
            generated_this_step = 4            
        
        # couple, 3 children
        elif i == 7:
            for j in range(3):                
                child_age = np.random.choice(30, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = min(n_ages-1,mother_age_at_birth + max(age[num_generated:(num_generated+3)]))
            age[num_generated + 3] = mother_current_age
            age[num_generated + 4] = min(n_ages-1,mother_current_age+3)
            generated_this_step = 5
        
        # family without nucleus
        elif i == 8:
            age[num_generated] = np.random.choice(n_ages-30, p=renormalized_adult_older) + 30
            age[num_generated+1] = np.random.choice(n_ages-30, p=renormalized_adult_older) + 30
            generated_this_step = 2         
                
        # nucleus with other persons (couple, 2 children, adult >= 60)
        elif i == 9:
            for j in range(2):                
                child_age = np.random.choice(30, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = min(n_ages-1,mother_age_at_birth + max(age[num_generated:(num_generated+2)]))
            age[num_generated + 2] = mother_current_age
            age[num_generated + 3] = min(n_ages-1,mother_current_age+3)
            age[num_generated + 4] = np.random.choice(n_ages-60, p=renormalized_grandparent) + 60
            generated_this_step = 5
            
        # households with 2 or more nuclei
        # a - couple with same age for mother/father sampled from > 18 + 2 children <= 18 + 2 grand-parents
        # b - couple with same age for mother/father sampled from > 18 + 2 children <= 18 + 2 children from other marriage <= 18
        # scenario b removed for now 
        
        elif i == 10:
            for j in range(2):                
                child_age = np.random.choice(30, p=renormalized_child)
                age[num_generated+j] = child_age
            mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            mother_current_age = min(n_ages-1,mother_age_at_birth + max(age[num_generated:(num_generated+2)]))
            age[num_generated + 2] = mother_current_age
            age[num_generated + 3] = min(n_ages-1,mother_current_age+3)
            #grandparent_age =  np.random.choice(n_ages-60, p=renormalized_grandparent) + 60
            grandmother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            grandmother_current_age = min(n_ages-1,grandmother_age_at_birth + mother_current_age)
            #age[num_generated + 4] = grandparent_age
            #age[num_generated + 5] = grandparent_age+3   
            age[num_generated + 4] = grandmother_current_age
            age[num_generated + 5] = min(n_ages-1,grandmother_current_age+3)   
            generated_this_step = 6
            
        #elif i == 11:
            #for j in range(4):                
                #child_age = np.random.choice(30, p=renormalized_child)
                #age[num_generated+j] = child_age
            #mother_age_at_birth = (np.random.choice(7, p=renormalized_mother) + 3)*5+np.random.randint(5)
            #mother_current_age = min(n_ages-1,mother_age_at_birth + max(age[num_generated:(num_generated+4)]))
            #age[num_generated + 4] = mother_current_age
            #age[num_generated + 5] = min(n_ages-1,mother_current_age+3)          
            #generated_this_step = 6
            
        #update list of household contacts
        for i in range(num_generated, num_generated+generated_this_step):
            curr_pos = 0
            for j in range(num_generated, num_generated+generated_this_step):
                if i != j:
                    households[i, curr_pos] = j
                    curr_pos += 1
        num_generated += generated_this_step
        
    return households, age