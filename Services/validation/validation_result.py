from dataclasses import dataclass, field


@dataclass
class ValidationIssue:
    rule_id: str
    severity: str
    message: str


@dataclass
class ValidationResult:
    is_valid: bool = True
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)
    pattern_warnings: list[ValidationIssue] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    pattern_hints: list[str] = field(default_factory=list)
    lexical_hints: list[str] = field(default_factory=list)

    def add_issue(self, issue: ValidationIssue) -> None:
        if issue.severity == "error":
            self.errors.append(issue)
            self.is_valid = False
            return

        self.warnings.append(issue)

    def add_suggestion(self, suggestion: str) -> None:
        if suggestion not in self.suggestions:
            self.suggestions.append(suggestion)

    def add_pattern_hint(self, hint: str) -> None:
        if hint not in self.pattern_hints:
            self.pattern_hints.append(hint)
        self.add_suggestion(hint)

    def add_pattern_warning(self, rule_id: str, message: str) -> None:
        issue = ValidationIssue(rule_id=rule_id, severity="warning", message=message)
        if not any(existing.rule_id == rule_id and existing.message == message for existing in self.pattern_warnings):
            self.pattern_warnings.append(issue)
        # Keep backward compatibility with old string-based UI/output.
        self.add_pattern_hint(message)

    def add_lexical_hint(self, hint: str) -> None:
        if hint not in self.lexical_hints:
            self.lexical_hints.append(hint)
        self.add_suggestion(hint)
