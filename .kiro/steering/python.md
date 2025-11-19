---
inclusion: always
---

# Python Style and Design Guide

## Code Formatting

### Line Length
- **Maximum 120 characters** per line (PEP 8 extended)
- Break long lines at logical points (after commas, operators)
- Use parentheses for implicit line continuation

### Imports
```python
# Standard library imports first
import os
import sys
from dataclasses import dataclass
from typing import Optional, Callable
from collections.abc import Sequence

# Relative imports for internal modules
from .utils import Helper
from .core import Base
```

### String Formatting
- Use **f-strings** for all string interpolation
    - f-strings should use single quotes
- Avoid `.format()` and old-style `%` formatting
- ALWAYS use single quotes instead of double quotes (excluding docstrings)

```python
msg = f'Processing {item} completed in {time:.2f}s'
output = f'{timestamp} - {user} - {status} - {message}'
```

## Naming Conventions

### Classes
- **PascalCase**: `Manager`, `Handler`, `Processor`
- Short, clear names

### Functions and Methods
- **snake_case**: `run()`, `parse()`, `get_size()`
- Brief verb-based names

### Variables and Parameters
- **snake_case**: `max_size`, `start_time`, `data`
- Short names, use abbreviations

### Constants
- **UPPER_SNAKE_CASE**: `MAX_SIZE`, `DEFAULT_PORT`
- Module-level constants at the top

### Private Members
- **Single underscore prefix**: `_size`, `_lock`, `_parse()`
- Double underscore for name mangling only when necessary

## Type Hints

### Function Signatures
```python
def process(
    data: list | None = None,
    *,
    validate: bool = False,
    filters: set[str] | list[str] | tuple[str, ...] | None = None,
    strict: bool = False
) -> dict | list[dict]:
    """Process data with validation."""
```

### Class Attributes
```python
class Handler:
    _max_size: int = 0
    _lock: threading.Lock = threading.Lock()
```

### Advanced Type Hints
```python
from typing import TypeVar, Generic, Protocol, Callable, Any, TypeAlias
from collections.abc import Iterable, Mapping, Sequence

# Generic types
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

class Cache(Generic[K, V]):
    def get(self, key: K) -> V | None: ...
    def set(self, key: K, value: V) -> None: ...

# Protocol for structural typing
class Processor(Protocol):
    def process(self, data: Any) -> str: ...

# Type aliases for complex types
JsonData: TypeAlias = dict[str, Any]
Handler: TypeAlias = Callable[[str], bool]
Config: TypeAlias = Mapping[str, str | int | bool]

# Function with generic constraints
def transform[T](items: Iterable[T], func: Callable[[T], str]) -> list[str]:
    return [func(item) for item in items]

# Overloaded functions
from typing import overload

@overload
def get_data(key: str) -> str: ...

@overload
def get_data(key: str, default: T) -> str | T: ...

def get_data(key: str, default: Any = None) -> Any:
    return storage.get(key, default)
```

### Return Types
- Always specify return types for public methods
- Use `None` explicitly when functions don't return values
- Use `|` for union types instead of `Union`
- Use built-in types (`list`, `dict`, `set`) instead of typing equivalents

## Documentation

### Google-Style Docstrings
```python
def process(data=None, *, validate=False, filters=None, strict=False):
    """Process data with optional validation and filtering.
    
    Args:
        data: Input data to process.
        validate: Enable validation checks.
        filters: Components to filter or specific field names.
        strict: Enable strict processing mode.
        
    Returns:
        Processed data or processing function.
        
    Example:
        @process
        def transform():
            return {'result': 'data'}
            
        @process(validate=True, filters=['name'])
        def clean(a, b):
            return a + b
    """
```

### Module Docstrings
```python
"""Brief module description.

Longer description if needed.
"""
```

### Class Docstrings
```python
class Manager:
    """Data manager with advanced features."""
```

### Method Docstrings
```python
def parse(self, data):
    """Parse input data with formatting."""
```

## Error Handling

### Minimal Error Handling
```python
def process(data):
    if not data:
        raise ValueError('Data required')
    return transform(data)
```

### Use Built-in Exceptions
- Prefer `ValueError`, `TypeError`, `KeyError` over custom exceptions
- Only handle errors that can be meaningfully recovered from

## Advanced Python Techniques

### Comprehensions and Generators
```python
# List comprehensions
items: list[str] = [transform(x) for x in data if x.valid]

# Dict comprehensions
mapping: dict[str, Any] = {k: process(v) for k, v in items.items()}

# Generator expressions
total: int = sum(x.value for x in items)

# Generator functions
def stream_data() -> Generator[Any, None, None]:
    """Stream processed data items."""
    for item in large_dataset:
        yield process(item)

# Generator with send/throw
def coroutine() -> Generator[None, Any, None]:
    """Coroutine for processing values."""
    while True:
        value = yield
        result = process(value)
```

### Advanced Data Structures
```python
from collections import defaultdict, deque, Counter, namedtuple, ChainMap
from collections.abc import MutableMapping, Iterator
from typing import Any

# Efficient collections
cache: defaultdict[str, list[Any]] = defaultdict(list)
queue: deque[str] = deque(maxlen=100)
counts: Counter[str] = Counter(items)
Point = namedtuple('Point', ['x', 'y'])
config: ChainMap[str, Any] = ChainMap(local_config, global_config)

# Custom mapping
class Registry(MutableMapping[str, Any]):
    """Custom registry for storing key-value pairs."""
    
    def __init__(self) -> None:
        self._data: dict[str, Any] = {}
    
    def __getitem__(self, key: str) -> Any:
        return self._data[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value
    
    def __delitem__(self, key: str) -> None:
        del self._data[key]
    
    def __iter__(self) -> Iterator[str]:
        return iter(self._data)
    
    def __len__(self) -> int:
        return len(self._data)
```

### Metaclasses and Duck Typing
```python
from typing import Protocol, Any, type_check_only

# Metaclass for automatic registration
class Registry(type):
    """Metaclass for automatic class registration."""
    _registry: dict[str, type] = {}
    
    def __new__(cls, name: str, bases: tuple[type, ...], attrs: dict[str, Any]) -> type:
        new_cls = super().__new__(cls, name, bases, attrs)
        cls._registry[name] = new_cls
        return new_cls

class Handler(metaclass=Registry):
    """Base handler class."""

# Duck typing with protocols
@type_check_only
class Drawable(Protocol):
    """Protocol for drawable objects."""
    def draw(self) -> None: ...

def render(obj: Drawable) -> None:
    """Render any drawable object."""
    obj.draw()
```

### Functools Advanced Usage
```python
import functools
from typing import Any, Callable

# Caching and memoization
@functools.lru_cache(maxsize=128)
def expensive_func(n: int) -> int:
    """Expensive calculation with caching."""
    return complex_calculation(n)

# Partial application
process_csv: Callable[[str], dict[str, Any]] = functools.partial(process_file, format='csv')

# Single dispatch for polymorphism
@functools.singledispatch
def process(data: Any) -> Any:
    """Process data based on type."""
    raise NotImplementedError

@process.register
def _(data: str) -> str:
    return data.upper()

@process.register
def _(data: list[Any]) -> list[Any]:
    return [process(item) for item in data]

# Reduce for complex operations
result: int = functools.reduce(lambda acc, x: acc + x.value, items, 0)
```

### Properties and Descriptors
```python
from typing import Any

# Property with validation
class Config:
    """Configuration with validated properties."""
    
    def __init__(self) -> None:
        self._size: int = 0
    
    @property
    def size(self) -> int:
        return self._size
    
    @size.setter
    def size(self, value: int) -> None:
        if value < 0:
            raise ValueError('Size must be positive')
        self._size = value

# Custom descriptor
class Validator:
    """Descriptor for value validation."""
    
    def __init__(self, min_val: int | None = None, max_val: int | None = None) -> None:
        self.min_val = min_val
        self.max_val = max_val
        self.name = ''
    
    def __set_name__(self, owner: type, name: str) -> None:
        self.name = f'_{name}'
    
    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        if obj is None:
            return self
        return getattr(obj, self.name)
    
    def __set__(self, obj: Any, value: int) -> None:
        if self.min_val is not None and value < self.min_val:
            raise ValueError(f'Value must be >= {self.min_val}')
        if self.max_val is not None and value > self.max_val:
            raise ValueError(f'Value must be <= {self.max_val}')
        setattr(obj, self.name, value)

class Item:
    """Item with validated size."""
    size = Validator(min_val=0, max_val=100)
```

### Multiprocessing and Thread Pools
```python
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed, Future
from typing import Any

# Process pool for CPU-bound tasks
def cpu_task(data: Any) -> Any:
    """CPU-intensive task for process pool."""
    return heavy_computation(data)

with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
    futures: list[Future[Any]] = [executor.submit(cpu_task, item) for item in data]
    results: list[Any] = [f.result() for f in as_completed(futures)]

# Thread pool for I/O-bound tasks
def io_task(url: str) -> dict[str, Any]:
    """I/O-bound task for thread pool."""
    return fetch_data(url)

with ThreadPoolExecutor(max_workers=10) as executor:
    futures: dict[Future[dict[str, Any]], str] = {executor.submit(io_task, url): url for url in urls}
    for future in as_completed(futures):
        url: str = futures[future]
        result: dict[str, Any] = future.result()

# Multiprocessing with shared state
def worker(shared_dict: dict[str, Any], lock: mp.Lock, data: Any) -> None:
    """Worker function with shared state."""
    with lock:
        shared_dict[data.id] = process(data)

manager: mp.Manager = mp.Manager()
shared_dict: dict[str, Any] = manager.dict()
lock: mp.Lock = manager.Lock()

processes: list[mp.Process] = []
for chunk in data_chunks:
    p = mp.Process(target=worker, args=(shared_dict, lock, chunk))
    processes.append(p)
    p.start()

for p in processes:
    p.join()
```

### Context Managers
```python
from contextlib import contextmanager, ExitStack
from typing import Any, Generator
import threading

# Custom context manager
class Resource:
    """Resource with automatic cleanup."""
    
    def __init__(self) -> None:
        self._lock = threading.Lock()
    
    def __enter__(self) -> 'Resource':
        self._lock.acquire()
        return self
        
    def __exit__(self, exc_type: type | None, exc_val: Exception | None, exc_tb: Any) -> bool:
        self._lock.release()
        return False

# Generator-based context manager
@contextmanager
def temp_config(new_config: dict[str, Any]) -> Generator[dict[str, Any], None, None]:
    """Temporarily change configuration."""
    old_config: dict[str, Any] = get_config()
    set_config(new_config)
    try:
        yield new_config
    finally:
        set_config(old_config)

# Managing multiple resources
with ExitStack() as stack:
    files: list[Any] = [stack.enter_context(open(f)) for f in filenames]
    process_files(files)
```

### Dataclasses and Slots
```python
from dataclasses import dataclass, field
from typing import Any

@dataclass(slots=True, frozen=True)
class Config:
    """Immutable configuration with slots."""
    validate: bool = False
    filters: set[str] = field(default_factory=set)
    
    def __post_init__(self) -> None:
        if not self.filters:
            object.__setattr__(self, 'filters', {'default'})

# Slots for memory efficiency
class Point:
    """Point with memory-efficient slots."""
    __slots__ = ('x', 'y', '__weakref__')
    
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
```

## Class Design

### Method Organization
```python
class Manager:
    def __init__(self, name: str):
        """Initialize manager."""
        
    def run(self, data: str):
        """Process data."""
        
    def _parse(self, data: str) -> str:
        """Parse input data."""
```

### Use Properties and Descriptors
```python
class Config:
    @property
    def enabled(self) -> bool:
        return self._enabled
        
    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = value
```

## Threading and Concurrency

### Thread Safety
```python
class Handler:
    _lock = threading.Lock()
    
    def process(self, data):
        with self._lock:
            self._update_size(len(data.content))
```

### Use Context Managers for Resources
```python
with self._lock:
    self._shared_state += 1
```

## Performance Optimization

### Use Built-in Functions
```python
# Efficient operations
result = ''.join(parts)
items = list(filter(predicate, data))
total = sum(values)
```

### Lazy Evaluation
```python
def process(items):
    return (transform(x) for x in items if x.valid)
```

### Slots for Memory Efficiency
```python
class Point:
    __slots__ = ('x', 'y')
```

## Code Organization

### Module Structure
- Single responsibility per module
- Use `__all__` for public API
- Minimal imports

### Function Design
- Single expression when possible
- Use lambda for simple operations
- Prefer built-ins over custom implementations

### Class Hierarchy
- Composition over inheritance
- Minimal interfaces
- Use mixins sparingly