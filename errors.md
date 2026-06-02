6/1

## on open
uvicorn app.main:app --reload --port 8200
INFO:     Will watch for changes in these directories: ['C:\\Users\\truth\\j8\\jax\\me\\x\\ebx\\earthbucks\\backend']
INFO:     Uvicorn running on http://127.0.0.1:8200 (Press CTRL+C to quit)
INFO:     Started reloader process [36592] using WatchFiles
INFO:     Started server process [38892]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     127.0.0.1:58604 - "GET /causes HTTP/1.1" 200 OK
INFO:     127.0.0.1:58604 - "GET /initiatives HTTP/1.1" 200 OK
INFO:     127.0.0.1:58604 - "GET /organizations HTTP/1.1" 200 OK
INFO:     127.0.0.1:51342 - "GET /auth/me HTTP/1.1" 500 Internal Server Error
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\uvicorn\protocols\http\httptools_impl.py", line 421, in run_asgi
    result = await app(  # type: ignore[func-returns-value]
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\uvicorn\middleware\proxy_headers.py", line 56, in __call__
    return await self.app(scope, receive, send)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\fastapi\applications.py", line 1159, in __call__
    await super().__call__(scope, receive, send)
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\starlette\applications.py", line 90, in __call__
    await self.middleware_stack(scope, receive, send)
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\starlette\middleware\errors.py", line 186, in __call__
    raise exc
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\starlette\middleware\errors.py", line 164, in __call__
    await self.app(scope, receive, _send)
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\starlette\middleware\cors.py", line 88, in __call__
    await self.app(scope, receive, send)
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\starlette\middleware\exceptions.py", line 63, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\fastapi\middleware\asyncexitstack.py", line 18, in __call__
    await self.app(scope, receive, send)
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\starlette\routing.py", line 660, in __call__
    await self.middleware_stack(scope, receive, send)
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\starlette\routing.py", line 680, in app
    await route.handle(scope, receive, send)
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\starlette\routing.py", line 276, in handle
    await self.app(scope, receive, send)
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\fastapi\routing.py", line 134, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\fastapi\routing.py", line 120, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\fastapi\routing.py", line 695, in app
    content = await serialize_response(
              ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\fastapi\routing.py", line 300, in serialize_response
    raise ResponseValidationError(
fastapi.exceptions.ResponseValidationError: 1 validation error:
  {'type': 'list_type', 'loc': ('response', 'watched_initiative_ids'), 'msg': 'Input should be a valid list', 'input': None}

  File "C:\Users\truth\j8\jax\me\x\ebx\earthbucks\backend\app\routers\auth.py", line 45, in me
    GET /auth/me
INFO:     127.0.0.1:58604 - "GET /posts?limit=50 HTTP/1.1" 200 OK
INFO:     127.0.0.1:58604 - "GET /auth/me HTTP/1.1" 500 Internal Server Error
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\uvicorn\protocols\http\httptools_impl.py", line 421, in run_asgi
    result = await app(  # type: ignore[func-returns-value]
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\uvicorn\middleware\proxy_headers.py", line 56, in __call__
    return await self.app(scope, receive, send)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\fastapi\applications.py", line 1159, in __call__
    await super().__call__(scope, receive, send)
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\starlette\applications.py", line 90, in __call__
    await self.middleware_stack(scope, receive, send)
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\starlette\middleware\errors.py", line 186, in __call__
    raise exc
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\starlette\middleware\errors.py", line 164, in __call__
    await self.app(scope, receive, _send)
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\starlette\middleware\cors.py", line 88, in __call__
    await self.app(scope, receive, send)
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\starlette\middleware\exceptions.py", line 63, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\fastapi\middleware\asyncexitstack.py", line 18, in __call__
    await self.app(scope, receive, send)
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\starlette\routing.py", line 660, in __call__
    await self.middleware_stack(scope, receive, send)
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\starlette\routing.py", line 680, in app
    await route.handle(scope, receive, send)
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\starlette\routing.py", line 276, in handle
    await self.app(scope, receive, send)
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\fastapi\routing.py", line 134, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\fastapi\routing.py", line 120, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\fastapi\routing.py", line 695, in app
    content = await serialize_response(
              ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\truth\AppData\Local\Programs\Python\Python311\Lib\site-packages\fastapi\routing.py", line 300, in serialize_response
    raise ResponseValidationError(
fastapi.exceptions.ResponseValidationError: 1 validation error:
  {'type': 'list_type', 'loc': ('response', 'watched_initiative_ids'), 'msg': 'Input should be a valid list', 'input': None}

  File "C:\Users\truth\j8\jax\me\x\ebx\earthbucks\backend\app\routers\auth.py", line 45, in me
    GET /auth/me
## 