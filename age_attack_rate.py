import pickle
import numpy as np
import matplotlib.pyplot as plt
import sys

country = sys.argv[1]

if country == 'Italy':
    pinf = 0.029
    d0 = 22
elif country == 'China':
    pinf = 0.020
    d0 = 15

n = int(1e7)

r_0_over_time, cfr_over_time, fraction_over_70_time, fraction_below_30_time, median_age_time, total_infections_time, total_documented_time, dead_by_age, total_deaths_time, all_final_s \
    = pickle.load(open('results_calibration_{}_{}_{}.pickle'.format(country, pinf, d0), 'rb'))

age, households, diabetes, hypertension, age_groups = pickle.load(open('{}_population_{}.pickle'.format(country, n), 'rb'))

def ci(a, alpha):
    a = a.copy()
    a.sort()
    return a[int((alpha/2)*a.shape[0])], a[int((1-(alpha/2))*a.shape[0])]


age_groups = ((0, 14), (15, 24), (25, 39), (40, 69), (70, 100))
infected_by_group = np.zeros((all_final_s.shape[0], len(age_groups)))
total_group = np.zeros((all_final_s.shape[0], len(age_groups)))
for sim in range(all_final_s.shape[0]):
    for idx, (lower, upper) in enumerate(age_groups):
        total = 0
        infected = 0
        for i in range(lower, upper+1):
            total += (age == i).sum()
            infected += (age == i).sum() - all_final_s[sim, age == i].sum()
        infected_by_group[sim, idx] = infected
        total_group[sim, idx] = total

print(total_group.sum(axis=1))
alpha = 0.2
vals = []
#ar = np.median(infected_by_group/total_group, axis=0)
for idx, (lower, upper) in enumerate(age_groups): 
    ar = infected_by_group[:, idx]/total_group[:, idx]
    ci_lower, ci_upper = ci(ar, alpha)
    print(lower, upper, np.median(ar), ci_lower, ci_upper)
    vals.append(np.median(ar))


if country == 'China':
    vals = [0.03958154842258677, 0.06703118877344183, 0.030919868737789652, 0.030665642884168953, 0.0272670906648379]
elif country == 'Italy':
    vals = [0.12383771159791997, 0.12402157408640054, 0.11628513551972947, 0.07242877101337657, 0.028495440299124535]

import matplotlib as mpl
#Ensure type 1 fonts are used
mpl.rcParams['ps.useafm'] = True
mpl.rcParams['pdf.use14corefonts'] = True
mpl.rcParams['text.usetex'] = True

colors = ['orange','green','blue','purple','black']
x = np.arange(len(age_groups))/1.25
fig, ax = plt.subplots()
plt.bar(x, vals, color=colors, edgecolor='black', alpha=0.7)
plt.xticks(x, ['{}-{}'.format(interval[0], interval[1]) for interval in age_groups], fontsize=15)
if country == 'China':
    plt.ylim((0, 0.15))
    plt.yticks((0, 0.05, 0.10, 0.15), (0, 5, 10, 15), fontsize=17)
elif country == 'Italy':
   plt.ylim((0, 0.15)) 
   plt.yticks((0, 0.05, 0.10, 0.15), (0, 5, 10, 15), fontsize=17)
for i, v in enumerate(vals):
    ax.text(i/1.25 - 0.17, v + 0.01, '{:.1f}\%'.format(v*100), fontsize=15)
plt.ylabel('Attack rate (\%)', fontsize=23)
plt.xlabel('Age', fontsize=23)
plt.tight_layout()
plt.savefig('img/heatmaps/age_attack_rate_{}.pdf'.format(country))

print(np.median(infected_by_group.sum(axis=1)), np.median(infected_by_group.sum(axis=1)/n))


for idx, (lower, upper) in enumerate(age_groups):
    fraction_of_cases = infected_by_group[:, idx]/infected_by_group.sum(axis=1)
    ci_lower, ci_upper = ci(fraction_of_cases, alpha)
    print(lower, upper, np.median(fraction_of_cases), ci_lower, ci_upper)


