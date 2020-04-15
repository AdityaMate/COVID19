#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  8 15:21:47 2020

@author: adityamate
"""

from datetime import date
import datetime
import numpy as np



if __name__=="__main__":
    
    #policies=['LLLL','SSSS', 'LSSS', 'LLSS', 'LLLS','SLLS','LSLS','SLSL','LLSL','MMMM','MSSS', 'MMSS', 'MMMS', 'LLMM', 'LLMS', 'LLLM', 'LMLM' ,'LMMS']
    policies=['SSSS','LSLS','SLSL', 'LLSS', 'LLSL','LLLS','LLLL']              ### Policies which should appear on the plot (make sure the simulations for these
                                                                               ###  are run and data is available in the correct subfolders) 
    
    sub_folder='params_p0.036_dmult6_dstart3.10'
    num_seeds=10     ### how many seeds to read and average over
    d_start=10       # start date 


    vline_y=0

    # Deaths plot:
    
    fig=plt.figure()
    for p in policies:
        deaths= np.array([np.load('policy_results/'+sub_folder+'/deaths_policy%s_s%s.npy'%(p, str(seed))) for seed in range(num_seeds)])
        vline_y=max(vline_y,1*max(np.mean(deaths, axis=0)[-1]))
        plt.plot(range(deaths.shape[2]), np.mean(deaths, axis=0)[0], label=p)
        #print("Final deaths %s:"%(p), np.mean(deaths, axis=0)[-1])
    plt.vlines(24-d_start, 000, vline_y, linestyles = '--', color='r',label='Lockdown start')
    plt.vlines(46-d_start, 000, vline_y, linestyles = '--', color='k',label='14 April',alpha=0.5)
    plt.vlines(52-d_start, 000, vline_y, linestyles = '--', color='k',label='21 April',alpha=0.5)
    plt.vlines(61-d_start, 000, vline_y, linestyles = '--', color='k',label='30 April',alpha=0.5)
    plt.vlines(68-d_start, 000, vline_y, linestyles = '--', color='k',label='7 May',alpha=0.5)
    #plt.xlabel('Days after d_start=03.1'+sub_folder[-1]+'.2020')
    
    date_labels = []
    for i in range(len(deaths[0,0])):
        new_date = date(2020, 3, 10) + datetime.timedelta(days=i)
        date_labels.append('{}/{}'.format(new_date.month, new_date.day))
    
    plt.tick_params(axis='both', which='major', labelsize=17)
    currticks = plt.xticks()
    currticks = [int(i) for i in currticks[0] if i >= 0 and i < len(deaths[0,0])]
    plt.xticks(currticks)
    plt.xticks(currticks, [date_labels[i] for i in currticks], rotation=45)
    plt.xlabel('Date', fontsize=15)


    plt.ylabel('Number of deaths',fontsize=15)
    plt.title('Deaths in Uttar Pradesh ',fontsize=14)
    plt.legend(bbox_to_anchor=(1.01, 0.1, 1.01, 0.9), loc=2, ncol=1, borderaxespad=0,fontsize = 12)
    plt.savefig('deaths_'+sub_folder+'.png')

    # Infections plot:
    fig=plt.figure()
    vline_y=0
    for p in policies:
        inf= np.array([np.load('policy_results/'+sub_folder+'/infections_policy%s_s%s.npy'%(p, str(seed))) for seed in range(num_seeds)])
        vline_y=max(vline_y,1*max(np.mean(inf, axis=0)[-1]))
        plt.plot(range(len(inf[0,0])), np.mean(inf, axis=0)[0], label=p)
        print("Final infections %s:"%(p), np.mean(inf, axis=0)[-1])
    plt.vlines(24-d_start+1, 000, vline_y, linestyles = '--', color='r',label='Lockdown start')
    plt.vlines(47-d_start, 000, vline_y, linestyles = '--', color='k',label='14 April',alpha=0.5)
    plt.vlines(54-d_start, 000, vline_y, linestyles = '--', color='k',label='21 April', alpha=0.5)
    plt.vlines(63-d_start, 000, vline_y, linestyles = '--', color='k',label='30 April', alpha=0.5)
    plt.vlines(70-d_start, 000, vline_y, linestyles = '--', color='k',label='7 May', alpha=0.5)
    
    
    date_labels = []
    for i in range(len(inf[0,0])):
        new_date = date(2020, 3, 10) + datetime.timedelta(days=i)
        date_labels.append('{}/{}'.format(new_date.month, new_date.day))
    
    plt.tick_params(axis='both', which='major', labelsize=17)
    currticks = plt.xticks()
    currticks = [int(i) for i in currticks[0] if i >= 0 and i < len(inf[0,0])]
    plt.xticks(currticks)
    plt.xticks(currticks, [date_labels[i] for i in currticks], rotation=45)
    plt.xlabel('Date', fontsize=15)
    #plt.xlabel('Days after d_start=03.0'+sub_folder[-1]+'.2020')
    plt.ylabel('Number of infections',fontsize=15)
    plt.title('Infections in Uttar Pradesh', fontsize=15)
    plt.legend(bbox_to_anchor=(1.01, 0.05, 1.01, 0.95), loc=2, ncol=1, borderaxespad=0,fontsize = 12)
    plt.savefig('infections_'+sub_folder+'.png')
    
    plt.show()