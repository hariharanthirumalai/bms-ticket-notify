import os

import re

import sys

import requests

NTFY_TOPIC = os.environ["NTFY_TOPIC"]  # your private ntfy.sh topic name

MOVIE = "Scene"

CINEMAS = {

    "KG Cinemas": "https://in.bookmyshow.com/cinemas/coimbatore/kg-cinemas-coimbatore/buytickets/KGCM/",

    "Karpagam Theatres": "https://in.bookmyshow.com/cinemas/coim/karpagam-theatres-4k-dolby-atmos-coimbatore/buytickets/KARP/",

    "Karpagam Grandplex": "https://in.bookmyshow.com/cinemas/coimbatore/karpagam-grandplex-sundarapuram/buytickets/KGNR/",

}

HEADERS = {

    "User-Agent": (

        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "

        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"

    ),

    "Accept-Language": "en-IN,en;q=0.9",

}

# Matches the title as a standalone word, e.g. "Scene" or "Scene (Tamil)",

# but not "scenes" or "Scene of the crime" in normal text.

TITLE_RE = re.compile(r'["\>]\s*Scene\s*(\(|"|<)', re.IGNORECASE)


def notify(title, message, click=None, priority="high"):

    headers = {"Title": title, "Priority": priority}

    if click:

        headers["Click"] = click

    requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=message.encode(), headers=headers, timeout=15)


def main():

    found = []

    blocked = []

    for name, url in CINEMAS.items():

        try:

            r = requests.get(url, headers=HEADERS, timeout=30)

        except requests.RequestException as e:

            print(f"{name}: request failed: {e}")

            blocked.append(name)

            continue

        print(f"{name}: HTTP {r.status_code}, {len(r.text)} bytes")

        if r.status_code != 200:

            blocked.append(name)

            continue

        if TITLE_RE.search(r.text):

            found.append((name, url))

    for name, url in found:

        notify(f"{MOVIE} bookings open!", f"{MOVIE} is now listed at {name}, Coimbatore.", click=url)

    if blocked and len(blocked) == len(CINEMAS):

        print("All pages blocked or failed; BookMyShow may be rejecting GitHub's servers.")

        # Notify only once per day-ish: run at minute 0-4 of hour 0 UTC

        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)

        if now.hour == 0 and now.minute < 5:

            notify("Scene checker blocked", "BookMyShow is blocking the checker.", priority="low")

    # Tell the workflow whether to switch itself off

    out = os.environ.get("GITHUB_OUTPUT")

    if out:

        with open(out, "a") as f:

            f.write(f"found={'true' if found else 'false'}\n")


if __name__ == "__main__":

    sys.exit(main())
 
