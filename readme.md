# Smart Forests Atlas

A tool to capture and narrate smart forests data, including fieldwork, interviews, social network analysis, maps and environmental data from instrumented forests.

See it live at https://atlas.smartforests.net

## Stack

- Django (fullstack django app, no js frontend)
- Bootstrap (css an' stuff)
- Wagtail (CMS, administration, editor workflows and storage)
- Webpack (asset pipeline)
- PostgreSQL (Database & search index)

## Hosting

- Digital Ocean (production)
- Fly.io (staging)

## Third party services

- Digital Ocean App Platform (Compute, database hosting, object storage & CDN)
- Mapbox

## Dev quickstart

### Easy mode: VSCode Dev Container

- Make sure you have Docker, VSCode, and the Remote Development extension installed.
- Open the repository in VSCode
- You should get a notification asking if you want to 'reopen in container'. Say yes.
  - If you don't get one, you should be able to 'reopen in container' via the command pallette
  - If you can't see an option to do that, make sure you have the Remote Development extension installed
- Wait for the dev container to build.
- Check your terminal and respond to any setup prompts it asks for
- Update `smartforests/settings/local.py` with the current correct settings & environment variables.
- Make sure VSCode has selected the correct python interpreter ('command palette > Python: Select Interpreter'). It should be set to the Python in the virtualenv (venv).
- Use vscode's 'run' command (usually aliased to F5) to run the app.
  - Make sure you use the 'App' configuration, which will start both the django app and the frontend build pipeline.
  - The `setup_pages` command in `manage.py` will set up the basic page structure in the development site.
- Go to localhost:8000/admin

### Hard mode: Using Dockerfiles

Figure it out for yourself based on the .devcontainer dockerfile and write it up here ;)

## Technical documentation

### Build process

This repository has a development dockerfile (.devcontainer/Dockerfile) and a production one (./Dockerfile).

They both run .bin in ./.bin to configure their environments and install dependencies:

- Base container configuration, which is run infrequently (installing apt packages, etc) should be configured in prepare.sh.
- Frequently-run .bin (installing pip packages, etc) should go in install.sh. The difference between these is that changing prepare.sh triggers a full rebuild of the development container, whereas install.sh is only run after the container is built.
- `build.sh` is the last thing run on deploy to production

### Seed content

```
python manage.py seed
```

Run `python manage.py seed --help` or check [source file](./smartforests/management/commands/seed.py) for options.

### Regenerating tag clouds and re-indexing logbooks

Producing tag clouds is a relatively computationally intensive operation, so we do it only occasionally with a Django management command.

```
python manage.py reindex_logbooks
```

This command:
- Saves all pages in order to update their location.
- Regenerates thumbnails for logbooks.
- Generates tag clouds.
- Creates a contributor page for each user.

You should run this command if you modify the save behaviour of models, or change the tag cloud generation algorithm.

### Background tasks to regenerate tag clouds

Tag clouds are also generated with a [background task](https://github.com/planetarypraxis/smartforests/blob/main/logbooks/tasks.py) using [django-background-tasks](https://django-background-tasks.readthedocs.io/en/latest/). This task is run 15 seconds [after a tag is saved](https://github.com/planetarypraxis/smartforests/blob/f6efb6a1ed87433df9d3d4c15e60afef34a5f310/logbooks/models/snippets.py#L21-L25). 

Reindexing all tags takes around 30 minutes.

### Translations

1. To (re)generate the message files (.po), run `yarn makemessages` or `python manage.py makemessages --locale=pt --locale=es --locale=fr --extension=html --ignore=env/**/*`
2. We use [django-deep-translate](https://pypi.org/project/django-deep-translator/) to automatically translate the message files. Ensure `DEEPL_TRANSLATE_KEY` is set in [`smartforests/settings/local.py`](./smartforests/settings/local.py) then run `python manage.py translate_messages`
3. After translation, you must compile the message files using `django-admin compilemessages`