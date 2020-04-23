# COVID19: Exploring lockdown policies for India
Code and data for an agent based simulation to analyze the effect of various lockdown policies in India 

### Start:
  To start, download the repository or clone using:  "git clone https://github.com/AdityaMate/COVID19.git"
  

### Population Sampling:

To run the simulations on states of Maharashtra, Uttar Pradesh and Tamil Nadu, you will need additional files which capture the sampled population, on which the simulation will run. Please download the pickle files for these from the following links and save them in the same directory as the rest of your code. 
- Maharashtra: https://www.dropbox.com/s/uh9vxkp5sm95avr/Maharashtra_population_10000000.pickle?dl=0
- Uttar Pradesh: https://www.dropbox.com/s/jgmlsp3v2ttzyhf/tamilnadu_population_10000000.pickle?dl=0
- Tamil Nadu: https://www.dropbox.com/s/p6ie5671zs8w1jl/up_population_10000000.pickle?dl=0

Alternatively, you can generate a population sample of your own using 'Population_Generation.ipynb'. Make sure to uncomment/comment lines in code specific to whichever state's population you wish to sample. 


### Running simulation:

Once the necessary population sample files are generated as above, you are all set to run the simulation! 

- Run: python3 run_simulation.py 
- Note that this is programmed to run two independent trials of the simulation just now. You can edit this setting and run as many independent runs as you may like. 

### Running policy simulations:

- Around line 131 in run_simulation.py, change the policy option from the list provided on line 130 to select some whichever other policy you may want to simulate. The default setting is 'LLLL', meaning a lockdown choice is made at all the four decision points. 
- To run this on a large scale on a cluster, please follow comments around line 131 to uncomment suitable lines to activate: (1) policy choice (2) seed settings
- The output results will be stored in ./policy_results/+save_subfolder

### Running param sweeps: 

- Please refer to README_paramter_sweep.txt for instructions on running param sweeps. 
