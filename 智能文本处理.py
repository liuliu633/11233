print("智能文本处理系统")
import jieba
import string
from zhon.hanzi import punctuation
import re
import json

SAVE_PATH = "word_data.json"

#自动保存
def load_counts():
    try:
        with open("word_data.json","r",encoding="utf-8") as f:
            data = json.load(f)
            return data.get("unique_words",[]),data.get("word_counts",[])
    except(FileNotFoundError,json.JSONDecodeError):
        return [],[]

#自动保存
def save_counts(uw,wc):
    with open("word_data.json","w",encording="utf-8") as f:
        json.dump({"unique_words":uw,"word_counts":wc},f,ensure_ascii=False)

#删除指定单词
def delete_word(uw,wc,word):
    target =word.strip().lower()
    for i in range(len(uw)):
        if uw[i].strip().lower() == target:
            uw.pop(i)
            wc.pop(i)
            return True
    return False
#清空所有历史记录
def clear_all(uw,wc):
    uw.clear()
    wc.clear()
    
#加载历史记录
unique_words,word_counts = load_counts()

while True:
    print("请选择操作：")
    print("1-输入文本并累计词频")
    print("2-删除某个单词")
    print("3-清空所有数据")
    print("0-退出程序")
    choice = input("请输入序号：").strip()

    if choice =="1":
        text = input("请输入要统计的文本！")
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
       
        #累计词频
        for word in word_list:
            if word not in unique_words:
                unique_words.append(word)
                word_counts.append(1)
            else:
                index = unique_words.index(word)
                word_counts[index] += 1

    #自动保存
   save_counts(unique_words,word_counts)
   print("词频已累计并保存")

elif choice == "2":
    del_word = input("请输入要删除的单词：").strip()
    if delete_word(unique_words,word_counts,del_word):
        print(f"已删除单词：{del_word}")
        save_counts(unique_words,word_counts)
    else:
        print("单词不存在！")

elif choice == "3":
    confirm = input("确定要清空所有数据吗？(y/n):")
    if confirm.lower() == "y":
        clear_all(unique_words,word_counts)
        save_counts(unique_words,word_counts)
        print("已清空所有数据！")
    else:
        print("已取消清空")

elif choice == "0":
    print("退出程序")
    break
else:
    print("输入无效，请重新选择！")
    
print("\n" + "="*30)
print("当前词频统计结果：")
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
