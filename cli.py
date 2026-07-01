import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--transcript",
    required=True
)

parser.add_argument(
    "--phone",
    required=True
)

args = parser.parse_args()

print(args.transcript)

print(args.phone)
