# Shamelessly copy/pasted from this awesome article :
# https://www.toptal.com/javascript/option-maybe-either-future-monads-js*
# by Alexey Karasev

from functools import reduce
import threading

class Monad:
  # pure :: a -> M a. Same as unit: a -> M a
  @staticmethod
  def pure(x):
    raise Exception("pure method needs to be implemented")
  
  # flat_map :: # M a -> (a -> M b) -> M b
  def flat_map(self, f):
    raise Exception("flat_map method needs to be implemented")

  # map :: # M a -> (a -> b) -> M b
  def map(self, f):
    return self.flat_map(lambda x: self.pure(f(x)))

class Option(Monad):
  # pure :: a -> Option a
  @staticmethod
  def pure(x):
    return Some(x)

  # flat_map :: # Option a -> (a -> Option b) -> Option b
  def flat_map(self, f):
    if self.defined:
      return f(self.value)
    else:
      return nil

class Some(Option):
  def __init__(self, value):
    self.value = value
    self.defined = True

class Nil(Option):
  def __init__(self):
    self.value = None
    self.defined = False

nil = Nil()

class Either(Monad):
  # pure :: a -> Either a
  @staticmethod
  def pure(value):
    return Right(value)

  # flat_map :: # Either a -> (a -> Either b) -> Either b
  def flat_map(self, f):
    if self.is_left:
      return self
    else:
      return f(self.value)

class Left(Either):
  def __init__(self, value):
    self.value = value
    self.is_left = True

class Right(Either):
  def __init__(self, value):
    self.value = value
    self.is_left = False

class Future(Monad):
  # __init__ :: ((Either err a -> void) -> void) -> Future (Either err a)
  def __init__(self, f):
    self.subscribers = []
    self.cache = nil
    self.semaphore = threading.BoundedSemaphore(1)
    f(self.callback)

  # pure :: a -> Future a
  @staticmethod
  def pure(value):
    return Future(lambda cb: cb(Either.pure(value)))

  def exec(f, cb):
    try:
      data = f()
      cb(Right(data))
    except Exception as err:
      cb(Left(err))

  def exec_on_thread(f, cb):
    t = threading.Thread(target=Future.exec, args=[f, cb])
    t.start()

  def asyn(f):
    return Future(lambda cb: Future.exec_on_thread(f, cb))

  # flat_map :: (a -> Future b) -> Future b
  def flat_map(self, f):
    return Future(
      lambda cb: self.subscribe(
        lambda value: cb(value) if (value.is_left) else f(value.value).subscribe(cb)
      )
    )

  # traverse :: [a] -> (a -> Future b) -> Future [b]
  def traverse(arr):
    return lambda f: reduce(
      lambda acc, elem: acc.flat_map(
        lambda values: f(elem).map(
          lambda value: values + [value]
        )
      ), arr, Future.pure([]))

  # callback :: Either err a -> void
  def callback(self, value):
    self.semaphore.acquire()
    self.cache = Some(value)
    while (len(self.subscribers) > 0):
      sub = self.subscribers.pop(0)
      t = threading.Thread(target=sub, args=[value])
      t.start()
    self.semaphore.release()
  
  # subscribe :: (Either err a -> void) -> void
  def subscribe(self, subscriber):
    self.semaphore.acquire()
    if (self.cache.defined):
      self.semaphore.release()
      subscriber(self.cache.value)
    else:
      self.subscribers.append(subscriber)
      self.semaphore.release()