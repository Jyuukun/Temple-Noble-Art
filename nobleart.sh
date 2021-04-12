# !/bin/bash

while true
do
    echo "# Launching script..."
    python $HOME/nobleart.py $1
    if [ "$?" -eq "0" ]; then
        sleep 7200
        break
    fi
done
