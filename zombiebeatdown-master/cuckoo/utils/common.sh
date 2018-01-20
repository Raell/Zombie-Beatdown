#/bin/bash

#./common.sh 1 2 3 4 5

array=()

if [ "$#" -gt 1 ];then


	for i in "$@";do
		array+=("$i")
	done

    #remove duplicates from array
    array=($(echo "${array[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' '))

	for i in "${array[@]}";do
		sort ../storage/analyses/$i/logs/fileslist > file$i.txt
		sort ../storage/analyses/$i/logs/registrylist > reg$i.txt
	done

	cp file$array.txt filetmp0
	cp reg$array.txt regtmp0

	counter=1
	for i in "${array[@]}";do
		comm -1 -2 file$i.txt filetmp$((counter-1))  > filetmp$counter
		comm -1 -2 reg$i.txt regtmp$((counter-1))  > regtmp$counter
		rm regtmp$((counter-1))
		rm filetmp$((counter-1))
		((counter++))
	done

	mv filetmp$((counter-1)) ../whitelist/commonfile.txt
	mv regtmp$((counter-1)) ../whitelist/commonreg.txt

	for i in "${array[@]}";do
		rm file$i.txt
		rm reg$i.txt
	done

else
	echo "Usage:"
	echo "./common.sh [task IDs]"
	echo "Requires at least 2 task IDs"
	echo "example ./common.sh 23 35 42 15"
fi
