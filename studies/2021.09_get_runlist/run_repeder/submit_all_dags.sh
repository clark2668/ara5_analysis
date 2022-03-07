#!/bin/bash

FILES=dag_repeder_*.dag
for f in $FILES
do
	condor_submit_dag $f
done
