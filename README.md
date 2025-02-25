# 文件管理系统

## 项目介绍

本项目是一个基于FastAPI框架开发的现代化文件管理系统，提供高性能的文件上传和下载功能。系统采用前后端分离架构，实现了大文件分片上传、批量文件删除、下载。

## 部署说明

### 启动方式

```bash
python server.py
```

### 配置说明

可在代码中配置启动端口和API路径：

```python
# 启动配置
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)

# API路径前缀配置
API_PREFIX = "/fup"
```

## 离线部署

本项目支持离线环境部署，所有依赖包已预先下载到packages目录。

### 离线安装Python包

```bash
pip install --no-index --find-links=packages -r requirements.txt
```

### requirements.txt

```
fastapi==0.115.8
uvicorn==0.34.0
```

