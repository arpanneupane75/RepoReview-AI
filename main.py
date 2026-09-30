import asyncio

from app.pipeline import run_full_review


REPO_URL = "https://github.com/arpanneupane75/ResearchMate.git"


def print_review(review):
    print("\n" + "=" * 60)
    print("FINAL CODE REVIEW")
    print("=" * 60)

    print(f"\nRepository:\n{review.repository}")
    print(f"\nSummary:\n{review.summary}")

    print("\nStrengths:")
    for strength in review.strengths:
        print(f"- {strength}")

    print("\nCode Quality Findings:")

    if review.quality_findings:
        for index, finding in enumerate(
            review.quality_findings,
            start=1,
        ):
            print(f"\n[{index}] {finding.title}")
            print(f"Severity: {finding.severity}")
            print(f"Description: {finding.description}")

            if finding.file:
                location = finding.file

                if finding.line is not None:
                    location += f":{finding.line}"

                print(f"Location: {location}")

            print(
                f"Recommendation: "
                f"{finding.recommendation}"
            )
    else:
        print("- None")

    print("\nSecurity Findings:")

    if review.security_findings:
        for index, finding in enumerate(
            review.security_findings,
            start=1,
        ):
            print(f"\n[{index}] {finding.title}")
            print(f"Severity: {finding.severity}")
            print(f"Description: {finding.description}")

            if finding.file:
                location = finding.file

                if finding.line is not None:
                    location += f":{finding.line}"

                print(f"Location: {location}")

            print(
                f"Recommendation: "
                f"{finding.recommendation}"
            )
    else:
        print("- None")

    print("\nRecommendations:")

    for recommendation in review.recommendations:
        print(f"- {recommendation}")


async def main():
    review = await run_full_review(REPO_URL)
    print_review(review)


if __name__ == "__main__":
    asyncio.run(main())