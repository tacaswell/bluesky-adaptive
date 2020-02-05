from bluesky_adaptive.runners import generator

import operator
from functools import reduce
import bluesky.preprocessors as bpp
import bluesky.plan_stubs as bps
import itertools


def learner_plan(dets, motors, learner, goal, *, md=None):

    dependent_keys = tuple(reduce(operator.add, (d.hints["fields"] for d in dets), []))
    dimensions = [(motor.hints["fields"], "primary") for motor in motors]
    independent_keys = [d for ((d,), s) in dimensions]
    _md = {"hints": {}}
    _md.update(md or {})
    _md["hints"].setdefault("dimensions", dimensions)

    @bpp.stage_decorator(dets + motors)
    @bpp.run_decorator(md=_md)
    def inner():

        gen = generator(learner, goal)
        # have to "prime the pump"
        xy = None
        while True:
            try:
                x = gen.send(xy)
            except StopIteration:
                break
            yield from bps.mov(*itertools.chain(*zip(motors, x)))
            ret = yield from bps.trigger_and_read(dets + motors)

            # handle simulated case
            if ret:
                y = tuple(ret[k]["value"] for k in dependent_keys)
                x = tuple(ret[k]["value"] for k in independent_keys)
            else:
                y = tuple(x[:1]) * len(dependent_keys)
                x = x

            xy = (x, y)

    return (yield from inner())
