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

USERNAME=$1
PASSWORD=$2

while true
do
    echo `date`
    DATE=`date +%Y%m%d`

    python weibo.py -u $USERNAME -p $PASSWORD -m chart
    python weibo.py -u $USERNAME -p $PASSWORD -m post
    python weibo.py -u $USERNAME -p $PASSWORD -m followers

    FILENAME=${DATE}_chart.csv
    iconv -f UTF-8 -t GB18030 ${FILENAME} > ${DATE}_喜爱值.csv

    FILENAME=${DATE}_post_data.csv
    iconv -f UTF-8 -t GB18030 ${FILENAME} > ${DATE}_微博具体信息.csv

    FILENAME=${DATE}_follower_counts.csv
    iconv -f UTF-8 -t GB18030 ${FILENAME} > ${DATE}_关注数.csv


    #FILENAMES=`python weibo.py`
    #FILENAME=$(echo `echo $FILENAMES` | cut -d \  -f 1)
    #iconv -f UTF-8 -t GB18030 $FILENAME > ${DATE}_粉丝数.csv

    #FILENAME=$(echo `echo $FILENAMES` | cut -d \  -f 2)
    #iconv -f UTF-8 -t GB18030 $FILENAME > ${DATE}_喜爱值.csv

    sleep 300
done
