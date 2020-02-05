from adaptive.learner.sequence_learner import SequenceLearner
from adaptive.learner.learner2D import Learner2D
import pytest
from bluesky_adaptive.plans import learner_plan, learner_callback_plan


class LearnerForTesting(SequenceLearner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._index_map = {}

    def ask(self, n, tell_pending=True):
        pts, loss = super().ask(n, tell_pending)
        self._index_map.update({tuple(pt[1]): pt[0] for pt in pts})

        return [pt[1] for pt in pts], loss

    def tell(self, x, y):
        x = [self._index_map.pop(tuple(x)), x]
        super().tell(x, y)


@pytest.mark.parametrize("plan", [learner_plan, learner_callback_plan])
def test_sequence_smoke(RE, hw, plan):
    RE(
        plan(
            [hw.det, hw.det1],
            [hw.motor, hw.motor1],
            LearnerForTesting(None, [[1, 1], [2.2, 2], [3, 3], [4, 4]]),
            lambda x: x.done(),
        )
    )


@pytest.mark.parametrize("plan", [learner_plan, learner_callback_plan])
def test_learner2D_smoke(RE, hw, plan):
    hw.det4.kind = "hinted"
    RE(
        plan(
            [hw.det4],
            [hw.motor1, hw.motor2],
            Learner2D(None, [(-5.0, 5.0), (-3.0, 3.0)]),
            lambda x: x.npoints >= 50,
        )
    )
