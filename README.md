# python_start
python learning dir

# 目的

开启这个python start，其一是简单使用python编写一些轮子，其二是用来熟悉 vscode github extension which use the git to control the whole dir.

# Git

## How to use the git in the vscode?

1. After modifying the file and saved, the changes will occur in the sidebar Source Control, then select the file and click the stage changes
2. After staging the changes, the file will moved to the **Staged Changed** line, next is to note Messsage and Commit the Staged Changes
3. Then the changes is send to the commit cache, Next is to click **Sync Changes**, in that way all the changes of the files will upload to the Github, and all the steps of the git is done.

## issue

1. GnuTLS recv error (-110): The TLS connection was non-properly terminated

```bash
# 手动更改github 代理地址和端口
# http
git config --global http.https://github.com.proxy http://127.0.0.1:7890
git config --global https.https://github.com.proxy https://127.0.0.1:7890
```