Title: S3 多文件下载优化：从本地打包到实时流式 ZIP 传输
Date: 2025-09-07 10:00
Category: 文章分类
Tags: 标签1, 标签2
Author: 作者名

# S3 多文件下载优化：从本地打包到实时流式 ZIP 传输

# 前言

记录一次 S3 多文件下载解决方法的优化。希望对碰到类似需求的伙计有所帮助。

# 优化前方案

我们先看看优化前的做法：

1. 服务端从 S3 中下载所有目标文件，保存到本地打包成一个压缩文件
2. 服务端将处理好的压缩文件上传 S3，将对应的 S3 分享链接返回给客户端
3. 客户端通过分享链接，直接从 S3 下载压缩文件

![流程图1](/static/CbxYbJcYDo79yWx4cM7ciowpn5f.png)

从以上的流程图中可以发现，整个过程来回的下载上传下载，效率很低。特别是大文件的处理非常耗时，只能以异步的方式处理用户的请求，这样会影响用户的体验；并且这种方案会导致 S3 存储冗余。

所以发现这些问题后，决定优化一下。

# 优化过程

开始考虑，S3 是否有接口可以让多文件的直接打包，由 S3 自身完成，就可以减少下载和上传带宽占用，速度肯定也更快。

查看 minio（开源的 S3 项目）文档后，发现并没有多文件打包的 api 接口，只有个 [compose_object](https://docs.min.io/community/minio-object-store/developers/python/API.html#compose_object) 的接口，是实现分片上传后的文件整合，但这个接口有硬性要求，除了最后一个文件其他文件必须大于 5M。因为这个限制，一些场景就无法使用，所以 pass。

最终选择了<strong>流量中转方案</strong>，以<strong>流式传输</strong>的方式（数据<strong>边生成/读取边传输</strong>）。

服务端作为 S3 和客户端的中转，一边从 S3 下载文件，一边以流式的方式往客户端传输。

![流程图2](/static/Ui8MbCtHkoDNbixn2uQcZs7wnxd.png)

流量中转的方案需采用流式响应，内存占用更小，实时性更好，不必等到全部数据准备好再发送，非常适合处理大文件。

# Python 实时流式 ZIP 处理解决方案

为了实现 S3 多文件中转下载，直接返回文件肯定不行，需要将 S3 的多文件加工成 zip 文件。涉及流式 zip 处理。因为项目是 django 框架，而 Python 原生的 `zipfile` 库无法进行真正的流式 ZIP 处理。

可以使用临时文件方式先将所有 s3 文件全部下载到磁盘，然后再返回给客户端。

更好的方式是使用实时流式 zip 传输，边下载 S3 文件，边以 zip 格式传输下载好的内容。减少响应等待时间。

为了实现低内存占用的实时流式 ZIP 生成，找到以下两种第三方库：

## 1. <strong>zipfly</strong>

- <strong>项目地址</strong>: [https://github.com/sandes/zipfly](https://github.com/sandes/zipfly)
- <strong>特点</strong>:

  - 项目始于 2020 年 3 月，自 2020 年 7 月以来低维护，但整体稳定。
  - 只能使用磁盘路径作为输入，无法直接处理内存缓冲区或流。
  - 基本是通过替换流写入器实现持续数据刷新到磁盘的“黑客式”方案。
- <strong>评估</strong>:

  - 虽然知名，但限制较多，不推荐用于高效内存管理场景。

## 2. <strong>stream-zip</strong>

- <strong>项目文档</strong>: https://stream-zip.docs.trade.gov.uk/get-started/（因为不知名原因 github 仓库地址被移除）
- <strong>特点</strong>:

  - 2021 年 12 月创建，并持续积极维护。
  - 对 ZIP 标准有深厚技术知识，作者用纯 Python 实现了 Deflate64 编码/解码器。
  - 支持使用 zlib 原生 C 代码直接生成压缩块。
  - API 允许从流中实时生成输入数据，可处理文件描述符，实现内存高效的实时数据读取。
  - 可针对每个文件调整压缩级别。
- <strong>优势</strong>:

  - 内存占用极低：例如创建 8GB ZIP 文件时，Python 仅占用约 6MB 内存。
  - 高性能：支持以 128KB 块进行输入/输出流式传输。
  - 与原生 `zipfile` 相比，性能和内存效率提升显著。
- <strong>推荐用途</strong>: 高效生成大文件 ZIP、实时流式数据压缩。
- <strong>扩展：</strong>如果还需要 <strong>流式解压缩</strong>，同一作者提供的相关项目也是最佳选择，代码安全、符合 ZIP 标准、维护良好。

## 核心代码

对比下来选择使用性能更好，持续维护的 stream-zip 包来实现，核心代码如下：

```
from stream_zip import stream_zip, ZIP_64
 
def generate_streaming_zip(data):
    buffer_size = 64 * 1024
    s3_client = get_s3_client()

    def file_iter(bucket_name, object_name):
        """返回一个生成器，按块读取 S3 对象内容"""
        try:
            response = s3_client.get_object(Bucket=bucket_name, Key=object_name)
            body = response['Body']
            for chunk in iter(lambda: body.read(buffer_size), b''):
                yield chunk
        except ClientError as e:
            logging.error(f"Error downloading {object_name} from S3: {e}")
            raise e

    # 当前时间作为文件时间戳
    now = datetime.datetime.now()
    files = [
        (
            obj.get('name'),        # 文件名
            now,              # 时间戳
            0o600,                  # 权限
            ZIP_64,           # 压缩方式
            file_iter(obj.get("bucket_name"), obj.get("object_name"))
        )
        for obj in data
    ]

    return stream_zip(files)
```

- 说明：使用 `yield` 流式返回 zip 文件内容，可以和 `StreamingHttpResponse` 配合。

# 其他知识点

- 为了让浏览器能够自动接管下载过程（浏览器接管下载进程。即使页面刷新，也不会中断下载进程），多文件下载中转接口采用了 GET 请求（浏览器无法“自动接管” POST 请求的下载过程）
- 为了支持传递复杂参数，由后端生成一个临时下载 URL，包含查询下载任务 id（可关联查询到下载参数），增加随机 code 做为校验。
- 使用临时文件通过磁盘读写方式来保存大文件内容。

  - 临时文件关闭后会被自动清理，不用担心磁盘残留问题。
  - 这里使用磁盘替换内存存储并不影响整体速度，因为网络是瓶颈，而磁盘比网络快得多
