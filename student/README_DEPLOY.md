Deployment notes

CI badge (add your repo owner/name):

```markdown
![CI](https://github.com/<owner>/<repo>/actions/workflows/ci.yml/badge.svg)
```

Replace `<owner>/<repo>` with your GitHub repository path.

Run locally with Docker:

```bash
docker build -t student-forum .
docker run -p 8000:8000 --env DJANGO_SETTINGS_MODULE=studentforum.settings student-forum
```

On Heroku, add a `SECRET_KEY` config var and use the provided `Procfile`:

```bash
heroku create
git push heroku main
heroku config:set SECRET_KEY="your-secret"
```

CI: GitHub Actions workflow at `.github/workflows/ci.yml` runs `flake8` and `pytest`.

Logo assets

- `static/images/logo.svg` — primary horizontal logo used in header
- `static/images/logo-mark.svg` — compact square mark for favicons and mobile
- `static/images/logo-small.svg` — small square for avatars and meta

Usage examples in templates:

```django
<img src="{% static 'images/logo.svg' %}" alt="StudentForum logo">
<img src="{% static 'images/logo-mark.svg' %}" alt="StudentForum mark" width="40" height="40">
```

If you'd like, I can generate PNG export variants (192x192, 512x512) and a `favicon.ico` next.
I generated a simple SVG `favicon.svg` and added `static/manifest.json`. To export PNG and ICO files locally on Windows you can run:

```powershell
mogrify -format png -resize 192x192 static/images/favicon.svg -path static/images/
mogrify -format png -resize 512x512 static/images/favicon.svg -path static/images/
# Create favicon.ico from 64/32/16 sizes
convert static/images/favicon.svg -resize 64 favicon-64.png
convert static/images/favicon.svg -resize 32 favicon-32.png
convert static/images/favicon.svg -resize 16 favicon-16.png
convert favicon-64.png favicon-32.png favicon-16.png static/images/favicon.ico
```

If you don't have ImageMagick (`mogrify`/`convert`), I can generate and add PNG/ICO files here.
