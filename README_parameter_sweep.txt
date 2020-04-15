# Running parameter sweeps

1. open parameter_sweep_lombardy.py
2. Set the parameters to be whatever you need. That is edit the contents of these arrays
	
	p_infect_given_contact_list = [round(0.02+0.001*i, 3) for i in range(12)]
	mortality_multiplier_list = [1, 2, 3, 4, 5]
	start_date_list = [10, 13, 16, 19, 22, 25]

3. run the following command:
python3 parameter_sweep_lombardy.py N_SIMS_PER_COMBO N_SIMS_PER_JOB --do_the_math

   where:
       N_SIMS_PER_COMBO = number of simulations you want per parameter combination
       N_SIMS_PER_JOB = number of simulations you want to run per slurm job

    Note: the larger N_SIMS_PER_JOB, the more time and memory it will take.
          But the smaller N_SIMS_PER_JOB, the less time and memory it will take, but more jobs and CPUs.

4. the script will spit out the command you need to run on fasrc in order to run the simulations. e.g.,

	python3 parameter_sweep_lombardy.py 50 10 --do_the_math --sim_name lombardy_batch

	NUM COMBOS: 360
	NUM INDICES: 1800

	Please launch jobs indexed from 0 to 1799, e.g.,
	sbatch --array=0-1799 job.parameter_sweep_lombardy.sh 50 10 lombardy_batch

5.  Note that if --array=0-N gives you some N that is larger than 9999 you will need to manually cut up your jobs into chunks of 10,000. E.g., if you see:

	sbatch --array=0-29999 job.parameter_sweep_lombardy.sh 50 10 lombardy_batch

you will need to run
	sbatch --array=0-9999 job.parameter_sweep_lombardy.sh 50 10 lombardy_batch

wait for those to finish, the run:
	sbatch --array=10000-19999 job.parameter_sweep_lombardy.sh 50 10 lombardy_batch

wait for those to finish, the run:
	sbatch --array=20000-29999 job.parameter_sweep_lombardy.sh 50 10 lombardy_batch


Or you can tune N_SIMS_PER_COMBO and N_SIMS_PER_JOB to give you fewer jobs. The choice is yours.


6. Note that results will be saved in the directory you specify as the final (4th) position argument of the sbatch command (so lombardy_batch in the above examples)


7. When things finish, zip up the directory (e.g., run: zip -r lombardy_batch.zip lombardy_batch), download the zip file, then send it to your favorite plot wizard.

8. If you are the plot wizard, open parse_parameter_sweep_distributed.py

9. In the if country == 'Italy' block at the top (near line 18), replace the parameter lists with your own.

10. In the if country == 'Italy' block around line 78, replace runs = [] with the list of directories containing your results (what you zipped and downloaded)

11. In the loop around line 191, gather your data

12. Do your plotting somewhere under that :)



