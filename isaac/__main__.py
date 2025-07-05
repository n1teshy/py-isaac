from importlib.util import find_spec
import sys


def main():
    if find_spec("piper") is None:
        print(
            (
                "please ensure piper-tts is installed, "
                "it was not installed by I.S.A.A.C because "
                "of some complications with piper-tts installation.\n"
                'run "pip install piper-phonemize-fix==1.2.1 --no-deps piper-tts==1.2.0".'
            )
        )
        sys.exit(1)

    from isaac.cli import main as cli_main

    cli_main()


if __name__ == "__main__":
    main()
