print("智能文本处理系统")
import jieba
import string
from zhon.hanzi import punctuation
import re
#input()
text = input("请输入你想要统计的文本：").strip()

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

unique_words = []
word_counts = []
for word in word_list:
    if word not in unique_words:
        unique_words.append(word)
        word_counts.append(1)

    else:
        index = unique_words.index(word) 
        word_counts[index] += 1

print("\n词频统计结果：")
print("单词\t\t频次")
print("-" * 20)
#遍历两个列表，打印每个单词和对应频次
for i in range(len(unique_words)):
    print(f"{unique_words[i]}\t\t{word_counts[i]}")

print("-" * 20)
total_words = sum(word_counts) 
different_words = len(unique_words) 
print(f"总单词数量：{total_words}")
print(f"不同单词数量：{different_words}")
