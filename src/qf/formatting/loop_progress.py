"""Iteration-aware progress tracking for loop execution.

Supports multi-iteration loops where steps can be revised after quality
gates or other blocking points. Tracks which iterations steps execute
in and whether they are first-pass or revision executions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Step:
    """Represents a single step execution within an iteration."""

    name: str
    agent: str
    is_revision: bool = False
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    blocked: bool = False
    blocking_issues: list[str] = field(default_factory=list)

    @property
    def duration(self) -> float:
        """Duration in seconds, or 0 if not completed."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    @property
    def status(self) -> str:
        """Step status: completed, running, or blocked."""
        if self.blocked:
            return "blocked"
        if self.end_time:
            return "completed"
        if self.start_time:
            return "running"
        return "pending"


@dataclass
class Iteration:
    """Represents a single iteration of a loop."""

    iteration_number: int
    steps: list[Step] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    stabilized: bool = False
    showrunner_decision: Optional[str] = None

    @property
    def duration(self) -> float:
        """Duration in seconds, or 0 if not completed."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    @property
    def completed_steps(self) -> int:
        """Count of completed steps."""
        return sum(1 for s in self.steps if s.status == "completed")

    @property
    def blocked_steps(self) -> int:
        """Count of blocked steps."""
        return sum(1 for s in self.steps if s.status == "blocked")

    @property
    def revised_steps(self) -> int:
        """Count of revision steps in this iteration."""
        return sum(1 for s in self.steps if s.is_revision)

    @property
    def first_pass_steps(self) -> int:
        """Count of first-pass steps in this iteration."""
        return sum(1 for s in self.steps if not s.is_revision)


@dataclass
class LoopProgressTracker:
    """Tracks multi-iteration loop execution with step-level detail.

    Supports:
    - Multiple iterations with revision cycles
    - Step-level status (running, completed, blocked)
    - First-pass vs revision step distinction
    - Showrunner decision recording
    - Loop stabilization tracking
    """

    loop_name: str
    iterations: list[Iteration] = field(default_factory=list)
    start_time: Optional[datetime] = None
    current_iteration: Optional[Iteration] = None

    def start_loop(self) -> None:
        """Record loop start time."""
        self.start_time = datetime.now()

    def start_iteration(self, iteration_number: int) -> Iteration:
        """Begin a new iteration.

        Args:
            iteration_number: Sequential iteration number (1, 2, 3, ...)

        Returns:
            New Iteration object for this iteration
        """
        iteration = Iteration(
            iteration_number=iteration_number, start_time=datetime.now()
        )
        self.iterations.append(iteration)
        self.current_iteration = iteration
        return iteration

    def start_step(
        self, step_name: str, agent: str, is_revision: bool = False
    ) -> Step:
        """Start executing a step.

        Args:
            step_name: Name of the step
            agent: Agent executing this step
            is_revision: True if this is a revision of a previous step

        Returns:
            Step object for tracking this step's execution
        """
        if not self.current_iteration:
            raise RuntimeError("No active iteration. Call start_iteration first.")

        step = Step(
            name=step_name, agent=agent, is_revision=is_revision, start_time=datetime.now()
        )
        self.current_iteration.steps.append(step)
        return step

    def complete_step(self, step: Step) -> None:
        """Mark a step as completed.

        Args:
            step: Step object to complete
        """
        step.end_time = datetime.now()

    def block_step(self, step: Step, issues: list[str]) -> None:
        """Mark a step as blocked with specific issues.

        Args:
            step: Step object to block
            issues: List of issue descriptions causing the block
        """
        step.blocked = True
        step.blocking_issues = issues
        step.end_time = datetime.now()

    def record_showrunner_decision(self, decision: str) -> None:
        """Record Showrunner's decision for current iteration.

        Args:
            decision: Description of the Showrunner's decision
        """
        if self.current_iteration:
            self.current_iteration.showrunner_decision = decision

    def complete_iteration(self) -> None:
        """Mark current iteration as complete."""
        if self.current_iteration:
            self.current_iteration.end_time = datetime.now()

    def mark_stabilized(self) -> None:
        """Mark the current iteration as achieving stability."""
        if self.current_iteration:
            self.current_iteration.stabilized = True
            self.current_iteration.end_time = datetime.now()

    @property
    def total_duration(self) -> float:
        """Total duration from loop start to now."""
        if self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return 0.0

    @property
    def is_multi_iteration(self) -> bool:
        """True if loop has more than one iteration."""
        return len(self.iterations) > 1

    @property
    def stabilized(self) -> bool:
        """True if loop has achieved stability."""
        if self.current_iteration:
            return self.current_iteration.stabilized
        return False

    def get_summary(self) -> dict:
        """Get summary statistics about loop execution.

        Returns:
            Dictionary with iteration counts, step statistics, etc.
        """
        return {
            "loop_name": self.loop_name,
            "iteration_count": len(self.iterations),
            "total_steps": sum(len(i.steps) for i in self.iterations),
            "total_duration": self.total_duration,
            "is_multi_iteration": self.is_multi_iteration,
            "stabilized": self.stabilized,
            "iterations": [
                {
                    "number": i.iteration_number,
                    "completed_steps": i.completed_steps,
                    "blocked_steps": i.blocked_steps,
                    "revised_steps": i.revised_steps,
                    "first_pass_steps": i.first_pass_steps,
                    "duration": i.duration,
                    "stabilized": i.stabilized,
                    "showrunner_decision": i.showrunner_decision,
                }
                for i in self.iterations
            ],
        }
