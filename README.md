# Calculate shortest path citation distance between pairs of disciplines in Web of Science (WoS)

For a set of disciplines in WoS, calculate the pairwise shortest path citation distance between them by calculating the average distance between a sample of papers from each discipline.

Use [Singularity](https://sylabs.io/singularity/) for containerization of python graph-tool and to run on HPC.

First, clean the input data using [src/data/clean_samples.py](src/data/clean_samples.py).

Next, convert to JSON using [src/data/make_json.py](src/data/make_json.py).

The analysis can be run on HPC with Singularity using the command:

```
# example command

singularity exec graph_tool.sif python3 -m src.process.calc_shortest_path_distances <PATH_TO_CITATIONS_TSV> <PATH_TO_SAMPLES_JSON> ./data/processed/discipline000 --discipline-index 0 --undirected --debug
```

This will calculate shortest path distances for one discipline. It will, for each separate paper ID, calculate shortest path distances between that paper and all of the others in the JSON file. It will output this to a separate file in the output directory (`./data/processed/discipline000` in the example above). In the example command above, it will run this analysis for the first discipline (discipline 0) in the JSON file.

On HPC, these jobs can run in the backfill queue on nodes with 200GB RAM. These jobs have a maximum of 4 hours. The command above will ignore everything that has already been calculated (in the output directory), and process as many IDs as it can before the time runs out. So, it may be necessary to run each discipline multiple times, until all the IDs have been processed.

The script [src/modify_slurm_script.py](src/modify_slurm_script.py) can generate multiple scripts to run on the Slurm scheduler on HPC. For example:

```
python -m src.modify_slurm_script scripts/201910040930/calc_shortest_path_slurm.sh --start=0 --end=35 --log-dir logs
```

(In this example, there are 36 disciplines. The file `calc_shortest_path_slurm.sh` is a template Slurm script.)

Then, the jobs can all be submitted at once with (for example):

```
for file in scripts/201910040930/calc_shortest_paths_discipline*.sh; do sbatch -p ckpt -A stf-ckpt --mail-user $EMAIL $file; done
```

(`$EMAIL` is an environment variable storing your email address. You will be notified when the job starts and ends.)
