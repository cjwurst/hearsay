"""A wrapper for two functions -- do and undo -- which are inverses of each other."""
class Invertible:
    def __init__(self, do:callable, undo:callable):
        if do == None:
            pass
        self.do = do
        self.undo = undo

    @staticmethod
    def compose(*args):
        """Return a new invertible which is a composition of the argument invertibles."""
        def do_nothing():
            pass
        big_invertible = Invertible(do_nothing, do_nothing)
        for invertible in args:
            big_invertible = Invertible._compose_two(big_invertible, invertible)
        return big_invertible

    @property
    def inverse(self):
        return Invertible(self.undo, self.do)

    @staticmethod
    def _compose_two(l_invertible:'Invertible', r_invertible:'Invertible'):
        def do_do():
            l_invertible.do()
            r_invertible.do()
        def undo_undo():
            r_invertible.undo()
            l_invertible.undo()
        return Invertible(do_do, undo_undo)

"""An object which tracks the invertibles passed to it, enabling game state changes to be reversed."""
class InvertibleStack:
    def __init__(self):
        self._undo_stack = []
        self._redo_stack = []

    def push(self, invertible):
        self._redo_stack = []
        self._undo_stack.append(invertible)
        invertible.do()

    def try_undo(self) -> bool:
        """Return whether or not there was anything to undo."""
        if len(self._undo_stack) == 0:
            return False
        invertible = self._undo_stack.pop()
        invertible.undo()
        self._redo_stack.append(invertible)
        return True

    def try_redo(self) -> bool:
        """Return whether or not there was anything to redo."""
        if len(self._redo_stack) == 0:
            return False
        invertible = self._redo_stack.pop()
        invertible.do()
        return True