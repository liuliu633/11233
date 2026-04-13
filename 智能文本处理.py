print("智能文本处理系统")
import jieba
import string
from zhon.hanzi import punctuation
import re
import json

#自动保存
def load_counts():
    try:
        with open("word_data.json","r",encoding="utf-8") as f:
            data = json.load(f)
            return data.get("unique_words",[]),data.get("word_counts",[])
    except(FileNotFoundError,json.JSONDecodeError):
        return [],[]

#加载历史记录
unique_words,word_counts = load_counts()

if not text:
    print("错误：你还没输入任何文本！")
else:
    all_punctuations = string.punctuation + punctuation
    for p in all_punctuations:
        text = text.replace(p, ' ')
    text = ' '.join(text.split())
    has_chinese = any('\u4e00' <= c <='\u9fff' for c  in text)
    if has_chinese:
        word_list = jieba.lcut(text)
        word_list = [w for w in word_list if w.strip()]
    else:
        text_lower = text.lower()
        word_list = text_lower.split()
    print("\n处理后的单词列表（线性表）：")
    print(word_list)
    print("-" * 50)

    #累计词频
    for word in word_list:
        if word not in unique_words:
            unique_words.append(word)
            word_counts.append(1)
        else:
            index = unique_words.index(word)
            word_counts[index] += 1

    #自动保存
    def save_counts(uw,wc):
        with open("word_data.json","w",encoding="utf-8") as f:
            json.dump({"unique_words":uw,"word_counts":wc},f,ensure_ascii=False)
    save_counts(unique_words,word_counts)

print("\n【累计】词频统计结果：")
print("单词\t\t频次)
print("-" * 20)
#遍历两个列表，打印每个单词和对应频次
for i in range(len(unique_words)):
    print(f"{unique_words[i]}\t\t{word_counts[i]}")

print("-" * 20)
total_words = sum(word_counts) 
different_words = len(unique_words) 
print(f"总单词数量：{total_words}")
print(f"不同单词数量：{different_words}")
print("\n数据已经自动保存，下次打开会继续累计")
