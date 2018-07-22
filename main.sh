# Run once every hour
# Should be able to create a cronjob to deal with it
# sleep 3600

# all iconv are used to convert UTF-8 to GB18030, so chinese are readable in excel spreadsheet
# has to encode them in UTF-8 first for debugging purposes

# Everyday will create .${DATE}_log.txt, .${DATE}_simple_log.txt and .${DATE}_error.log
# Should not exceed 100M per day => 40days * 100M = 4G
# In long run it can be a problem
# May pull them to local machine once every a few days

# Need to send files ${DATE}_粉丝数.csv ${DATE}_视频观看数.csv ${DATE}_礼物数.csv ${DATE}_喜爱值.csv through email

while true
do
    echo `date`
    DATE=`date +%Y%m%d`
    FILENAME=`python iqiyi.py`
    iconv -f UTF-8 -t GB18030 ${FILENAME} > ${DATE}_视频观看数.csv

    FILENAME=`python vote.py`
    iconv -f UTF-8 -t GB18030 ${FILENAME} > ${DATE}_礼物数.csv

    FILENAMES=`python weibo.py wzm1990@gmail.com KawasakiH2`
    FILENAME=$(echo `echo $FILENAMES` | cut -d \  -f 1)
    iconv -f UTF-8 -t GB18030 $FILENAME > ${DATE}_粉丝数.csv

    FILENAME=$(echo `echo $FILENAMES` | cut -d \  -f 2)
    iconv -f UTF-8 -t GB18030 $FILENAME > ${DATE}_喜爱值.csv

    sleep 3600
done
