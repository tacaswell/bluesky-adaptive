from adaptive.learner.sequence_learner import SequenceLearner
from adaptive.learner.learner2D import Learner2D

from bluesky_adaptive.plans import learner_plan


class LearnerForTesting(SequenceLearner):
    def ask(self, n, tell_pending=True):
        pts, loss = super().ask(n, tell_pending)
        return [pt[1] for pt in pts], loss


def test_sequence_smoke(RE, hw):
    RE(
        learner_plan(
            [hw.det, hw.det1],
            [hw.motor, hw.motor1],
            LearnerForTesting(None, [[1, 1], [2, 2], [3, 3]]),
            lambda x: x.done(),
        )
    )


def test_learner2D_smoke(RE, hw):
    hw.det4.kind = 'hinted'
    RE(
        learner_plan(
            [hw.det4],
            [hw.motor1, hw.motor2],
            Learner2D(None, [(-5.0, 5.0), (-3.0, 3.0)]),
            lambda x: x.npoints >= 50,
        )
    )
