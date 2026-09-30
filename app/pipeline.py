import shutil

from app.agent import repository_agent
from app.models import CodeReview, ReviewContext
from app.quality_agent import quality_agent
from app.security_agent import security_agent
from app.senior_agent import senior_reviewer
from app.tools.repository import clone_repository


async def run_full_review(repo_url: str) -> dict:
    """Run the complete four-agent repository review pipeline."""

    print("Cloning repository...")
    repo_path = clone_repository(repo_url)

    try:
        # =====================================================
        # Agent 1 — Repository Analyst
        # =====================================================

        print("\n[1/4] Running repository analysis...")

        repository_result = await repository_agent.run(
            """
Analyze this repository.

Identify:
- the primary programming language
- frameworks and technologies
- important files
- likely entry points
- high-level architecture
- repository strengths

Use the repository tools to inspect files when necessary.
""",
            deps=repo_path,
        )

        repository_analysis = repository_result.output

        print("[1/4] Repository analysis complete.")

        # =====================================================
        # Agent 2 — Code Quality Reviewer
        # =====================================================

        print("\n[2/4] Running code quality review...")

        quality_result = await quality_agent.run(
            """
Perform a code quality and maintainability review of this repository.

Focus on:
- naming
- duplication
- complexity
- organization
- error handling
- separation of concerns
- maintainability
- testing
- obvious performance problems

Use the repository tools to inspect actual source files.
""",
            deps=repo_path,
        )

        quality_review = quality_result.output

        print("[2/4] Code quality review complete.")

        # =====================================================
        # Agent 3 — Security & Bug Reviewer
        # =====================================================

        print("\n[3/4] Running security and bug review...")

        security_result = await security_agent.run(
            """
Perform a security and obvious bug review of this repository.

Focus on:
- hardcoded secrets
- environment variables
- injection
- unsafe file operations
- path traversal
- subprocess usage
- authentication/authorization
- sensitive information exposure
- insecure API usage
- dependency security concerns
- obvious runtime or logic bugs

Use the repository tools to inspect files.
""",
            deps=repo_path,
        )

        security_review = security_result.output

        print("[3/4] Security and bug review complete.")

        # =====================================================
        # Agent 4 — Senior Reviewer
        # =====================================================

        print("\n[4/4] Running senior review synthesis...")

        review_context = ReviewContext(
            repository_analysis=repository_analysis,
            quality_review=quality_review,
            security_review=security_review,
        )

        final_result = await senior_reviewer.run(
            """
Produce the final code review for this repository.

Review the three supplied specialist reports.

Your final review should:
- validate findings
- remove duplicates
- exclude unsupported/speculative findings
- preserve legitimate findings
- prioritize actionable findings
- identify repository strengths
- provide 3-7 practical recommendations when
  legitimate findings exist

Recommendations must be derived from the accepted
quality and security findings.

Do not leave recommendations empty when legitimate
findings exist.

Return the final structured CodeReview.
""",
            deps=review_context,
        )

        final_review: CodeReview = final_result.output

        # =====================================================
        # Recommendation Safety Net
        # =====================================================

        # Agent 4 should normally generate recommendations.
        # If it returns an empty list despite having accepted
        # findings, derive recommendations from those findings.

        if not final_review.recommendations:

            recommendations = []

            # Security recommendations first
            for finding in final_review.security_findings:
                if finding.recommendation:
                    recommendations.append(
                        finding.recommendation
                    )

            # Quality recommendations second
            for finding in final_review.quality_findings:
                if finding.recommendation:
                    recommendations.append(
                        finding.recommendation
                    )

            # Remove duplicates while preserving order
            recommendations = list(
                dict.fromkeys(recommendations)
            )

            # Keep the final list concise
            final_review.recommendations = recommendations[:7]

            if final_review.recommendations:
                print(
                    "[4/4] Recommendations generated "
                    "from accepted findings."
                )

        print("[4/4] Senior review complete.")

        # =====================================================
        # Return All Agent Outputs
        # =====================================================

        return {
            "repository_analysis": repository_analysis,
            "quality_review": quality_review,
            "security_review": security_review,
            "final_review": final_review,
        }

    finally:
        # =====================================================
        # Cleanup
        # =====================================================

        print("\nCleaning up temporary repository...")

        shutil.rmtree(
            repo_path,
            ignore_errors=True,
        )

        print("Temporary repository cleaned up.")