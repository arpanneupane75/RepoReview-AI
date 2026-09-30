
from typing import Literal

from pydantic import BaseModel, Field


Severity = Literal[
    "critical",
    "high",
    "medium",
    "low",
    "info",
]


class RepositoryAnalysis(BaseModel):
    repository: str
    summary: str
    primary_language: str
    frameworks: list[str] = Field(default_factory=list)
    key_files: list[str] = Field(default_factory=list)
    architecture_notes: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)


class CodeQualityFinding(BaseModel):
    title: str
    description: str
    severity: Severity
    file: str | None = None
    line: int | None = None
    recommendation: str


class CodeQualityReview(BaseModel):
    summary: str
    findings: list[CodeQualityFinding] = Field(
        default_factory=list
    )


class SecurityFinding(BaseModel):
    title: str
    description: str
    severity: Severity
    file: str | None = None
    line: int | None = None
    recommendation: str


class SecurityReview(BaseModel):
    summary: str
    findings: list[SecurityFinding] = Field(
        default_factory=list
    )


class CodeReview(BaseModel):
    repository: str
    summary: str
    strengths: list[str] = Field(default_factory=list)
    quality_findings: list[CodeQualityFinding] = Field(
        default_factory=list
    )
    security_findings: list[SecurityFinding] = Field(
        default_factory=list
    )
    recommendations: list[str] = Field(default_factory=list)


class ReviewContext(BaseModel):
    repository_analysis: RepositoryAnalysis
    quality_review: CodeQualityReview
    security_review: SecurityReview

