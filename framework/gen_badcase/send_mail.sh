#!/bin/bash

#receiver=zhaoxiaoping@baidu.com

source ./send_mail.conf
mail_subject="$1"
mail_text_file="$2"
add_file="$3"

#./sendmail -f word-not-related@baidu.com -t ${receiver} -s hotswap-in.baidu.com -u ${mail_subject} -o message-file=${mail_text_file} 1>/dev/null

./sendmail -f badcase@baidu.com -t ${receiver} -s hotswap-in.baidu.com -u ${mail_subject} -o message-file=${mail_text_file} -o message-content-type=text -a ${add_file} 1>/dev/null

