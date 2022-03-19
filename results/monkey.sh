
#!/bin/sh
i=0





while [ $i -ne 40 ]
do      
        zufallswert_x=$((RANDOM%(1050-1+1)+1))
        zufallswert_y=$((RANDOM%(2000-200+1)+200))
        i=$(($i+1))
        input tap $zufallswert_x $zufallswert_y
done