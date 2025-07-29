# Temple-Noble-Art

Automatically subscribe to lessons at [Temple Noble Art](https://www.temple-nobleart.com/).

## Features

-   **Automatic lesson registration**: Script to auto-register for lessons by lesson ID.
-   **Lesson status check**: See if you or a coach are registered for upcoming lessons.
-   **Retry logic**: Automatically retries registration if the lesson is full or during restricted hours.

## Requirements

-   Python 3.6+
-   [woob](https://woob.tech/) (Web Outside Of Browsers)
-   [termcolor](https://pypi.org/project/termcolor/)
-   [python-dateutil](https://pypi.org/project/python-dateutil/)

## Installation

1. **Clone the repository**
    ```bash
    git clone <repo_url>
    cd Temple-Noble-Art
    ```
2. **Install dependencies**
    ```bash
    pip install woob termcolor python-dateutil
    ```
3. **Create your configuration file**
    - Copy `config.example` to `config`:
        ```bash
        cp config.example config
        ```
    - Edit `config` and fill in your email and password:
        ```ini
        [credentials]
        email = <your_email>
        password = <your_password>
        ```

## Usage

### Register for a lesson by ID

```bash
python3 nobleart.py <lesson_id>
```

-   `<lesson_id>`: The 5-digit ID of the lesson you want to register for.

### Check registration status

-   To check if a partner or coach is registered for lessons:
    ```bash
    python3 nobleart.py <name>
    ```
    -   If `<name>` is a single word, it checks for a coach.
    -   If `<name>` contains spaces, it checks for a partner.

### Using the helper script (optional)

A helper script `nobleart.sh` is provided to repeatedly attempt registration:

```bash
./nobleart.sh <lesson_id>
```

## Notes

-   The script will avoid running between 3AM and 6AM (Europe/Paris timezone).
-   If a lesson is full, it will retry every 15 seconds until successful.
-   Make sure your credentials are correct in the `config` file.

## Credits

Built using [woob](https://woob.tech/)

## License

MIT License. See LICENSE file.
