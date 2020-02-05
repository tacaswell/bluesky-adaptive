def generator(learner, goal=None):
    """Treat learner as an iterable.

    Iterates by asking the learner for a new point and yielding out
    the next point.

    The evaluated point needs to send back into the generator.

    This is used as ::

       gen = generator(learner, goal)
       y = None
       while True:
          try:
              x = gen.send(y)
          except StopIteration:
              break
          y = learner.function(x)


    By inverting the loop logic, it is easier to integrate existing
    external control loops.

    Parameters
    ----------
    learner : ~`adaptive.BaseLearner` instance
    goal : Callable[BaseLearner, Bool]
        The end condition for the calculation. This function must take the
        learner as its sole argument, and return True if we should stop.

    Yields
    ------
    x : value in domain of function

    Receives
    --------
    x : value in domain of function
       Where it was actually measured
    y : value in the image of the function
       Value where it was measured
    """
    if goal is None:

        def goal(learner):
            return learner.done()

    while not goal(learner):
        xs, _ = learner.ask(1)
        # ask is "up to n", might be empty list
        if not len(xs):
            break
        (x_out,) = xs
        (x_in, y) = yield x_out
        learner.tell(x_in, y)
