import numpy as np
from numba import jit
import networkx as nx
import random
from math import exp
from itertools import product
import copy
import torch
import csv
from family import *

def create_families(country,Family_num):
    with open('Houseshold.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if row[0]==country:
                family_size_percentage=row[5:9]
                break
        #1 member	2-3 members	4-5 members	6 or more members
        family_size=[1,3,5,6]
        family_size_percentage=[float(s)/100 for s in family_size_percentage]
        all_family_list=[]
        for i in range(Family_num):
            p=family_size_percentage[0]
            r=random.random()
            for j in range(len(family_size_percentage)):
                if r<p:
                    all_family_list.append(FamilyUnit(family_size[j],0))
                    break
                else:
                    p+=family_size_percentage[j+1]
    return all_family_list

def get_SIR_num(G):
    S_num=0
    I_num=0
    R_num=0
    for v in range(len(G)):
        if G.node[v]['state']==0:
            S_num+=1
        if G.node[v]['state']==1:
            I_num+=1
        if G.node[v]['state']==2:
            R_num+=1
    return S_num, I_num, R_num




def SIS_proc(G,beta,gamma):
    H=copy.deepcopy(G)
    for v in range(len(G)):
        if H.node[v]['state']==1:
            if random.random()<gamma:
                G.node[v]['state']=0
        else:
            infect_neighbor=0
            for u in G.neighbors(v):
                if H.node[u]['state']==1:
                    infect_neighbor+=1
            infect_prob=1-(1-beta)**infect_neighbor
            if random.random()<infect_prob:
                G.node[v]['state']=1

def SIR_proc(G,beta,gamma):
    H=copy.deepcopy(G)
    for v in range(len(G)):
        if H.node[v]['state']==0:
            infect_neighbor=0
            for u in G.neighbors(v):
                if H.node[u]['state']==1:
                    infect_neighbor+=1
            infect_prob=1-(1-beta)**infect_neighbor
            if random.random()<infect_prob:
                G.node[v]['state']=1
        elif H.node[v]['state']==1:
            if random.random()<gamma:
                G.node[v]['state']=2

def load_data_new(n, do_bootstrap=False, n_samples=1000):
    beta = np.loadtxt('tb_code_release-master/annBeta.csv', delimiter=',', skiprows=1)
    beta_full = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            i_idx = min((int(i/5), beta.shape[0]-1))
            j_idx = min((int(j/5), beta.shape[0]-1))
            beta_full[i, j] = beta[i_idx, j_idx]
    beta = torch.from_numpy(beta_full)

    a = np.loadtxt('tb_code_release-master/ann2018_alphaFastProb.csv.csv', delimiter=',', skiprows=1)
    num_samples = a.shape[0]

    alpha_fast = load_as_diag('tb_code_release-master/ann2018_alphaFastProb.csv.csv', num_samples, n)

    alpha_slow = load_as_diag('tb_code_release-master/ann2018_alphaSlowProb.csv.csv', num_samples, n)

    nu_sq = np.loadtxt('tb_code_release-master/ann2018_clearanceProb.csv.csv', delimiter=',', skiprows=1)
    nu_sq[np.isnan(nu_sq)] = 0
    nu_sq = nu_sq.mean(axis = 0)
    nu_sq = torch.from_numpy(nu_sq)

    d = load_as_diag('tb_code_release-master/ann2018_deathProb_TB.csv.csv', num_samples, n, oneminus=True)

    mu = load_as_diag('tb_code_release-master/ann2018_deathProb_nat.csv.csv', num_samples, n, oneminus=True)

    S = load_as_diag_time('tb_code_release-master/2018_hasHealthy.csv', num_samples, n)

    N = load_as_diag_time('tb_code_release-master/2018_N.csv', num_samples, n, invert=True)

    E = load_as_vec_time('tb_code_release-master/2018_haslatTB.csv', num_samples, n)

    I = load_as_vec_time('tb_code_release-master/2018_hasTB.csv', num_samples, n)

    if do_bootstrap == True:
        S_boot = torch.zeros(S.shape[0], n_samples, *S.shape[2:]).double()
        for t in range(S.shape[0]):
            S_boot[t] = bootstrap(S[t], n_samples)

        E_boot = torch.zeros(E.shape[0], n_samples, *E.shape[2:]).double()
        for t in range(E.shape[0]):
            E_boot[t] = bootstrap(E[t], n_samples)

        I_boot = torch.zeros(I.shape[0], n_samples, *I.shape[2:]).double()
        for t in range(I.shape[0]):
            I_boot[t] = bootstrap(I[t], n_samples)

        N_boot = torch.zeros(N.shape[0], n_samples, *N.shape[2:]).double()
        for t in range(N.shape[0]):
            N_boot[t] = bootstrap(N[t], n_samples)

        beta = beta.expand_as(mu)
        alpha_fast = bootstrap(alpha_fast, n_samples)
        alpha_slow = bootstrap(alpha_slow, n_samples)
        mu = bootstrap(mu, n_samples)
        d = bootstrap(d, n_samples)
        beta = bootstrap(beta, n_samples)

        S = S_boot
        E = E_boot
        I = I_boot
        N = N_boot


    return S, E, I, N, alpha_fast, alpha_slow, beta, mu, d, nu_sq

def load_as_diag(fname, num_samples, n, oneminus = False):
    a = np.loadtxt(fname, delimiter=',', skiprows=1, dtype=np.complex)
    a[np.isnan(a)] = 0
    a = np.real(a)
    a[np.isneginf(a)] = 0
    if oneminus:
        a = 1 - a
    mat = np.zeros((num_samples, n, n))
    for i in range(num_samples):
        mat[i] = np.diag(a[i])
    return torch.from_numpy(mat).double()

def load_as_diag_time(fname, num_samples, n, invert = False):
    a = np.loadtxt(fname, delimiter=',', skiprows=1, dtype=np.complex)
    #yearly: take every 12th row
    a = a[::12]
    a[np.isnan(a)] = 0
    a = np.real(a)
    a[np.isneginf(a)] = 0
    a = torch.from_numpy(a).double()
    mat = torch.zeros(a.shape[0], num_samples, n, n).double()
    for i in range(a.shape[0]):
        if not invert:
            mat[i] = torch.diag(a[i]).expand_as(mat[i])
        else:
            inverse = 1./a[i]
            inverse[torch.isinf(inverse)] = 1
            mat[i] = torch.diag(inverse).expand_as(mat[i])
    return mat.double()


def load_as_vec(fname, num_samples, n):
    E = np.loadtxt(fname, delimiter=',', skiprows=1, dtype=np.complex)
    E[np.isnan(E)] = 0
    E = np.real(E)
    E[np.isneginf(E)] = 0
    E = torch.from_numpy(E)
    E = E.view(num_samples, n, 1)
    return E.double()

def load_as_vec_time(fname, num_samples, n):
    E = np.loadtxt(fname, delimiter=',', skiprows=1, dtype=np.complex)
    E = E[::12]
    E[np.isnan(E)] = 0
    E = np.real(E)
    E[np.isneginf(E)] = 0
    E = torch.from_numpy(E)
    E_expand = torch.zeros(E.shape[0], num_samples, n, 1)
    for i in range(E.shape[0]):
        E_expand[i] = E[i].unsqueeze(1).expand_as(E_expand[i])
    return E_expand.double()

def bootstrap(A, n_samples):
    pop = list(range(A.shape[0]))
    indices = np.random.choice(pop, n_samples)
    indices = torch.tensor(indices).long()
    return A[indices]

def vector_to_diag(not_informed_fraction, beta):
    not_informed_fraction_diag = torch.zeros_like(beta)
    for s in range(beta.shape[0]):
        not_informed_fraction_diag[s] = torch.diag(not_informed_fraction[s].squeeze())
    return not_informed_fraction_diag

def run_seis_information_new(T, G, S, I, migration_I, migration_E, nu, mu, d, beta, N, alpha_fast, alpha_slow, E, beta_information, nu_max):
    '''
    Runs the linearized SEIS model, returning the total number of infected agents
    summed over all time steps.
    '''
    #read in for first period of F, informed
    #nu_sq = np.loadtxt('ann2018_clearanceProb.csv.csv', delimiter=',', skiprows=1)
    #nu_sq[np.isnan(nu_sq)] = 0
    #nu_sq = nu_sq.mean(axis = 0)
    #nu_sq = torch.from_numpy(nu_sq)

    #duplicate these variables along an additional axis to match the batch size
    beta = beta.expand_as(G)
    informed = nu.view(len(nu), 1)
    informed = informed.expand(beta.shape[0], *informed.shape)
    nu = torch.diag(1 - nu).expand_as(beta)
    num_samples = G.shape[0]
    #keep track of infected, latent, and informed at each time step
    all_I = torch.zeros(T, num_samples, beta.shape[1], 1).double()
    all_E = torch.zeros(T, num_samples, E.shape[1], E.shape[2]).double()
    all_F = torch.zeros_like(all_I).double()
    all_I[0] = I[0]
    all_E[0] = E[0]
    #all_I[0] = I[30]
    #all_E[0] = E[30]

    all_F[0] = informed

    #run the main loop for the linearized disease dynamics
    for t in range(1, T):
        #update nu with new information spread
        not_informed_fraction = 1 - informed
        not_informed_fraction_diag = vector_to_diag(not_informed_fraction, beta)
        #constant scaling the beta for information spread
        informed = not_informed_fraction_diag@beta_information@informed + informed
        #print('here is info beta mat')
        #print(beta_information)
        #print('here is informed')
        #print(informed)
        #debug sze
        nu = nu_max*informed
        nu = vector_to_diag(1 - nu, beta)

        #infections
        new_infections = S[t-1] @ mu @ beta @ N[t-1] @ I
        new_infections_active = alpha_fast @ new_infections
        new_infections_latent = new_infections - new_infections_active
        E = mu @ E
        activations = alpha_slow@E
        E = E - activations
        E += new_infections_latent
        E = G @ E + migration_E[t] #CHANGING TO USING THE LAST MIGRATION PERIOD
        #E = G @ E + migration_E[30]


        old_infections = nu @ d @ I
        I = new_infections_active + old_infections + activations
        I = G @ I + migration_I[t]   #CHANGING TO USING THE LAST MIGRATION PERIOD
        #I = G @ I + migration_I[30]


        #return E, I, F by time and age group
        #mean across samples
        all_I[t] = I
        all_E[t] = E
        all_F[t] = informed

    #print(all_I)
    return all_I, all_E, all_F


@jit
def categorical_sample(p):
    threshold = np.random.rand()
    current = 0
    for i in range(p.shape[0]):
        current += p[i]
        if current > threshold:
            return i
@jit
#def threshold_exponential(mean):
#    return 1 + np.round(np.random.exponential(mean-1))
def threshold_exponential(mean):
    return np.round(np.random.exponential(mean))

@jit
def threshold_log_normal(mean, sigma):
    x = np.random.lognormal(mean, sigma)
    if x <= 0:
        return 1
    else:
        return np.round(x)
