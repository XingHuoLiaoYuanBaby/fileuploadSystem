# 文件管理系统

分为文件上传和文件下载

文件上传可以批量上传多个文件，且可以上传大文件

文件下载可以下载、删除已经上传好的文件

## 启动方式

```
python server.py
```

代码中可以配置启动的端口，和启动的路径

```
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
```

```
# 配置API路径前缀
API_PREFIX = "/fup"
```

## 离线安装python包

本代码在Python 3.12.4环境下编写

将文件打包后放到离线主机上，并进行安装

```
pip install --no-index --find-links=packages -r requirements.txt
```

## requirements.txt

```
fastapi==0.115.8
uvicorn==0.34.0
```

