print("智能文本处理系统")
import jieba
import string
from zhon.hanzi import punctuation
import re
import json
import threading

saved_texts = []
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
def save_counts(words,counts):
    data = {"words": words,"counts": counts}
    with open("word_data.json","w",encording="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

#删除指定单词
def delete_word(words. counts, word):
    if word in words:
        idx = words.index(word)
        words.pop(idx)
        counts.pop(idx)
        return True
    return False
#清空所有历史记录
def clear_all(uw,wc):
    uw.clear()
    wc.clear()

def grammar_check(text):
    raw_text = text.strip()
    if not raw_text:
        return "⚠️ 文本为空"

    errors = []
    corrected = raw_text

    #BF暴力算法
    def bf_find_repeat(s,pattern_len=2):
        #BF:检测文本中连续重复的短语（长度为pattern_len）
        repeats = []
        n = len(s)
        for i in range(n - 2*pattern_len + 1):
            #暴力匹配：直接比较两段子串是否相同
            if s[i:i+pattern_len] == s[i+pattern_len:i+2*pattern_len]:
                repeats.append(s[i:i+pattern_len])
            return repeats

    #检测连续重复的2个词
    dup_phrass = bf_find_repeat(corrected, pattern_len=2)
    for w in set(dup_phrass):
        errors.append(f"语义重复：「{w}{w}」重复冗余（BF匹配检测）")
        corrected = corrected.replace(f"{w}{w}", w)

    #KMP算法next数组
    def compute_next(pattern):
        #KMP算法：计算模式串的next数组
        m = len(pattern)
        next_arr = [0] * m
        j = 0
        for i in range(1, m):
            while j > 0 and pattern[i] != pattern[j]:
                j = next_arr[j-1]
            if pattern[i] == pattern[j]:
                j += 1
                next_arr[i] = j
            else:
                next_arr[i] = 0
        return next_arr

    def kmp_search(text, pattern):
        #KMP串匹配算法：利用next数组避免主串回溯
        if not pattern:
            return[]
        n = len(text)
        m = len(pattern)
        if m > n:
            return []
        next_arr = compute_next(pattern)
        j = 0
        matches = []
        for i in range(n):
            while j > 0 and text[i] != pattern[j]:
                j = next_arr[j-1]
            if text[i] == pattern[j]:
                j += 1
            if j == m:
                matches.append(i - m + 1)
                j = next_arr[j-1]
        return matches       
    
    # 语义重复检测（可扩展）
    repeat_groups = [
        ["大约", "差不多", "左右", "大概", "估计"],
        ["必须", "务必", "一定要"],
        ["全部", "所有", "都", "完全"],
        ["非常", "很", "特别", "十分"],
        ["经常", "常常", "时常"]
    ]

    for group in repeat_groups:
        found = []
        for w in group:
            #用KMP算法在文本中快捷查找词
            if kmp_search(corrected, w):
                found,append(w)
        if len(found) >= 2:
            errors.append(f"语义重复：{', '.join(found)} 意思重复")
            # 删除found[1:]里的词，found[0]不动
            for w in found[1:]:
                corrected = corrected.replace(w, "")


    has_chinese = any('\u4e00' <= c <='\u9fff' for c in raw_text)
    has_english = any(c.isalpha() for c in raw_text)

    # 连续字符重复检测
    repeat_pattern = re.compile(r'([\u4e00-\u9fff-zA-Z])\1{2,}')
    repeats = repeat_pattern.findall(corrected)
    for ch in set(repeats):
        errors.append(f"冗余重复：字符「{ch}」连续重复过多")
        corrected = re.sub(f"{ch}+", ch, corrected)

    # 中文语法规则
    if has_chinese:
        # 标点不规范检测
        half_punct = r'[,.!?;:\'"()\[\]]'
        if re.search(half_punct, corrected):
            errors.append("标点不规范：请使用中文标点")

        # 句尾标点检测
        if not re.search(r'[。？！；]$', corrected):
            errors.append("句式不完整，中文句子缺少结尾标点")
            corrected += "。"

        # 词语重复检测（如“开心开心”）
        word_repeat = re.compile(r'([\u4e00-\u9fff-zA-Z]{2})\s*\1')
        dup_words = word_repeat.findall(corrected)
        for w in set(dup_words):
            errors.append(f"语义重复：「{w}{w}」重复冗余")
            corrected = re.sub(f"{w}\\s*{w}", w, corrected)
        # 新增：通用中文语序语病提示
        if len(corrected) >= 6:
            errors.append("语法提示：语句语序或搭配可能存在问题，请检查通顺度")

    # 英文语法规则
    if has_english and not has_chinese:
        if corrected and corrected[0].islower():
            errors.append("格式规范：英文句子首字母应大写")
            corrected = corrected[0].upper() + corrected[1:]

        if not re.search(r'[.!?]$', corrected):
            errors.append("句式不完整：英文句子缺少结尾标点")
            corrected += "."

        if re.search(r'\s{2,}', corrected):
            errors.append("格式规范：存在连续多余空格")
            corrected = re.sub(r'\s+', ' ', corrected)
    
        words = corrected.strip().split()
        if len(words) >= 3:
            if words[0] in {"i", "you", "he", "she", "we", "they", "it"}:
                has_neg = any(w in {"don't", "doesn't", "can't", "won't", "isn't", "aren't"} for w in words)
                has_verb = any(w.endswith(("e", "s", "es", "ing", "ed")) for w in words)
                if has_neg and has_verb and words.index("don't" if "don't" in words else "doesn't" if "doesn't" in words else "can't" if "can't" in words else "won't" if "won't" in words else "isn't" if "isn't" in words else "aren't") > 1:
                    errors.append("语法警告：英文语序可能不符合主谓宾结构，请检查助动词/否定词的位置")
                elif len(words) >= 4 and has_verb and not has_neg:
                    errors.append("语法提示：句子结构较复杂，请检查主谓宾顺序是否合理")

        words = corrected.strip().split()
        if len(words) >= 3:
            # 1. 识别主语（人称代词开头）
            subject_pronouns = {"i", "you", "he", "she", "we", "they", "it"}
            starts_with_pronoun = words[0].lower() in subject_pronouns
            if starts_with_pronoun:
                # 2. 检测否定词/助动词的位置
                neg_words = {"don't", "doesn't", "can't", "won't", "isn't", "aren't"}
                for idx, word in enumerate(words):
                    if word.lower() in neg_words:
                        # 否定词不在第1或第2位，就是错误
                        if idx not in (1, 2):
                            errors.append("语法警告：英文语序可能存在问题，助动词/否定词位置不当")
                            break
    
                # 3. 检测双动词结构（主语+动词+动词，中间无连接词）
                verb_suffixes = ("e", "s", "es", "ing", "ed")
                verb_positions = []
                for idx, word in enumerate(words):
                    if any(word.lower().endswith(suffix) for suffix in verb_suffixes):
                        verb_positions.append(idx)
                # 如果有两个动词，且位置相邻，且不是情态动词+动词结构
                if len(verb_positions) >= 2 and verb_positions[1] == verb_positions[0] + 1:
                    errors.append("语法警告：英文句子中出现多个连续动词，可能存在语序错误")

    if not errors:
        return "✅ 文本语法格式规范，未检测到错误"

    res = ["\n=== 语法检测结果 ==="]
    for idx, err in enumerate(errors, 1):
        res.append(f"{idx}. {err}")
    return "\n".join(res)

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
        text = input("请输入要统计的文本！").strip()
        
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
# ---------- 1. HTML/XML 标签校验（栈）----------
def validate_tags(text):
     #存放开标签的栈
     stack = []   
        #遍历文本里的字符，找标签
        i = 0
        while i < len(text):
            if text[i] == '<':
                j = i
                while j < len(text) and text[j] == '>':
                    j += 1
                #把<>中间的内容拿出来
                tag = text[i:j+1]
                i = j + 1
                
                #判断是不是闭合标签（以 </ 开头）
                if tag.startswith('</'):
                    # 拿到标签名字，比如 </div> → div
                    tag_name = tag[2:-1]

                    # 如果栈是空的，说明多了一个闭合标签
                     if len(stack) == 0:
                         return False, "错误：多出来的闭合标签"

                     # 拿出栈最上面的标签
                     last_tag = stack.pop()

                      # 如果名字对不上，说明嵌套错了
                      if last_tag != tag_name:
                          return False, "错误：标签嵌套顺序错了" 

                 # 否则是开标签，直接放进栈里
                 else:
                     tag_name = tag[1:-1]
                     stack.append(tag_name)
            else:
                 i += 1

                 # 遍历完后，如果栈里还有东西，说明没闭合
            if len(stack) > 0:
                return False, "错误：有标签没有关闭"         
            return True, "正确：所有标签都配对了"
            
 # ---------- 2. 文本撤销/重做（栈）----------
class TextEditor:
     def __init__(self):
         self.text = ""
         self.history_stack = []
         self.redo_stack = []

     # 更新文本，并保存历史（输入新内容时自动记录）
     def update_text(self, new_text):
         # 只有内容真的变了，才记录
          if self.text != new_text:
              # 把【当前文本】压入撤销栈（留着以后撤销用）
              self.history_stack.append(self.text)
               # 更新成新文本
              self.text = new_text
               # 一旦输入新内容，重做栈必须清空
              self.redo_stack.clear()

     # 撤销：回到上一步
     def undo(self):
         # 如果没有历史，不能撤销
         if len(self.history_stack) == 0:
             return False, "没有可以重做的操作"

          # 把当前文本压回撤销栈
         self.history_stack.append(self.text)

           # 恢复重做栈里的内容
         self.text = self.redo_stack.pop()
         return True, "重做成功！当前文本：" + self.text
              
    # ---------- 3. 文本逐行/逐句处理（队列）----------
# 注意：必须导入队列
from collections import deque

class TextProcessor:
    def __init__(self):
        self.text = ""

    def process_line_by_line(self, text): 
        # 把文本按行切开，变成列表
        lines = text.splitlines()
        
        # 如果没有内容
        if not lines:
            return "没有可处理的行。"

        # 创建队列，并把所有行放进去
        queue = deque(lines)
        result_list = []  # 存放最终结果
        line_number = 1  # 当前是第几行
        
        # 从队列里一行一行取出来处理
        while queue:
            current_line = queue.popleft()  # 出队
            # 如果这一行是空的
            if current_line.strip() == "":
                 result_list.append(f"第{line_number}行：空行")
                 line_number += 1
                 continue

             # 统计这一行的单词
            result_str, _ = self.basic_word_freq(current_line)
            
             # 从结果里提取关键信息：总单词数、不同单词数
            result_lines = result_str.splitlines()
            total_words = ""
            different_words = ""

            for line in result_lines:
                if "总单词数量" in line:
                    total_words = line
                if "不同单词数量" in line:
                    different_words = line

             # 把这一行的结果存起来
            result_list.append(f"第{line_number}行：{total_words}，{different_words}")
            line_number += 1

        # 把所有行结果拼成字符串返回
        return "\n".join(result_list)

    def process_sentence_by_sentence(self, text):
        # 如果文本为空
        if not text.strip():
            return "没有可处理的句子。"

        # 按中英文句号、问号、感叹号分句
        sentences = []
        temp = ""
        for char in text:
            temp += char
            if char in ".?!。？！":
                sentences.append(temp.strip())
                temp = ""
        if temp.strip():
            sentences.append(temp.strip())

        # 创建队列，把所有句子放进去
        queue = deque(sentences)
        result_list = []
        sentence_number = 1

         # 依次从队列取出句子处理
        while queue:
            current_sentence = queue.popleft()

            if not current_sentence:
                result_list.append(f"第{sentence_number}句：空句子")
                sentence_number += 1
                continue

             # 统计单词 
            result_str, _ = self.basic_word_freq(current_sentence)
            result_lines = result_str.splitlines()
            total_words = ""
            different_words = ""

            for line in result_lines:
                if "总单词数量" in line:
                    total_words = line
                if "不同单词数量" in line:
                    different_words = line

            result_list.append(f"第{sentence_number}句：{total_words}，{different_words}") 
            sentence_number += 1

       return "\n".join(result_list)

   def basic_word_freq(self, text):
       words = text.split()
       total = len(words)
       unique = len(set(words))
       return f"总单词数量：{total}\n不同单词数量：{unique}", None

# ---------- 4. 流水线处理（队列）----------
def pipeline_process(self, text):
    steps = deque([
        ("清洗标点", self._step_clean),
        ("分词", self._step_tokenize),
        ("统计词频", self._step_count),
        ("格式化结果", self._step_format)
    ])

    data = text
    while steps:
        name, func = steps.popleft()    
        print(f"[流水线] {name}")
        data = func(data)
    return data

def _step_clean(self, text):
    all_punctuations = string.punctuation + punctuation
    cleaned = text
    for p in all_punctuations:
        cleaned = cleaned.replace(p, ' ')
    return ' '.join(cleaned.split())

def _step_tokenize(self, text):
    has_chinese = any('\u4e00' <= c <= '\u9fff' for c in text)
    if has_chinese:
         words = jieba.lcut(text)
    else:
         words = text.lower().split()
    return [w for w in words if w.strip()]

def _step_count(self, word_list):
    freq = {}
    for w in word_list:
        freq[w] = freq.get(w, 0) + 1
    return freq

def _step_format(self, freq_dict):
    lines = ["流水线处理结果：","单词\t频次","-"*20]
    for word, count in freq_dict.items():
        lines.append(f"{word}\t{count}")
    lines.append("-" * 20)
    lines.append(f"总单词数：{sum(freq_dict.values())}")
    lines.append(f"不同单词数：{len(freq_dict)}")
    return "\n".join(lines)



kkk: 04-28 10:27:17
# ---------- 5. 异步保存结果（线程）----------
def save_async(self, content, filename="result.txt"):
     """启动后台线程保存结果到文件"""
    def _save():
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
             print(f"[异步保存] 结果已保存至 {filename}")
        except Exception as e:
            print(f"[异步保存] 保存失败：{e}")
        
    thread = threading.Thread(target=_save, daemon=True)
    thread.start()
    return f"异步保存任务已启动，文件将保存为 {filename}"

# ---------- 交互菜单 ----------
class TextProcessingSystem:
    def __init__(self):
        self.text = ""
        self.history_stack = []
        self.redo_stack = []
        self.processed_result = None
        self.unique_words = []
        self.word_counts = []

    def update_text(self, new_text):
        if self.text != new_text:
            self.history_stack.append(self.text)
            self.text = new_text
            self.redo_stack.clear()

    def undo(self):
        if not self.history_stack:
            return False, "无撤销操作"
        self.redo_stack.append(self.text)
        self.text = self.history_stack.pop()
        return True, f"撤销成功：{self.text[:40]}..."

    def redo(self): 
        if not self.redo_stack:
            return False, "无重做操作"
        self.history_stack.append(self.text)
        self.text = self.redo_stack.pop()
        return True, f"重做成功：{self.text[:40]}..."

    def validate_tags(self, text): 
        stack = []
        i = 0
        while i < len(text):
            if text[i] == '<':
                j = i
                while j < len(text) and text[j] != '>':
                    j += 1
                tag = text[i:j + 1]
                i = j + 1
                if tag.startswith('</'):
                    name = tag[2:-1].strip()
                    if not stack: return False, "多余闭合标签"
                    if stack.pop() != name: return False, "标签不匹配"
                else:
                    name = tag[1:-1].strip()
                    if name and not name.startswith('!'):
                        stack.append(name)
            else:
                i += 1
       return (True, "标签正确") if not stack else (False, f"未闭合标签：{stack}")    

   def basic_word_freq(self, text): 
       words = text.split()
       total = len(words)
       unique = len(set(words))
       return f"总单词：{total}，不同单词：{unique}", None

   def process_line_by_line(self, text):
       from collections import deque
       lines = text.splitlines()
       q = deque(lines)
       res = []
       n = 1
       while q:
           line = q.popleft()
           res.append(f"第{n}行：{self.basic_word_freq(line)[0]}")
           n += 1
       return "\n".join(res)

  def process_sentence_by_sentence(self, text):
      from collections import deque
      sentences = []
      temp = ""
      for c in text:
          temp += c
          if c in ".?!。？！":
              sentences.append(temp.strip())
              temp = ""
       if temp: sentences.append(temp.strip())
       q = deque(sentences)
       res = []
       n = 1
       while q:
           s = q.popleft()
           res.append(f"第{n}句：{self.basic_word_freq(s)[0]}")
           n += 1
       return "\n".join(res)  

    def pipeline_process(self, text):
        from collections import deque
        import jieba, string
        from zhon.hanzi import punctuation

        def clean(t):
            for p in string.punctuation + punctuation:
                t = t.replace(p, ' ')
            return ' '.join(t.split())    

        def cut(t):
            if any('\u4e00' <= c <= '\u9fff' for c in t):
                return [w for w in jieba.lcut(t) if w.strip()]
            return [w.lower() for w in t.split() if w.strip()]

        def count(wl):
            d = {}
            for w in wl: d[w] = d.get(w, 0) + 1
            return d   

        def fmt(fd):
            lines = ["单词\t频次", "-" * 20]
            for w, c in fd.items(): lines.append(f"{w}\t{c}")
            lines.append(f"总计：{sum(fd.values())}，不同：{len(fd)}")
            return "\n".join(lines)

        data = clean(text)
        data = cut(data)
        data = count(data)
        return fmt(data)

   def save_async(self, content, fn="result.txt"):
       import threading
       def run():
           with open(fn, 'w', encoding='utf-8') as f:
               f.write(content)

       threading.Thread(target=run, daemon=True).start()
       return "已启动异步保存"

       
def main():
    system = TextProcessingSystem()
    
    while True:
        print("\n" + "="*50)
        print("智能文本处理系统（增强版）")
        print("="*50)
        print("当前文本长度:", len(system.text), "字符")
        print("1. 输入/修改文本")
        print("2. 基础词频统计")
        print("3. HTML/XML 标签校验")
        print("4. 撤销 (Undo)")
        print("5. 重做 (Redo)")
        print("6. 逐行处理")
        print("7. 逐句处理")
        print("8. 流水线处理")
        print("9. 异步保存上次处理结果")
        print("0. 退出")
        print("-"*50)
        
        choice = input("请选择操作：").strip()
        
        if choice == "1":
            print("请输入新文本（支持多行，输入单独一行 'END' 结束）：")
            lines = []
            while True:
                line = input()
                if line == "END":
                    break
                lines.append(line)
            new_text = "\n".join(lines)
            system.update_text(new_text)
            print("文本已更新。")
        
        elif choice == "2":
            if not system.text:
                print("请先输入文本！")
            else:
                result, freq = system.basic_word_freq(system.text)
                system.processed_result = result
                print(result)
        
        elif choice == "3":
            if not system.text:
                print("请先输入文本！")
            else:
                valid, msg = system.validate_tags(system.text)
                print("校验结果:", msg)
        
        elif choice == "4":
            success, msg = system.undo()
            print(msg)
        
        elif choice == "5":
            success, msg = system.redo()
            print(msg)
        
        elif choice == "6":
            if not system.text:
                print("请先输入文本！")
            else:
                result = system.process_line_by_line(system.text)
                system.processed_result = result
                print(result)
        
        elif choice == "7":
            if not system.text:
                print("请先输入文本！")
            else:
                result = system.process_sentence_by_sentence(system.text)
                system.processed_result = result
                print(result)
        
        elif choice == "8":
            if not system.text:
                print("请先输入文本！")
            else:
                result = system.pipeline_process(system.text)
                system.processed_result = result
                print(result)
        
        elif choice == "9":
            if system.processed_result is None:
                print("没有可保存的处理结果，请先执行一项处理。")
            else:
                filename = input("请输入保存文件名（默认 result.txt）：").strip()
                if not filename:
                    filename = "result.txt"
                msg = system.save_async(system.processed_result, filename)
                print(msg)
        
        elif choice == "0":
            print("感谢使用，再见！")
            break
        
        else:
            print("无效选择，请重新输入。")

if __name__ == "__main__":
    main()

# ---------- 语法检测 ----------
import language_tool_python

class TextSystem:
    def __init__(self):
        self.text = ""
        self.processed_result = None
        self.grammar_tool = language_tool_python.LanguageTool('zh-CN')
        self.nlp = None

    def grammar_check(self, text):
        """语法检查与纠错"""
        matches = self.grammar_tool.check(text)
        if not matches:
            return "✅ 未检测到语法错误，文本语法规范。"
        
        # 生成错误报告
        result = []
        result.append("⚠️ 检测到以下语法问题：")
        for idx, match in enumerate(matches, 1):
            error_msg = f"{idx}. 错误位置：{match.offset}-{match.offset+match.length}"
            error_msg += f"\n   错误描述：{match.message}"
            if match.replacements:
                error_msg += f"\n   建议修改：{', '.join(match.replacements[:3])}"
            result.append(error_msg)
        
        # 生成纠错后的文本
        corrected_text = language_tool_python.utils.correct(text, matches)
        result.append(f"\n--- 纠错后文本 ---\n{corrected_text}")
        
        return "\n".join(result)

# ---------- 句法分析(spaCy)模块 ----------
import spacy
    def syntax_analysis(self, text):
        """句法分析：词性标注+依存关系+句子成分提取"""
        try:
            if self.nlp is None:
               self.nlp = spacy.load("zh-core-web-sm") 
        except:
            return"❌ 未安装中文模型，请先运行：python -m spacy download zh-core-web-sm"
            
        doc = self.nlp(text)
        result = []
        result.append("📊 句法分析结果")
        result.append("=" * 30)
        result.append("单词\t词性\t依存关系\t中心词")
        result.append("-" * 30)
        
        # 词性标注和依存关系分析
        for token in doc:
            result.append(f"{token.text}\t{token.pos_}\t{token.dep_}\t{token.head.text}")
        
        # 提取主谓宾成分
        result.append("\n--- 句子成分提取 ---")
        subject = [tok.text for tok in doc if tok.dep_ == "nsubj"]
        verb = [tok.text for tok in doc if tok.dep_ == "ROOT"]
        obj = [tok.text for tok in doc if tok.dep_ == "dobj"]
        
        result.append(f"主语：{subject if subject else '未识别到主语'}")
        result.append(f"谓语：{verb if verb else '未识别到谓语'}")
        result.append(f"宾语：{obj if obj else '未识别到宾语'}")
        
        return "\n".join(result)

    def pipeline_process(self, text):
        """将句法分析整合到处理流程"""
        syntax_result = self.syntax_analysis(text)
        final_result = f"=== 原文本 ===\n{text}\n\n=== 句法分析结果 ===\n{syntax_result}"
        return final_result 

# 测试语法与句法功能
if __name__ == "__main__":
    ts = TextSystem()
    text = input("请输入测试语句：")
    print("\n==== 语法检测 ====")
    print(ts.grammar_check(text))
    print("\n==== 句法分析 ====")
    print(ts.syntax_analysis(text))
#该版本的库对中文支持不如英文完整，主要能识别错别字、标点错误和简单的搭配问题，复杂的语法问题识别能力有限，
#将会在下个版本做改进
#注：language_tool_python是调用Java版的LanguageTool来做语法检查

