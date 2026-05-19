#!/usr/bin/env python3
"""
AI 自動審查引擎 - 實現 01_AI審查Prompt.md 的三大規範

審查三大規範：
1. 禁止宣傳療效/醫療功效
2. 禁止虛假宣傳
3. 內容準確性檢查
"""

import re
import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class ReviewIssue:
    """審查問題"""
    rule: str              # 違反的規範 (rule_1, rule_2, rule_3)
    severity: str          # 嚴重程度 (critical, warning, info)
    location: str          # 位置 (e.g., "第2段", "標題")
    issue: str             # 問題描述
    suggestion: str        # 修改建議


@dataclass
class ReviewResult:
    """審查結果"""
    passed: bool           # 是否通過
    overall_score: int     # 總分 (0-100)
    issues: List[ReviewIssue]  # 問題列表
    summary: str           # 總結
    reviewed_at: str       # 審查時間


class AIReviewEngine:
    """
    AI 自動審查引擎
    實現 01_AI審查Prompt.md 中的三大規範
    """

    # 規範 1：禁止療效宣傳詞彙
    BANNED_EFFICACY_WORDS = {
        '治療', '治癒', '預防', '改善', '緩解',
        '醫治', '恢復', '治好', '修復', '減輕'
    }

    # 規範 1：允許的表述
    ALLOWED_EXPRESSIONS = {
        '支持', '有助於', '幫助', '促進', '維持',
        '傳統用途', '傳統上', '據信', '可能有助於',
        '研究表明', '科學證實'
    }

    # 規範 2：禁止的絕對詞彙
    BANNED_ABSOLUTE_WORDS = {
        '100%', '完全', '絕對', '保證', '一定',
        '必然', '肯定', '無疑', '毫無疑問',
        '最好', '最有效'
    }

    # 規範 3：特殊人群安全詞彙（應該包含）
    SAFETY_KEYWORDS = {
        '孕婦', '兒童', '過敏', '安全', '警告',
        '禁忌', '不適用', '請勿', '諮詢', '醫生',
        '患者', '病人', '藥物相互作用'
    }

    def __init__(self):
        """初始化審查引擎"""
        self.issues = []
        self.score = 100

    def review(self, article: Dict) -> ReviewResult:
        """
        執行完整審查

        Args:
            article: 包含以下字段的文章字典
                - meta_title: SEO 標題
                - meta_description: SEO 描述
                - article_body: 文章內容 (HTML)
                - category: 分類

        Returns:
            ReviewResult: 審查結果
        """
        self.issues = []
        self.score = 100

        logger.info("🔍 開始 AI 自動審查...")

        # 規範 1：檢查療效宣傳
        self._check_efficacy_claims(article)

        # 規範 2：檢查虛假宣傳
        self._check_false_claims(article)

        # 規範 3：檢查內容準確性
        self._check_accuracy(article)

        # 生成結果
        passed = len([i for i in self.issues if i.severity == 'critical']) == 0
        summary = self._generate_summary()

        result = ReviewResult(
            passed=passed,
            overall_score=max(0, self.score),
            issues=self.issues,
            summary=summary,
            reviewed_at=self._get_timestamp()
        )

        self._log_result(result)
        return result

    def _check_efficacy_claims(self, article: Dict) -> None:
        """規範 1：檢查療效宣傳"""
        content = self._extract_text(article)

        # 檢查禁止詞彙
        for word in self.BANNED_EFFICACY_WORDS:
            if word in content:
                matches = re.finditer(word, content)
                for match in matches:
                    location = self._find_location(content, match.start())
                    self.issues.append(ReviewIssue(
                        rule='rule_1',
                        severity='critical',
                        location=location,
                        issue=f"使用了禁止詞彙「{word}」(療效宣傳)",
                        suggestion=f"改為「支持」、「有助於」、「可能有助於」等允許詞彙"
                    ))
                    self.score -= 20

        # 檢查是否宣稱可替代藥物
        if re.search(r'(替代|代替|而非|不用)(藥|醫療|治療)', content):
            self.issues.append(ReviewIssue(
                rule='rule_1',
                severity='critical',
                location='文章主體',
                issue="宣稱可替代藥物或醫療",
                suggestion="刪除此類宣稱，改為「傳統用途」表述"
            ))
            self.score -= 15

    def _check_false_claims(self, article: Dict) -> None:
        """規範 2：檢查虛假宣傳"""
        content = self._extract_text(article)

        # 檢查絕對詞彙
        for word in self.BANNED_ABSOLUTE_WORDS:
            if word in content:
                self.issues.append(ReviewIssue(
                    rule='rule_2',
                    severity='warning',
                    location=self._find_location(content, content.find(word)),
                    issue=f"使用了絕對詞彙「{word}」",
                    suggestion="改為「可能」、「據研究」、「通常」等限定表述"
                ))
                self.score -= 10

        # 檢查是否有科學依據（references）
        if not article.get('references') or len(article.get('references', [])) == 0:
            self.issues.append(ReviewIssue(
                rule='rule_2',
                severity='warning',
                location='文章結構',
                issue="缺少科學參考來源",
                suggestion="添加至少 3-5 個經驗證的科學參考"
            ))
            self.score -= 5

    def _check_accuracy(self, article: Dict) -> None:
        """規範 3：檢查內容準確性"""
        content = self._extract_text(article)

        # 檢查是否包含特殊人群安全提示
        has_safety_info = any(keyword in content for keyword in self.SAFETY_KEYWORDS)

        if not has_safety_info:
            self.issues.append(ReviewIssue(
                rule='rule_3',
                severity='info',
                location='文章結構',
                issue="缺少特殊人群安全提示",
                suggestion="添加孕婦、兒童、過敏者等的安全提示"
            ))
            self.score -= 5

        # 檢查靈芝的基本信息
        if '靈芝' not in content:
            self.issues.append(ReviewIssue(
                rule='rule_3',
                severity='warning',
                location='文章主體',
                issue="未提及靈芝的相關信息",
                suggestion="確保文章包含關於靈芝的正確基本信息"
            ))
            self.score -= 10

        # 檢查科學名稱準確性
        if not any(name in content for name in ['靈芝', 'Ganoderma', 'Reishi']):
            self.issues.append(ReviewIssue(
                rule='rule_3',
                severity='info',
                location='第一段',
                issue="未包含靈芝的科學名稱",
                suggestion="在第一次提到靈芝時，可加上科學名稱 Ganoderma lucidum (Reishi)"
            ))
            self.score -= 3

    def _extract_text(self, article: Dict) -> str:
        """提取文章文本（移除HTML標籤）"""
        html_content = f"{article.get('meta_title', '')} {article.get('meta_description', '')} {article.get('article_body', '')}"
        # 移除 HTML 標籤
        text = re.sub(r'<[^>]+>', '', html_content)
        # 移除多餘空白
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _find_location(self, content: str, pos: int) -> str:
        """根據位置查找段落編號"""
        paragraphs = content.split('。')
        char_count = 0
        for i, para in enumerate(paragraphs, 1):
            char_count += len(para) + 1
            if char_count >= pos:
                return f"第 {i} 段"
        return "文章主體"

    def _generate_summary(self) -> str:
        """生成審查摘要"""
        critical_count = len([i for i in self.issues if i.severity == 'critical'])
        warning_count = len([i for i in self.issues if i.severity == 'warning'])
        info_count = len([i for i in self.issues if i.severity == 'info'])

        if critical_count == 0 and warning_count == 0:
            return f"✅ 審查通過！文章符合所有規範。(評分: {self.score}/100)"
        else:
            summary = "❌ 審查結果："
            if critical_count > 0:
                summary += f" {critical_count} 個嚴重問題"
            if warning_count > 0:
                summary += f" {warning_count} 個警告"
            if info_count > 0:
                summary += f" {info_count} 個建議"
            summary += f" (評分: {self.score}/100)"
            return summary

    def _log_result(self, result: ReviewResult) -> None:
        """記錄審查結果"""
        if result.passed:
            logger.info(f"✅ {result.summary}")
        else:
            logger.warning(f"⚠️ {result.summary}")
            for issue in result.issues:
                if issue.severity == 'critical':
                    logger.error(f"  🔴 [{issue.location}] {issue.issue}")
                elif issue.severity == 'warning':
                    logger.warning(f"  🟡 [{issue.location}] {issue.issue}")
                else:
                    logger.info(f"  ℹ️ [{issue.location}] {issue.issue}")

    @staticmethod
    def _get_timestamp() -> str:
        """獲取當前時間戳"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()


# 方便的函數
def review_article(article: Dict) -> ReviewResult:
    """快速審查文章"""
    engine = AIReviewEngine()
    return engine.review(article)
