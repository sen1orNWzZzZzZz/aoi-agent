from pathlib import Path
from rapidfuzz import fuzz, process

def fuzzy_search_directory(
    directory: str,
    keyword: str,
    *,
    threshold: int = 50,
    max_results: int = 20,
    case_sensitive: bool = False
) -> list[dict]:
    """
    使用 rapidfuzz 进行模糊搜索
    
    Args:
        threshold: 相似度阈值 (0~100)，rapidfuzz 默认按百分比
    """
    if not keyword.strip():
        return []
    
    #收集所有文件/目录路径
    all_names = []
    all_paths = []
    all_is_dir = []
    
    for p in Path(directory).rglob("*"):
        #跳过目录本身，只保留名字用于匹配，他们的idx都是一样的所以可以方便拿到所有文件的路径以及是不是文件夹等信息
        name = p.name
        all_names.append(name)
        all_paths.append(str(p))
        all_is_dir.append(p.is_dir())
    
    #rapidfuzz.process.extract 会自动批量匹配
    #scorer 可选：fuzz.ratio, fuzz.partial_ratio, fuzz.token_sort_ratio 等
    matches = process.extract(
        keyword,
        all_names,
        scorer=fuzz.partial_ratio,   # partial_ratio 对子串匹配更友好
        limit=max_results
    )
    
    results = []
    for name, score, idx in matches:
        if score < threshold:
            continue
        results.append({
            "path": all_paths[idx],
            "name": name,
            "score": score,
            "is_dir": all_is_dir[idx]
        })
    
    return results



# 以下createByKimi
# ========== 使用示例 ==========
if __name__ == "__main__":
    search_path = "/mnt/agents/upload"
    keyword = "reprot"  # 故意拼写错误，也能匹配到 report
    
    matches = fuzzy_search_directory(search_path, keyword, threshold=40)
    
    print(f"搜索 '{keyword}' 的结果：\n")
    for item in matches:
        type_icon = "📁" if item["is_dir"] else "📄"
        print(f"{type_icon} [{item['score']}] {item['name']}")
        print(f"   → {item['path']}\n")
