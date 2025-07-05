from importlib.util import find_spec


if __name__ == "__main__":
    if find_spec("piper") is None:
        import sys

        print(
            (
                "please ensure piper-tts is installed, "
                "it was not installed by I.S.A.A.C because "
                "of some complications with piper-tts installation.\n"
                'run "pip install piper-phonemize-fix==1.2.1 --no-deps piper-tts==1.2.0".'
            )
        )
        sys.exit(1)

    from isaac.cli import main

    main()
