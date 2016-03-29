# Python应用示例

## 本地运行

```sh
$ git clone https://github.com/sinacloud/python-getting-started.git
$ cd python-getting-started
$ python main.py
```

现在，本示例应用已经跑在了你的 localhost:5050 端口上了。

## 部署到sinacloud

首先，提交代码到你的sinacloud应用的git仓库。

```
$ git remote add sinacloud $GIT_REPOS_URL_FOR_YOUR_APPLICATIRON
$ git push sinacloud master:1
```

登陆sinacloud容器云的管理页面，在部署页面中，点击部署。

部署完成之后，你就可以通过 http://$APPNAME.sinaapp.com 来访问你的应用了。

## 相关文档

- [Python应用部署指南](http://www.sinacloud.com/doc/sae/docker/python-getting-started.html)


