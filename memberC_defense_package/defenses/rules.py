"""Rule definitions for RAG prompt-injection and leakage defense.

This module is intentionally dependency-free so it can be copied into a small
course project without installing extra packages.

Responsible member: C - Defense module.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Pattern
import re


@dataclass(frozen=True)
class Rule:
    """A detection rule for suspicious text.

    Attributes:
        name: Short readable name.
        category: Attack category, e.g. prompt_injection, task_hijack.
        pattern: Regular expression pattern.
        weight: Risk score added when this rule matches.
    """

    name: str
    category: str
    pattern: str
    weight: int = 1

    def compile(self) -> Pattern[str]:
        return re.compile(self.pattern, flags=re.IGNORECASE | re.MULTILINE)


# Rules for suspicious instructions in user questions or retrieved documents.
# These rules are defensive filters. They are designed for a class project and
# should be tuned after observing real false positives / false negatives.
SUSPICIOUS_RULES: List[Rule] = [
    # Direct instruction override / prompt injection
    Rule("ignore_previous_cn", "prompt_injection", r"忽略(之前|以上|前面|所有).{0,12}(规则|指令|要求|内容|限制)", 3),
    Rule("ignore_previous_en", "prompt_injection", r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|rules|messages)", 3),
    Rule("override_instruction_cn", "prompt_injection", r"(覆盖|替换|无视|绕过).{0,12}(系统|开发者|安全|原有).{0,12}(指令|规则|限制)", 3),
    Rule("override_instruction_en", "prompt_injection", r"(override|bypass|disable|forget).{0,30}(system|developer|safety).{0,30}(instruction|rule|policy)", 3),

    # System prompt / hidden prompt exfiltration
    Rule("reveal_system_prompt_cn", "secret_exfiltration", r"(输出|泄露|展示|告诉我|打印).{0,15}(系统提示词|系统 prompt|隐藏提示词|开发者提示词|内部规则)", 4),
    Rule("reveal_system_prompt_en", "secret_exfiltration", r"(reveal|print|show|dump|leak).{0,30}(system prompt|developer message|hidden prompt|internal instructions)", 4),

    # Credential / secret exfiltration
    Rule("credential_cn", "secret_exfiltration", r"(输出|泄露|告诉我|显示).{0,15}(密钥|密码|口令|token|api.?key|secret.?key|管理员密钥)", 4),
    Rule("credential_en", "secret_exfiltration", r"(reveal|print|show|dump|leak).{0,30}(api.?key|secret.?key|token|password|credential|private.?key)", 4),

    # Task hijacking / role manipulation
    Rule("role_hijack_cn", "task_hijack", r"你现在(不是|扮演|作为|变成).{0,18}(管理员|系统|开发者|黑客|审计员|root|admin)", 3),
    Rule("role_hijack_en", "task_hijack", r"you\s+are\s+now\s+(an?\s+)?(admin|root|developer|system|hacker)", 3),
    Rule("stop_being_assistant_cn", "task_hijack", r"不要再(作为|扮演).{0,12}(课程助手|问答助手|AI助手)", 2),

    # Malicious document pretending to be higher-priority message
    Rule("fake_system_cn", "indirect_injection", r"(系统消息|开发者消息|最高优先级|内部通知|安全测试).{0,20}(执行|遵守|优先|忽略)", 3),
    Rule("fake_system_en", "indirect_injection", r"(system message|developer message|highest priority|internal notice).{0,30}(follow|obey|execute|ignore)", 3),

    # Common coercive or jailbreak expressions
    Rule("jailbreak_cn", "jailbreak", r"(越狱|jailbreak|不受限制|无视安全|绕过安全|开发者模式)", 2),
    Rule("jailbreak_en", "jailbreak", r"(jailbreak|developer mode|do anything now|DAN|no restrictions)", 2),

    # Instruction to change output destination or format to hidden data
    Rule("forced_output_cn", "prompt_injection", r"不要回答.{0,20}(课程|问题|用户).{0,20}(改为|直接|只需要).{0,20}(输出|返回)", 3),
    Rule("forced_output_en", "prompt_injection", r"do\s+not\s+answer.{0,40}(instead|only|just).{0,20}(output|return|print)", 3),
]


# Patterns that indicate the model answer may have leaked sensitive data.
# The project should use simulated secrets only, but the guard still catches
# typical secret-looking strings to demonstrate risk control.
SENSITIVE_OUTPUT_RULES: List[Rule] = [
    Rule("simulated_secret_key", "sensitive_output", r"\b[A-Z0-9_]*(SECRET|TOKEN|PASSWORD|API[_-]?KEY|PRIVATE[_-]?KEY)[A-Z0-9_]*\b\s*[:=]\s*[A-Za-z0-9_\-{}]{4,}", 5),
    Rule("explicit_secret_cn", "sensitive_output", r"(管理员密钥|隐藏密钥|内部密钥|系统提示词|开发者提示词)\s*[:：=]", 5),
    Rule("explicit_secret_en", "sensitive_output", r"(system prompt|developer message|hidden prompt|admin secret|secret key|api key)\s*[:=]", 5),
    Rule("long_token_like", "sensitive_output", r"\b(sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_\-]{20,})\b", 5),
]


# Terms that are normal for this project. These are not used to suppress high-risk
# matches automatically; they are useful for explaining false positives and can be
# extended by the group.
COURSE_ALLOWLIST_TERMS: List[str] = [
    "课程", "作业", "PPT", "汇报", "评分", "小组", "GitHub", "助教", "提交", "Q&A", "人工智能安全", "伦理",
]


SAFE_REFUSAL = (
    "抱歉，我不能提供系统提示词、隐藏规则、密钥、密码或其他敏感信息。"
    "你可以询问课程安排、作业要求、评分方式或项目相关的正常问题。"
)

SAFE_DOC_REMOVED_NOTE = "[安全过滤提示：部分检索文档包含疑似提示注入或敏感信息诱导内容，已被过滤。]"

# Default thresholds. A score >= threshold is considered suspicious.
DEFAULT_SUSPICIOUS_THRESHOLD = 3
DEFAULT_OUTPUT_THRESHOLD = 5
