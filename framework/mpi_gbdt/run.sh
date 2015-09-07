#!/bin/bash

chmod a+x ./gbdt_bin/gbdt-predictor

echo $1 | ./gbdt_bin/gbdt-predictor -m ./gbdt_bin/gbdt_model
