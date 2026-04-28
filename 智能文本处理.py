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
# ---------- 1. HTML/XML 标签校验（栈）----------
 def validate_tags(self, text):
        """使用栈校验 HTML/XML 标签是否闭合正确"""
        # 匹配标签：<...> 或 </...>，并捕获标签名
        tag_pattern = re.compile(r'</?([a-zA-Z0-9]+)[^>]*>')
        stack = []
        for match in tag_pattern.finditer(text):
            full_tag = match.group(0)
            tag_name = match.group(1)
            # 判断是否为闭合标签
            is_closing = full_tag.startswith('</')
            if not is_closing:
                # 开标签入栈
                stack.append(tag_name)
            else:
                # 闭合标签：检查栈顶是否匹配
                if not stack:
                    return False, f"错误：多余的闭合标签 </{tag_name}>"
                if stack[-1] != tag_name:
                    return False, f"错误：期望闭合 </{stack[-1]}>，但遇到了 </{tag_name}>"
                stack.pop()
        if stack:
            return False, f"错误：未闭合的标签 {stack}"
        return True, "标签校验通过，所有标签正确闭合。"

    # ---------- 2. 文本撤销/重做（栈）----------
    def update_text(self, new_text):
        """更新文本并保存历史（用于撤销/重做）"""
        if self.text != new_text:
            self.history.append(self.text)
            self.text = new_text
            self.redo_stack.clear()  # 新操作后清空重做栈

    def undo(self):
        """撤销操作"""
        if not self.history:
            return False, "没有可撤销的操作。"
        self.redo_stack.append(self.text)
        self.text = self.history.pop()
        return True, f"撤销成功，当前文本：\n{self.text[:200]}..."

    def redo(self):
        """重做操作"""
        if not self.redo_stack:
            return False, "没有可重做的操作。"
        self.history.append(self.text)
        self.text = self.redo_stack.pop()
        return True, f"重做成功，当前文本：\n{self.text[:200]}..."

    # ---------- 3. 文本逐行/逐句处理（队列）----------
    def process_line_by_line(self, text):
        """逐行处理：将每行放入队列，依次进行词频统计"""
        lines = text.splitlines()
        if not lines:
            return "没有可处理的行。"

        queue = deque(lines)
        results = []
        line_num = 1
        while queue:
            line = queue.popleft()
            if not line.strip():
                results.append(f"第{line_num}行（空行）")
                line_num += 1
                continue
            result_str, _ = self.basic_word_freq(line)
            # 只提取简要统计信息
            lines_in_result = result_str.splitlines()
            # 取总单词数和不同单词数
            total = next((l for l in lines_in_result if "总单词数量" in l), "")
            diff = next((l for l in lines_in_result if "不同单词数量" in l), "")
            results.append(f"第{line_num}行处理完成：{total}, {diff}")
            line_num += 1

        return "\n".join(results)

    def process_sentence_by_sentence(self, text):
        """逐句处理：按中英文标点分句，放入队列依次处理"""
        # 简单分句：以。！？.!? 分割
        sentences = re.split(r'[。！？.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if not sentences:
            return "没有可处理的句子。"

        queue = deque(sentences)
        results = []
        sent_num = 1
        while queue:
            sent = queue.popleft()
            result_str, _ = self.basic_word_freq(sent)
            lines_in_result = result_str.splitlines()
            total = next((l for l in lines_in_result if "总单词数量" in l), "")
            diff = next((l for l in lines_in_result if "不同单词数量" in l), "")
            results.append(f"第{sent_num}句处理完成：{total}, {diff}")
            sent_num += 1

        return "\n".join(results)
kkk: 04-28 10:23:24
# ---------- 4. 流水线处理（队列）----------
    def pipeline_process(self, text):
        """
        流水线：清洗 -> 分词 -> 统计 -> 格式化
        每步的输出作为下一步的输入，使用队列传递。
        """
        steps = deque([
            ("清洗标点", self._step_clean),
            ("分词", self._step_tokenize),
            ("统计词频", self._step_count),
            ("格式化结果", self._step_format)
        ])
        
        data = text
        while steps:
            step_name, step_func = steps.popleft()
            print(f"[流水线] 正在执行: {step_name}")
            data = step_func(data)
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
        lines = ["流水线处理结果："]
        lines.append("单词\t\t频次")
        lines.append("-" * 20)
        for word, count in freq_dict.items():
            lines.append(f"{word}\t\t{count}")
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
