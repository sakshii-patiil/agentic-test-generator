"""
Gherkin / BDD Feature File Parser
Parses .feature files into structured TestScenario objects
consumed by the agentic test generator.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import re


@dataclass
class Step:
    keyword: str   # Given / When / Then / And / But
    text: str


@dataclass
class TestScenario:
    feature:     str
    scenario:    str
    steps:       List[Step]
    tags:        List[str] = field(default_factory=list)
    examples:    Optional[List[dict]] = None  # for Scenario Outline


class GherkinParser:
    """
    Parses Gherkin feature files into TestScenario objects.

    Usage:
        parser = GherkinParser()
        scenarios = parser.parse_file("features/subscription.feature")
    """

    STEP_KEYWORDS = ("Given", "When", "Then", "And", "But")

    def parse_text(self, text: str) -> List[TestScenario]:
        scenarios = []
        current_feature  = ""
        current_scenario = ""
        current_steps    = []
        current_tags     = []
        in_scenario      = False

        for raw_line in text.splitlines():
            line = raw_line.strip()

            if line.startswith("Feature:"):
                current_feature = line[len("Feature:"):].strip()

            elif line.startswith("@"):
                current_tags = [t.lstrip("@") for t in line.split()]

            elif line.startswith(("Scenario:", "Scenario Outline:")):
                if in_scenario and current_steps:
                    scenarios.append(TestScenario(
                        feature=current_feature,
                        scenario=current_scenario,
                        steps=current_steps,
                        tags=current_tags,
                    ))
                current_scenario = re.sub(r"^Scenario( Outline)?:", "", line).strip()
                current_steps    = []
                in_scenario      = True

            elif any(line.startswith(kw) for kw in self.STEP_KEYWORDS):
                keyword, _, text_part = line.partition(" ")
                current_steps.append(Step(keyword=keyword, text=text_part))

        # Flush last scenario
        if in_scenario and current_steps:
            scenarios.append(TestScenario(
                feature=current_feature,
                scenario=current_scenario,
                steps=current_steps,
                tags=current_tags,
            ))
        return scenarios

    def parse_file(self, path: str) -> List[TestScenario]:
        with open(path, "r", encoding="utf-8") as f:
            return self.parse_text(f.read())
