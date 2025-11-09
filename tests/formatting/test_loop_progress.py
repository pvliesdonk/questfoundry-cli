"""Tests for loop iteration progress tracking."""

from datetime import datetime, timedelta
from time import sleep

from qf.formatting.loop_progress import Iteration, LoopProgressTracker, Step


class TestStep:
    """Tests for Step class."""

    def test_step_creation(self) -> None:
        """Test creating a step."""
        step = Step(name="Context Init", agent="Lore Weaver")

        assert step.name == "Context Init"
        assert step.agent == "Lore Weaver"
        assert not step.is_revision
        assert not step.blocked
        assert step.status == "pending"

    def test_step_completed_status(self) -> None:
        """Test step completion tracking."""
        step = Step(name="Test Step", agent="Agent")
        step.start_time = datetime.now()
        step.end_time = step.start_time + timedelta(seconds=1)

        assert step.status == "completed"
        assert step.duration == 1.0

    def test_step_blocked_status(self) -> None:
        """Test step blocking tracking."""
        step = Step(name="Test Step", agent="Agent")
        step.blocked = True
        step.blocking_issues = ["Issue 1", "Issue 2"]

        assert step.status == "blocked"
        assert len(step.blocking_issues) == 2


class TestIteration:
    """Tests for Iteration class."""

    def test_iteration_creation(self) -> None:
        """Test creating an iteration."""
        iteration = Iteration(iteration_number=1)

        assert iteration.iteration_number == 1
        assert len(iteration.steps) == 0
        assert not iteration.stabilized

    def test_iteration_step_counts(self) -> None:
        """Test step counting in iteration."""
        iteration = Iteration(iteration_number=1)

        # Create step1 with 1 second duration
        now = datetime.now()
        step1 = Step(name="Step 1", agent="Agent", is_revision=False)
        step1.start_time = now
        step1.end_time = now + timedelta(seconds=1)

        # Create step2 with 1 second duration
        now2 = datetime.now()
        step2 = Step(name="Step 2", agent="Agent", is_revision=True)
        step2.start_time = now2
        step2.end_time = now2 + timedelta(seconds=1)

        # Create step3 as blocked (no end time)
        step3 = Step(name="Step 3", agent="Agent", is_revision=False)
        step3.blocked = True

        iteration.steps = [step1, step2, step3]

        # Both step1 and step2 have end_time, so both are completed
        assert iteration.completed_steps == 2
        assert iteration.blocked_steps == 1
        # Only step2 is marked as revision
        assert iteration.revised_steps == 1
        # step1 and step3 are not revisions (first-pass steps)
        assert iteration.first_pass_steps == 2


class TestLoopProgressTracker:
    """Tests for LoopProgressTracker class."""

    def test_tracker_creation(self) -> None:
        """Test creating a progress tracker."""
        tracker = LoopProgressTracker(loop_name="Story Spark")

        assert tracker.loop_name == "Story Spark"
        assert len(tracker.iterations) == 0
        assert not tracker.is_multi_iteration

    def test_single_iteration_execution(self) -> None:
        """Test tracking a single-iteration loop."""
        tracker = LoopProgressTracker(loop_name="Hook Harvest")
        tracker.start_loop()

        iteration = tracker.start_iteration(1)
        assert iteration.iteration_number == 1

        step1 = tracker.start_step("Analysis", "Lore Weaver")
        sleep(0.01)  # Simulate work
        tracker.complete_step(step1)

        tracker.mark_stabilized()
        tracker.complete_iteration()

        assert tracker.stabilized
        assert not tracker.is_multi_iteration
        assert tracker.total_duration > 0

    def test_multi_iteration_execution(self) -> None:
        """Test tracking a multi-iteration loop with revisions."""
        tracker = LoopProgressTracker(loop_name="Story Spark")
        tracker.start_loop()

        # Iteration 1
        tracker.start_iteration(1)
        step1_iter1 = tracker.start_step("Step 1", "Agent A")
        tracker.complete_step(step1_iter1)

        step2_iter1 = tracker.start_step("Step 2", "Agent B")
        tracker.complete_step(step2_iter1)

        step3_iter1 = tracker.start_step("Step 3", "Agent C")
        tracker.block_step(step3_iter1, ["Quality issue found"])

        tracker.complete_iteration()
        tracker.record_showrunner_decision("Revising steps 1-2")

        # Iteration 2
        tracker.start_iteration(2)
        step1_iter2 = tracker.start_step(
            "Step 1 (revised)", "Agent A", is_revision=True
        )
        tracker.complete_step(step1_iter2)

        step2_iter2 = tracker.start_step(
            "Step 2 (revised)", "Agent B", is_revision=True
        )
        tracker.complete_step(step2_iter2)

        step3_iter2 = tracker.start_step("Step 3", "Agent C")
        tracker.complete_step(step3_iter2)

        tracker.mark_stabilized()
        tracker.complete_iteration()

        assert tracker.is_multi_iteration
        assert len(tracker.iterations) == 2
        assert tracker.stabilized
        assert tracker.iterations[0].blocked_steps == 1
        assert tracker.iterations[1].revised_steps == 2

    def test_showrunner_decision_recording(self) -> None:
        """Test recording Showrunner decisions."""
        tracker = LoopProgressTracker(loop_name="Lore Deepening")
        tracker.start_loop()

        iter1 = tracker.start_iteration(1)
        assert iter1.showrunner_decision is None

        decision = "Revising topology analysis based on inconsistency"
        tracker.record_showrunner_decision(decision)

        assert iter1.showrunner_decision == decision

    def test_get_summary(self) -> None:
        """Test getting execution summary."""
        tracker = LoopProgressTracker(loop_name="Story Spark")
        tracker.start_loop()

        tracker.start_iteration(1)
        step = tracker.start_step("Test", "Agent")
        tracker.complete_step(step)
        tracker.mark_stabilized()
        tracker.complete_iteration()

        summary = tracker.get_summary()

        assert summary["loop_name"] == "Story Spark"
        assert summary["iteration_count"] == 1
        assert summary["total_steps"] == 1
        assert summary["stabilized"]
        assert not summary["is_multi_iteration"]

    def test_efficiency_metrics(self) -> None:
        """Test efficiency calculation for multi-iteration loops."""
        tracker = LoopProgressTracker(loop_name="Hook Harvest")
        tracker.start_loop()

        # Iteration 1: 3 steps
        tracker.start_iteration(1)
        for i in range(3):
            step = tracker.start_step(f"Step {i+1}", "Agent")
            tracker.complete_step(step)
        tracker.complete_iteration()

        # Iteration 2: 1 revised + 2 reused
        tracker.start_iteration(2)
        revised = tracker.start_step(
            "Step 1 (revised)", "Agent", is_revision=True
        )
        tracker.complete_step(revised)
        for i in range(1, 3):
            step = tracker.start_step(f"Step {i+1} (reused)", "Agent")
            tracker.complete_step(step)
        tracker.mark_stabilized()
        tracker.complete_iteration()

        summary = tracker.get_summary()

        assert summary["is_multi_iteration"]
        assert summary["iteration_count"] == 2
        # Total: 3 (iter1) + 3 (iter2) = 6 steps
        assert summary["total_steps"] == 6
        # Revised in iteration 2: 1
        assert summary["iterations"][1]["revised_steps"] == 1
