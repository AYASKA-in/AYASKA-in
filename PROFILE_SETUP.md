# GitHub Profile Setup

This repo is ready to become `AYASKA-in/AYASKA-in`. The banner is already generated, the snake workflow is included, and the README has placeholder blocks for the self-hosted stats cards.

## 1. Upload the generated files

- Create or open the public GitHub repo named `AYASKA-in`.
- Upload `README.md`, `dark.svg`, `light.svg`, the `.github/workflows/` folder, `scripts/generate_banner.py`, and `PROFILE_SETUP.md`.

## 2. Self-host the GitHub Readme Stats cards

- Create a GitHub classic token at `Settings -> Developer settings -> Personal access tokens -> Tokens (classic)`.
- Give it the `repo` scope and copy it immediately. Do not paste it anywhere public.
- Fork `anuraghazra/github-readme-stats`.
- Import that fork into Vercel on the Hobby plan.
- Add environment variable `PAT_1` with your token, then deploy.
- Copy your Vercel hostname.
- In `README.md`, replace every `YOUR-README-STATS-INSTANCE` value with that hostname.
- Uncomment the block between `STATS BLOCK START` and `STATS BLOCK END`.

`hide_rank=true` is already set because the rank grade is driven heavily by stars and followers, which is a weak signal for a newer personal profile.

## 3. Enable the snake workflow

- In the GitHub repo, open `Settings -> Actions -> General`.
- Under `Workflow permissions`, choose `Read and write permissions`.
- Commit the included `.github/workflows/snake.yml`.
- Open the `Actions` tab and run `Generate Snake Animation` once.
- After the run finishes green, the `output` branch will exist.
- In `README.md`, uncomment the block between `SNAKE BLOCK START` and `SNAKE BLOCK END`.

## 4. Regenerate the banner if you want a new crop or a new photo

- From this repo root, run `python scripts/generate_banner.py --source ..\photo.jpeg`.
- If you swap in a new image, point `--source` at that file instead.
- The script rebuilds `dark.svg`, `light.svg`, and the portrait assets in `assets/`.

## 5. Content note

- The Bosch role is written as upcoming because the provided start date is August 2026 and today is July 29, 2026.
- The degree is phrased as completed because the provided graduation month is June 2026, which is already in the past.
- I left the phone number out of the public README for privacy.
