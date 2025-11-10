from collections import deque

class LinkQueue:
    """
    Simple FIFO queue with 'seen' guard handled externally.
    """

    def __init__(self):
        self._dq = deque()

    def push(self, url: str) -> None:
        if url:
            self._dq.append(url)

    def pop(self) -> str:
        return self._dq.popleft()

    def empty(self) -> bool:
        return len(self._dq) == 0

    def __len__(self) -> int:
        return len(self._dq)