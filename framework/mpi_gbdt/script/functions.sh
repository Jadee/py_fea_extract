#!/bin/bash

function getHadoopConf ()
{
	local name=$1
	local fname=${2:-${LOCAL_HADOOP_HOME}/conf/hadoop-site.xml}
	grep -P -A50 "${name}" ${fname} | awk 'BEGIN{start=0;end=0;}
	{
		if($0~/<value>/)
		{
			start=1;
		}
		if(start==1 && end==0)
		{
			print $0;
		}
		if($0~/<\/value>/)
		{
			end=1;
		}
	}' | awk -F'<value>|</value>| |\t' '{for(i=1;i<=NF;i++){if($i!="")print $i}}'
}

