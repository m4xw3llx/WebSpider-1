while true
do
    echo `date`
    DATE=`date +%Y%m%d`
    FILENAME=`python iqiyi.py`
    iconv -f UTF-8 -t GB18030 ${FILENAME} > ${DATE}_视频观看数.csv

    FILENAME=`python vote.py`
    iconv -f UTF-8 -t GB18030 ${FILENAME} > ${DATE}_礼物数.csv

    FILENAMES=`python weibo.py`
    FILENAME=$(echo `echo $FILENAMES` | cut -d \  -f 1)
    iconv -f UTF-8 -t GB18030 $FILENAME > ${DATE}_粉丝数.csv

    FILENAME=$(echo `echo $FILENAMES` | cut -d \  -f 2)
    iconv -f UTF-8 -t GB18030 $FILENAME > ${DATE}_喜爱值.csv


    git add ${DATE}_粉丝数.csv ${DATE}_视频观看数.csv ${DATE}_礼物数.csv ${DATE}_喜爱值.csv
    git commit -m "update"
    git push
    sleep 3600
done
