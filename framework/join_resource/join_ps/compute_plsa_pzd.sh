#!/bin/bash

cd plsa/
chmod a+x src/test_client_new

echo $1 | ./src/test_client_new ./conf/plsa_pzd.conf ./conf/plsa_client.conf 1 1 1
