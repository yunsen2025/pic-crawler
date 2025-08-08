import requests
import os
import time
import hashlib
from urllib.parse import urlparse
from PIL import Image
import io

class RandomImageCrawler:
    def __init__(self, base_url, download_dir="downloaded_images"):
        self.base_url = base_url
        self.download_dir = download_dir
        self.session = requests.Session()
        
        # 设置请求头，模拟浏览器访问
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # 创建下载目录
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
    
    def get_image_hash(self, image_data):
        """计算图片的MD5哈希值，用于去重"""
        return hashlib.md5(image_data).hexdigest()
    
    def download_image(self, url, filename=None):
        """下载单张图片"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # 检查响应是否为图片
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                print(f"警告: URL返回的不是图片格式，Content-Type: {content_type}")
                return None
            
            image_data = response.content
            image_hash = self.get_image_hash(image_data)
            
            # 尝试获取图片格式
            try:
                img = Image.open(io.BytesIO(image_data))
                img_format = img.format.lower() if img.format else 'jpg'
            except:
                img_format = 'jpg'
            
            # 生成文件名
            if not filename:
                filename = f"image_{image_hash[:8]}.{img_format}"
            
            filepath = os.path.join(self.download_dir, filename)
            
            # 检查文件是否已存在（基于哈希值去重）
            for existing_file in os.listdir(self.download_dir):
                existing_path = os.path.join(self.download_dir, existing_file)
                if os.path.isfile(existing_path):
                    with open(existing_path, 'rb') as f:
                        existing_hash = self.get_image_hash(f.read())
                    if existing_hash == image_hash:
                        print(f"图片已存在，跳过: {existing_file}")
                        return existing_path
            
            # 保存图片
            with open(filepath, 'wb') as f:
                f.write(image_data)
            
            print(f"成功下载: {filename} ({len(image_data)} bytes)")
            return filepath
            
        except requests.exceptions.RequestException as e:
            print(f"下载失败: {e}")
            return None
        except Exception as e:
            print(f"保存图片时出错: {e}")
            return None
    
    def crawl_images(self, count=10, delay=1):
        """批量爬取图片
        
        Args:
            count: 要下载的图片数量
            delay: 每次请求之间的延迟时间（秒）
        """
        print(f"开始爬取 {count} 张随机图片...")
        print(f"目标URL: {self.base_url}")
        print(f"保存目录: {self.download_dir}")
        print("-" * 50)
        
        successful_downloads = 0
        total_attempts = 0
        
        while successful_downloads < count:
            total_attempts += 1
            print(f"\n尝试第 {total_attempts} 次下载 (成功: {successful_downloads}/{count})")
            
            # 下载图片
            result = self.download_image(self.base_url)
            
            if result:
                successful_downloads += 1
            
            # 如果还需要继续下载，等待一段时间
            if successful_downloads < count:
                print(f"等待 {delay} 秒后继续...")
                time.sleep(delay)
            
            # 防止无限循环，如果尝试次数过多则退出
            if total_attempts > count * 3:
                print("尝试次数过多，可能网站返回重复图片，停止爬取")
                break
        
        print(f"\n爬取完成！")
        print(f"成功下载: {successful_downloads} 张图片")
        print(f"总尝试次数: {total_attempts}")
        print(f"图片保存在: {os.path.abspath(self.download_dir)}")

def main():
    # 配置参数
    url = ""  # 随机图片URL
    download_count = 20  # 要下载的图片数量
    delay_seconds = 2    # 每次请求间隔（秒）
    
    # 创建爬虫实例
    crawler = RandomImageCrawler(url)
    
    # 开始爬取
    try:
        crawler.crawl_images(count=download_count, delay=delay_seconds)
    except KeyboardInterrupt:
        print("\n\n用户中断了爬取过程")
    except Exception as e:
        print(f"\n爬取过程中出现错误: {e}")

if __name__ == "__main__":
    main()