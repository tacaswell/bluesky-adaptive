from event_model import DocumentRouter
import operator
from functools import reduce


class AdaptiveCallback(DocumentRouter):
    def __init__(self, learner, goal, out_queue):
        self.learner = learner
        self.goal = goal

        self.out_queue = out_queue
        self._exogenous_keys = None
        self._endogenous_keys = None

    def start(self, doc):
        # TODO extract dimensions
        dimensions = doc["hints"]["dimensions"]
        self._endogenous_keys = [d for ((d,), s) in dimensions]
        print("in start", self._endogenous_keys)

        # send out the first request
        xs, _ = self.learner.ask(1)
        if not len(xs):
            self.out_queue.put(None)
        (x_out,) = xs
        print(f"putting {x_out} in start")
        self.out_queue.put(x_out)

    def descriptor(self, doc):
        # TODO make this configurable
        if doc["name"] != "primary":
            return
        hints = doc["hints"]
        # TODO handle things with more than 1 hint
        self._exogenous_keys = tuple(
            reduce(operator.add, (d["fields"] for d in hints.values()), [])
        )
        print(self._exogenous_keys)

    def event(self, doc):
        ret = doc["data"]
        y = tuple(ret[k] for k in self._exogenous_keys)
        x = tuple(ret[k] for k in self._endogenous_keys)

        self.learner.tell(x, y)

        if self.goal(self.learner):
            print("putting done!")
            self.out_queue.put(None)
            return

        xs, _ = self.learner.ask(1)
        if not len(xs):
            print("putting done!")
            self.out_queue.put(None)
            return

        (x_out,) = xs
        print(f"putting {x_out}!")
        self.out_queue.put(x_out)
