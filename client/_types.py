from typing import Callable, Coroutine, Any

coroutine = Coroutine[Any, Any, Any]
coroutineFunction = Callable[..., coroutine]
