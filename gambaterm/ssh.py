
import os
import asyncio
import argparse
import traceback
from pathlib import Path

import asyncssh

from .run import run
from .xinput import gb_input_context

message = """\
Please enable X11 forwarding using `-X` option.\r
"""

CSI = b"\033["


class SSHSession(asyncssh.SSHServerSession):

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def connection_made(self, chan):
        self._read_stdin_pipe, self._write_stdin_pipe = os.pipe()
        self._read_stdout_pipe, self._write_stdout_pipe = os.pipe()
        self._stdin = os.fdopen(self._read_stdin_pipe, "rb", buffering=0)
        self._stdout = os.fdopen(self._write_stdout_pipe, "wb", buffering=0)
        self._channel = chan
        self._size = 10, 10

    def close_all_pipes(self):
        for pipe in (
            self._read_stdin_pipe, self._write_stdin_pipe,
            self._read_stdout_pipe, self._write_stdout_pipe
        ):
            try:
                os.close(pipe)
            except OSError:
                pass

    def shell_requested(self) -> bool:
        return True

    def session_started(self) -> None:
        asyncio.get_event_loop().create_task(self.safe_interact())

    async def safe_interact(self) -> None:
        try:
            await self.interact()
        except BaseException:
            traceback.print_exc()
        finally:
            self.close_all_pipes()
            self._channel.close()

    async def interact(self):
        display = self._channel.get_x11_display()

        # X11 is required
        if not display:
            self._channel.write(message.encode())
            return

        def _data_received():
            try:
                data = os.read(self._read_stdout_pipe, 2*1024*1024)
            except OSError:
                return
            self._channel.write(data)

        loop = asyncio.get_event_loop()
        try:
            width, height, _, _ = self._channel.get_terminal_size()
            self._size = width, height
            self._channel.write(b"\033[?25l")
            loop.add_reader(self._read_stdout_pipe, _data_received)
            await loop.run_in_executor(None, self.thread_target, display)
        except OSError:
            self._channel.write(CSI + b"0m" + CSI + b"2J" + b"\r\n")
        finally:
            loop.remove_reader(self._read_stdout_pipe)
            self._channel.write(b"\033[?25h")

    def thread_target(self, display):
        with gb_input_context(display=display) as get_gb_input:
            run(
                self.kwargs["romfile"],
                get_gb_input,
                stdin=self._stdin,
                stdout=self._stdout,
                get_size=lambda: self._size,
                test=self.kwargs["test"],
                fast=self.kwargs["fast"],
            )

    def terminal_size_changed(self, width, height, pixwidth, pixheight):
        self._size = width, height

    def data_received(self, data, datatype):
        if b"\x03" in data or b"\x04" in data:
            self.close_all_pipes()
        try:
            os.write(self._write_stdin_pipe, data)
        except OSError:
            pass


class SSHServer(asyncssh.SSHServer):

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def begin_auth(self, username):
        return False

    def session_requested(self):
        return SSHSession(**self.kwargs)


async def run_server(bind="localhost", port=8022, **kwargs):
    user_private_key = str(Path("~/.ssh/id_rsa").expanduser())
    user_public_key = str(Path("~/.ssh/id_rsa.pub").expanduser())

    server = await asyncssh.create_server(
        lambda: SSHServer(**kwargs),
        bind,
        port,
        server_host_keys=[user_private_key],
        authorized_client_keys=user_public_key,
        x11_forwarding=True,
        encoding=None,
    )
    bind, port = server.sockets[0].getsockname()
    print(f"Running ssh server on {bind}:{port}...")

    while True:
        await asyncio.sleep(60)


def main(args=None):
    parser = argparse.ArgumentParser(
        description='Gambatte terminal frontend over ssh')
    parser.add_argument('romfile', metavar='ROM', type=str)
    parser.add_argument('--bind', '-b', type=str, default="localhost")
    parser.add_argument('--port', '-p', type=int, default=8022)
    parser.add_argument('--test', '-t', action='store_true')
    parser.add_argument('--fast', '-f', action='store_true')
    args = parser.parse_args(args)
    kwargs = dict(args._get_kwargs())
    asyncio.run(run_server(**kwargs))


if __name__ == "__main__":
    main()