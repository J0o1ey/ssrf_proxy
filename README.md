# ssrf_proxy
一个在全回显SSRF情况下的proxy代理

挂上代理后可以直接浏览器访问目标内网业务

或可使用nuclei等程序对目标内网web系统进行漏扫

支持向目标内网发送GET/POST请求（POST需要目标ssrf点支持gopher协议）

```
python3 ssrf_proxy.py -u "http://vulnweb.com/ssrf.php?url="
```

![image-20230528121404664](https://j0o1ey-1251589192.cos.ap-beijing.myqcloud.com/202305281214731.png)



## Todo

- 支持解析http request&response包，指定ssrf输入点与reponse输出点
- 提高发包效率
