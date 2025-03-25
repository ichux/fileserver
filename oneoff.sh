#!/bin/bash

scp -i ~/.ssh/iam_server ~/offloads/crashcourse.mp4 iam@server:~/offloads

ssh iamserver -t "rm -rf ~/offloads/.fs_auth.db; cd ~/devcode/fileserver; make uh; make up t='username secret_password'"

TOKEN=$(curl -sX POST "https://fileserver.bit.wise/pulls/generate-token?filepath=crashcourse.mp4" \
  -H "Authorization: Basic $(echo -n 'username:secret_password' | base64)")

echo $TOKEN

#rm -rf crashcourse.mp4 && \
#  wget --no-check-certificate -c --content-disposition --show-progress \
#  "http://192.168.2.193:16000/pulls/crashcourse.mp4?token=$TOKEN"

#rm -rf crashcourse.mp4 && curl -k -OJ "https://fileserver.bit.wise/pulls/crashcourse.mp4?token=$TOKEN"

rm -rf crashcourse.mp4 && curl -k -C - -o "crashcourse.mp4" \
"https://fileserver.bit.wise/pulls/crashcourse.mp4?token=$TOKEN"
