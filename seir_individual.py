import numpy as np
from numba import jit
import sample_households
import global_parameters
import scipy.special
import sample_comorbidities
import csv
import functions
import pickle
from datetime import date


"""3. RUN SIMULATION."""

def run_complete_simulation(seed, country, contact_matrix, p_mild_severe, p_severe_critical, p_critical_death, mean_time_to_isolate_factor, lockdown_factor_age, p_infect_household, fraction_stay_home, params, load_population=False):
    n = int(params['n'])
    n_ages = int(params['n_ages'])
    np.random.seed(seed)
    if load_population:
        print('loading')
        age, households, diabetes, hypertension, age_groups = pickle.load(open('{}_population_{}.pickle'.format(country, n), 'rb'))
    else:
        if country == "Italy":
          households, age = sample_households.sample_households_italy(n)      
        elif country == "Germany":
          households, age = sample_households.sample_households_germany(n)
        elif country == "UK":
          households, age = sample_households.sample_households_uk(n)
        elif country == "Spain":
          households, age = sample_households.sample_households_spain(n)
        elif country == "China": 
          households, age = sample_households.sample_households_china(n)
        else:
          households, age = sample_households.sample_households_un(n, country)
    #
        age_groups = tuple([np.where(age == i)[0] for i in range(0, n_ages)])
    #    age_group_sizes = np.array([age_groups[i].shape[0] for i in range(0, n_ages)])
    #    diabetes = sample_comorbidities.sample_diabetes_china(age)
    #    hypertension = sample_comorbidities.sample_hypertension_china(age)
        diabetes, hypertension = sample_comorbidities.sample_joint_comorbidities(age, country)
    print('starting simulation')
    return run_model(seed, households, age, age_groups, diabetes, hypertension, contact_matrix, p_mild_severe, p_severe_critical, p_critical_death, mean_time_to_isolate_factor, lockdown_factor_age, p_infect_household, fraction_stay_home, params)

@jit(nopython=True)
def get_isolation_factor(age, mean_time_to_isolate_factor):
    for i in range(len(mean_time_to_isolate_factor)):
        if age >= mean_time_to_isolate_factor[i, 0] and age <= mean_time_to_isolate_factor[i, 1]:
            return mean_time_to_isolate_factor[i, 2]
    return 1

@jit(nopython=True)
def get_lockdown_factor_age(age, lockdown_factor_age):
    for i in range(len(lockdown_factor_age)):
        if age >= lockdown_factor_age[i, 0] and age <= lockdown_factor_age[i, 1]:
            return lockdown_factor_age[i, 2]
    return 1

@jit(nopython=True)
def do_contact_tracing(i, infected_by, p_trace_outside, Q, S, t, households, p_trace_household, Documented, time_documented, traced):
    #trace contacts within the household
    for j in range(households.shape[1]):
        contact = households[i, j]
        if contact == -1:
            break
        if not S[t-1, contact] and not traced[contact] and np.random.rand() < p_trace_household:
            Q[t, contact] = True
            Documented[t, contact] = True
            traced[contact] = True
            time_documented[contact] = t
            do_contact_tracing(contact, infected_by, p_trace_outside, Q, S, t, households, p_trace_household, Documented, time_documented, traced)
    #trace outside of household contacts
    for j in range(infected_by.shape[1]):
        contact = infected_by[i, j]
        if contact == -1:
            break
        if np.random.rand() < p_trace_outside:
            Q[t, contact] = True
            Documented[t, contact] = True
            time_documented[contact] = t
            traced[contact] = True
            do_contact_tracing(contact, infected_by, p_trace_outside, Q, S, t, households, p_trace_household, Documented, time_documented, traced)

@jit(nopython=True)
def run_model(seed, households, age, age_groups, diabetes, hypertension, contact_matrix, p_mild_severe, p_severe_critical, p_critical_death, mean_time_to_isolate_factor, lockdown_factor_age, p_infect_household, fraction_stay_home, params):
    print('run_model')
    """Run the SEIR model to completion.

    Args:
        seed (int): Random seed.
        households: Household structure.
        age (int vector of length n): Age of each individual.
        diabetes (bool vector of length n): Diabetes state of each individual.
        hypertension (bool vector of length n): Hypertension state of each
            individual.

    Returns:
        S (bool T x n matrix): Matrix where S[i][j] represents
            whether individual i was in the Susceptible state at time j.
        E (bool T x n matrix): same for Exposed state.
        Mild (bool T x n matrix): same for Mild state.
        Severe (bool T x n matrix): same for Severe state.
        Critical (bool T x n matrix): same for Critical state.
        R (bool T x n matrix): same for Recovered state.
        D (bool T x n matrix): same for Dead state.
        Q (bool T x n matrix): same for Quarantined state.
        num_infected_by (n vector): num_infected_by[i] is the number of individuals
            infected by individual i.
        time_to_activation (n vector): TODO
        time_to_death (n vector):  TODO
        time_to_recovery: TODO
        time_critical: TODO
        time_exposed: TODO
    """
    time_to_activation_mean = params['time_to_activation_mean']
    time_to_activation_std = params['time_to_activation_std']
    mean_time_to_death = params['mean_time_to_death']
    mean_time_critical_recovery = params['mean_time_critical_recovery']
    mean_time_severe_recovery = params['mean_time_severe_recovery']
    mean_time_to_severe = params['mean_time_to_severe']
    mean_time_mild_recovery = params['mean_time_mild_recovery']
    mean_time_to_critical = params['mean_time_to_critical']
    p_documented_in_mild = params['p_documented_in_mild']
    mean_time_to_isolate_asympt = params['mean_time_to_isolate_asympt']
    asymptomatic_transmissibility = params['asymptomatic_transmissibility']
    p_infect_given_contact = params['p_infect_given_contact']
    T = int(params['T'])
    initial_infected_fraction = params['initial_infected_fraction']
    t_lockdown = int(params['t_lockdown'])
    t_lockdown_end=int(params['t_lockdown_end'])
    #points=params['event_points']
    lockdown_factor = params['lockdown_factor']
    mild_dist_factor=params['mild_dist_factor']
    #social_dist_factor=params['social_dist_factor']
    mean_time_to_isolate = params['mean_time_to_isolate']
    n = int(params['n'])
    n_ages = int(params['n_ages'])
    contact_tracing = bool(params['contact_tracing'])
    p_trace_outside = params['p_trace_outside']
    p_trace_household = params['p_trace_household']
    t_tracing_start = int(params['t_tracing_start'])
    t_stayinghome_start = int(params['t_stayhome_start'])
    if contact_tracing:
        tracing_enabled = True
        contact_tracing = False
    
    np.random.seed(seed)
    max_household_size = households.shape[1]
    S = np.zeros((T, n), dtype=np.bool8)
    E = np.zeros((T, n), dtype=np.bool8)
    Mild = np.zeros((T, n), dtype=np.bool8)
    Documented = np.zeros((T, n), dtype=np.bool8)
    Severe = np.zeros((T, n), dtype=np.bool8)
    Critical = np.zeros((T, n), dtype=np.bool8)
    R = np.zeros((T, n), dtype=np.bool8)
    D = np.zeros((T, n), dtype=np.bool8)
    Q = np.zeros((T, n), dtype=np.bool8)
    traced = np.zeros((n), dtype=np.bool8)
    Home_real = np.zeros(n, dtype=np.bool8)
    Home_real[:] = False
    for i in range(n_ages):
        matches = np.where(age == i)[0]
        if matches.shape[0] > 0:
            to_stay_home = np.random.choice(matches, int(fraction_stay_home[i]*matches.shape[0]), replace=False)
            Home_real[to_stay_home] = True
    dummy_Home = np.zeros(n, dtype=np.bool8)
    dummy_Home[:] = False
    Home = dummy_Home
    initial_infected = np.random.choice(n, int(initial_infected_fraction*n), replace=False)
    S[0] = True
    E[0] = False
    R[0] = False
    D[0] = False
    Mild[0] = False
    Documented[0]=False
    Severe[0] = False
    Critical[0] = False

    infected_by = np.zeros((n, 100), dtype=np.int32)
    infected_by[:] = -1
    
    time_exposed = np.zeros(n)
    time_infected = np.zeros(n)
    time_severe = np.zeros(n)
    time_critical = np.zeros(n)
    time_documented=np.zeros(n)
    time_exposed[:] = -1
    #total number of infections caused by every individual, -1 if never become infectious
    num_infected_by = np.zeros(n)
    num_infected_by_outside = np.zeros(n, dtype=np.int32)
    num_infected_asympt = np.zeros(n)
    num_infected_by[:] = -1
    num_infected_by_outside[:] = -1
    num_infected_asympt[:] = -1
    time_to_severe = np.zeros(n)
    time_to_recovery = np.zeros(n)
    time_to_critical = np.zeros(n)
    time_to_death = np.zeros(n)
    time_to_isolate = np.zeros(n)
    time_to_activation = np.zeros(n)
#    time_to_documented= np.zeros(n)

    for i in range(initial_infected.shape[0]):
        E[0, initial_infected[i]] = True
        S[0, initial_infected[i]] = False
        time_exposed[initial_infected[i]] = 0
        num_infected_by[initial_infected[i]] = 0
        num_infected_by_outside[initial_infected[i]] = 0
        num_infected_asympt[initial_infected[i]] = 0
        time_to_activation[initial_infected[i]] = functions.threshold_log_normal(time_to_activation_mean, time_to_activation_std)
    print('Initialized finished')
    print('mean_time_to_isolate',mean_time_to_isolate)
    
    original_contact_matrix=np.copy(contact_matrix)
    for t in range(1, T):
        if t % 10 == 0:
            print(t,"/",T)
        # print(S.sum(axis=1)[t-1])
        if t == t_lockdown:
        #    for i in range(contact_matrix.shape[0]):
        #        for j in range(contact_matrix.shape[1]):
        #            contact_matrix[i,j] = contact_matrix[i,j]/(get_lockdown_factor_age(i,lockdown_factor_age)*get_lockdown_factor_age(j,lockdown_factor_age))
            contact_matrix = contact_matrix/lockdown_factor
        
        if t==params['t1']: # 14 April
            contact_matrix = np.copy(original_contact_matrix)
            contact_matrix = contact_matrix/params['factor_t1']
        if t==params['t2']: # 21 April
            contact_matrix = np.copy(original_contact_matrix)
            contact_matrix = contact_matrix/params['factor_t2']
        if t==params['t3']: # 30 April
            contact_matrix = np.copy(original_contact_matrix)
            contact_matrix = contact_matrix/params['factor_t3']
        if t==params['t4']: # 7 May
            contact_matrix = np.copy(original_contact_matrix)
            contact_matrix = contact_matrix/params['factor_t4']
        
        
        if t==t_lockdown_end:
            contact_matrix = contact_matrix*(lockdown_factor)
        if t == t_tracing_start and tracing_enabled:
            contact_tracing = True
        if t == t_stayinghome_start:
            Home = Home_real
        S[t] = S[t-1]
        E[t] = E[t-1]
        Mild[t] = Mild[t-1]
        Documented[t]=Documented[t-1]
        Severe[t] = Severe[t-1]
        Critical[t] = Critical[t-1]
        R[t] = R[t-1]
        D[t] = D[t-1]
        Q[t] = Q[t-1]
        for i in range(n):
            #exposed -> (mildly) infected
            if E[t-1, i]:
                if t - time_exposed[i] == time_to_activation[i]:
                    Mild[t, i] = True
                    time_infected[i] = t
                    E[t, i] = False
                    #draw whether they will progress to severe illness
                    if np.random.rand() < p_mild_severe[age[i], diabetes[i], hypertension[i]]:
                        time_to_severe[i] = functions.threshold_exponential(mean_time_to_severe)
                        time_to_recovery[i] = np.inf
                    #draw time to recovery
                    else:
                        time_to_recovery[i] = functions.threshold_exponential(mean_time_mild_recovery)
                        time_to_severe[i] = np.inf
                    #draw time to isolation
                    time_to_isolate[i] = functions.threshold_exponential(mean_time_to_isolate*get_isolation_factor(age[i], mean_time_to_isolate_factor))
                    if time_to_isolate[i] == 0:
                        Q[t, i] = True
            #symptomatic individuals
            if (Mild[t-1, i] or Severe[t-1, i] or Critical[t-1, i]):
                #recovery
                if t - time_infected[i] == time_to_recovery[i]:
                    R[t, i] = True
                    Mild[t, i] = Severe[t, i] = Critical[t, i] = Q[t, i] = False
                    continue
                if Mild[t-1, i] and not Documented[t-1, i]:
                    if np.random.rand() < p_documented_in_mild:
                        Documented[t, i]=True
                        time_documented[i]=t
                        traced[i] = True
                        if contact_tracing:
                            Q[t, i] = True
                            do_contact_tracing(i, infected_by, p_trace_outside, Q, S, t, households, p_trace_household, Documented, time_documented, traced)
                #progression between infection states
                if Mild[t-1, i] and t - time_infected[i] == time_to_severe[i]:
                    Mild[t, i] = False
                    Severe[t, i] = True
                    if not Documented[t-1, i]:
                        Documented[t, i]=True
                        time_documented[i]=t
                        traced[i] = True
                        if contact_tracing:
                            Q[t, i] = True
                            do_contact_tracing(i, infected_by, p_trace_outside, Q, S, t, households, p_trace_household, Documented, time_documented, traced)
                    Q[t, i] = True
                    time_severe[i] = t
                    if np.random.rand() < p_severe_critical[age[i], diabetes[i], hypertension[i]]:
                        time_to_critical[i] = functions.threshold_exponential(mean_time_to_critical)
                        time_to_recovery[i] = np.inf
                    else:
                        time_to_recovery[i] = functions.threshold_exponential(mean_time_severe_recovery) + time_to_severe[i]
                        time_to_critical[i] = np.inf
                elif Severe[t-1, i] and t - time_severe[i] == time_to_critical[i]:
                    Severe[t, i] = False
                    Critical[t, i] = True
                    time_critical[i] = t
                    if np.random.rand() < p_critical_death[age[i], diabetes[i], hypertension[i]]:
                        time_to_death[i] = functions.threshold_exponential(mean_time_to_death)
                        time_to_recovery[i] = np.inf
                    else:
                        time_to_recovery[i] = functions.threshold_exponential(mean_time_critical_recovery) + time_to_severe[i] + time_to_critical[i]
                        time_to_death[i] = np.inf
                #risk of mortality for critically ill patients
                elif Critical[t-1, i]:
                    if t - time_critical[i] == time_to_death[i]:
                        Critical[t, i] = False
                        Q[t, i] = False
                        D[t, i] = True
            if E[t-1, i] or Mild[t-1, i] or Severe[t-1, i] or Critical[t-1, i]:
                #not isolated: either enter isolation or infect others
                if not Q[t-1, i]:
                    #isolation
                    if not E[t-1, i] and t - time_infected[i] == time_to_isolate[i]:
                        Q[t, i] = True
                        continue
                    if E[t-1, i] and t - time_exposed[i] == time_to_isolate[i]:
                        Q[t, i] = True
                        continue
                    #infect within family
                    for j in range(max_household_size):
                        if households[i,j] == -1:
                            break
                        contact = households[i,j]
                        infectiousness = p_infect_household[i]
                        if E[t-1, i]:
                            infectiousness *= asymptomatic_transmissibility
                        if S[t-1, contact] and np.random.rand() < infectiousness:
                                E[t, contact] = True
                                num_infected_by[contact] = 0
                                num_infected_by_outside[contact] = 0
                                num_infected_asympt[contact] = 0
                                S[t, contact] = False
                                time_to_isolate[contact] = functions.threshold_exponential(mean_time_to_isolate_asympt*get_isolation_factor(age[contact], mean_time_to_isolate_factor))
                                if time_to_isolate[contact] == 0:
                                    Q[t, contact] = True
                                time_exposed[contact] = t
                                time_to_activation[contact] = functions.threshold_log_normal(time_to_activation_mean, time_to_activation_std)
                                num_infected_by[i] += 1
                                if E[t-1, i]:
                                    num_infected_asympt[i] += 1
                    #infect across families
                    if not Home[i]:
                        infectiousness = p_infect_given_contact
                        if E[t-1, i]:
                            infectiousness *= asymptomatic_transmissibility
                        for contact_age in range(n_ages):
                            if age_groups[contact_age].shape[0] == 0:
                                continue
                            num_contacts = np.random.poisson(contact_matrix[age[i], contact_age])
                            for j in range(num_contacts):
                                if np.random.rand() < infectiousness:
                                    contact = np.random.choice(age_groups[contact_age])
                                    if S[t-1, contact] and not Home[contact]:
                                        E[t, contact] = True
                                        num_infected_by[contact] = 0
                                        num_infected_by_outside[contact] = 0
                                        num_infected_asympt[contact] = 0
                                        S[t, contact] = False
                                        time_to_isolate[contact] = functions.threshold_exponential(mean_time_to_isolate_asympt*get_isolation_factor(age[contact], mean_time_to_isolate_factor))
                                        if time_to_isolate[contact] == 0:
                                            Q[t, contact] = True
                                        time_exposed[contact] = t
                                        time_to_activation[contact] = functions.threshold_log_normal(time_to_activation_mean, time_to_activation_std)
                                        num_infected_by[i] += 1
                                        infected_by[i, num_infected_by_outside[i]] = contact
                                        num_infected_by_outside[i] += 1
                                        if E[t-1, i]:
                                            num_infected_asympt[i] += 1

    return S, E, Mild, Documented, Severe, Critical, R, D, Q, num_infected_by,time_documented, time_to_activation, time_to_death, time_to_recovery, time_critical, time_exposed, num_infected_asympt, age, time_infected, time_to_severe


def compute_reported_cases(Mild, Severe, Critical, R, D, Mild_reporting_rate):

    T = Mild.shape[0]
    N = Mild.shape[1]
    confirmed = np.zeros(T)
    recovered = np.zeros(T)
    deaths = D.sum(axis=1) # all deaths get reported

    # Need a helper to flag which patients we are allowed to count from recovered
    case_was_reported = np.zeros(N)

    # If patient ever goes severe or critical, we count them in recovered
    # Sufficient to check severe since all will go to recovered, critical or dead
    case_was_reported = Severe.any(axis=0)

    # Now randomly pick Mild_reporting_rate% of the mild cases 
    # (note some will be same as severe) to simulate happening in real time
    mild_cases = Mild.any(axis=0)
    for i in range(mild_cases.shape[0]):
        # if it's mild but fails the coin flip, it doesn't get reported
        if mild_cases[i] and not(np.random.rand() < Mild_reporting_rate):
            mild_cases[i] = False

    # combine
    case_was_reported = np.logical_or(case_was_reported, mild_cases)

    # constrict our view to only reported cases and only report as soon as they're mild
    restricted_mild_view = Mild[:, case_was_reported]
    
    has_been_reported = np.zeros(N)

    for i in range(T):
        for j in range(restricted_mild_view.shape[1]):
            if restricted_mild_view[i][j] and not has_been_reported[j]:
                confirmed[i]+=1
                has_been_reported[j] = 1

    confirmed = confirmed.cumsum()

    restricted_recovered_view = R[:, case_was_reported]
    recovered = restricted_recovered_view.sum(axis=1)

    return confirmed, recovered, deaths
