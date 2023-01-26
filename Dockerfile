FROM ghcr.io/commonknowledge/do-app-baseimage-django-node@sha256:451f5e98c024ff3d03a92f7739d24a4d7ad0bb257f2518a908b3b470972ef940

# Install the project requirements and build.
COPY --chown=app:app .bin/install.sh Pipfile Pipfile.lock package.json yarn.lock ./
RUN SKIP_MIGRATE=1 bash install.sh
RUN yarn

# Copy the rest of the sources over
COPY --chown=app:app . ./
ENV DJANGO_SETTINGS_MODULE=smartforests.settings.production
ENV NODE_ENV=production

# Build
RUN pipenv run bash .bin/build.sh

# Run
EXPOSE ${PORT:-8080}
RUN pipenv run bash .bin/release.sh