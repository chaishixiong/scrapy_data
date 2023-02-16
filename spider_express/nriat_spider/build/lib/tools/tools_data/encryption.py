import hashlib
def encode_md5(str):
    hash1 = hashlib.md5()
    hash1.update(str.encode())
    md5_test = hash1.hexdigest()
    return md5_test

if __name__=="__main__":
    url = "https://blog.csdn.net/diyiday/article/details/79626177"
    md5_test = encode_md5(url)
    print(md5_test)
